from src.meetings import db
from src.meetings.scripts import delete_outdated_meetings

if __name__ == '__main__':
    delete_outdated_meetings(db.session)
