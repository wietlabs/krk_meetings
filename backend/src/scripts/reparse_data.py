from src.data_provider.DataProvider import DataProvider

if __name__ == "__main__":
    data_provider = DataProvider()
    data_provider.reparse_data()
    data_provider.stop()
