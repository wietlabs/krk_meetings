import json
import time

import requests

from src.config import URL
from src.examples.sample_queries import ConnectionQuerySamples

if __name__ == "__main__":
    query_json = ConnectionQuerySamples.nightly_maki_biezanow_before_midnight.value

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
    print(time.time() - execution_start)
