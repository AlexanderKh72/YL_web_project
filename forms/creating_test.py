from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired


class NewTestForm(FlaskForm):
    title = StringField('Название теста', validators=[DataRequired()])
    # start_time = DateTimeField('Время начала доступа')
    # finish_time = DateTimeField('Время окончания доступа')
    # runtime = DateTimeField('Время выполнения (чч:мм:сс)')
    # is_available = BooleanField('Доступен?')

    submit = SubmitField('Создать')
