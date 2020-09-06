import json
import requests

from src.config import URL
from src.data_classes.MeetingResults import MeetingResults

if __name__ == "__main__":
    query_json = {
        "start_stop_names": ["Azory", "Kawiory", "Rondo Mogilskie"],
        "metric": "square"
    }

    response = requests.post(URL.MEETING.value, json=json.dumps(query_json))
    meeting = json.dumps(response.json())
    meeting = MeetingResults.from_json(meeting)
    print(meeting.meeting_points)
