from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SelectField,  validators
from wtforms.validators import DataRequired, NumberRange, Optional, NoneOf
from datetime import datetime


class PostEditForm(FlaskForm):
    content = StringField("Content", validators= [DataRequired()])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class RegisterForm(FlaskForm):
    first_name = StringField("First Name", [validators.Length(max=20)])
    last_name = StringField("Last Name", [validators.Length(max=30)])
    email = StringField("Email Address", [validators.Length(max=50)])
    phone_num = StringField("Phone Number")

    username = StringField("Username", [
        validators.DataRequired(),
        validators.Length(min=3,max=50)
    ])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match!')
    ])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])

class AddPostForm(FlaskForm):
    content = StringField("Content", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    url = StringField("URL")
    photo = FileField("Photo")
    category = SelectField("Category", coerce=int, validators=[DataRequired(), NoneOf([0])])

class ProfileEditForm(FlaskForm):
    first_name = StringField("First Name", [validators.Length(max=20)])
    last_name = StringField("Last Name", [validators.Length(max=30)])
    email = StringField("Email Address", [validators.Length(max=50)])
    phone_num = StringField("Phone Number")

    username = StringField("Username", [
        validators.Length(min=3,max=50)
    ])

class SearchForm(FlaskForm):
    search_username = StringField("Username")
    post_title = StringField("Post Title")
    search_category = SelectField("Category", coerce=int)

class AddCategoryForm(FlaskForm):
    add_category = StringField("Add Category", validators=[DataRequired()])

class DeleteCategoryForm(FlaskForm):
    delete_category = SelectField("Delete Category", coerce=int, validators=[DataRequired()])

class ContactForm(FlaskForm):
    name = StringField("Your Honorable Name", validators=[DataRequired()])
    subject = StringField("What is it about?", validators=[DataRequired()])
    message = StringField("WHat is your honorable thoughts, what do you want to tell us ?", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])