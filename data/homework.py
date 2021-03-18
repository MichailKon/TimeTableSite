import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Homework(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'homework'
    homework_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    homework_schedule = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("schedule.schedule_id"))
    homework_week = sqlalchemy.Column(sqlalchemy.Integer)
