import uuid
from datetime import datetime
from typing import Optional

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
    stop_name = db.Column(db.String(STOP_NAME_MAX_LENGTH), nullable=True)
    owner_uuid = owner_uuid = db.Column(CHAR(36), db.ForeignKey('users.uuid'), nullable=False)
    created_at = db.Column(db.DateTime(), default=func.now(), nullable=False)

    owner = db.relationship('User')
    users = db.relationship('Membership', back_populates='meeting', order_by='Membership.joined_at', cascade="all, delete-orphan")


class Membership(db.Model):
    __tablename__ = 'memberships'
    meeting_uuid = db.Column(CHAR(36), db.ForeignKey('meetings.uuid'), primary_key=True)
    user_uuid = db.Column(CHAR(36), db.ForeignKey('users.uuid'), primary_key=True)
    nickname = db.Column(db.String(NICKNAME_MAX_LENGTH))
    stop_name = db.Column(db.String(STOP_NAME_MAX_LENGTH), nullable=True)
    joined_at = db.Column(db.DateTime(), default=func.now(), nullable=False)

    user = db.relationship('User', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='users')


class ApiException(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


def is_uuid_valid(string: str) -> bool:
    try:
        uuid.UUID(string, version=4)
    except ValueError:
        return False
    return True


def parse_datetime(string: str) -> datetime:
    try:
        return datetime.fromisoformat(string)
    except ValueError:
        raise ApiException('Invalid meeting datetime', 400)


def format_datetime(dt: datetime) -> Optional[str]:
    if dt is None:
        return None
    return dt.isoformat()


def validate_user_uuid(user_uuid: str) -> None:
    if not is_uuid_valid(user_uuid):
        raise ApiException('Invalid user uuid', 400)


def validate_meeting_uuid(meeting_uuid: str) -> None:
    if not is_uuid_valid(meeting_uuid):
        raise ApiException('Invalid meeting uuid', 400)


def validate_meeting_name(stop_name: str) -> None:
    if len(stop_name) > MEETING_NAME_MAX_LENGTH:
        raise ApiException('Meeting name too long', 400)


def validate_stop_name(stop_name: str) -> None:
    if len(stop_name) > STOP_NAME_MAX_LENGTH:
        raise ApiException('Stop name too long', 400)


def validate_nickname(nickname: str) -> None:
    if len(nickname) > NICKNAME_MAX_LENGTH:
        raise ApiException('Nickname too long', 400)


def check_json_data() -> None:
    if request.json is None:
        raise ApiException('Missing JSON data', 400)


def get_user_uuid() -> str:
    if 'user_uuid' not in request.json:
        raise ApiException('Missing user uuid', 400)
    user_uuid = request.json['user_uuid']
    validate_user_uuid(user_uuid)
    return user_uuid


def get_nickname() -> Optional[str]:
    if 'nickname' not in request.json:
        return None
    nickname = request.json['nickname']
    validate_nickname(nickname)
    return nickname


def get_meeting_name() -> Optional[str]:
    if 'name' not in request.json:
        return None
    name = request.json['name']
    validate_meeting_name(name)
    return name


def get_stop_name() -> Optional[str]:
    if 'stop_name' not in request.json:
        return None
    stop_name = request.json['stop_name']
    validate_stop_name(stop_name)
    return stop_name


def get_datetime() -> Optional[datetime]:
    if 'datetime' not in request.json:
        return None
    return parse_datetime(request.json['datetime'])


def find_user(user_uuid: str) -> User:
    user = User.query.get(user_uuid)
    if user is None:
        raise ApiException('User not found', 404)
    return user


def find_meeting(meeting_uuid: str) -> Meeting:
    meeting = Meeting.query.get(meeting_uuid)
    if meeting is None:
        raise ApiException('Meeting not found', 404)
    return meeting


def find_membership(meeting_uuid: str, user_uuid: str) -> Membership:
    membership = Membership.query.get((meeting_uuid, user_uuid))
    if membership is None:
        raise ApiException('Membership not found', 404)
    return membership


def is_owner(user: User, meeting: Meeting) -> bool:
    return user == meeting.owner


def must_be_meeting_owner(user: User, meeting: Meeting) -> None:
    if not is_owner(user, meeting):
        raise ApiException('You are not a meeting owner', 403)


def get_meeting_owner_nickname(meeting: Meeting) -> str:
    return next(
        membership.nickname
        for membership in meeting.users
        if is_owner(membership.user, meeting)
    )


@app.errorhandler(ApiException)
def handle_api_exception(e):
    return {'error': str(e)}, e.status_code


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
    validate_user_uuid(user_uuid)
    find_user(user_uuid)
    return '', 204


@app.route('/api/v1/users/<user_uuid>/meetings', methods=['GET'])
def get_user_meetings(user_uuid: str):
    validate_user_uuid(user_uuid)
    user = find_user(user_uuid)

    return {
        'meetings': [
            {
                'uuid': membership.meeting.uuid,
                'name': membership.meeting.name,
                'nickname': membership.nickname,
                'datetime': format_datetime(membership.meeting.datetime),
                'members_count': len(membership.meeting.users),  # TODO: use COUNT()
            }
            for membership in user.meetings
        ]
    }, 200


@app.route('/api/v1/users/<user_uuid>/meetings/<meeting_uuid>', methods=['GET'])
def get_meeting_details(user_uuid: str, meeting_uuid: str):
    validate_user_uuid(user_uuid)
    validate_meeting_uuid(meeting_uuid)

    user = find_user(user_uuid)
    meeting = find_meeting(meeting_uuid)
    membership = find_membership(meeting_uuid, user_uuid)

    return {
        'uuid': meeting.uuid,
        'name': meeting.name,
        'datetime': format_datetime(meeting.datetime),
        'stop_name': meeting.stop_name,
        'members': [
            {
                'nickname': membership.nickname,
                'is_owner': is_owner(membership.user, meeting),
                'is_you': membership.user == user,
                'stop_name': membership.stop_name,
            }
            for membership in meeting.users
        ],
        'membership': {
            'is_owner': is_owner(user, meeting),
            'stop_name': membership.stop_name,
        }
    }, 200


@app.route('/api/v1/users/<user_uuid>/meetings/<meeting_uuid>', methods=['PATCH'])
def update_meeting_member_details(user_uuid: str, meeting_uuid: str):
    validate_user_uuid(user_uuid)
    validate_meeting_uuid(meeting_uuid)
    check_json_data()
    stop_name = get_stop_name()

    membership = find_membership(meeting_uuid, user_uuid)
    membership.stop_name = stop_name
    db.session.commit()

    return '', 204


@app.route('/api/v1/meetings', methods=['POST'])
def create_meeting():
    check_json_data()
    user_uuid = get_user_uuid()
    nickname = get_nickname()
    meeting_name = get_meeting_name()
    dt = get_datetime()

    user = find_user(user_uuid)

    meeting = Meeting(name=meeting_name, datetime=dt, owner=user)
    membership = Membership(meeting=meeting, user=user, nickname=nickname)
    db.session.add(membership)
    db.session.commit()

    return make_response({
        'uuid': meeting.uuid,
    }, 201, {
        'Location': f'/api/v1/meetings/{meeting.uuid}'
    })


@app.route('/api/v1/meetings/<meeting_uuid>', methods=['GET'])
def get_meeting_join_info(meeting_uuid: str):
    validate_meeting_uuid(meeting_uuid)

    meeting = find_meeting(meeting_uuid)

    return {
        'uuid': meeting.uuid,
        'name': meeting.name,
        'members_count': len(meeting.users),
        'owner_nickname': get_meeting_owner_nickname(meeting)
    }, 200


@app.route('/api/v1/meetings/<meeting_uuid>', methods=['PATCH'])
def edit_meeting(meeting_uuid: str):
    validate_meeting_uuid(meeting_uuid)
    check_json_data()
    user_uuid = get_user_uuid()
    stop_name = get_stop_name()
    dt = get_datetime()

    meeting = find_meeting(meeting_uuid)
    user = find_user(user_uuid)
    must_be_meeting_owner(user, meeting)

    if stop_name is not None:
        meeting.stop_name = stop_name
    if dt is not None:
        meeting.datetime = dt
    db.session.commit()

    return '', 204


@app.route('/api/v1/meetings/<meeting_uuid>', methods=['DELETE'])
def delete_meeting(meeting_uuid: str):
    validate_meeting_uuid(meeting_uuid)
    check_json_data()
    user_uuid = get_user_uuid()

    meeting = find_meeting(meeting_uuid)
    user = find_user(user_uuid)
    must_be_meeting_owner(user, meeting)

    db.session.delete(meeting)
    db.session.commit()

    return '', 204


@app.route('/api/v1/meetings/<meeting_uuid>/members', methods=['POST'])
def join_meeting(meeting_uuid: str):
    validate_meeting_uuid(meeting_uuid)
    check_json_data()
    user_uuid = get_user_uuid()
    nickname = get_nickname()

    user = find_user(user_uuid)
    meeting = find_meeting(meeting_uuid)

    membership = Membership(user=user, meeting=meeting, nickname=nickname)
    db.session.add(membership)
    try:
        db.session.commit()
    except IntegrityError:
        raise ApiException('Already a member', 400)

    return '', 204


@app.route('/api/v1/meetings/<meeting_uuid>/members/<user_uuid>', methods=['DELETE'])
def leave_meeting(meeting_uuid: str, user_uuid: str):
    validate_meeting_uuid(meeting_uuid)
    validate_user_uuid(user_uuid)

    user = find_user(user_uuid)
    meeting = find_meeting(meeting_uuid)

    if is_owner(user, meeting):
        raise ApiException('Meeting owner cannot leave meeting', 403)

    membership = find_membership(meeting_uuid, user_uuid)
    db.session.delete(membership)
    db.session.commit()

    return '', 204


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8000)
