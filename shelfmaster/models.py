import sqlalchemy as sa
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from datetime import datetime, timedelta
from shelfmaster import db, login_manager


def create_database():
    with app.app_context():
        db.create_all()

        admin = Admin(username="rahulreji", password="power", role_id=2)
        db.session.add(admin)
        db.session.commit()

        for usn_name in read_namelist():
            u = User(
                username=usn_name[0],
                name=usn_name[1],
                is_teacher=False,
                class_section="4A",
            )
            db.session.add(u)
            db.session.commit()

        for book_details in read_booklist():
            entity = Entity(
                type="Book",
                title=book_details["title"],
                author=book_details["author"],
                accession_number=book_details["accession_number"],
                call_number=book_details["call_number"],
                publisher=book_details["publisher"],
                place_of_publication=book_details["place_of_publication"],
                isbn=book_details["isbn"],
                vendor=book_details["vendor"],
                bill_number=book_details["bill_number"],
                amount=book_details["price"],
                language="English",
            )
            db.session.add(entity)
            db.session.commit()


class User(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    username = sa.Column(sa.String(20), nullable=False, unique=True)
    name = sa.Column(sa.String(32))
    is_teacher = sa.Column(sa.Boolean)
    class_section = sa.Column(sa.String(10))

    borrowed_entities = relationship("Entity", backref="user", lazy=True)
    transaction = relationship("TransactionLog", backref="user", lazy=True)

    def __repr__(self):
        return f"ID: {str(self.id)}; {self.username}"


class Admin(db.Model, UserMixin):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    username = sa.Column(sa.String(40), nullable=False)
    password = sa.Column(sa.String(64), nullable=False)

    """
    ROLE ID RUBRIK:

    1: LIBRARIAN
    - Can borrow/return books
    - Can view books/students list
    - Can add users
    - Can delete users

    2: ADMIN
    - Cannot borrow/return books
    - Can add books, add users, delete users
    """
    role_id = sa.Column(sa.Integer)

    def __repr__(self):
        return f"{str(self.id)}. {self.username} with {self.password}"


class TransactionLog(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))
    entity_id = sa.Column(sa.Integer, sa.ForeignKey("entity.id"))
    borrowed_time = sa.Column(sa.DateTime, default=datetime.now)
    due_date = sa.Column(
        sa.DateTime, default=lambda: datetime.now() + timedelta(days=7)
    )

    def __repr__(self):
        return f"{str(self.id)}"


# class ReadingLog(db.Model):
#     id = sa.Column(sa.Integer, primary_key=True, unique=True)
#     user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id")) # TODO must add relationships
#     entity_id = sa.Column(sa.Integer, sa.ForeignKey("entity.id"))
#     returned_time = sa.Column(sa.DateTime)
#     librarian_remarks = sa.Column(sa.String(120))

#     def __repr__(self):
#         return f"{str(self.id)}"


class AdminActionsLog(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    username = sa.Column(sa.String(20))
    action = sa.Column(sa.String(120))
    time = sa.Column(sa.DateTime, default=datetime.now)

    def __repr__(self):
        return f"{self.username} performed {self.action}"


class Entity(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    type = sa.Column(sa.String(40))
    title = sa.Column(sa.String(100))
    author = sa.Column(sa.String(100))
    rack_number = sa.Column(sa.String(20))
    shelf_number = sa.Column(sa.String(20))
    accession_number = sa.Column(sa.String(25), unique=True)
    call_number = sa.Column(sa.String(32))
    publisher = sa.Column(sa.String(120))
    place_of_publication = sa.Column(sa.String(64))
    isbn = sa.Column(sa.String(20))
    vendor = sa.Column(sa.String(32))
    bill_number = sa.Column(sa.String(32))
    bill_date = sa.Column(sa.DateTime)
    amount = sa.Column(sa.String(10))
    remarks = sa.Column(sa.String(120))
    language = sa.Column(sa.String(32))
    is_borrowed = sa.Column(sa.Boolean, default=False)
    due_date = sa.Column(sa.DateTime)
    date_added = sa.Column(sa.DateTime, default=datetime.now)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))
    transaction = relationship("TransactionLog", backref="entity", lazy=True)

    def __repr__(self):
        return f"{self.accession_number}"


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


class FinesLog(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)

    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))
    entity_id = sa.Column(sa.Integer, sa.ForeignKey("entity.id"))

    due_date = sa.Column(sa.DateTime)
    date_returned = sa.Column(sa.DateTime)

    is_paid = sa.Column(sa.Boolean, default=False)
    days_late = sa.Column(sa.Integer)
