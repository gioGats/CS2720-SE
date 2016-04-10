from app import db
from models import *
from datetime import *


# Create the database and the db tables #
db.create_all()

# Insert #
db.session.add(Supplier("Ethan", "myEmail@email.com"))
db.session.add(User("admin", "admin", 1))
db.session.add(Product("poop", "human waste", 1, 10, 4, 10.40))
db.session.add(Product("bananas","fruit", 1, 30, 3, 0.40))
db.session.add(Item(1, date(2016, 5, 4), 1))
db.session.add(Item(2, date(2015, 4, 10), 1))
db.session.add(Item(2, date(2015, 5, 10), 1))

# Commit changes #
db.session.commit()
