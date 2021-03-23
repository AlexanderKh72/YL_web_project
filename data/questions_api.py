import flask
from flask import jsonify, request

import flask_login
from flask_login import login_required

from . import db_session
from .questions import Question

blueprint = flask.Blueprint(
    'questions',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/questions')
@login_required
def get_questions():
    db_sess = db_session.create_session()
    questions_list = db_sess.query(Question).filter(Question.author.id == flask_login.current_user.id)
    return jsonify(
        {
            'questions': [
                item.to_dict(only=('id', 'author', 'text', 'type', 'answ', 'score', 'categories'))
                for item in questions_list
            ]
        }
    )


@blueprint.route('/api/questions/<int:question_id>')
@login_required
def get_one_question(question_id):
    db_sess = db_session.create_session()
    res = db_sess.query(Question).get(question_id)
    if not res:
        return jsonify({'error': 'Not found'})

    if res.author.id != flask_login.current_user.id:
        return jsonify({'error': 'No access'})

    return jsonify(
            {
                'questions': res.to_dict(only=('id', 'author', 'text', 'type',
                                               'answ', 'score', 'categories'))
            }
        )


@blueprint.route('/api/questions', methods=['POST'])
@login_required
def create_question():
    if not request.json:
        return jsonify({'error': 'Empty request'})

    elif not all(key in request.json for key in
                 ['text', 'type_id', 'answ', 'score', 'categories']):
        return jsonify({'error': 'Bad request'})

    db_sess = db_session.create_session()
    question = Question(
        author_id=flask_login.current_user.id,
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
