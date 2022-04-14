from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, EmailField, SelectMultipleField
from wtforms.validators import InputRequired, Email, Length

# The LoginForm describes the fields and validators corresponding to the login page
class LoginForm(FlaskForm):
    email = EmailField('', 
                        validators=[InputRequired(), Email(message='Invalid email!'), Length(max=50)],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('', 
                            validators=[InputRequired(), Length(min=6, max=80)],
                            render_kw={"placeholder": "Password"})

# The SignUpForm describes the fields and validators corresponding to the signup page
class SignUpForm(FlaskForm):
    name = StringField('', 
                        validators=[InputRequired(), Length(min=2, max=50)],
                        render_kw={"placeholder": "Name"})
    email = EmailField('', 
                        validators=[InputRequired(), Email(message='Invalid email!'), Length(max=50)],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('', 
                            validators=[InputRequired(), Length(min=6, max=80)],
                            render_kw={"placeholder": "Password"})

# The TrainingForm describes the fields and validators corresponding to the training page
class TrainingForm(FlaskForm):
    file = FileField('Reference image:', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg'], 'Allowed file formats: .jpg, .jpeg!')
    ])
    
    personSelect = SelectMultipleField('Select an existing person', 
                               choices=[
                                 ('Kanye', 'Kanye'), 
                                 ('Elon', 'Elon'), 
                                 ('Kaden', 'Kaden'), 
                                 ('Jacob', 'Jacob')
                               ])
    
    newPersonName = StringField('Add a person',
                        validators=[Length(max=30)],
                        render_kw={"placeholder": "Person name"})

    def validate(self, extra_validators=None):
        if super().validate(extra_validators):

            if not ((self.personSelect.data and not self.newPersonName.data) or (not self.personSelect.data and self.newPersonName.data)):
                self.newPersonName.errors.append('You must provide a name!')
                return False
            else:
                return True

        return False
