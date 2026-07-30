from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class ComplaintForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    mobile = StringField("Mobile Number", validators=[DataRequired(), Regexp(r"^[0-9+() -]{7,20}$", message="Enter a valid mobile number.")])
    category_id = SelectField("Complaint Category", coerce=int, validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=10)])
    priority = SelectField("Priority", choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")])
    attachment = FileField("Attachment")
    submit = SubmitField("Save Complaint")
