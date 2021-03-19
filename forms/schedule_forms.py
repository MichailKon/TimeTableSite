from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField

from constants import MAX_SUBJECTS


class EditSubjects(FlaskForm):
    for i in range(1, MAX_SUBJECTS + 1):
        exec(f'subject_{i} = SelectField("Предмет {i}", default="")')
    cancel = SubmitField('Отмена')
    submit = SubmitField('Сохранить')
