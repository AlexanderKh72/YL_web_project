import flask
from flask import jsonify, request

import flask_login
from flask_login import login_required

from . import db_session
from .questions import Question
from .users import User


blueprint = flask.Blueprint(
    'questions',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/questions/<int:question_id>')
@login_required
def get_one_question(question_id):
    db_sess = db_session.create_session()
    res = db_sess.query(Question).get(question_id)
    if not res:
        return jsonify({'error': 'Not found'})

    return jsonify(
            {
                'questions': res.to_dict(only=('id', 'author', 'title', 'text', 'type',
                                               'answ', 'score', 'categories'))
            }
        )


@blueprint.route('/api/questions', methods=['POST'])
@login_required
def create_question():
    if not request.json:
        return jsonify({'error': 'Empty request'})

    elif not all(key in request.json for key in
                 ['title', 'text', 'type_id', 'answ', 'score', 'categories']):
        return jsonify({'error': 'Bad request'})

    db_sess = db_session.create_session()
    question = Question(
        author_id=flask_login.current_user.id,
        title=request.json['title'],
        text=request.json['text'],
        type_id=request.json['type_id'],
        answ=request.json['answ'],
        score=request.json['score']
    )
    for category in request.json['categories']:
        question.categories.append(category)

    db_sess.add(question)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/categories/<int:user_id>')
def get_users_categories(user_id):
    categories = set()
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    for question in user.questions:
        categories = categories | set(question.categories)
    return jsonify({'categories': [item.to_dict() for item in categories]})
