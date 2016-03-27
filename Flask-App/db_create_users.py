from app import db
from models import User

# insert data
db.session.add(User("Jacob", "admin", 1))
db.session.add(User("Admin2", "aonetwothree", 1))
db.session.add(User("Jake", "password", 1))

# commit the changes
db.session.commit()
