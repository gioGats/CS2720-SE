from app import db
from models import *
from datetime import *


# Create the database and the db tables #
db.create_all()

# Insert #
db.session.add(Supplier("Ethan", "myEmail@email.com"))
db.session.add(User("admin", "admin", 1))
db.session.add(Product("poop", 1, 10, 4, 10.40))
db.session.add(Product("bananas", 1, 30, 3, 0.40))
db.session.add(Item("Apple", .99, 1, date(2016, 5, 4), 1))
db.session.add(Item("Grape", 1.25, 2, date(2015, 4, 10), 1))
db.session.add(Item("Almonds", 1.43, 2, date(2015, 5, 10), 1))

# Commit changes #
db.session.commit()
