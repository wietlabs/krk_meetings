import time
import requests
from src.config import URL
import random

from src.examples.flask_examples.sample_queries import FAILING_CONNECTIONS


def loop_connection_query():
    response = requests.get(URL.STOPS.value, timeout=1.0)
    result = response.json()
    stops = [s['name'] for s in result['stops']]
    len_stops = len(stops)
    counter = 0
    fail_counter = 0
    start_time = time.time()
    while True:
        counter += 1
        stop_1 = stops[random.randint(0, len_stops-1)]
        stop_2 = stops[random.randint(0, len_stops-1)]
        try:
            query_json = {"start_datetime": "2020-11-18 12:00:00", "start_stop_name": stop_1,
                          "end_stop_name": stop_2}
            # query_json = FAILING_CONNECTIONS[counter - 1]
            response = requests.post(URL.CONNECTION.value, json=query_json, timeout=1.0)
            query_id = response.json()["query_id"]
            for _ in range(100):
                response = requests.get(URL.RESULTS.value.format(query_id), timeout=1.0)
                result = response.json()
                if response.status_code != 202:
                    break
                elif result["is_done"]:
                    break
                time.sleep(0.2)
            if not result["is_done"]:
                print("is_done false")
                print(stop_1, stop_2)
                print(f"Processed {counter} queries in {time.time() - start_time} seconds.")
                print(f"One connection for {(time.time() - start_time) / counter}")
                return
            if not result["connections"]:
                fail_counter += 1
                print(f"{query_json},")
                print(f"Fail rate: {fail_counter/counter}")

        except Exception as e:
            print(stop_1, stop_2)
            print(f"Processed {counter} queries in {time.time() - start_time} seconds.")
            print(f"One connection for {(time.time() - start_time) / counter}")
            print(type(e))
            return


if __name__ == "__main__":
    loop_connection_query()
