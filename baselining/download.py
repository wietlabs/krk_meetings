import sys
from time import time, sleep
from itertools import count
from requests import get
from urllib.request import urlretrieve
from threading import Thread


def tick(seconds, n=None, timefunc=time):
    start = timefunc()
    yield start
    gen = count(1) if n is None else range(1, n)
    for i in gen:
        while True:
            now = timefunc()
            if now-start >= i*seconds:
                yield now
                break
            sleep((start+i*seconds-now)*0.5)  # adaptive waiting


def download_json(url, params, path, retries=5):
    for _ in range(retries):
        try:
            response = get(url, params)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return
        except:
            pass


def download_protobuf(url, path, retries=5):
    for _ in range(retries):
        try:
            urlretrieve(url, path)
            return
        except:
            pass


if __name__ == '__main__':
    seconds = int(sys.argv[1]) if len(sys.argv) >= 2 else 5
    try:
        for now in tick(seconds):
            print(now)
            timestamp = int(now)

            jobs = [
                (
                    download_json,
                    'http://www.ttss.krakow.pl/internetservice/geoserviceDispatcher/services/vehicleinfo/vehicles',
                    {'positionType': 'CORRECTED'},
                    f'download/vehicles_T_{timestamp}.json',
                ),
                (
                    download_json,
                    'http://91.223.13.70/internetservice/geoserviceDispatcher/services/vehicleinfo/vehicles',
                    {},
                    f'download/vehicles_A_{timestamp}.json',
                ),
                (
                    download_protobuf,
                    'ftp://ztp.krakow.pl/pliki-gtfs/VehiclePositions_A.pb',
                    f'download/VehiclePositions_A_{timestamp}.pb',
                ),
                (
                    download_protobuf,
                    'ftp://ztp.krakow.pl/pliki-gtfs/VehiclePositions_T.pb',
                    f'download/VehiclePositions_T_{timestamp}.pb',
                ),
            ]

            for func, *args in jobs:
                Thread(target=func, args=args, daemon=True).start()

    except KeyboardInterrupt:
        pass
