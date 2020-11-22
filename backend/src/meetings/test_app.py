from datetime import datetime

import pytest
from flask.testing import FlaskClient
from sqlalchemy.testing import mock

from src.meetings.MeetingsServer import app, db, User


@pytest.fixture
def client() -> FlaskClient:
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # in-memory database (:memory:)

    with app.test_client() as client:
        db.create_all()
        yield client

    db.drop_all()


expected_uuid = '12345678-1234-5678-1234-567812345678'
expected_created_at = datetime(2020, 10, 21, 20, 30, 40)


@mock.patch('uuid.uuid4', lambda: expected_uuid)
def test_create_user(client: FlaskClient) -> None:
    response = client.post('/api/v1/users')

    user = User.query.get(expected_uuid)
    assert user is not None
    assert user.uuid == expected_uuid

    assert response.status_code == 201
    assert response.json == {'uuid': expected_uuid}
    assert response.headers['Location'].endswith(f'/api/v1/users/{expected_uuid}')


def test_create_meeting_missing_json_data(client: FlaskClient) -> None:
    response = client.post('/api/v1/meetings')

    assert response.status_code == 400
    assert response.json == {'error': 'Missing JSON data'}


def test_create_meeting_missing_user_uuid(client: FlaskClient) -> None:
    response = client.post('/api/v1/meetings', json={})

    assert response.status_code == 400
    assert response.json == {'error': 'Missing user_uuid'}


def test_create_meeting_invalid_user_uuid(client: FlaskClient) -> None:
    response = client.post('/api/v1/meetings', json={'user_uuid': 'foobar'})

    assert response.status_code == 400
    assert response.json == {'error': 'Invalid user_uuid'}


def test_create_meeting_nickname_too_long(client: FlaskClient) -> None:
    response = client.post('/api/v1/meetings', json={
        'user_uuid': '12345678-1234-5678-1234-567812345678',
        'nickname': 'a' * 51,
    })

    assert response.status_code == 400
    assert response.json == {'error': 'Nickname too long'}


def test_create_meeting_name_too_long(client: FlaskClient) -> None:
    response = client.post('/api/v1/meetings', json={
        'user_uuid': '12345678-1234-5678-1234-567812345678',
        'name': 'a' * 51,
    })

    assert response.status_code == 400
    assert response.json == {'error': 'Meeting name too long'}


def test_create_meeting_invalid_datetime(client: FlaskClient) -> None:
    response = client.post('/api/v1/meetings', json={
        'user_uuid': '12345678-1234-5678-1234-567812345678',
        'datetime': 'abcdef',
    })

    assert response.status_code == 400
    assert response.json == {'error': 'Invalid meeting datetime'}


def test_create_meeting_user_not_found(client: FlaskClient) -> None:
    response = client.post('/api/v1/meetings', json={
        'user_uuid': '12345678-1234-5678-1234-567812345678',
        'nickname': 'nickname',
    })

    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}


def test_create_meeting(client: FlaskClient) -> None:
    response = client.post('/api/v1/users')
    owner_uuid = response.json['uuid']

    with mock.patch('uuid.uuid4', lambda: expected_uuid):
        response = client.post('/api/v1/meetings', json={
            'user_uuid': owner_uuid,
            'nickname': 'Alice',
            'name': 'My meeting',
            'datetime': '2020-01-02T03:04:05',
        })

    assert response.status_code == 201
    assert response.json == {'uuid': expected_uuid}
    assert response.headers['Location'].endswith(f'/api/v1/meetings/{expected_uuid}')

    response = client.get(f'/api/v1/meetings/{expected_uuid}')

    assert response.status_code == 200
    assert response.json == {
        'uuid': expected_uuid,
        'name': 'My meeting',
        'members_count': 1,
        'owner_nickname': 'Alice',
    }

    response = client.get(f'/api/v1/users/{owner_uuid}/meetings/{expected_uuid}')

    assert response.status_code == 200
    assert response.json == {
        'uuid': expected_uuid,
        'name': 'My meeting',
        'stop_name': None,
        'members': [
            {
                'nickname': 'Alice',
                'is_owner': True,
                'is_you': True,
                'stop_name': None,
            }
        ],
        'membership': {
            'is_owner': True,
            'stop_name': None,
        },
    }
