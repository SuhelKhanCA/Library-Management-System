from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, BooleanField, DateField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional, NumberRange
from datetime import datetime, timedelta  # Add this line
from models import User, Book

class AdminRegisterForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                      validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class MembershipForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    duration = SelectField('Membership Duration', choices=[(6, '6 Months'), (12, '1 Year'), (24, '2 Years')], coerce=int, default=6)
    submit = SubmitField('Add Membership')


class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=150)])
    author = StringField('Author', validators=[DataRequired(), Length(min=2, max=150)])
    category = RadioField('Category', choices=[('book', 'Book'), ('movie', 'Movie')], default='book')
    copies = IntegerField('Total Copies', validators=[DataRequired(), NumberRange(min=1)])
    search = StringField('Search Book Title', validators=[Optional()])
    submit = SubmitField('Submit')


class IssueForm(FlaskForm):
    title = StringField('Book Title', validators=[DataRequired()])
    issue_date = DateField('Issue Date', default=datetime.utcnow, validators=[DataRequired()])
    return_date = DateField('Return Date', default=lambda: datetime.utcnow() + timedelta(days=15))
    remarks = TextAreaField('Remarks', validators=[Optional()])
    submit = SubmitField('Issue Book')

    def validate_issue_date(form, field):
        if field.data < datetime.utcnow().date():
            raise ValidationError("Issue date cannot be in the past.")


class ReturnForm(FlaskForm):
    book_id = IntegerField('Book ID', validators=[DataRequired()])
    title = StringField('Book Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    issue_date = DateField('Issue Date', validators=[DataRequired()])
    return_date = DateField('Return Date', validators=[DataRequired()])
    confirm_return = BooleanField('Confirm Return', default=False)
    submit = SubmitField('Return Book')


class FinePaymentForm(FlaskForm):
    fine_paid = BooleanField('Fine Paid', default=False)
    remarks = TextAreaField('Remarks', validators=[Optional()])
    submit = SubmitField('Confirm Payment')


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    submit = SubmitField('Add/Update User')

    def validate_username(form, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists.')
