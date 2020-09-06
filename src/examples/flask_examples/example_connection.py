import json
import requests

from src.config import URL
from src.data_classes.ConnectionResults import ConnectionResults

if __name__ == "__main__":
    query_json = {
        "start_date": "24/5/2020",
        "start_time": "20:00:00",
        "start_stop_name": 'Teatr Słowackiego',
        "end_stop_name": 'Kurdwanów P+R'
    }

    response = requests.post(URL.CONNECTION.value, json=json.dumps(query_json))
    connections = json.dumps(response.json())
    connections = ConnectionResults.from_json(connections)
    for connection in connections:
        print(connection)
        print('-' * 30)
