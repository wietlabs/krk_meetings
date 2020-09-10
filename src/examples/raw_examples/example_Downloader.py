from src.data_provider.Downloader import Downloader

if __name__ == '__main__':
    downloader = Downloader()
    last_update = downloader.get_last_update_time()
    merged_data = downloader.download_merged_data()
