from uuid import UUID

import pytest
from flask.testing import FlaskClient

from src.meetings.app import app, db


@pytest.fixture
def client() -> FlaskClient:
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # in-memory database (:memory:)

    with app.test_client() as client:
        db.create_all()
        yield client


def test_create_user(client: FlaskClient) -> None:
    response = client.post('/api/v1/users')

    uuid = response.json['uuid']
    UUID(uuid, version=4)
    # TODO: mock uuid4 function

    assert response.status_code == 201
    assert response.json == {'uuid': uuid}
    assert response.headers['Location'] == f'http://localhost/users/{uuid}'
