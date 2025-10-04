from flask import Flask, render_template, request
from books.books import all_books
from config import TITLES, BOOK_CATEGORIES, UI_CONFIG, MESSAGES

app = Flask(__name__)

app.static_folder = 'assets'

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

@app.route('/', methods=['GET', 'POST'])
def book_titles():
    """Display filtered and sorted book titles with previews"""
    category_filter = request.form.get('category', 'All')
    
    filtered_books = all_books
    if category_filter != 'All':
        filtered_books = [book for book in all_books if category_filter in book['category']]

    sorted_books = sorted(filtered_books, key=lambda x: x['title'])

    for i, book in enumerate(sorted_books):
        original_index = all_books.index(book)
        book['original_index'] = original_index
        
        paragraphs = book['description']
        max_preview = UI_CONFIG['max_description_preview']
        if len(paragraphs) > 1 and max_preview >= 2:
            book['description_preview'] = f"{paragraphs[0]}<br><br>{paragraphs[-1]}"
        else:
            book['description_preview'] = paragraphs[0] if paragraphs else ""

    return render_template('bookTitles.html', 
                         books=sorted_books, 
                         book_count=len(sorted_books),
                         selected_category=category_filter,
                         categories=BOOK_CATEGORIES)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    """Display detailed view of a specific book"""
    try:
        book = all_books[book_id]
        return render_template('bookDetails.html', book=book)
    except IndexError:
        return render_template('bookDetails.html', 
                             book=None, 
                             error_message=MESSAGES['book_not_found'])

if __name__ == '__main__':
    app.run(debug=True)

