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
        validators=[
            DataRequired(),
            Regexp(
                "^[0123]\d{1}[01][NLU0123456789]?\d{3}$",
                message="That is not a real USN.",
            ),
        ],
    )
    book_id = StringField("Book ID", validators=[DataRequired()])

    submit = SubmitField("Borrow")


class ReturnForm(FlaskForm):
    book_id = StringField("Book ID", validators=[DataRequired()])
    submit = SubmitField("Return")
