from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Regexp


class LoginForm(FlaskForm):
    username = StringField(
        "Username", Regexp("^\d{2}[01][NLU123456789]?\d{3}$")
    )  # USN for students, 'admin' for librarian
    password = (
        PasswordField()
    )  # Password is roll number for all students, admin password is provisionally 'admin'


class BorrowForm(FlaskForm):
    usn = StringField(
        "USN",
        validators=[
            DataRequired(),
            Regexp("^\d{2}[01][NLU123456789]?\d{3}$", message="Invalid USN"),
        ],
    )
    book_id = StringField("Book ID:", validators=[DataRequired()])

    submit = SubmitField("Borrow")
