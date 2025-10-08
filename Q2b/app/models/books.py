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
    # Get the category filter from the form (default is 'All')
    category_filter = request.form.get('category', 'All')
    
    # Filter books by category using MongoDB queries
    if category_filter != 'All':
        filtered_books = Book.objects(category=category_filter)
    else:
        filtered_books = Book.objects()

    # Sort books by title (MongoDB query)
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
        # Get the book details from MongoDB using ObjectId
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
        # Handle case where book_id is invalid
        return render_template('bookDetails.html', 
                             book=None, 
                             error_message=MESSAGES['book_not_found'])
    except Exception as e:
        # Handle other errors (invalid ObjectId format, etc.)
        return render_template('bookDetails.html', 
                             book=None, 
                             error_message=MESSAGES['book_not_found'])

@books.route('/db-status')
def db_status():
    """Check database status"""
    try:
        # Try to count books instead of server_info which can cause socket issues
        book_count = Book.objects.count()
        return f"MongoDB connected successfully<br>Books in database: {book_count}<br>Application is now using MongoDB data"
    except Exception as e:
        return f"Database error: {str(e)}<br>Try restarting the app to reinitialize the database."

@books.route('/add-book', methods=['GET', 'POST'])
@login_required
def add_book():
    """Add new book - Admin only"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('books.book_titles'))
    
    form = AddBookForm()
    
    if request.method == 'POST':
        # Process form data to handle checkbox genres properly
        form.process(request.form)
        
        # Handle "Add More Authors" button
        if 'add_author' in request.form:
            current_count = session.get('author_count', 5)
            session['author_count'] = current_count + 1
            return render_template('addBook.html', form=form, panel="ADD A BOOK")
        
        # Handle form submission (when submit button is clicked)
        if 'submit' in request.form or 'confirm_duplicate' in request.form or 'confirm_repeated_authors' in request.form:
            if form.validate():
                try:
                    # Collect authors (skip empty fields)
                    authors = []
                    
                    # Get the standard form authors (1-5)
                    for i in range(1, 6):
                        author = getattr(form, f'author{i}').data
                        if author and author.strip():
                            # Check if this author is also an illustrator
                            is_illustrator = getattr(form, f'illustrator{i}').data
                            author_name = author.strip()
                            if is_illustrator:
                                author_name += " (Illustrator)"
                            authors.append(author_name)
                    
                    # Get dynamically added authors from form data
                    author_count = session.get('author_count', 5)
                    for i in range(6, author_count + 1):
                        author = request.form.get(f'author{i}')
                        if author and author.strip():
                            author_name = author.strip()
                            # Check if this dynamic author is also an illustrator
                            if request.form.get(f'illustrator{i}'):
                                author_name += " (Illustrator)"
                            authors.append(author_name)
                    
                    # Check for repeated authors within the same book (only if not confirming)
                    if 'confirm_repeated_authors' not in request.form and 'confirm_duplicate' not in request.form:
                        # Normalize authors for comparison (remove illustrator tag and convert to lowercase)
                        normalized_authors = [author.lower().replace(' (illustrator)', '') for author in authors]
                        
                        # Check for duplicates in the list
                        if len(normalized_authors) != len(set(normalized_authors)):
                            # Find which authors are repeated
                            repeated_authors = []
                            seen = set()
                            for author in normalized_authors:
                                if author in seen and author not in repeated_authors:
                                    repeated_authors.append(author)
                                seen.add(author)
                            
                            # Show repeated authors modal
                            return render_template('addBook.html', form=form, panel="ADD A BOOK", 
                                                 show_repeated_authors_modal=True, 
                                                 repeated_authors=repeated_authors)
                    
                    # Check for potential duplicates (only if not confirming)
                    if 'confirm_duplicate' not in request.form and 'confirm_repeated_authors' not in request.form:
                        # Check if a book with same title and at least one matching author exists
                        existing_books = Book.objects(title__iexact=form.title.data.strip())
                        
                        for existing_book in existing_books:
                            # Check if any author matches (case insensitive)
                            existing_authors = [author.lower().replace(' (illustrator)', '') for author in existing_book.authors]
                            new_authors = [author.lower().replace(' (illustrator)', '') for author in authors]
                            
                            if any(new_author in existing_authors for new_author in new_authors):
                                # Potential duplicate found - show confirmation modal
                                return render_template('addBook.html', form=form, panel="ADD A BOOK", 
                                                     show_duplicate_modal=True, 
                                                     existing_book=existing_book)
                    
                    # Process description - preserve line breaks
                    description_text = form.description.data
                    # Split by single newlines and filter out empty lines
                    description_lines = [line.strip() for line in description_text.split('\n') if line.strip()]
                    
                    # Create book data
                    book_data = {
                        'title': form.title.data,
                        'genres': form.genres.data,
                        'category': form.category.data,
                        'authors': authors,
                        'url': form.url.data,
                        'description': description_lines,  # Now stores as list of lines
                        'pages': form.pages.data,
                        'copies': form.copies.data,
                        'available': form.copies.data  # Initially all copies are available
                    }
                    
                    # Save book to database
                    Book.create_book(book_data)
                    
                    # Clear session data and form data after successful submission
                    session.pop('author_count', None)
                    
                    # Flash success message and stay on same page with fresh form
                    flash(f'Book "{form.title.data}" has been successfully added to the library!', 'success')
                    
                    # Create a fresh form for the next book
                    form = AddBookForm()
                    return render_template('addBook.html', form=form, panel="ADD A BOOK")
                    
                except Exception as e:
                    flash(f'Error adding book: {str(e)}', 'error')
                    return render_template('addBook.html', form=form, panel="ADD A BOOK")
            else:
                # Form validation failed - show errors
                flash('Please correct the errors below and try again.', 'error')
                return render_template('addBook.html', form=form, panel="ADD A BOOK")
    else:
        # Clear session data on GET request (new form)
        session.pop('author_count', None)
    
    return render_template('addBook.html', form=form, panel="ADD A BOOK")
