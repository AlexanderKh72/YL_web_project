import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


questions_to_categories_table = sqlalchemy.Table(
        'questions_to_categories',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('question_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('questions.id')),
    sqlalchemy.Column('category_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('categories.id'))
)


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'categories'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True)
