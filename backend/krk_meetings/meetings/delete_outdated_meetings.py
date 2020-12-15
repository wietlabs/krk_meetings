from krk_meetings.meetings import db
from krk_meetings.meetings.scripts import delete_outdated_meetings

if __name__ == '__main__':
    delete_outdated_meetings(db.session)
