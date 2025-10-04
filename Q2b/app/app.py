from flask import render_template, request
from books.books import all_books  # Import the book data from book.py
from app.config import TITLES, BOOK_CATEGORIES, UI_CONFIG, MESSAGES
from app import app, db
from app.models.books import Book

# Import and register the books controller
from app.controllers.booksController import books
from app.controllers.authentication import auth

app.register_blueprint(books)
app.register_blueprint(auth)

# Configure Flask app to serve static files from assets folder
app.static_folder = 'assets'

# Make config available in templates
@app.context_processor
def inject_config():
    """Make configuration variables available in all templates"""
    return {
        'config': {
            'TITLES': TITLES,
            'BOOK_CATEGORIES': BOOK_CATEGORIES,
            'UI_CONFIG': UI_CONFIG,
            'MESSAGES': MESSAGES
        }
    }

# Automatically upload books on app startup
try:
    with app.app_context():
        Book.bookDatabase()
        
        # Create default users
        from app.models.users import User
        
        # Create admin user
        admin_user = User.getUser('admin@lib.sg')
        if not admin_user:
            User.createUser('admin@lib.sg', 'Admin', '12345', is_admin=True)
            print("Created admin user: admin@lib.sg")
        
        # Create regular user
        regular_user = User.getUser('poh@lib.sg')
        if not regular_user:
            User.createUser('poh@lib.sg', 'Peter Oh', '12345', is_admin=False)
            print("Created regular user: poh@lib.sg")
            
except Exception as e:
    print(f"Warning: Could not initialize database on startup: {e}")
    print("You can manually upload books by visiting /db-status route")