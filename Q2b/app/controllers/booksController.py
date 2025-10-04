from flask import Blueprint, render_template, request
from app.config import BOOK_CATEGORIES, UI_CONFIG, MESSAGES
from app.models.books import Book

books = Blueprint('books', __name__)

@books.route('/', methods=['GET', 'POST'])
def book_titles():
    """Display filtered and sorted book titles with previews"""
    category_filter = request.form.get('category', 'All')

    if category_filter != 'All':
        filtered_books = Book.objects(category=category_filter)
    else:
        filtered_books = Book.objects()

    sorted_books = filtered_books.order_by('title')

    return render_template('bookTitles.html', 
                         books=sorted_books, 
                         book_count=sorted_books.count(),
                         selected_category=category_filter,
                         categories=BOOK_CATEGORIES)

@books.route('/book/<book_id>')
def book_details(book_id):
    """Display detailed view of a specific book"""
    try:
        book = Book.objects.get(id=book_id)
        return render_template('bookDetails.html', book=book)
    except Book.DoesNotExist:
        return render_template('bookDetails.html', 
                             book=None, 
                             error_message=MESSAGES['book_not_found'])