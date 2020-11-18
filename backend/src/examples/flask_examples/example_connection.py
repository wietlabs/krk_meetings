import json
import time

import requests

from src.config import URL
from src.examples.flask_examples.sample_queries import ConnectionQuerySamples

if __name__ == "__main__":
    query_json = ConnectionQuerySamples.jubilat_baluckiego.value
    query_json = {'start_datetime': '2020-05-24 12:00:00', 'start_stop_name': 'Skawina Korabnicka Szkoła (nż)', 'end_stop_name': 'Tor Kajakowy'}

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

    print(json.dumps(result, ensure_ascii=False))
    print(time.time() - execution_start)
