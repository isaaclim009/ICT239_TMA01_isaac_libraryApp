# (Keep all existing imports)
from app.models.users import User # Add this import

# ... (Keep existing code for books blueprint and context processor) ...

# Register the new authentication blueprint
from app.controllers.authentication import auth
app.register_blueprint(auth)

# Automatically populate database and create default users
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

if __name__ == "__main__":
    app.run(debug=True)