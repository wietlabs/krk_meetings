import json
import time

import requests
from datetime import datetime
from krk_meetings.config import URL, DATETIME_FORMAT
from krk_meetings.examples.sample_queries import ConnectionQuerySamples

if __name__ == "__main__":
    query_json = ConnectionQuerySamples.walking_only.value
    query_json['start_datetime'] = datetime.now().strftime(DATETIME_FORMAT)
    execution_start = time.time()
    response = requests.post(URL.CONNECTION.value, json=query_json, timeout=1.0)
    query_id = response.json()["query_id"]
    result = None

    for _ in range(100):
        response = requests.get(URL.RESULTS.value.format(query_id), timeout=1.0)
        result = response.json()
        if response.status_code != 202:
            break
        elif result["is_done"]:
            break
        time.sleep(0.2)

    print(len(result["connections"]))
    print(json.dumps(result, ensure_ascii=False))
    print([[action["delay"] if "delay" in action else 0 for action in connection["actions"]] for connection in result["connections"]])
    print(time.time() - execution_start)
