from flask import request
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, Regexp
from flask_wtf.file import FileAllowed
import pandas as pd
from logic import get_car_data

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=60)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+]).{8,50}$', message='Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character (!@#$%^&*+).')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[DataRequired(), Regexp(r'^(\+?\d{1,3}-?)?\d{10,15}$', message='Phone must be 10-15 digits long with optional country code and hyphens.')])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=200)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=60)])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=50)])
    zip_code = StringField('Zip Code', validators=[DataRequired(), Regexp(r'^\d{5,7}$', message='Zip code must be 5-7 digits long.')])
    country = StringField('Country', validators=[DataRequired(), Length(min=2, max=50)])
    car_brand = StringField('Car Brand', validators=[DataRequired(), Length(min=2, max=50)])
    car_model = StringField('Car Model', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+]).{8,50}$', message='Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character (!@#$%^&*+).')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class EstimateForm(FlaskForm):
    brandlist, modellist = get_car_data() # brandlist is of type numpy.ndarray and modellist is of type dict of numpy.ndarray
    car_brand = SelectField('Car Brand', choices=[(brand, brand) for brand in brandlist], validators=[DataRequired()])
    
    submit_car_brand = SubmitField('Next')
    
    car_model = SelectField('Car Model', choices=[], validators=[DataRequired()])
        
    upload_image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')], render_kw={
        'accept': 'image/*', 
        'capture': 'camera', 
        'multiple': False, 
        'title': 'Upload an Image', 
        'style': 'display: block;', 
        'draggable': True, 
        'ondrop': 'dropHandler(event);', 
        'ondragover': 'dragOverHandler(event);'
    })
    submit = SubmitField('Estimate')
    
    # Dynamically set 'upload_image' required based on which button is pressed
    def __init__(self, *args, **kwargs):
        super(EstimateForm, self).__init__(*args, **kwargs)
        # if submit button is pressed, set 'upload_image' required to True
        if request and 'submit' in request.form:
            self.upload_image.validators = [FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'), DataRequired()]
        else:
            self.upload_image.validators = [FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'), Optional()]

class UpdateAccountForm(FlaskForm):
    name = StringField('Name', validators=[Optional(), Length(min=2, max=60)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Regexp(r'^(\+?\d{1,3}-?)?\d{10,15}$', message='Phone must be 10-15 digits long with optional country code and hyphens.')])
    address = StringField('Address', validators=[Optional(), Length(min=2, max=200)])
    city = StringField('City', validators=[Optional(), Length(min=2, max=60)])
    state = StringField('State', validators=[Optional(), Length(min=2, max=50)])
    zip_code = StringField('Zip Code', validators=[Optional(), Regexp(r'^\d{5,7}$', message='Zip code must be 5-7 digits long.')])
    country = StringField('Country', validators=[Optional(), Length(min=2, max=50)])
    car_brand = StringField('Car Brand', validators=[Optional(), Length(min=2, max=50)])
    car_model = StringField('Car Model', validators=[Optional(), Length(min=2, max=50)])
    picture = FileField('Update Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update Account')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=8, max=50), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+]).{8,50}$', message='Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character (!@#$%^&*+).')])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=50), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+]).{8,50}$', message='Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character (!@#$%^&*+).')])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=50), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+]).{8,50}$', message='Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character (!@#$%^&*+).')])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset Password')

class CarDataForm(FlaskForm):
    car_brand = StringField('Car Brand', validators=[DataRequired()])
    car_model = StringField('Car Model', validators=[DataRequired()])
    car_part = SelectField('Car Part', choices=[('Bonnet', 'Bonnet'), ('Bumper', 'Bumper'), ('Door', 'Door'), ('Fender', 'Fender'), ('Windshield', 'Windshield'),('Dickey', 'Dickey'), ('Light', 'Light')])
    car_part_price = StringField('Car Part Price', validators=[DataRequired()])
    submit = SubmitField('Add/Update Car Data')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')
    
class DeleteUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+]).{8,50}$', message='Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character (!@#$%^&*+).')])
    submit = SubmitField('Delete User')
    