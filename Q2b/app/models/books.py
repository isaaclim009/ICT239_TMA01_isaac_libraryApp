from app import db
from books.books import all_books  # Import the global book data

class Book(db.Document):
    meta = {'collection': 'books'}
    genres = db.ListField(db.StringField(), required=True)
    title = db.StringField(required=True)
    category = db.StringField(required=True)  # Changed from ListField to StringField
    url = db.StringField()  # URL to the book cover image
    description = db.ListField(db.StringField(), required=True)  # List of paragraphs
    authors = db.ListField(db.StringField(), required=True)  # Changed to ListField for multiple authors
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
        """
        Create a new book and save to database
        """
        try:
            book = Book(**book_data)
            book.save()
            return book
        except Exception as e:
            raise Exception(f"Error creating book: {str(e)}")

    def borrow(self, quantity=1):
        """
        Borrow a given quantity of this book.
        Decrements `available` by `quantity` and saves the document.

        Sanity checks:
        - quantity must be a positive integer
        - there must be at least `quantity` available copies

        Returns the updated Book instance on success.
        Raises ValueError or Exception on invalid operations.
        """
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

        # perform the borrow
        self.available = self.available - qty
        if self.available < 0:
            # extra guard - should not happen because of check above
            self.available = 0
        self.save()
        return self

    def return_book(self, quantity=1):
        """
        Return a given quantity of this book.
        Increments `available` by `quantity` and saves the document.

        Sanity checks:
        - quantity must be a positive integer
        - cannot return more copies than have been borrowed (i.e., borrowed = copies - available)

        Returns the updated Book instance on success.
        Raises ValueError or Exception on invalid operations.
        """
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be an integer")

        if qty <= 0:
            raise ValueError("Quantity to return must be positive")

        # Ensure numeric fields are set
        total_copies = int(self.copies or 0)
        avail = int(self.available or 0)

        borrowed = total_copies - avail
        if borrowed <= 0:
            raise Exception("No copies of this title are currently borrowed")

        if qty > borrowed:
            raise Exception("Cannot return more copies than have been borrowed")

        # perform the return
        self.available = avail + qty
        # ensure available does not exceed total copies
        if self.available > total_copies:
            self.available = total_copies
        self.save()
        return self
    
    @staticmethod
    def bookDatabase():
        """
        Check each book from all_books and add to database if title doesn't exist.
        This prevents duplicates and allows for incremental additions.
        """
        books_added = 0
        books_skipped = 0
        
        print("Checking books for database upload...")
        
        # Check each book individually by title
        for book_data in all_books:
            try:
                title = book_data.get('title', '')
                
                # Check if book with this title already exists
                if not Book.objects(title=title).first():
                    # Create a new Book instance with the data
                    book = Book(**book_data)
                    book.save()
                    books_added += 1
                else:
                    books_skipped += 1
                    
            except Exception as e:
                print(f"Error saving book {book_data.get('title', 'Unknown')}: {e}")
        
        print(f"Database update complete. Added Books: {books_added}, Skipped Books: {books_skipped}")
        return books_added, books_skipped