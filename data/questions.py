import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
import json


class Question(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author = orm.relation("User")
    title = sqlalchemy.Column(sqlalchemy.String)
    text = sqlalchemy.Column(sqlalchemy.String)
    type_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("types.id"))
    type = orm.relation("Type")
    answ = sqlalchemy.Column(sqlalchemy.BLOB)
    score = sqlalchemy.Column(sqlalchemy.Integer)
    categories = orm.relation("Category",
                              secondary="questions_to_categories",
                              backref="questions")

    def __repr__(self):
        return f"{self.title}\n{self.text}"

    def __str__(self):
        return f"{self.title}\n{self.text}"
