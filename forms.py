from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Regexp


class LoginForm(FlaskForm):
    username = StringField("Username", Regexp("^\d{2}[01][NLU0123456789]?\d{3}$"))
    password = PasswordField()


class BorrowForm(FlaskForm):
    usn = StringField("USN",validators=[DataRequired()])
    book_id = StringField("Book ID:", validators=[DataRequired()])

    submit = SubmitField("Borrow")


class ReturnForm(FlaskForm):
    book_id = StringField("Book ID", validators=[DataRequired()])

    submit = SubmitField("Return")
