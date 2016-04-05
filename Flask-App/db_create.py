from app import db
from models import Items, User

# Create the database and the db tables #
db.create_all()

# Insert #
db.session.add(Items("Apple", .99))
db.session.add(Items("Grape", 1.25))

db.session.add(User("admin", "admin", 1))

# Commit changes #
db.session.commit()