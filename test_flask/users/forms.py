from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from test_flask.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm password:', validators=[EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please, choose another one')
        
    def validate_email(self, email):
        eamil = User.query.filter_by(email=email.data).first()
        if eamil:
            raise ValidationError('This email is already taken. Please, choose another one')

class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember password:')
    submit = SubmitField("Log in")



class UpdateAccountForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update information')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already taken. Please, choose another one')
            
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()  # Изменил переменную на user
            if user:
                raise ValidationError('This email is already taken. Please, choose another one')
            

class RequestResetForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    submit = SubmitField('Change password')

    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Аккаунт с данным email-адресом отсутствует. Вы можеет его зарегестрировать')
        

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm password', validators=[EqualTo('password')])
    submit = SubmitField('Change password')