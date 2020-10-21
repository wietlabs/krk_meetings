import pytest
from flask.testing import FlaskClient
from sqlalchemy.testing import mock

from src.meetings.app import app, db


@pytest.fixture
def client() -> FlaskClient:
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # in-memory database (:memory:)

    with app.test_client() as client:
        db.create_all()
        yield client


expected_uuid = '12345678-1234-5678-1234-567812345678'

@mock.patch('uuid.uuid4', lambda: expected_uuid)
def test_create_user(client: FlaskClient) -> None:
    response = client.post('/api/v1/users')

    assert response.status_code == 201
    assert response.json == {'uuid': expected_uuid}
    assert response.headers['Location'].endswith(f'/api/v1/users/{expected_uuid}')
