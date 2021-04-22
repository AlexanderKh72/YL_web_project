from flask import Flask
from flask import render_template
from flask import url_for, redirect
import flask_login
from flask_login import login_user, logout_user
from flask_login import login_required
from flask_login import LoginManager
from flask_wtf import FlaskForm

from forms.user import RegisterForm
from forms.authorization import LoginForm
from forms.creating_question import NewQuestionForm
from forms.creating_test import NewTestForm
from forms.question import QuestionForm

from wtforms import SelectMultipleField, SelectField, StringField, FloatField, BooleanField

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

import datetime
import copy
import random

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
    if not flask_login.current_user.is_authenticated:
        return render_template('index.html', title='Главная страница')
    db_sess = db_session.create_session()

    works = db_sess.query(Work).filter(Work.user_id == flask_login.current_user.id, Work.is_finished).all()

    user_answers = []
    for work in works:
        answers = work.answers.split(';;')
        v_answers = []
        for question_id in range(len(answers) - 1):
            question = work.test.questions[question_id]
            corr_answ = get(f'http://127.0.0.1:5000/api/questions/answ/{question.id}').json()
            answer = answers[question_id]
            v_answer = []
            print(corr_answ, '\n\n\n')
            print(question.text)
            if question.type_id == 3 or question.type_id == 4:
                for a in answer.split(','):
                    print(a)
                    v_answer.append(corr_answ['corr'].get(a, corr_answ['incorr'].get(a, 0)))
                v_answer = ', '.join(v_answer)
            else:
                v_answer = answer
            v_answers.append(v_answer)
        user_answers.append(v_answers)

    correct_answers = []
    for work in works:
        print('\n\n\n', get(f'http://127.0.0.1:5000/api/tests/answ/{work.test.id}').json())
        correct_answers.append(get(f'http://127.0.0.1:5000/api/tests/answ/{work.test.id}').json()['corr'])

    return render_template('index.html', title='Главная страница',
                           current_user=flask_login.current_user,
                           works=works,
                           user_answers=user_answers,
                           corr_answers=correct_answers)


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
            if form.type.data == '3' or form.type.data == '4':
                corr_answ_count = len(form.correct_answer.data.split('\r\n\r\n'))
                corr = {i: form.correct_answer.data.split('\r\n\r\n')[i] for i in range(corr_answ_count)}
                incorr_answ_count = len(form.incorrect_answers.data.split('\r\n\r\n'))
                incorr = {i: form.incorrect_answers.data.split('\r\n\r\n')[i - corr_answ_count] for i in range(corr_answ_count, corr_answ_count + incorr_answ_count)}

                answ = {
                    'corr': copy.deepcopy(corr),
                    'incorr': copy.deepcopy(incorr)
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
        if form.categories.data:
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
                                         choices=[(str(question.id), f"""{question.title}: {question.text}, {', '.join(list(map(lambda c: c.title, question.categories)))}""") for question in flask_login.current_user.questions])
    form = NewTestForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        test = Test(
            author_id=flask_login.current_user.id,
            title=form.title.data
            # start_time=form.start_time.data,
            # finish_time=form.finish_time.data,
            # is_available=form.is_available.data,
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
    answers = []
    for q in flask_login.current_user.questions:
        answ = {}
        answ_json = get(f'http://127.0.0.1:5000/api/questions/answ/{q.id}').json()
        if q.type_id == 3 or q.type_id == 4:
            answ['incorr'] = '; '.join(list(answ_json['incorr'].values()))
            answ['corr'] = '; '.join(list(answ_json['corr'].values()))
        else:
            answ['corr'] = answ_json['corr']
        answers.append(answ)

    return render_template("my_questions.html", questions=flask_login.current_user.questions,
                           categories_titles=['; '.join(get(f'http://127.0.0.1:5000/api/questions/categories/{q.id}').json()['categories_titles']) for q in flask_login.current_user.questions],
                           answers=answers)


@app.route('/test/<int:test_id>/<int:question_id>', methods=['GET', 'POST'])
@login_required
def test_passing(test_id, question_id):
    db_sess = db_session.create_session()
    test = db_sess.query(Test).get(test_id)
    question = test.questions[question_id - 1]

    # print(f'\n\n\n{question.id}\n\n')

    work = db_sess.query(Work).filter(Work.user_id == flask_login.current_user.id, Work.test_id == test_id).first()
    if not work:
        questions_count = len(db_sess.query(Test).get(test_id).questions)
        work = Work(
            user_id=flask_login.current_user.id,
            test_id=test_id,
            start_time=datetime.datetime.now(),
            is_finished=False,
            answers=';;' * questions_count
        )
        db_sess.add(work)
        db_sess.commit()

    if question_id == 0:
        try:
            del QuestionForm.answer
        except Exception:
            pass
        form = QuestionForm()
        if form.validate_on_submit():
            work.finish_time = datetime.datetime.now()
            work.is_finished = True

            score = 0
            user_answers = work.answers.split(';;')
            corr_answers = [get(f'http://127.0.0.1:5000/api/questions/answ/{q.id}').json() for q in test.questions]

            for i, question in enumerate(test.questions):
                if question.type_id == 3 or question.type_id == 4:
                    if set(user_answers[i].split(',')) == set(corr_answers[i]['corr'].keys()):
                        score += question.score
                elif question.type_id == 2:
                    if float(user_answers[i]) == float(corr_answers[i]['corr']):
                        score += question.score
                else:
                    if user_answers[i] == corr_answers[i]['corr']:
                        score += question.score
            work.result = score

            db_sess.commit()
            return redirect('/')
        return render_template("finish_test.html", form=form)

    if test.questions[question_id - 1].type_id == 1:
        QuestionForm.answer = StringField('Ответ:')
    elif test.questions[question_id - 1].type_id == 2:
        QuestionForm.answer = FloatField('Ответ:')
    elif test.questions[question_id - 1].type_id == 3:
        answers = get(f'http://127.0.0.1:5000/api/questions/answ/{question.id}').json()
        corr = [(key, value) for key, value in answers['corr'].items()]
        incorr = [(key, value) for key, value in answers['incorr'].items()]
        choices = corr + incorr
        random.shuffle(choices)
        QuestionForm.answer = SelectMultipleField('Ответ:', choices=choices)
    elif test.questions[question_id - 1].type_id == 4:
        answers = get(f'http://127.0.0.1:5000/api/questions/answ/{question.id}').json()
        # print(f'{answers}\n\n')
        corr = [(int(key), value) for key, value in answers['corr'].items()]
        incorr = [(int(key), value) for key, value in answers['incorr'].items()]
        choices = corr + incorr
        random.shuffle(choices)
        # print(f'{choices}\n\n')
        # print(f'{type(choices)}\n\n')
        QuestionForm.answer = SelectField('Ответ:', choices=choices)
    elif test.questions[question_id - 1].type_id == 5:
        QuestionForm.answer = BooleanField('Ответ:')

    form = QuestionForm()
    if form.validate_on_submit():
        answers = work.answers.split(';;')
        if test.questions[question_id - 1].type_id == 3:
            answers[question_id - 1] = ','.join(list(map(str, form.answer.data)))
        else:
            answers[question_id - 1] = str(form.answer.data)
        work.answers = ';;'.join(answers)
        db_sess.commit()
        if question_id == len(test.questions):
            return redirect(f'/test/{test_id}/0')
        else:
            return redirect(f'/test/{test_id}/{question_id + 1}')

    return render_template("question.html",
                           q=question,
                           form=form,
                           q_id=question_id,
                           t_id=test.id,
                           q_count=len(test.questions))


@app.route('/test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def test_passing1(test_id):
    return redirect(f'/test/{test_id}/1')


@app.route('/my_tests')
@login_required
def my_tests():
    db_sess = db_session.create_session()
    tests = db_sess.query(Test).filter(Test.author_id == flask_login.current_user.id).all()
    completed_works = [len(db_sess.query(Work).filter(Work.test_id == test.id, Work.is_finished).all()) for test in tests]
    uncompleted_works = [len(db_sess.query(Work).filter(Work.test_id == test.id, not Work.is_finished).all()) for test in tests]
    return render_template('my_tests.html',
                           tests=tests,
                           completed_works=completed_works,
                           uncompleted_works=uncompleted_works)


@app.route('/my_tests/<int:test_id>')
@login_required
def my_test(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(Test).filter(Test.id == test_id, Test.author_id == flask_login.current_user.id).first()
    completed_works = len(db_sess.query(Work).filter(Work.test_id == test.id, Work.is_finished).all())
    uncompleted_works = len(db_sess.query(Work).filter(Work.test_id == test.id, not Work.is_finished).all())
    answers = []
    for q in test.questions:
        answ = {}
        answ_json = get(f'http://127.0.0.1:5000/api/questions/answ/{q.id}').json()
        if q.type_id == 3 or q.type_id == 4:
            answ['incorr'] = '; '.join(list(answ_json['incorr'].values()))
            answ['corr'] = '; '.join(list(answ_json['corr'].values()))
        else:
            answ['corr'] = answ_json['corr']
        answers.append(answ)
    if not test:
        return redirect('/my_tests')
    return render_template('test.html', test=test,
                           completed_works=completed_works,
                           uncompleted_works=uncompleted_works,
                           categories_titles=['; '.join(get(f'http://127.0.0.1:5000/api/questions/categories/{q.id}').json()['categories_titles']) for q in test.questions],
                           answers=answers)


if __name__ == '__main__':
    main()
