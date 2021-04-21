import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


tests_to_questions_table = sqlalchemy.Table(
    'tests_to_questions',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('test_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('tests.id')),
    sqlalchemy.Column('question_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('questions.id'))
)


class Test(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tests'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author = orm.relation("User")
    title = sqlalchemy.Column(sqlalchemy.String)
    # start_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    # finish_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    # runtime = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    # is_available = sqlalchemy.Column(sqlalchemy.Boolean)
    questions = orm.relation("Question",
                              secondary="tests_to_questions",
                              backref="tests")
