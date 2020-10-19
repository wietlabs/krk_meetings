import json
import time

import requests

from src.config import URL

if __name__ == "__main__":
    query_json = {
        "start_datetime": "2020-05-24 20:00:00",
        "start_stop_name": 'Jubilat',
        "end_stop_name": 'Kostrze Szkoła'
    }

    response = requests.post(URL.CONNECTION.value, json=json.dumps(query_json), timeout=1.0)
    query_id = response.json()
    response = requests.get(URL.GET.value.format(query_id), json=query_json, timeout=1.0)
    result = response.json()
    print(result)
    time.sleep(3)
    response = requests.get(URL.GET.value.format(query_id), json=json.dumps(query_json), timeout=1.0)
    result = response.json()
    print(result)
