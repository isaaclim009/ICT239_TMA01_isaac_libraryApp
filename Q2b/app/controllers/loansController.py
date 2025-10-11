from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.config import TITLES, UI_CONFIG, MESSAGES
from app.models.loans import Loan
from app.models.books import Book
from app.models.users import User
from datetime import datetime

# Create Blueprint for loan-related routes
loans = Blueprint('loans', __name__)

@loans.route('/make_loan/<book_id>')
@login_required
def make_loan(book_id):
    """
    Create a loan for the current user for the specified book.
    This route is accessed via Make Loan buttons in book views.
    """
    # Check if user is admin - admins cannot make loans
    if current_user.is_admin:
        flash('Admin users cannot borrow books.', 'error')
        return redirect(url_for('books.book_titles'))
    
    try:
        # Get the book
        book = Book.objects.get(id=book_id)
        
        # Create the loan
        loan = Loan.create_loan(current_user, book)

        # Log and flash borrow date and due date to help debug any datetime issues
        borrow_dt = loan.borrowDate
        due_dt = loan.due_date
        try:
            # use app logger if available
            from app import app as flask_app
            flask_app.logger.info(f"Loan created: user={current_user.email}, book={book.title}, borrowDate={borrow_dt}, dueDate={due_dt}")
        except Exception:
            pass

        flash(f'Successfully borrowed "{book.title}". Borrow Date: {borrow_dt.strftime("%d %b %Y")}. Due Date: {due_dt.strftime("%d %b %Y")}.', 'success')
        # Redirect to the loans page so the user can immediately see their active loans
        return redirect(url_for('loans.view_loans'))
    except Book.DoesNotExist:
        flash('Book not found.', 'error')
    except Exception as e:
        msg = str(e)
        flash(msg, 'error')
        # For any other exception (e.g., not available, already have unreturned loan),
        # redirect the user to their loans page so they can see current loan state.
        return redirect(url_for('loans.view_loans'))

    # If we reach here it means loan creation didn't succeed for other reasons
    # Redirect back to where they came from or book titles
    referrer = request.referrer
    if referrer and 'book_details' in referrer:
        return redirect(url_for('books.book_details', book_id=book_id))
    else:
        return redirect(url_for('books.book_titles'))

@loans.route('/loans')
@login_required
def view_loans():
    """
    Display all loans for the current user with management options.
    """
    # Check if user is admin - redirect admins away
    if current_user.is_admin:
        flash('Admin users do not have loan records.', 'info')
        return redirect(url_for('books.book_titles'))
    
    # Get all loans for the current user
    user_loans = Loan.get_user_loans(current_user)
    
    # Prepare loan data for template
    loans_data = []
    for loan in user_loans:
        loan_info = {
            'id': str(loan.id),
            'book_title': loan.book.title,
            'book_authors': ', '.join(loan.book.authors),
            'book_url': loan.book.url,
            'borrow_date': loan.borrowDate,
            'due_date': loan.due_date,
            'return_date': loan.returnDate,
            'renew_count': loan.renewCount,
            'is_overdue': loan.is_overdue,
            'is_returned': loan.is_returned,
            'can_renew': loan.can_renew,
            'can_return': loan.can_return,
            'can_delete': loan.can_delete
        }
        loans_data.append(loan_info)
    
    return render_template('loans.html', 
                         loans=loans_data, 
                         panel="CURRENT LOANS",
                         no_loans_message="No loan currently" if not loans_data else None)

@loans.route('/renew_loan/<loan_id>')
@login_required
def renew_loan(loan_id):
    """
    Renew a specific loan for the current user.
    """
    try:
        loan = Loan.get_loan_by_id(loan_id)
        
        if not loan:
            flash('Loan not found.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        # Check if loan belongs to current user
        if loan.member != current_user:
            flash('You can only renew your own loans.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        # Renew the loan
        loan.renew_loan()
        
        flash(f'Successfully renewed "{loan.book.title}". New due date: {loan.due_date.strftime("%d %b %Y")}.', 'success')
        
    except Exception as e:
        flash(str(e), 'error')
    
    return redirect(url_for('loans.view_loans'))

@loans.route('/return_loan/<loan_id>')
@login_required
def return_loan(loan_id):
    """
    Return a specific loan for the current user.
    """
    try:
        loan = Loan.get_loan_by_id(loan_id)
        
        if not loan:
            flash('Loan not found.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        # Check if loan belongs to current user
        if loan.member != current_user:
            flash('You can only return your own loans.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        # Return the loan
        book_title = loan.book.title
        loan.return_loan()
        
        flash(f'Successfully returned "{book_title}".', 'success')
        
    except Exception as e:
        flash(str(e), 'error')
    
    return redirect(url_for('loans.view_loans'))

@loans.route('/delete_loan/<loan_id>')
@login_required
def delete_loan(loan_id):
    """
    Delete a specific returned loan for the current user.
    """
    try:
        loan = Loan.get_loan_by_id(loan_id)
        
        if not loan:
            flash('Loan not found.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        # Check if loan belongs to current user
        if loan.member != current_user:
            flash('You can only delete your own loans.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        # Delete the loan
        book_title = loan.book.title
        loan.delete_loan()
        
        flash(f'Successfully deleted loan record for "{book_title}".', 'success')
        
    except Exception as e:
        flash(str(e), 'error')
    
    return redirect(url_for('loans.view_loans'))

# Helper function for template context
@loans.app_template_filter('format_date')
def format_date(date):
    """Format date for display in templates"""
    if date:
        return date.strftime('%d %b %Y')
    return ''

# Context processor to add loan-related data to all templates
@loans.app_context_processor
def inject_loan_context():
    """Inject loan-related context into all templates"""
    context = {}
    
    if current_user.is_authenticated and not current_user.is_admin:
        # Get current user's active loans count
        active_loans = Loan.objects(member=current_user, returnDate__exists=False).count()
        context['active_loans_count'] = active_loans
    
    return context
