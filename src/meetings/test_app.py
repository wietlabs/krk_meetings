from datetime import datetime

import pytest
from flask.testing import FlaskClient
from sqlalchemy.testing import mock

from src.meetings.app import app, db, User


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


def test_create_meeting_user_not_found(client: FlaskClient) -> None:
    response = client.post('/api/v1/meetings', json={
        'user_uuid': '12345678-1234-5678-1234-567812345678',
        'nickname': 'nickname',
    })

    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}
