import requests
from src.config import URL

if __name__ == "__main__":
    response = requests.get(URL.STOPS.value, timeout=1.0)
    result = response.json()
    print(result)
