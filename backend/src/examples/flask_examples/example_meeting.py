import requests
import time
from src.config import URL
from src.examples.flask_examples.sample_queries import MeetingQuerySamples

if __name__ == "__main__":
    query_json = MeetingQuerySamples.square_3_stops.value

    execution_start = time.time()
    response = requests.post(URL.MEETING.value, json=query_json, timeout=1.0)
    query_id = response.json()["query_id"]
    result = None

    for _ in range(30):
        response = requests.get(URL.RESULTS.value.format(query_id), timeout=1.0)
        result = response.json()
        if response.status_code != 202:
            break
        elif result["is_done"]:
            break
        time.sleep(0.2)

    print(result)
    print(time.time() - execution_start)
