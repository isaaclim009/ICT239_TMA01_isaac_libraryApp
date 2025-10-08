APP_NAME = "SG Library"
APP_DESCRIPTION = "Singapore Library Management System"

TITLES = {
    'home': '📚 Book Titles',
    'book_details': '📚 Book Details',
    'base': 'SG Library'
}

BOOK_CATEGORIES = [
    ('All', 'All'),
    ('Children', 'Children'),
    ('Teens', 'Teens'),
    ('Adult', 'Adult')
]

UI_CONFIG = {
    'books_per_page': None,
    'max_description_preview': 2,
    'card_shadow': '4px 4px 12px 0 rgba(0,0,0,0.18)',
    'border_radius': '8px'
}

COLORS = {
    'primary': '#bed1be',
    'secondary': '#def0e2',
    'success': '#198754',
    'light': '#f4f4f4',
    'dark': '#333333',
    'shadow': 'rgba(0,0,0,0.18)'
}

MESSAGES = {
    'no_books': 'No books found for the selected category.',
    'book_not_found': 'Book not found.',
    'search_placeholder': 'Search by category...'
}

FONTS = {
    'primary': "'Montserrat', Helvetica, Arial, sans-serif",
    'weight_normal': '400',
    'weight_bold': '700'
}
