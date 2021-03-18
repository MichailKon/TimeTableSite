from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from constants import MAX_SUBJECTS


class EditSubjects(FlaskForm):
    for i in range(1, MAX_SUBJECTS + 1):
        exec(f'subject_{i} = StringField("Предмет {i}")')
    submit = SubmitField('Сохранить')
