from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    IntegerField,
    SelectField,
    DateField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length


class AddAdminsForm(FlaskForm):
    username = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    roles = ["Librarian", "Super-Admin"]
    role = SelectField("Role", choices=roles)
    submit = SubmitField("Add Admin")


class AddBookForm(FlaskForm):
    choices = ["Book", "Map", "Magazine", "Newspaper", "EVS Material"]
    type = SelectField("Type of Entity", choices=choices)
    title = StringField("Title", validators=[DataRequired(), Length(max=100)])
    author = StringField("Author", validators=[Length(max=100)])
    rack_number = StringField("Rack number", validators=[Length(max=20)])
    shelf_number = StringField("Shelf number", validators=[Length(max=20)])
    accession_number = StringField("Accession number", validators=[Length(max=25)])
    call_number = StringField("Call number", validators=[Length(max=32)])
    publisher = StringField("Publisher", validators=[Length(max=120)])

    isbn = StringField("ISBN")
    vendor = StringField("Vendor", validators=[Length(max=32)])
    bill_number = StringField("Bill number", validators=[Length(max=32)])
    bill_date = StringField("Bill date", validators=[Length(max=32)])
    amount = StringField("Amount")
    remarks = TextAreaField("Remarks", validators=[Length(max=120)])

    language_choices = ["English", "Hindi", "Kannada", "Sanskrit"]
    language = SelectField("Language", choices=language_choices)

    submit = SubmitField("Add Entity")


class AddUserForm(FlaskForm):
    username = StringField(
        "USN",
        validators=[
            DataRequired(),
            Length(max=20),
        ],
    )
    name = StringField("Name", validators=[DataRequired(), Length(max=32)])
    is_teacher = SelectField("Role", choices=["Student", "Teacher"])
    class_section = StringField("Class and Section", validators=[Length(max=4)])

    submit = SubmitField("Add User")


class CatalogForm(FlaskForm):
    options = [
        ("accession_number", "Accession Number"),
        ("call_number", "Call Number"),
        ("author", "Author"),
        ("title", "Title"),
    ]

    criteria = SelectField("Search criteria", choices=options)
    query = StringField("Search query")

    submit = SubmitField("Search")


class ReportsForm(FlaskForm):
    options = [
        ("books", "Popular Books"),
        ("readers", "Avid Readers"),
    ]

    report_type = SelectField("Report type", choices=options)
    submit = SubmitField("Generate reports")


class FineReceivedForm(FlaskForm):
    payer = StringField(
        "Paid by (USN)"
    )  # TODO make this a dropdown of outstanding fine users
    amount = IntegerField("Amount received")
    submit = SubmitField("Confirm")


class AddHolidayForm(FlaskForm):
    date = DateField("Holiday")
    submit = SubmitField("Add Holiday")
