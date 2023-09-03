from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Regexp


class LoginForm(FlaskForm):
    username = StringField()
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
