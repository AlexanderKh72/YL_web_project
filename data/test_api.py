import flask
from flask import jsonify, request

import flask_login
from flask_login import login_required

from . import db_session
from .tests import Test

blueprint = flask.Blueprint(
    'tests',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/questions')
@login_required
def get_tests():
    db_sess = db_session.create_session()
    tests_list = db_sess.query(Test).filter(Test.author.id == flask_login.current_user.id)
    return jsonify(
        {
            'tests': [
                item.to_dict(only=('id', 'author', 'start_time', 'finish_time',
                                   'runtime', 'is_available', 'questions'))
                for item in tests_list
            ]
        }
    )


@blueprint.route('/api/questions/<int:test_id>')
@login_required
def get_one_test(test_id):
    db_sess = db_session.create_session()
    res = db_sess.query(Test).get(test_id)
    if not res:
        return jsonify({'error': 'Not found'})

    if res.author.id != flask_login.current_user.id:
        return jsonify({'error': 'No access'})

    return jsonify(
            {
                'tests': res.to_dict(only=('id', 'author', 'start_time', 'finish_time',
                                           'runtime', 'is_available', 'questions'))
            }
        )


@blueprint.route('/api/questions', methods=['POST'])
@login_required
def create_test():
    if not request.json:
        return jsonify({'error': 'Empty request'})

    elif not all(key in request.json for key in
                 ['is_available', 'questions']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    test = Test(
        is_available=request.json['is_available']
    )
    if request.json['start_time']:
        test.start_time = request.json['start_time']

    if request.json['finish_time']:
        test.start_time = request.json['finish_time']

    if request.json['runtime']:
        test.start_time = request.json['runtime']

    for question in request.json['questions']:
        test.categories.append(question)

    db_sess.add(test)
    db_sess.commit()
    return jsonify({'success': 'OK'})
