import json
import requests

from src.config import URL

if __name__ == "__main__":
    query_json = {
        "start_datetime": "2020-05-24 20:00:00",
        "start_stop_name": 'Jubilat',
        "end_stop_name": 'Kostrze Szkoła'
    }

    response = requests.post(URL.CONNECTION.value, json=json.dumps(query_json))
    connections = response.json()
    print({'connections': [connections['connections'][1]]})
