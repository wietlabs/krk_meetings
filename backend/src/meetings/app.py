import uuid
from datetime import datetime

from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CHAR, func
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db = SQLAlchemy(app)

MEETING_NAME_MAX_LENGTH = 50
NICKNAME_MAX_LENGTH = 50
STOP_NAME_MAX_LENGTH = 100


class User(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(CHAR(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    created_at = db.Column(db.DateTime(), default=func.now(), nullable=False)

    meetings = db.relationship('Membership', back_populates='user')


class Meeting(db.Model):
    __tablename__ = 'meetings'
    uuid = db.Column(CHAR(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    name = db.Column(db.String(MEETING_NAME_MAX_LENGTH), nullable=True)
    datetime = db.Column(db.DateTime(), nullable=True)
    owner_uuid = owner_uuid = db.Column(CHAR(36), db.ForeignKey('users.uuid'), nullable=False)
    created_at = db.Column(db.DateTime(), default=func.now(), nullable=False)

    owner = db.relationship('User')
    users = db.relationship('Membership', back_populates='meeting', order_by='Membership.joined_at')


class Membership(db.Model):
    __tablename__ = 'memberships'
    meeting_uuid = db.Column(CHAR(36), db.ForeignKey('meetings.uuid'), primary_key=True)
    user_uuid = db.Column(CHAR(36), db.ForeignKey('users.uuid'), primary_key=True)
    nickname = db.Column(db.String(NICKNAME_MAX_LENGTH))
    # position_stop_name = db.Column(db.String(STOP_NAME_MAX_LENGTH), nullable=True)
    # position_latitude = db.Column(db.Float(), nullable=True)
    # position_longitude = db.Column(db.Float(), nullable=True)
    joined_at = db.Column(db.DateTime(), default=func.now(), nullable=False)

    user = db.relationship('User', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='users')


@app.route('/api/v1/users', methods=['POST'])
def create_user():
    user = User()
    db.session.add(user)
    db.session.commit()

    return make_response({
        'uuid': user.uuid,
    }, 201, {
        'Location': f'/api/v1/users/{user.uuid}'
    })


@app.route('/api/v1/users/<user_uuid>', methods=['GET'])
def get_user(user_uuid: str):
    try:
        uuid.UUID(user_uuid, version=4)
    except ValueError:
        return {'error': 'Invalid user_uuid'}, 400

    user = User.query.get(user_uuid)
    if not user:
        return {'error': 'User not found'}, 404

    return {}, 200


@app.route('/api/v1/users/<user_uuid>/meetings', methods=['GET'])
def get_meetings(user_uuid: str):
    try:
        uuid.UUID(user_uuid, version=4)
    except ValueError:
        return {'error': 'Invalid user_uuid'}, 400

    user = User.query.get(user_uuid)
    if not user:
        return {'error': 'User not found'}, 404

    return {
        'meetings': [
            {
                'uuid': membership.meeting.uuid,
                'name': membership.meeting.name,
                'nickname': membership.nickname,
                # 'datetime': membership.meeting.datetime.isoformat(),
                'members_count': len(membership.meeting.users),  # TODO: use COUNT()
            }
            for membership in user.meetings
        ]
    }, 200


@app.route('/api/v1/meetings', methods=['POST'])
def create_meeting():
    if request.json is None:
        return {'error': 'Missing JSON data'}, 400

    if 'user_uuid' not in request.json:
        return {'error': 'Missing user_uuid'}, 400
    user_uuid = request.json['user_uuid']

    try:
        uuid.UUID(user_uuid, version=4)
    except ValueError:
        return {'error': 'Invalid user_uuid'}, 400

    if 'nickname' in request.json:
        nickname = request.json['nickname']
        if len(nickname) > NICKNAME_MAX_LENGTH:
            return {'error': 'Nickname too long'}, 400
    else:
        nickname = None

    if 'name' in request.json:
        name = request.json['name']
        if len(name) > MEETING_NAME_MAX_LENGTH:
            return {'error': 'Meeting name too long'}, 400
    else:
        name = None

    if 'datetime' in request.json:
        dt = request.json['datetime']
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return {'error': 'Invalid meeting datetime'}, 400
    else:
        dt = None

    user = User.query.get(user_uuid)
    if not user:
        return {'error': 'User not found'}, 404

    meeting = Meeting(name=name, datetime=dt, owner=user)
    membership = Membership(meeting=meeting, user=user, nickname=nickname)

    db.session.add(membership)
    db.session.commit()

    return make_response({
        'uuid': meeting.uuid,
    }, 201, {
        'Location': f'/api/v1/meetings/{meeting.uuid}'
    })


@app.route('/api/v1/meetings/<meeting_uuid>', methods=['GET'])
def get_meeting(meeting_uuid: str):
    try:
        uuid.UUID(meeting_uuid, version=4)
    except ValueError:
        return {'error': 'Invalid meeting_uuid'}, 400

    meeting = Meeting.query.get(meeting_uuid)
    if meeting is None:
        return {'error': 'Meeting not found'}, 404

    memberships = meeting.users

    return {
        'uuid': meeting.uuid,
        'name': meeting.name,
        'members': [
            {
                'nickname': membership.nickname,
                'is_owner': membership.user == meeting.owner,
            }
            for membership in memberships
        ],
    }, 200


@app.route('/api/v1/meetings/<meeting_uuid>/members', methods=['POST'])
def join_meeting(meeting_uuid: str):
    try:
        uuid.UUID(meeting_uuid, version=4)
    except ValueError:
        return {'error': 'Invalid meeting_uuid'}, 400

    if 'user_uuid' not in request.json:
        return {'error': 'Missing user_uuid'}, 400
    user_uuid = request.json['user_uuid']

    try:
        uuid.UUID(user_uuid, version=4)
    except ValueError:
        return {'error': 'Invalid user_uuid'}, 400

    if 'nickname' not in request.json:
        return {'error': 'Missing nickname'}, 400
    nickname = request.json['nickname']

    if len(nickname) > NICKNAME_MAX_LENGTH:
        return {'error': 'Nickname too long'}, 400

    user = User.query.get(user_uuid)
    if not user:
        return {'error': 'User not found'}, 404

    meeting = Meeting.query.get(meeting_uuid)
    if meeting is None:
        return {'error': 'Meeting not found'}, 404

    user = User.query.get(user_uuid)
    if user is None:
        return {'error': 'User not found'}, 404

    membership = Membership(user=user, meeting=meeting, nickname=nickname)

    db.session.add(membership)
    try:
        db.session.commit()
    except IntegrityError:
        return {'error': 'Already a member'}, 400

    return {}, 201


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0')