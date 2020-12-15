from flask import make_response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from krk_meetings.meetings import app, limiter, db
from krk_meetings.meetings.exceptions import ApiException
from krk_meetings.meetings.models import User, Meeting, Membership
from krk_meetings.meetings.utils import validate_user_uuid, find_user, format_datetime, check_json_data, get_owner_uuid, \
    get_meeting_description, get_meeting_name, get_datetime, get_nickname, validate_meeting_uuid, find_meeting, \
    get_meeting_owner_nickname, get_stop_name, must_be_meeting_owner, find_membership, is_owner


@app.errorhandler(ApiException)
def handle_api_exception(e):
    return {'error': str(e)}, e.status_code


@app.route('/api/v1/users', methods=['POST'])
@limiter.limit('10 per day')
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
def check_if_user_exists(user_uuid: str):
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


@app.route('/api/v1/meetings', methods=['POST'])
@limiter.limit('10 per hour')
def create_meeting():
    check_json_data()
    owner_uuid = get_owner_uuid()
    name = get_meeting_name()
    description = get_meeting_description()
    dt = get_datetime()
    nickname = get_nickname()

    owner = find_user(owner_uuid)

    meeting = Meeting(name=name, description=description, datetime=dt, owner=owner)
    membership = Membership(meeting=meeting, user=owner, nickname=nickname)
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
        'name': meeting.name,
        'datetime': format_datetime(meeting.datetime),
        'members_count': len(meeting.users),
        'owner_nickname': get_meeting_owner_nickname(meeting)
    }, 200


@app.route('/api/v1/meetings/<meeting_uuid>', methods=['PATCH'])
def edit_meeting(meeting_uuid: str):
    validate_meeting_uuid(meeting_uuid)

    check_json_data()
    owner_uuid = get_owner_uuid()
    name = get_meeting_name()
    description = get_meeting_description()
    stop_name = get_stop_name()
    dt = get_datetime()

    meeting = find_meeting(meeting_uuid)
    user = find_user(owner_uuid)
    must_be_meeting_owner(user, meeting)

    if name is not None:
        meeting.name = name
    if description is not None:
        meeting.description = description
    if dt is not None:
        meeting.datetime = dt
    if stop_name is not None:
        meeting.stop_name = stop_name
    db.session.commit()

    return '', 204


@app.route('/api/v1/meetings/<meeting_uuid>', methods=['DELETE'])
def delete_meeting(meeting_uuid: str):
    validate_meeting_uuid(meeting_uuid)

    check_json_data()
    owner_uuid = get_owner_uuid()

    meeting = find_meeting(meeting_uuid)
    user = find_user(owner_uuid)
    must_be_meeting_owner(user, meeting)

    db.session.delete(meeting)
    db.session.commit()

    return '', 204


@app.route('/api/v1/memberships/<meeting_uuid>/<user_uuid>', methods=['PUT'])
def join_meeting(meeting_uuid: str, user_uuid: str):
    validate_meeting_uuid(meeting_uuid)
    validate_user_uuid(user_uuid)

    check_json_data()
    nickname = get_nickname()

    meeting = find_meeting(meeting_uuid)
    user = find_user(user_uuid)

    membership = Membership(user=user, meeting=meeting, nickname=nickname)
    db.session.add(membership)
    try:
        db.session.commit()
    except (IntegrityError, FlushError):
        raise ApiException('Already a member', 400)

    return '', 204


@app.route('/api/v1/memberships/<meeting_uuid>/<user_uuid>', methods=['GET'])
def get_membership_details(meeting_uuid: str, user_uuid: str):
    validate_meeting_uuid(meeting_uuid)
    validate_user_uuid(user_uuid)

    meeting = find_meeting(meeting_uuid)
    user = find_user(user_uuid)
    membership = find_membership(meeting_uuid, user_uuid)

    return {
        'uuid': meeting.uuid,
        'name': meeting.name,
        'description': meeting.description,
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


@app.route('/api/v1/memberships/<meeting_uuid>/<user_uuid>', methods=['PATCH'])
def edit_membership_details(meeting_uuid: str, user_uuid: str):
    validate_meeting_uuid(meeting_uuid)
    validate_user_uuid(user_uuid)

    check_json_data()
    stop_name = get_stop_name()

    membership = find_membership(meeting_uuid, user_uuid)
    membership.stop_name = stop_name
    db.session.commit()

    return '', 204


@app.route('/api/v1/memberships/<meeting_uuid>/<user_uuid>', methods=['DELETE'])
def leave_meeting(user_uuid: str, meeting_uuid: str):
    validate_user_uuid(user_uuid)
    validate_meeting_uuid(meeting_uuid)

    meeting = find_meeting(meeting_uuid)
    user = find_user(user_uuid)

    if is_owner(user, meeting):
        raise ApiException('Meeting owner cannot leave meeting', 403)

    membership = find_membership(meeting_uuid, user_uuid)
    db.session.delete(membership)
    db.session.commit()

    return '', 204
