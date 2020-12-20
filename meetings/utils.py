import uuid
from datetime import datetime
from typing import Optional

from flask import request

from exceptions import ApiException
from models import MEETING_NAME_MAX_LENGTH, MEETING_DESCRIPTION_MAX_LENGTH, STOP_NAME_MAX_LENGTH, \
    NICKNAME_MAX_LENGTH, User, Meeting, Membership


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


def validate_meeting_description(description: str) -> None:
    if len(description) > MEETING_DESCRIPTION_MAX_LENGTH:
        raise ApiException('Meeting description too long', 400)


def validate_stop_name(stop_name: str) -> None:
    if len(stop_name) > STOP_NAME_MAX_LENGTH:
        raise ApiException('Stop name too long', 400)


def validate_nickname(nickname: str) -> None:
    if len(nickname) > NICKNAME_MAX_LENGTH:
        raise ApiException('Nickname too long', 400)


def check_json_data() -> None:
    if request.json is None:
        raise ApiException('Missing JSON data', 400)


def get_owner_uuid() -> str:
    if 'owner_uuid' not in request.json:
        raise ApiException('Missing owner uuid', 400)
    owner_uuid = request.json['owner_uuid']
    validate_user_uuid(owner_uuid)
    return owner_uuid


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


def get_meeting_description() -> Optional[str]:
    if 'description' not in request.json:
        return None
    name = request.json['description']
    validate_meeting_description(name)
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
