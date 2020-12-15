from datetime import datetime
from typing import Optional

import pytest
from sqlalchemy.orm import Session

from krk_meetings.meetings import app, db
from krk_meetings.meetings.models import User, Meeting, Membership
from krk_meetings.meetings.scripts import delete_outdated_meetings

example_uuid1 = '11111111-1111-1111-1111-111111111111'
example_uuid2 = '22222222-2222-2222-2222-222222222222'
example_uuid3 = '33333333-3333-3333-3333-333333333333'


@pytest.fixture(scope='function', autouse=True)
def session() -> Session:
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # in-memory database (:memory:)

    db.create_all()
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
    db.drop_all()


@pytest.mark.freeze_time('2020-06-10 12:00:00')
@pytest.mark.parametrize('dt, should_be_deleted', [
    (datetime(2020, 5, 9), True),
    (datetime(2020, 5, 10), True),
    (datetime(2020, 5, 11, 11, 59, 59), True),
    (datetime(2020, 5, 11, 12, 0, 0), False),
    (datetime(2020, 6, 9), False),
    (datetime(2020, 6, 10), False),
    (datetime(2020, 6, 11), False),
    (None, False),
])
def test_delete_outdated_meetings(session: Session, dt: Optional[datetime], should_be_deleted: bool):
    owner = User(uuid=example_uuid1)
    user = User(uuid=example_uuid2)
    meeting = Meeting(uuid=example_uuid3, owner=owner, datetime=dt)
    membership1 = Membership(meeting=meeting, user=owner, nickname='Alice')
    membership2 = Membership(meeting=meeting, user=user, nickname='Bob')
    db.session.add(membership1)
    db.session.add(membership2)
    db.session.commit()

    delete_outdated_meetings(session)

    assert (Meeting.query.get(example_uuid3) is None) is should_be_deleted
    assert (Membership.query.get((example_uuid3, example_uuid1)) is None) is should_be_deleted
    assert (Membership.query.get((example_uuid3, example_uuid2)) is None) is should_be_deleted
