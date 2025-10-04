from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Document):
    meta = {'collection': 'libraryUsers'}
    email = db.StringField(max_length=30, required=True, unique=True)
    password = db.StringField(required=True)
    name = db.StringField(max_length=50, required=True)
    is_admin = db.BooleanField(default=False)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hashed password"""
        return check_password_hash(self.password, password)
    
    @staticmethod
    def getUser(email):
        """Get user by email"""
        return User.objects(email=email).first()

    @staticmethod
    def getUserById(user_id):
        """Get user by ID"""
        return User.objects(pk=user_id).first()
    
    @staticmethod 
    def createUser(email, name, password, is_admin=False):
        """Create a new user"""
        user = User.getUser(email)
        if not user:
            user = User(email=email, name=name, is_admin=is_admin)
            user.set_password(password)
            user.save()
        return user

    def __repr__(self):
        return f'<User {self.email}>'