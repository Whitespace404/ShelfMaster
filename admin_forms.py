from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    IntegerField,
    SelectField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Regexp


class AddAdminsForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Add Admin")


class AddBookForm(FlaskForm):
    choices = ["Book", "Map", "Magazine", "Newspaper", "EVS Material"]
    type = SelectField("Type of Entity", choices=choices)

    rack_number = StringField("Rack number", validators=[Length(max=20)])
    shelf_number = StringField("Shelf number", validators=[Length(max=20)])
    accession_number = StringField("Accession number", validators=[Length(max=25)])
    call_number = StringField("Call number", validators=[Length(max=32)])
    publisher = StringField("Publisher", validators=[Length(max=120)])
    isbn = IntegerField("ISBN", validators=[Length(max=13)])
    vendor = StringField("Vendor", validators=[Length(max=32)])
    bill_number = StringField("Bill number", validators=[Length(max=32)])
    amount = IntegerField("Amount", validators=[Length(max=10)])
    remarks = TextAreaField("Remarks", validators=[Length(max=120)])
    language = StringField("Language", validators=[Length(max=32)])

    submit = SubmitField("Add Entity")


class AddUserForm(FlaskForm):
    username = StringField(
        "USN",
        validators=[
            DataRequired(),
            # Regexp(
            #     "^[0123]\d{1}[01][NLU0123456789]?\d{3}$",
            #     message="That is not a real USN.",
            # ),
            Length(max=20),
        ],
    )
    name = StringField("Name", validators=[DataRequired(), Length(max=32)])
    is_teacher = SelectField("Role", choices=["Student", "Teacher"])
    class_section = StringField("Class and Section", validators=[Length(max=4)])

    submit = SubmitField("Add User")
