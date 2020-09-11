from src.data_provider.FloydDataProvider import FloydDataProvider

if __name__ == "__main__":
    data_provider = FloydDataProvider()
    data = data_provider.load_floyd_data()
    print(data.stop_times_0_dict)
