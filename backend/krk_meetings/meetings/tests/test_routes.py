from datetime import datetime

import pytest
from flask.testing import FlaskClient
from sqlalchemy.testing import mock

from krk_meetings.meetings import app, db
from krk_meetings.meetings.models import User, Meeting, Membership

example_uuid1 = '11111111-1111-1111-1111-111111111111'
example_uuid2 = '22222222-2222-2222-2222-222222222222'
example_uuid3 = '33333333-3333-3333-3333-333333333333'
example_uuid4 = '44444444-4444-4444-4444-444444444444'
example_uuid5 = '55555555-5555-5555-5555-555555555555'


@pytest.fixture(scope='function')
def client() -> FlaskClient:
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # in-memory database (:memory:)

    with app.test_client() as client:
        db.create_all()
        yield client

    db.drop_all()


def test_create_user(client: FlaskClient) -> None:
    with mock.patch('uuid.uuid4', lambda: example_uuid1):
        response = client.post('/api/v1/users')
    assert response.status_code == 201
    assert response.json == {'uuid': example_uuid1}
    assert response.headers['Location'].endswith(f'/api/v1/users/{example_uuid1}')

    user = User.query.get(example_uuid1)
    assert user is not None
    assert user.uuid == example_uuid1


def test_check_if_user_exists_true(client: FlaskClient) -> None:
    user = User(uuid=example_uuid1)
    db.session.add(user)
    db.session.commit()

    response = client.get(f'/api/v1/users/{example_uuid1}')
    assert response.status_code == 204
    assert response.data == b''


def test_check_if_user_exists_false(client: FlaskClient) -> None:
    response = client.get(f'/api/v1/users/{example_uuid1}')
    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}


def test_get_user_meetings(client: FlaskClient) -> None:
    user1 = User(uuid=example_uuid1)
    user2 = User(uuid=example_uuid2)
    user3 = User(uuid=example_uuid3)
    meeting1 = Meeting(uuid=example_uuid4, owner=user1, name='Lorem ipsum')
    meeting2 = Meeting(uuid=example_uuid5, owner=user2, datetime=datetime(2020, 1, 2, 3, 4, 5))
    membership1 = Membership(meeting=meeting1, user=user1, nickname='Alice')
    membership2 = Membership(meeting=meeting1, user=user3, nickname='Charlie')
    membership3 = Membership(meeting=meeting2, user=user1, nickname='Ala')
    membership4 = Membership(meeting=meeting2, user=user2, nickname='Bob')
    membership5 = Membership(meeting=meeting2, user=user3, nickname='Charlie')
    db.session.add(membership1)
    db.session.add(membership2)
    db.session.add(membership3)
    db.session.add(membership4)
    db.session.add(membership5)
    db.session.commit()

    response = client.get(f'/api/v1/users/{user1.uuid}/meetings')
    assert response.status_code == 200
    assert response.json == {
        'meetings': [
            {
                'uuid': meeting1.uuid,
                'name': 'Lorem ipsum',
                'nickname': 'Alice',
                'datetime': None,
                'members_count': 2,
            },
            {
                'uuid': meeting2.uuid,
                'name': None,
                'nickname': 'Ala',
                'datetime': '2020-01-02T03:04:05',
                'members_count': 3,
            },
        ]
    }


def test_create_meeting(client: FlaskClient) -> None:
    user = User(uuid=example_uuid1)
    db.session.add(user)
    db.session.commit()

    with mock.patch('uuid.uuid4', lambda: example_uuid2):
        response = client.post('/api/v1/meetings', json={
            'owner_uuid': user.uuid,
            'name': 'Lorem ipsum',
            'description': 'Lorem ipsum sit dolor amet.',
            'datetime': '2020-01-02T03:04:05',
            'nickname': 'Alice',
        })
    assert response.status_code == 201
    assert response.json == {'uuid': example_uuid2}
    assert response.headers['Location'].endswith(f'/api/v1/meetings/{example_uuid2}')

    meeting = Meeting.query.get(example_uuid2)
    assert meeting is not None
    assert meeting.uuid == example_uuid2
    assert meeting.name == 'Lorem ipsum'
    assert meeting.description == 'Lorem ipsum sit dolor amet.'
    assert meeting.datetime == datetime(2020, 1, 2, 3, 4, 5)

    membership = Membership.query.get((meeting.uuid, user.uuid))
    assert membership is not None
    assert membership.nickname == 'Alice'
    assert membership.stop_name is None


