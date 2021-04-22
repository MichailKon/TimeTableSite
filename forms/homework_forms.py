from flask_wtf import FlaskForm
from wtforms import SubmitField, TextField, FileField

from constants import MAX_SUBJECTS


class EditHomework(FlaskForm):
    for i in range(1, MAX_SUBJECTS + 1):
        exec(f'subject_{i} = TextField("")')
        exec(f'subject_{i}_file = FileField("Дополнительный файл: ")')
    cancel = SubmitField('Отмена')
    submit = SubmitField('Сохранить')
