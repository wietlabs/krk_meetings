import json
import time

import requests

from src.config import URL

if __name__ == "__main__":
    query_json = {
        "start_datetime": "2020-05-24 12:00:00",
        "start_stop_name": 'Krzeszowice Dworzec Autobusowy',
        "end_stop_name": 'Wolica Most'
    }

    execution_start = time.time()
    response = requests.post(URL.CONNECTION.value, json=query_json, timeout=1.0)
    query_id = response.json()
    result = None

    for _ in range(30):
        try:
            response = requests.get(URL.GET.value.format(query_id), json=query_json, timeout=1.0)
        except requests.exceptions.ChunkedEncodingError:
            time.sleep(1)
            continue
        result = response.json()
        if result["is_done"]:
            break
        time.sleep(1)
    if result['connections']:
        print(result['connections'][0])
    print(time.time() - execution_start)
