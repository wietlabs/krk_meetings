import time
import random
import requests
from krk_meetings.config import URL


if __name__ == "__main__":
    response = requests.get(URL.STOPS.value, timeout=1.0)
    result = response.json()
    stops = [s['name'] for s in result['stops']]
    len_stops = len(stops)
    query_ids = []
    random.seed(0)
    start_time = time.time()
    for _ in range(1000):
        # query_json = {"start_datetime": "2020-11-18 12:00:00", "start_stop_name": stops[random.randint(0, len_stops-1)],
        #               "end_stop_name": stops[random.randint(0, len_stops-1)]}
        # query_json = {"start_stop_names": [stops[random.randint(0, len_stops-1)] for _ in range(5)], "metric": "square"}
        query_json = {"start_stop_name": stops[random.randint(0, len_stops-1)],
                      "end_stop_name": stops[random.randint(0, len_stops-1)],
                      "stops_to_visit": [stops[random.randint(0, len_stops-1)] for _ in range(5)]}
        response = requests.post(URL.SEQUENCE.value, json=query_json, timeout=1.0)
        query_ids.append(response.json()["query_id"])
    print(query_ids)
    for query_id in query_ids:
        for _ in range(100):
            response = requests.get(URL.RESULTS.value.format(query_id), timeout=1.0)
            result = response.json()
            if result["is_done"]:
                print(result)
                break
            time.sleep(0.1)
    print(time.time() - start_time)
