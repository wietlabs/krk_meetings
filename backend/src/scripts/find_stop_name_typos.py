from typing import List, Set

import requests

from src.data_provider.Downloader import Downloader
from src.data_provider.gtfs_static.Merger import Merger
from src.data_provider.gtfs_static.Parser import Parser


def get_official_stop_names() -> List[str]:
    with requests.Session() as s:
        s.get('http://rozklady.mpk.krakow.pl/')
        response = s.get('http://rozklady.mpk.krakow.pl/?lang=PL&akcja=przystanek')

    text = response.text

    prefix = "var przystanki_lista = [  '"
    suffix = "',  ];"
    text = text[text.find(prefix) + len(prefix): text.rfind(suffix)]

    separator = "',  '"
    official_stop_names = text.split(separator)
    return official_stop_names


def get_feed_stop_names() -> List[str]:
    downloader = Downloader()
    gtfs_zip_T, gtfs_zip_A = downloader.download_gtfs_static_data()

    parser = Parser()
    parsed_data_A = parser.parse(gtfs_zip_A)
    parsed_data_T = parser.parse(gtfs_zip_T)

    merger = Merger()
    merged_data, _ = merger.merge(parsed_data_A, parsed_data_T)

    stops_df = merged_data.stops_df
    stop_names_without_nz = stops_df['stop_name'].str.replace(r'\ \(nż\)', '')
    feed_stop_names = list(stop_names_without_nz)
    return feed_stop_names


if __name__ == '__main__':
    official_stop_names = get_official_stop_names()
    feed_stop_names = get_feed_stop_names()
    different_stop_names = sorted(set(official_stop_names) ^ set(feed_stop_names))
    print('\n'.join(different_stop_names))
