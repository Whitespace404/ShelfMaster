from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Regexp


class LoginForm(FlaskForm):
    username = StringField("Username", Regexp("^\d{2}[01][NLU0123456789]?\d{3}$"))
    password = PasswordField()


class BorrowForm(FlaskForm):
    usn = StringField(
        "USN",
        validators=[
            DataRequired(),
            Regexp("^[123]\d{1}[01][NLU0123456789]?\d{3}$", message="Invalid USN"),
        ],
    )
    book_id = StringField("Book ID:", validators=[DataRequired()])

    submit = SubmitField("Borrow")