def test_get_meeting_join_info(client: FlaskClient) -> None:
    user1 = User(uuid=example_uuid1)
    user2 = User(uuid=example_uuid2)
    user3 = User(uuid=example_uuid3)
    meeting = Meeting(uuid=example_uuid4, owner=user1,
                      name='Lorem ipsum', description='Lorem ipsum sit dolor amet.',
                      datetime=datetime(2020, 1, 2, 3, 4, 5))
    membership1 = Membership(meeting=meeting, user=user1, nickname='Alice')
    membership2 = Membership(meeting=meeting, user=user2, nickname='Bob')
    membership3 = Membership(meeting=meeting, user=user3, nickname='Charlie')
    db.session.add(membership1)
    db.session.add(membership2)
    db.session.add(membership3)
    db.session.commit()

    response = client.get(f'/api/v1/meetings/{meeting.uuid}')
    assert response.status_code == 200
    assert response.json == {
        'name': 'Lorem ipsum',
        'datetime': '2020-01-02T03:04:05',
        'members_count': 3,
        'owner_nickname': 'Alice',
    }


def test_edit_meeting(client: FlaskClient) -> None:
    owner = User(uuid=example_uuid1)
    meeting = Meeting(uuid=example_uuid2, owner=owner)
    db.session.add(meeting)
    db.session.commit()

    response = client.patch(f'/api/v1/meetings/{meeting.uuid}', json={
        'owner_uuid': owner.uuid,
        'name': 'Lorem ipsum',
        'description': 'Lorem ipsum sit dolor amet.',
        'datetime': '2020-01-02T03:04:05',
        'stop_name': 'Czarnowiejska',
    })
    assert response.status_code == 204

    meeting = Meeting.query.get(meeting.uuid)
    assert meeting.name == 'Lorem ipsum'
    assert meeting.description == 'Lorem ipsum sit dolor amet.'
    assert meeting.datetime == datetime(2020, 1, 2, 3, 4, 5)
    assert meeting.stop_name == 'Czarnowiejska'


def test_delete_meeting(client: FlaskClient) -> None:
    owner = User(uuid=example_uuid1)
    user = User(uuid=example_uuid2)
    meeting = Meeting(uuid=example_uuid3, owner=owner)
    membership1 = Membership(meeting=meeting, user=owner, nickname='Alice')
    membership2 = Membership(meeting=meeting, user=user, nickname='Bob')
    db.session.add(membership1)
    db.session.add(membership2)
    db.session.commit()

    response = client.delete(f'/api/v1/meetings/{meeting.uuid}', json={'owner_uuid': owner.uuid})
    assert response.status_code == 204
    assert response.data == b''

    assert Meeting.query.get(meeting.uuid) is None
    assert Membership.query.get((meeting.uuid, owner.uuid)) is None
    assert Membership.query.get((meeting.uuid, user.uuid)) is None


def test_join_meeting(client: FlaskClient) -> None:
    owner = User(uuid=example_uuid1)
    user = User(uuid=example_uuid2)
    meeting = Meeting(uuid=example_uuid3, owner=owner)
    db.session.add(meeting)
    db.session.add(user)
    db.session.commit()

    response = client.put(f'/api/v1/memberships/{meeting.uuid}/{user.uuid}', json={'nickname': 'Bob'})
    assert response.status_code == 204
    assert response.data == b''

    membership = Membership.query.get((meeting.uuid, user.uuid))
    assert membership is not None
    assert membership.nickname == 'Bob'
    assert membership.stop_name is None


