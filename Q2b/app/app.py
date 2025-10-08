from app import app, db
from app.models.books import Book
from app.config import TITLES, BOOK_CATEGORIES, UI_CONFIG, MESSAGES
from flask import render_template

# Import and register the books controller (Blueprint)
from app.controllers.booksController import books
app.register_blueprint(books)

# We will register other blueprints for auth and loans here in later steps

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
except Exception as e:
    print(f"Warning: Could not initialize database on startup: {e}")
