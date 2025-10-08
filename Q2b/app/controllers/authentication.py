from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash
from app import app

from app.models.forms import RegisterForm, LoginForm
from app.models.users import User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate():
            existing_user = User.getUser(email=form.email.data)
            if not existing_user:
                User.createUser(email=form.email.data, password=form.password.data, name=form.name.data)
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                form.email.errors.append("User already exists")
    return render_template('register.html', form=form, panel="REGISTER")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate():
            user = User.getUser(email=form.email.data)
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('books.book_titles'))      
            else:
                if user:
                    form.password.errors.append("Incorrect password")
                else:
                    form.email.errors.append("No user found with this email")
    return render_template('login.html', form=form, panel="LOGIN")

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('books.book_titles'))
