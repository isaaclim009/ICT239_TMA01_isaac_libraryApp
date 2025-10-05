from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import Email, Length, InputRequired, DataRequired, NumberRange

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=20)])
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=20)])
    submit = SubmitField('Submit')

class AddBookForm(FlaskForm):    
    # Multiple genres selection
    genres = SelectMultipleField('Choose multiple Genres', 
                                choices=[
                                    ('Animals', 'Animals'),
                                    ('Business', 'Business'),
                                    ('Comics', 'Comics'),
                                    ('Communication', 'Communication'),
                                    ('Dark Academia', 'Dark Academia'),
                                    ('Emotion', 'Emotion'),
                                    ('Fantasy', 'Fantasy'),
                                    ('Fiction', 'Fiction'),
                                    ('Friendship', 'Friendship'),
                                    ('Graphic Novels', 'Graphic Novels'),
                                    ('Grief', 'Grief'),
                                    ('Historical Fiction', 'Historical Fiction'),
                                    ('Indigenous', 'Indigenous'),
                                    ('Inspirational', 'Inspirational'),
                                    ('Magic', 'Magic'),
                                    ('Mental Health', 'Mental Health'),
                                    ('Nonfiction', 'Nonfiction'),
                                    ('Personal Development', 'Personal Development'),
                                    ('Philosophy', 'Philosophy'),
                                    ('Picture Books', 'Picture Books'),
                                    ('Poetry', 'Poetry'),
                                    ('Productivity', 'Productivity'),
                                    ('Psychology', 'Psychology'),
                                    ('Romance', 'Romance'),
                                    ('School', 'School'),
                                    ('Self Help', 'Self Help'),
                                    ('Science', 'Science'),
                                    ('Technology', 'Technology')
                                ])

    # Title
    title = StringField('Title:', validators=[InputRequired(), Length(max=200)])
    
    # Category selection
    category = SelectField('Choose a category:', 
                          choices=[
                              ('Children', 'Children'),
                              ('Teens', 'Teens'),
                              ('Adult', 'Adult')
                          ],
                          validators=[InputRequired()])
    
    # URL for cover
    url = StringField('URL for Cover:')
    
    # Description
    description = TextAreaField('Description:', validators=[InputRequired()])
    
    # Authors (up to 5)
    author1 = StringField('Author 1:', validators=[InputRequired()])
    author2 = StringField('Author 2:')
    author3 = StringField('Author 3:')
    author4 = StringField('Author 4:') 
    author5 = StringField('Author 5:')
    
    # Illustrator checkboxes
    illustrator1 = BooleanField('Illustrator')
    illustrator2 = BooleanField('Illustrator')
    illustrator3 = BooleanField('Illustrator')
    illustrator4 = BooleanField('Illustrator')
    illustrator5 = BooleanField('Illustrator')
    
    # Number fields
    pages = IntegerField('Number of pages:', validators=[InputRequired(), NumberRange(min=1)])
    copies = IntegerField('Number of copies:', validators=[InputRequired(), NumberRange(min=1)])
    
    submit = SubmitField('Submit')
