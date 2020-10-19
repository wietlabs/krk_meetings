import json
import requests
import time
from src.config import URL

if __name__ == "__main__":
    query_json = {
        "start_stop_names": ["Azory", "Kawiory", "Rondo Mogilskie"],
        "metric": "square"
    }

    response = requests.post(URL.MEETING.value, json=query_json, timeout=1.0)
    query_id = response.json()
    response = requests.get(URL.GET.value.format(query_id), json=query_json, timeout=1.0)
    result = response.json()
    print(result)
    time.sleep(3)
    response = requests.get(URL.GET.value.format(query_id), json=query_json, timeout=1.0)
    result = response.json()
    print(result)
