from flask import Flask
from flask import render_template
from flask import url_for, redirect
from authorization import LoginForm
from flask_login import login_user

from data import db_session
from data.users import User
from data.questions import Question
from data.tests import Test
from data.works import Work
from data.types import Type
from data.categories import Category


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/testing.db")

    # app.run()


if __name__ == '__main__':
    main()