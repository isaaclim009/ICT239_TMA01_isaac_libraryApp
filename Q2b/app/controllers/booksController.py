from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.config import TITLES, BOOK_CATEGORIES, UI_CONFIG, MESSAGES
from app.models.books import Book
from app.models.forms import AddBookForm

# Create Blueprint for book-related routes
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

    # Convert to list and add preview descriptions
    books_list = []
    for book in sorted_books:
        book_dict = {
            'id': str(book.id),  # Use MongoDB ObjectId as identifier
            'title': book.title,
            'category': book.category,
            'genres': book.genres,
            'authors': book.authors,
            'url': book.url,
            'pages': book.pages,
            'available': book.available,
            'copies': book.copies,
            'description': book.description
        }
        
        # Create description preview
        paragraphs = book.description
        if 'max_description_preview' in UI_CONFIG:
            max_preview = UI_CONFIG['max_description_preview']
            if len(paragraphs) > 1 and max_preview >= 2:
                book_dict['description_preview'] = f"{paragraphs[0]}<br><br>{paragraphs[-1]}"
            else:
                book_dict['description_preview'] = paragraphs[0] if paragraphs else ""
        
        books_list.append(book_dict)

    return render_template('bookTitles.html', 
                         books=books_list, 
                         book_count=len(books_list),
                         selected_category=category_filter,
                         categories=BOOK_CATEGORIES)

@books.route('/book/<book_id>')
def book_details(book_id):
    """Display detailed view of a specific book"""
    try:
        book = Book.objects.get(id=book_id)
        
        # Convert to dict for template compatibility
        book_dict = {
            'id': str(book.id),
            'title': book.title,
            'category': book.category,
            'genres': book.genres,
            'authors': book.authors,
            'url': book.url,
            'pages': book.pages,
            'available': book.available,
            'copies': book.copies,
            'description': book.description
        }
        
        return render_template('bookDetails.html', book=book_dict)
    except Book.DoesNotExist:
        return render_template('bookDetails.html', 
                             book=None, 
                             error_message=MESSAGES['book_not_found'])
    except Exception as e:
        return render_template('bookDetails.html', 
                             book=None, 
                             error_message=MESSAGES['book_not_found'])