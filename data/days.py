import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Day(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'days'
    day_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    day_name = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)
