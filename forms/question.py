from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField


class QuestionForm(FlaskForm):
    submit = SubmitField('Сохранить ответ')