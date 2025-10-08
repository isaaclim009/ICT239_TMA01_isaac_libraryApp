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
    def create_book(book_data):
        """
        Create a new book and save to database
        """
        try:
            book = Book(**book_data)
            book.save()
            return book
        except Exception as e:
            raise Exception(f"Error creating book: {str(e)}")

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