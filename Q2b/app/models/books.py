from app import db
from books.books import all_books  # Import the global book data

class Book(db.Document):
    meta = {'collection': 'books'}
    genres = db.ListField(db.StringField(), required=True)
    title = db.StringField(required=True)
    category = db.StringField(required=True)
    url = db.StringField()
    description = db.ListField(db.StringField(), required=True)
    authors = db.ListField(db.StringField(), required=True)
    pages = db.IntField()
    available = db.IntField()
    copies = db.IntField()

    @staticmethod
    def getTitles(title):
        try:
            return Book.objects.get(title=title)
        except Book.DoesNotExist:
            return None

    @staticmethod
    def saveBook(book_data):
        book = Book(**book_data)
        book.save()
        return book

    @staticmethod
    def create_book(book_data):
        try:
            book = Book(**book_data)
            book.save()
            return book
        except Exception as e:
            raise Exception(f"Error creating book: {str(e)}")

    def borrow(self, quantity=1):
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be an integer")

        if qty <= 0:
            raise ValueError("Quantity to borrow must be positive")

        if self.available is None:
            self.available = 0

        if self.available < qty:
            raise Exception("Not enough available copies to borrow")

        self.available = self.available - qty
        if self.available < 0:
            self.available = 0
        self.save()
        return self

    def return_book(self, quantity=1):
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be an integer")

        if qty <= 0:
            raise ValueError("Quantity to return must be positive")

        total_copies = int(self.copies or 0)
        avail = int(self.available or 0)
        borrowed = total_copies - avail

        if borrowed <= 0:
            raise Exception("No copies of this title are currently borrowed")

        if qty > borrowed:
            raise Exception("Cannot return more copies than have been borrowed")

        self.available = avail + qty
        if self.available > total_copies:
            self.available = total_copies
        self.save()
        return self

    @staticmethod
    def bookDatabase():
        """
        Check each book from all_books and add to database if title doesn't exist.
        """
        books_added = 0
        books_skipped = 0

        print("Checking books for database upload...")

        for book_data in all_books:
            try:
                title = book_data.get('title', '')
                if not Book.objects(title=title).first():
                    book = Book(**book_data)
                    book.save()
                    books_added += 1
                else:
                    books_skipped += 1
            except Exception as e:
                print(f"Error saving book {book_data.get('title', 'Unknown')}: {e}")

        print(f"Database update complete. Added Books: {books_added}, Skipped Books: {books_skipped}")
        return books_added, books_skipped