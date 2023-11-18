from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired
from shelfmaster.models import Admin
from shelfmaster import app


class LoginForm(FlaskForm):
    with app.app_context():
        admins = Admin().query.filter_by().all()
        admins_usernames = [a.username for a in admins]

    username = SelectField(choices=admins_usernames)
    password = PasswordField()
    submit = SubmitField("Login")


class BorrowForm(FlaskForm):
    usn = StringField(
        "USN",
        validators=[DataRequired()],
    )
    book_id = StringField("Accession Number", validators=[DataRequired()])

    submit = SubmitField("Borrow")


class ReturnForm(FlaskForm):
    book_id = StringField("Accession Number", validators=[DataRequired()])
    submit = SubmitField("Return")


class ConfirmReturnForm(FlaskForm):
    librarian_remarks = TextAreaField("Remarks")
    submit = SubmitField("Return")


class SuggestBookForm(FlaskForm):
    usn = StringField("Student USN", validators=[DataRequired()])
    book = StringField("Name of the book*", validators=[DataRequired()])
    author = StringField("Author")
    reason = TextAreaField(
        "Briefly explain why this book would be a valuable addition to our library."
    )
    submit = SubmitField("Submit")
