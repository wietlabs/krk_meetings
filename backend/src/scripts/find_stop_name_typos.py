from typing import List

import pandas as pd
import requests

from src.data_classes.ParsedData import ParsedData
from src.data_provider.Downloader import Downloader
from src.data_provider.gtfs_static.Merger import Merger
from src.data_provider.gtfs_static.Parser import Parser


def download_merged_data() -> ParsedData:
    downloader = Downloader()
    gtfs_zip_T, gtfs_zip_A = downloader.download_gtfs_static_data()

    parser = Parser()
    parsed_data_A = parser.parse(gtfs_zip_A)
    parsed_data_T = parser.parse(gtfs_zip_T)

    merger = Merger()
    merged_data, _ = merger.merge(parsed_data_A, parsed_data_T)
    return merged_data


def get_names_from_df(df: pd.DataFrame, column_name: str) -> List[str]:
    names_without_nz = df[column_name].str.replace(r'\ \(nż\)', '')
    return list(names_without_nz)


def get_feed_stop_names(parsed_data: ParsedData) -> List[str]:
    return get_names_from_df(parsed_data.stops_df, 'stop_name')


def get_feed_peron_names(parsed_data: ParsedData) -> List[str]:
    return get_names_from_df(parsed_data.perons_df, 'peron_name')


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


if __name__ == '__main__':
    merged_data = download_merged_data()
    feed_stop_names = get_feed_stop_names(merged_data)
    feed_peron_names = get_feed_peron_names(merged_data)
    official_stop_names = get_official_stop_names()
    different_stop_names = sorted(set(official_stop_names) ^ set(feed_stop_names))
    print('\n'.join(different_stop_names))
