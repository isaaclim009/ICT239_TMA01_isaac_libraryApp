from app import db
from datetime import datetime, timedelta
from flask import current_app
import random
from .books import Book
from .users import User


class Loan(db.Document):
    meta = {'collection': 'loans'}

    # Required fields based on class diagram
    member = db.ReferenceField(User, required=True)  # User who borrowed the book
    book = db.ReferenceField(Book, required=True)    # Book that was borrowed
    borrowDate = db.DateTimeField(required=True)     # Date when book was borrowed
    returnDate = db.DateTimeField()                  # Date when book was returned (None if not returned)
    renewCount = db.IntField(default=0)              # Number of times loan has been renewed

    def __repr__(self):
        return f'<Loan {self.member.email} - {self.book.title}>'

    @property
    def due_date(self):
        """Calculate due date (2 weeks after borrow date)"""
        return self.borrowDate + timedelta(days=14)

    @property
    def is_overdue(self):
        """Check if loan is overdue"""
        if self.returnDate:  # Already returned
            return False
        # Use UTC for comparisons to avoid timezone-related shifts
        return datetime.utcnow() > self.due_date

    @property
    def is_returned(self):
        """Check if loan has been returned"""
        return self.returnDate is not None

    @property
    def can_renew(self):
        """Check if loan can be renewed (not overdue and renew count < 2)"""
        return not self.is_returned and not self.is_overdue and self.renewCount < 2

    @property
    def can_return(self):
        """Check if loan can be returned (not already returned)"""
        return not self.is_returned

    @property
    def can_delete(self):
        """Check if loan can be deleted (only returned loans)"""
        return self.is_returned

    @staticmethod
    def create_loan(user, book, borrow_date=None):
        """
        Create a new loan document.

        Args:
            user: User object who is borrowing the book
            book: Book object being borrowed
            borrow_date: Optional datetime for borrow date, if None will generate random date

        Returns:
            Loan object if successful

        Raises:
            Exception with appropriate error message
        """
        # Check if user already has an unreturned loan for the same book title
        existing_loan = Loan.objects(
            member=user,
            book=book,
            returnDate__exists=False  # No return date means not returned
        ).first()

        if existing_loan:
            raise Exception(f"You already have an unreturned loan for '{book.title}'")

        # Check if book is available
        if book.available <= 0:
            raise Exception(f"'{book.title}' is currently not available for loan")

        # Generate random borrow date if not provided (10-20 days before now UTC)
        if borrow_date is None:
            days_ago = random.randint(10, 20)
            borrow_date = datetime.utcnow() - timedelta(days=days_ago)

            # Log generated borrow date and days_ago for debugging
            try:
                current_app.logger.info(
                    f"create_loan: user={getattr(user, 'email', None)} book={getattr(book, 'title', None)} days_ago={days_ago} borrow_date={borrow_date}"
                )
            except Exception:
                pass

        # Create the loan
        loan = Loan(
            member=user,
            book=book,
            borrowDate=borrow_date,
            renewCount=0,
        )
        loan.save()

        # Update book's available count
        book.borrow(1)

        return loan

    @staticmethod
    def get_user_loans(user, include_returned=True):
        """
        Retrieve all loans for a specific user.

        Args:
            user: User object
            include_returned: If False, only return unreturned loans

        Returns:
            QuerySet of Loan objects sorted by borrow date (descending)
        """
        query = Loan.objects(member=user)

        if not include_returned:
            query = query.filter(returnDate__exists=False)

        return query.order_by('-borrowDate')

    @staticmethod
    def get_loan_by_id(loan_id):
        """
        Retrieve a specific loan by ID.

        Args:
            loan_id: String ID of the loan

        Returns:
            Loan object or None if not found
        """
        try:
            return Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return None

    def renew_loan(self):
        """
        Renew the loan by updating renew count and borrow date.

        Returns:
            Updated Loan object

        Raises:
            Exception if loan cannot be renewed
        """
        if not self.can_renew:
            if self.is_returned:
                raise Exception("Cannot renew a returned loan")
            elif self.is_overdue:
                raise Exception("Cannot renew an overdue loan")
            elif self.renewCount >= 2:
                raise Exception("Maximum renewal limit (2) reached")

        # Generate new borrow date (10-20 days after current borrow date)
        days_to_add = random.randint(10, 20)
        candidate = self.borrowDate + timedelta(days=days_to_add)

        # Cap the new borrow date to now (UTC) (cannot be later than now)
        now = datetime.utcnow()
        new_borrow_date = candidate if candidate <= now else now

        # Ensure borrowDate does not move backwards (monotonic)
        if new_borrow_date < self.borrowDate:
            new_borrow_date = self.borrowDate

        # Only apply and count the renewal if the borrow date actually moves forward
        if new_borrow_date > self.borrowDate:
            self.borrowDate = new_borrow_date
            self.renewCount += 1
        else:
            # No effective change possible; treat as invalid renewal attempt
            raise Exception("Cannot renew loan because the new borrow date would not move forward")

        self.save()

        return self

    def return_loan(self):
        """
        Return the loan by setting return date and updating book availability.

        Returns:
            Updated Loan object

        Raises:
            Exception if loan cannot be returned
        """
        if not self.can_return:
            raise Exception("Loan has already been returned")

        # Set return date to now (UTC) to reflect actual return action
        now = datetime.utcnow()
        return_date = now

        # Ensure return date is not earlier than borrow date
        if return_date < self.borrowDate:
            return_date = self.borrowDate

        self.returnDate = return_date
        self.save()

        # Update book's available count
        self.book.return_book(1)

        return self

    def delete_loan(self):
        """
        Delete the loan document.

        Raises:
            Exception if loan cannot be deleted
        """
        if not self.can_delete:
            raise Exception("Only returned loans can be deleted")

        self.delete()

    @staticmethod
    def get_loans_by_book(book):
        """
        Helper method to get all loans for a specific book.

        Args:
            book: Book object

        Returns:
            QuerySet of Loan objects
        """
        return Loan.objects(book=book).order_by('-borrowDate')

    @staticmethod
    def get_overdue_loans():
        """
        Helper method to get all overdue loans.

        Returns:
            QuerySet of overdue Loan objects
        """
        current_date = datetime.utcnow()
        two_weeks_ago = current_date - timedelta(days=14)

        return Loan.objects(
            returnDate__exists=False,  # Not returned
            borrowDate__lt=two_weeks_ago  # Borrowed more than 2 weeks ago
        ).order_by('-borrowDate')

    @staticmethod
    def get_loan_statistics(user=None):
        """
        Helper method to get loan statistics.

        Args:
            user: Optional User object to get stats for specific user

        Returns:
            Dictionary with loan statistics
        """
        if user:
            query = Loan.objects(member=user)
        else:
            query = Loan.objects()

        total_loans = query.count()
        active_loans = query.filter(returnDate__exists=False).count()
        returned_loans = query.filter(returnDate__exists=True).count()

        return {
            'total_loans': total_loans,
            'active_loans': active_loans,
            'returned_loans': returned_loans,
        }
