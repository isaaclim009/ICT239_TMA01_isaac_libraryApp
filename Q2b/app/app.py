from app import app, db
from app.models.books import Book
from app.config import TITLES, BOOK_CATEGORIES, UI_CONFIG, MESSAGES
from flask import render_template
from app.models.users import User

# Import and register the books controller (Blueprint)
from app.controllers.booksController import books
from app.controllers.authentication import auth
from app.controllers.loansController import loans

app.register_blueprint(books)
app.register_blueprint(auth)
app.register_blueprint(loans)

# Make config variables available in all templates
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

# Automatically populate the book database on startup
try:
    with app.app_context():
        Book.bookDatabase()

        # Create admin user
        if not User.getUser('admin@lib.sg'):
            User.createUser('admin@lib.sg', 'Admin', '12345', is_admin=True)
            print("Created admin user: admin@lib.sg")

        # Create regular user
        if not User.getUser('poh@lib.sg'):
            User.createUser('poh@lib.sg', 'Peter Oh', '12345', is_admin=False)
            print("Created regular user: poh@lib.sg")
except Exception as e:
    print(f"Warning: Could not initialize database on startup: {e}")