def test_join_meeting_already_a_member(client: FlaskClient) -> None:
    owner = User(uuid=example_uuid1)
    user = User(uuid=example_uuid2)
    meeting = Meeting(uuid=example_uuid3, owner=owner)
    membership = Membership(meeting=meeting, user=user, nickname='Bob')
    db.session.add(membership)
    db.session.commit()

    response = client.put(f'/api/v1/memberships/{meeting.uuid}/{user.uuid}', json={'nickname': 'Bobby'})
    assert response.status_code == 400
    assert response.json == {'error': 'Already a member'}


def test_get_membership_details(client: FlaskClient) -> None:
    user1 = User(uuid=example_uuid1)
    user2 = User(uuid=example_uuid2)
    meeting = Meeting(uuid=example_uuid3, owner=user1,
                      name='Lorem ipsum', description='Lorem ipsum sit dolor amet.',
                      datetime=datetime(2020, 1, 2, 3, 4, 5), stop_name='Czarnowiejska')
    membership1 = Membership(meeting=meeting, user=user1, nickname='Alice', stop_name='Kawiory')
    membership2 = Membership(meeting=meeting, user=user2, nickname='Bob', stop_name='Muzeum Narodowe')
    db.session.add(membership1)
    db.session.add(membership2)
    db.session.commit()

    response = client.get(f'/api/v1/memberships/{meeting.uuid}/{user2.uuid}')
    assert response.status_code == 200
    assert response.json == {
        'uuid': meeting.uuid,
        'name': 'Lorem ipsum',
        'description': 'Lorem ipsum sit dolor amet.',
        'datetime': '2020-01-02T03:04:05',
        'stop_name': 'Czarnowiejska',
        'members': [
            {
                'nickname': 'Alice',
                'is_owner': True,
                'is_you': False,
                'stop_name': 'Kawiory',
            },
            {
                'nickname': 'Bob',
                'is_owner': False,
                'is_you': True,
                'stop_name': 'Muzeum Narodowe',
            },
        ],
        'membership': {
            'is_owner': False,
            'stop_name': 'Muzeum Narodowe',
        }
    }


def test_edit_membership_details(client: FlaskClient) -> None:
    user = User(uuid=example_uuid1)
    meeting = Meeting(uuid=example_uuid2, owner=user)
    membership = Membership(meeting=meeting, user=user)
    db.session.add(membership)
    db.session.commit()

    response = client.patch(f'/api/v1/memberships/{meeting.uuid}/{user.uuid}', json={'stop_name': 'Chopina'})
    assert response.status_code == 204
    assert response.data == b''

    membership = Membership.query.get((meeting.uuid, user.uuid))
    assert membership.stop_name == 'Chopina'


def test_leave_meeting(client: FlaskClient) -> None:
    owner = User(uuid=example_uuid1)
    user = User(uuid=example_uuid2)
    meeting = Meeting(uuid=example_uuid3, owner=owner)
    membership1 = Membership(meeting=meeting, user=owner)
    membership2 = Membership(meeting=meeting, user=user)
    db.session.add(membership1)
    db.session.add(membership2)
    db.session.commit()

    response = client.delete(f'/api/v1/memberships/{meeting.uuid}/{user.uuid}')
    assert response.status_code == 204
    assert response.data == b''

    assert Membership.query.get((meeting.uuid, user.uuid)) is None


def test_leave_meeting_owner(client: FlaskClient) -> None:
    owner = User(uuid=example_uuid1)
    meeting = Meeting(uuid=example_uuid2, owner=owner)
    membership = Membership(meeting=meeting, user=owner)
    db.session.add(membership)
    db.session.commit()

    response = client.delete(f'/api/v1/memberships/{meeting.uuid}/{owner.uuid}')
    assert response.status_code == 403
    assert response.json == {'error': 'Meeting owner cannot leave meeting'}
