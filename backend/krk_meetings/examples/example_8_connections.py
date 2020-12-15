import time
import requests
from krk_meetings.config import URL
import random


def loop_connection_query():
    response = requests.get(URL.STOPS.value, timeout=1.0)
    result = response.json()
    stops = [s['name'] for s in result['stops']]
    len_stops = len(stops)
    counter = 0
    start_time = time.time()
    query_ids = []
    random.seed(1)
    for _ in range(8):
        counter += 1
        stop_1 = stops[random.randint(0, len_stops-1)]
        stop_2 = stops[random.randint(0, len_stops-1)]
        query_json = {"start_datetime": "2020-11-18 12:00:00", "start_stop_name": stop_1,
                      "end_stop_name": stop_2}
        response = requests.post(URL.CONNECTION.value, json=query_json, timeout=1.0)
        query_id = response.json()["query_id"]
        query_ids.append(query_id)
    for query_id in query_ids:
        for _ in range(100):
            response = requests.get(URL.RESULTS.value.format(query_id), timeout=1.0)
            result = response.json()
            if response.status_code != 202:
                break
            elif result["is_done"]:
                break
            time.sleep(0.2)
        print(result)
    print(f"Execution time: {time.time() - start_time}")


if __name__ == "__main__":
    loop_connection_query()
