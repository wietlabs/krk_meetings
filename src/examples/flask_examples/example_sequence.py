import json
import requests
import time
from src.config import URL

if __name__ == "__main__":
    query_json = {
        "start_stop_name": "Wrocławska",
        "end_stop_name": "AGH / UR",
        "stops_to_visit": ["Biprostal", "Kawiory", "Rondo Mogilskie", "Czarnowiejska"]
    }

    response = requests.post(URL.SEQUENCE.value, json=query_json, timeout=1.0)
    query_id = response.json()
    response = requests.get(URL.RESULTS.value.format(query_id), json=query_json, timeout=1.0)
    result = response.json()
    print(result)
    time.sleep(3)
    response = requests.get(URL.RESULTS.value.format(query_id), json=query_json, timeout=1.0)
    result = response.json()
    print(result)
