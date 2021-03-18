import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Subject(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'subjects'
    subject_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    subject_name = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)
