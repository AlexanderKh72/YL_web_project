from flask import Flask
from flask import render_template
from flask import url_for, redirect
import flask_login
from flask_login import login_user, logout_user
from flask_login import login_required
from flask_login import LoginManager
from forms.user import RegisterForm
from forms.authorization import LoginForm
from forms.creating_question import NewQuestionForm
from forms.creating_test import NewTestForm

from wtforms import SelectMultipleField

from data import db_session
from data.users import User
from data.questions import Question
from data.tests import Test
from data.works import Work
from data.types import Type
from data.categories import Category
from data import questions_api
from data import test_api

from requests import post, get
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/testing.db")
    # db_sess = db_session.create_session()
    # user = db_sess.query(User).first()
    # print(user.questions)

    app.register_blueprint(questions_api.blueprint)
    # app.register_blueprint(test_api.blueprint)
    app.run(port=5000, host='127.0.0.1')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', title='Главная страница',
                           current_user=flask_login.current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с такой почтой уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/new_question', methods=['GET', 'POST'])
@login_required
def new_question():
    form = NewQuestionForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        print(form.type.data, type(form.type.data))
        if form.type.data in ['3', '4']:
            if not form.incorrect_answers.data:
                message = 'Необходимо заполнить поле "Варианты неверных ответов" или изменить тип'
                return render_template('new_question.html', title='Регистрация', form=form,
                                       message=message)
            if form.type.data == '3':
                answ = {
                    'corr': form.correct_answer.data.split('\r\n\r\n'),
                    'incorr': form.incorrect_answers.data.split('\r\n\r\n')
                }
            else:
                answ = {
                    'corr': form.correct_answer.data,
                    'incorr': form.incorrect_answers.data.split('\r\n\r\n')
                }
        else:
            answ = {
                'corr': form.correct_answer.data
            }
        question = Question(
            author_id=flask_login.current_user.id,
            title=form.title.data,
            text=form.text.data,
            type_id=int(form.type.data),
            answ=bytes(str(answ).replace("'", '"'), encoding='utf-8'),
            score=form.score.data
        )
        for category_title in form.categories.data.split('\r\n\r\n'):
            category = db_sess.query(Category).filter(Category.title == category_title).first()
            if not category:
                category = Category(title=category_title)
                db_sess.add(category)
                db_sess.commit()
            question.categories.append(category)
        db_sess.add(question)
        db_sess.commit()
        return redirect('/')

    return render_template('new_question.html', title='Регистрация', form=form)


@app.route('/new_test', methods=['GET', 'POST'])
@login_required
def new_test():
    NewTestForm.questions = SelectMultipleField('Выберете вопрос',
                                         choices=[(str(question.id), f"""{question.title}-{question.text}-{', '.join(list(map(lambda c: c.title, question.categories)))}""") for question in flask_login.current_user.questions])
    form = NewTestForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        test = Test(
            author_id=flask_login.current_user.id,
            title=form.title.data,
            start_time=form.start_time.data,
            finish_time=form.finish_time.data,
            is_available=form.is_available.data,
        )
        for question_id in form.questions.data:
            question = db_sess.query(Question).get(question_id)
            test.questions.append(question)
        db_sess.add(test)
        db_sess.commit()
        return redirect('/')

    return render_template('new_test.html', title='Регистрация', form=form)


@app.route('/my_questions')
@login_required
def my_questions():
    answ_json = [dict(get(f'http://127.0.0.1:5000/api/questions/answ/{q.id}').json()) for q in flask_login.current_user.questions]
    print(answ_json)
    return render_template("my_questions.html", questions=flask_login.current_user.questions,
                           categories_titles=[get(f'http://127.0.0.1:5000/api/questions/categories/{q.id}').json() for q in flask_login.current_user.questions],
                           answ_json=answ_json)


if __name__ == '__main__':
    main()
