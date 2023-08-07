from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

class BorrowForm(FlaskForm):
    usn = StringField("USN", validators=[DataRequired(), Regexp("^\d{3}[NLU12]?\d{3}$")])
    book_id = StringField("Book ID:", validators=[DataRequired()])

    submit = SubmitField("Borrow")

