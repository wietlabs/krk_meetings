from development.DataProviders.DataProvider import DataProvider

if __name__ == '__main__':
    DataProvider.parse_and_extract_floyd_data()
    DataProvider.parse_and_extract_bfs_data()
