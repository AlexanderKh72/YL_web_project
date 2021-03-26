from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired


class NewQuestionForm(FlaskForm):
    title = StringField('Название вопроса', validators=[DataRequired()])
    text = TextAreaField('Текст вопроса', validators=[DataRequired()])
    type = SelectField('Тип вопроса', choices=[(1, 'Текстовый ответ'),
                                               (2, 'Числовой ответ'),
                                               (3, 'Множественный выбор'),
                                               (4, 'Единственный выбор'),
                                               (5, 'Верно/неверно')], validators=[DataRequired()])
    incorrect_answers = TextAreaField('Варианты неверных ответов')
    correct_answer = TextAreaField('Верный ответ')
    score = IntegerField('Количество баллов за верный ответ')

    categories = TextAreaField('Категории')

    submit = SubmitField('Создать')
