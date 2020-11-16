import time
import requests
from src.config import URL
import random


def loop_connection_query():
    response = requests.get(URL.STOPS.value, timeout=1.0)
    result = response.json()
    stops = [s['name'] for s in result['stops']]
    len_stops = len(stops)
    while True:
        stop_1 = stops[random.randint(0, len_stops)]
        stop_2 = stops[random.randint(0, len_stops)]
        try:
            query_json = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": stop_1,
                          "end_stop_name": stop_2}
            response = requests.post(URL.CONNECTION.value, json=query_json, timeout=1.0)
            query_id = response.json()["query_id"]
            for _ in range(30):
                response = requests.get(URL.RESULTS.value.format(query_id), timeout=1.0)
                result = response.json()
                if response.status_code != 202:
                    break
                elif result["is_done"]:
                    break
                time.sleep(0.2)
            if not result["is_done"]:
                print(stop_1, stop_2)
                return
        except Exception as e:
            print(stop_1, stop_2)
            print(type(e))
            return


if __name__ == "__main__":
    loop_connection_query()
