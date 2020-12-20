from datetime import timedelta, datetime

from sqlalchemy.orm import Session

from models import Meeting


def delete_outdated_meetings(session: Session, expiration_interval: timedelta = timedelta(days=30)) -> None:
    threshold = datetime.now() - expiration_interval
    Meeting.query.filter(Meeting.datetime < threshold).delete()
    session.commit()
