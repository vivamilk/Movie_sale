from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, EqualTo, ValidationError, AnyOf


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    type = StringField('Type (Individual or Business)', validators=[DataRequired(), AnyOf(['Individual', 'Business'])])
    address = StringField('Address')
    phone_number = IntegerField('Phone Number')
    submit = SubmitField('Register')

    def validate_username(self, username):
        from app import User
        user = User().query_by_username(username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')
