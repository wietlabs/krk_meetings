import json
import requests

from src.config import URL

if __name__ == "__main__":
    query_json = {
        "start_date": "2020-5-24",
        "start_time": "20:00:00",
        "start_stop_name": 'Jubilat',
        "end_stop_name": 'Kostrze Szkoła'
    }

    response = requests.post(URL.CONNECTION.value, json=json.dumps(query_json))
    connections = json.dumps(response.json(), ensure_ascii=False)
    print(connections)
