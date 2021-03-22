import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Question(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author = orm.relation("User")
    text = sqlalchemy.Column(sqlalchemy.String)
    type_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("types.id"))
    type = orm.relation("Type")
    answ = sqlalchemy.Column(sqlalchemy.BLOB)
    score = sqlalchemy.Column(sqlalchemy.Integer)
    categories = orm.relation("Category",
                              secondary="questions_to_categories",
                              backref="questions")
