from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, EmailField, SelectMultipleField
from wtforms.validators import InputRequired, Email, Length

class LoginForm(FlaskForm):
    email = EmailField('', 
                        validators=[InputRequired(), Email(message='Invalid email!'), Length(max=50)],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('', 
                            validators=[InputRequired(), Length(min=6, max=80)],
                            render_kw={"placeholder": "Password"})

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
    
    newPersonName = StringField('Add a new person',
                        validators=[Length(max=30)],
                        render_kw={"placeholder": "New person name"})

    def validate(self, extra_validators=None):
        if super().validate(extra_validators):

            if not ((self.personSelect.data and not self.newPersonName.data) or (not self.personSelect.data and self.newPersonName.data)):
                self.newPersonName.errors.append('You must choose an existing person OR provide a new name, not both!')
                return False
            else:
                return True

        return False
