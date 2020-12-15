import uuid

from sqlalchemy import CHAR, event, func
from sqlalchemy.engine import Engine

from krk_meetings.meetings import db

MEETING_NAME_MAX_LENGTH = 50
MEETING_DESCRIPTION_MAX_LENGTH = 500
NICKNAME_MAX_LENGTH = 50
STOP_NAME_MAX_LENGTH = 100

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class User(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(CHAR(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    created_at = db.Column(db.DateTime(), default=func.now(), nullable=False)

    meetings = db.relationship('Membership', back_populates='user')


class Meeting(db.Model):
    __tablename__ = 'meetings'
    uuid = db.Column(CHAR(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    name = db.Column(db.String(MEETING_NAME_MAX_LENGTH), nullable=True)
    description = db.Column(db.String(MEETING_DESCRIPTION_MAX_LENGTH), nullable=True)
    datetime = db.Column(db.DateTime(), nullable=True)
    stop_name = db.Column(db.String(STOP_NAME_MAX_LENGTH), nullable=True)
    owner_uuid = db.Column(CHAR(36), db.ForeignKey('users.uuid'), nullable=False)
    created_at = db.Column(db.DateTime(), default=func.now(), nullable=False)

    owner = db.relationship('User')
    users = db.relationship('Membership', back_populates='meeting',
                            order_by='Membership.joined_at', cascade='all, delete')


class Membership(db.Model):
    __tablename__ = 'memberships'
    meeting_uuid = db.Column(CHAR(36), db.ForeignKey('meetings.uuid', ondelete='CASCADE'), primary_key=True)
    user_uuid = db.Column(CHAR(36), db.ForeignKey('users.uuid'), primary_key=True)
    nickname = db.Column(db.String(NICKNAME_MAX_LENGTH))
    stop_name = db.Column(db.String(STOP_NAME_MAX_LENGTH), nullable=True)
    joined_at = db.Column(db.DateTime(), default=func.now(), nullable=False)

    user = db.relationship('User', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='users')
