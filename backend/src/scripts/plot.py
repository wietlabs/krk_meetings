from pathlib import Path
from typing import Dict

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config import FloydDataPaths
from src.data_provider.data_provider_utils import get_walking_distance
from src.solver.solver_utils import get_stop_id_by_name

plt.style.use('ggplot')
plt.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['#1f77b4'])
format = 'pdf'


def calculate_distance_km(start_stop_name: str, end_stop_name: str, stops_df_by_name: pd.DataFrame) -> float:
    start_stop_lat = stops_df_by_name.at[start_stop_name, 'stop_lat']
    start_stop_lon = stops_df_by_name.at[start_stop_name, 'stop_lon']
    end_stop_lat = stops_df_by_name.at[end_stop_name, 'stop_lat']
    end_stop_lon = stops_df_by_name.at[end_stop_name, 'stop_lon']
    distance_m = get_walking_distance(start_stop_lon, start_stop_lat, end_stop_lon, end_stop_lat)
    distance_km = distance_m / 1e3
    return distance_km


def get_distance_from_dict_km(start_stop_name: str, end_stop_name: str,
                              stops_df_by_name: pd.DataFrame, distances_dict: Dict[int, Dict[int, float]]) -> float:
    start_stop_id = get_stop_id_by_name(start_stop_name, stops_df_by_name)
    end_stop_id = get_stop_id_by_name(end_stop_name, stops_df_by_name)
    distance_km = distances_dict[start_stop_id][end_stop_id]
    return distance_km


def plot_connection_solver_execution_time_pdf(execution_time: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.distplot(execution_time, bins=50, ax=ax)
    ax.set(xlabel='Czas wyszukiwania [s]',
           ylabel='Gęstość prawdopodobieństwa',
           xticks=range(10),
           xlim=(-0.5, 6.5))
    # ax.grid()
    return fig


def plot_connection_solver_execution_time_cdf(execution_time: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.distplot(execution_time, bins=1000, ax=ax, hist_kws={'cumulative': True}, kde_kws={'cumulative': True})
    ax.set(xlabel='Czas wyszukiwania [s]',
           ylabel='Gęstość prawdopodobieństwa',
           xticks=range(10),
           xlim=(-0.5, 6.5))
    # ax.grid()
    return fig


def plot_connection_solver_execution_time_vs_distance(performance_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(data=performance_df, x='distance_km', y='execution_time', ax=ax)
    ax.set(xlabel='Odległość pomiędzy przystankami [km]',
           ylabel='Czas wyszukiwania [s]')
    # ax.grid()
    return fig


def plot_meeting_solver_execution_time_by_participants_count(performance_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(data=performance_df, x='participants', y='time', ax=ax)
    ax.set(xlabel='Liczba uczestników',
           ylabel='Czas wyszukiwania [s]')
    # ax.grid()
    return fig


def plot_sequence_solver_execution_time_by_stops_to_visit(performance_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(data=performance_df, x='stops_to_visit', y='time', ax=ax)
    ax.set(xlabel='Liczba przystanków',
           ylabel='Czas wyszukiwania [s]',
           yscale='log')
    # ax.grid()
    return fig


def generate_connection_solver_plots():
    pickle_path = Path(__file__).parent / 'data' / 'ConnectionSolverPerformance_3sec.pickle'
    performance_df = pd.read_pickle(pickle_path)
    stops_df_by_name = pd.read_pickle(FloydDataPaths.stops_df_by_name.value)

    execution_time = performance_df['execution_time']  # TODO: execution time
    get_distance_for_row = lambda row: calculate_distance_km(row['start_stop_name'], row['end_stop_name'],
                                                             stops_df_by_name)
    performance_df['distance_km'] = performance_df.apply(get_distance_for_row, axis=1)

    plot_connection_solver_execution_time_pdf(execution_time) \
        .savefig(f'output/connection_solver_execution_time_pdf.{format}')
    plot_connection_solver_execution_time_cdf(execution_time) \
        .savefig(f'output/connection_solver_execution_time_cdf.{format}')
    plot_connection_solver_execution_time_vs_distance(performance_df) \
        .savefig(f'output/connection_solver_execution_time_vs_distance.{format}')


def generate_meeting_solver_plots():
    pickle_path = Path(__file__).parent / 'data' / 'MeetingSolverPerformance.pickle'
    performance_df = pd.read_pickle(pickle_path)

    plot_meeting_solver_execution_time_by_participants_count(performance_df) \
        .savefig(f'output/meeting_solver_execution_time_by_participants_count.{format}')


def generate_sequence_solver_plots():
    pickle_path = Path(__file__).parent / 'data' / 'SequenceSolverPerformance.pickle'
    performance_df = pd.read_pickle(pickle_path)

    plot_sequence_solver_execution_time_by_stops_to_visit(performance_df) \
        .savefig(f'output/sequence_solver_execution_time_by_stops_to_visit.{format}')


if __name__ == '__main__':
    generate_connection_solver_plots()
    generate_meeting_solver_plots()
    generate_sequence_solver_plots()
