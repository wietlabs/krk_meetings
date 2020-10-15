from src.data_provider.Extractor import Extractor
from src.data_provider.FloydDataProvider import FloydDataProvider

if __name__ == "__main__":
    data_provider = FloydDataProvider()
    extractor = Extractor()
    data = data_provider.load_floyd_data()
    print(data.distances_dict)
