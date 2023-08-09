from shelfmaster import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    borrowed_book = db.relationship("Book", backref="borrower", lazy=True)

    def __repr__(self):
        return self.id + self.username


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return self.title + " borrowed by " + self.user_id
