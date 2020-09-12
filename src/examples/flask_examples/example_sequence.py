import json
import requests

from src.config import URL
from src.data_classes.SequenceResults import SequenceResults

if __name__ == "__main__":
    query_json = {
        "start_stop_name": "Wrocławska",
        "end_stop_name": "AGH / UR",
        "stops_to_visit": ["Biprostal", "Kawiory", "Rondo Mogilskie", "Czarnowiejska"]
    }

    response = requests.post(URL.SEQUENCE.value, json=json.dumps(query_json))
    sequence = json.dumps(response.json())
    sequence = SequenceResults.from_json(sequence)
    print(sequence.best_sequence)
