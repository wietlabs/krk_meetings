import uuid
from datetime import datetime

from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CHAR

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db = SQLAlchemy(app)


class Membership(db.Model):
    __tablename__ = 'memberships'
    meeting_uuid = db.Column(CHAR(36), db.ForeignKey('meetings.uuid'), primary_key=True)
    user_uuid = db.Column(CHAR(36), db.ForeignKey('users.uuid'), primary_key=True)
    nickname = db.Column(db.String(50))
    joined_at = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    user = db.relationship('User', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='users')


class User(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(CHAR(36), default=lambda: str(uuid.uuid4()), primary_key=True)

    meetings = db.relationship('Membership', back_populates='user')


class Meeting(db.Model):
    __tablename__ = 'meetings'
    uuid = db.Column(CHAR(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    owner_uuid = owner_uuid = db.Column(CHAR(36), db.ForeignKey('users.uuid'), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    owner = db.relationship('User')
    users = db.relationship('Membership', back_populates='meeting')


@app.route('/users', methods=['POST'])
def create_user():
    user = User()
    db.session.add(user)
    db.session.commit()

    return make_response({
        'uuid': user.uuid,
    }, 201, {
        'Location': f'/users/{user.uuid}'
    })


@app.route('/meetings', methods=['POST'])
def create_meeting():
    user_uuid = request.args['user_uuid']
    nickname = request.args['nickname']

    # TODO: validate request args

    user = User.query.get(user_uuid)
    if not user:
        return {'error': 'User not found'}, 404

    meeting = Meeting(owner=user)
    membership = Membership(meeting=meeting, user=user, nickname=nickname)

    # db.session.add(meeting)  # not mandatory
    db.session.add(membership)
    db.session.commit()

    return make_response({
        'uuid': meeting.uuid,
    }, 201, {
        'Location': f'/meetings/{meeting.uuid}'
    })


@app.route('/meetings/<meeting_uuid>', methods=['GET'])
def get_meeting(meeting_uuid: str):
    meeting = Meeting.query.get(meeting_uuid)
    if meeting is None:
        return {'error': 'Meeting not found'}, 404

    return {
        'uuid': meeting.uuid,
        'created_at': meeting.created_at.isoformat(),
        'members': [
            {
                'nickname': member.nickname,
                'is_owner': member.user == meeting.owner,  # OR: member.user.uuid == meeting.owner_uuid
            }
            for member in meeting.users
        ],
    }, 200


@app.route('/meetings/<meeting_uuid>/members', methods=['POST'])
def join_meeting(meeting_uuid: str):
    user_uuid = request.args['user_uuid']
    nickname = request.args['nickname']

    # TODO: validate args

    meeting = Meeting.query.get(meeting_uuid)
    if meeting is None:
        return {'error': 'Meeting not found'}, 404

    user = User.query.get(user_uuid)
    if user is None:
        return {'error': 'User not found'}, 404

    membership = Membership(user=user, meeting=meeting, nickname=nickname)
    db.session.add(membership)
    db.session.commit()

    return {
        # TODO: return meeting info
    }, 201


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
