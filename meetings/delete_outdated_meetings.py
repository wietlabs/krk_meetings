from app import db
from scripts import delete_outdated_meetings

if __name__ == '__main__':
    delete_outdated_meetings(db.session)
