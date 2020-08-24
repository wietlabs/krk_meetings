from pathlib import Path

from src.data_provider.Merger import Merger
from src.data_provider.Parser import Parser
from src.data_provider.Selector import Selector

if __name__ == '__main__':
    parent_dir = Path(__file__).parent

    parser = Parser()
    parsed_data_A = parser.parse(parent_dir / 'GTFS_KRK_A')
    parsed_data_T = parser.parse(parent_dir / 'GTFS_KRK_T')

    selector = Selector()
    selected_data_A = selector.select(parsed_data_A, service_id=1)
    selected_data_T = selector.select(parsed_data_T, service_id=1)

    merger = Merger()
    merged_data = merger.merge(selected_data_A, selected_data_T)
