import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Schedule(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'schedule'
    schedule_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    schedule_subject = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("subjects.subject_id"))
    schedule_day = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("days.day_id"))
    schedule_num = sqlalchemy.Column(sqlalchemy.Integer)
