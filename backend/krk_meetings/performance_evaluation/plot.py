from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import PercentFormatter

color = '#1f77b4'
format = 'png'

plt.style.use('ggplot')
plt.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=[color])


def plot_connection_solver_execution_time_hist(execution_time: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(execution_time, binwidth=0.2, kde=True, ax=ax)
    ax.set(xlabel='Czas wyszukiwania połączeń [s]',
           ylabel='Procent przetworzonych zapytań')
    ax.yaxis.set_major_formatter(PercentFormatter(len(execution_time)))
    return fig


def plot_connection_solver_execution_time_ecdf(execution_time: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.ecdfplot(execution_time, ax=ax)
    sns.rugplot(execution_time, linewidth=0.2, alpha=0.5, ax=ax)
    ax.set(xlabel='Czas wyszukiwania połączeń [s]',
           ylabel='Procent przetworzonych zapytań',
           ylim=(-0.03, 1.03))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    return fig


def plot_connection_solver_path_execution_time_hist(execution_time: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(execution_time, binwidth=0.05, kde=True, ax=ax)
    ax.axvline(x=3, color='gray', linestyle='--', linewidth=0.8)
    ax.set(xlabel='Czas wyszukiwania ścieżek [s]',
           ylabel='Procent przetworzonych zapytań')
    ax.yaxis.set_major_formatter(PercentFormatter(len(execution_time)))
    return fig


def plot_connection_solver_path_execution_time_ecdf(execution_time: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.ecdfplot(execution_time, ax=ax)
    sns.rugplot(execution_time, linewidth=0.2, alpha=0.5, ax=ax)
    ax.axvline(x=3, color='gray', linestyle='--', linewidth=0.8)
    ax.set(xlabel='Czas wyszukiwania ścieżek [s]',
           ylabel='Procent przetworzonych zapytań',
           ylim=(-0.03, 1.03))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    return fig


def plot_connection_solver_execution_time_vs_distance(performance_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    # sns.scatterplot(data=performance_df, x='distance_km', y='execution_time', marker='o', s=10, ax=ax)
    cmap = LinearSegmentedColormap.from_list('', ['#e5e5e5', color])
    sns.histplot(data=performance_df, x='distance_km', y='execution_time',
                 binrange=((0, 50), (0, 7)), binwidth=(1, 0.2), cbar=True, cmap=cmap, ax=ax)
    ax.axhline(y=3, color='gray', linestyle='--', linewidth=0.8)
    ax.set(xlabel='Odległość pomiędzy przystankami [km]',
           ylabel='Czas wyszukiwania połączeń [s]',
           xlim=(0, 50),
           ylim=(0, 7))
    ax.grid(False)
    return fig


def plot_meeting_solver_execution_time_by_participants_count(performance_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    performance_df['execution_time_ms'] = performance_df['execution_time'] * 1e3
    sns.boxplot(data=performance_df, x='participants_count', y='execution_time_ms',
                linewidth=0.6, fliersize=3, ax=ax)
    ax.set(xlabel='Liczba uczestników',
           ylabel='Czas wyszukiwania miejsc spotkania [ms]',
           xticks=[0, *range(4, 30, 5)])
    return fig


def plot_sequence_solver_execution_time_by_stops_to_visit(performance_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    performance_df['execution_time_ms'] = performance_df['execution_time'] * 1e3
    sns.boxplot(data=performance_df, x='stops_count', y='execution_time_ms',
                linewidth=0.6, fliersize=3, ax=ax)
    ax.set(xlabel='Liczba przystanków',
           ylabel='Czas wyszukiwania sekwencji [ms]',
           yscale='log')
    return fig


def generate_connection_solver_plots():
    pickle_path = Path(__file__).parent / 'data' / 'connection_solver_performance.pickle'
    performance_df = pd.read_pickle(pickle_path)
    performance_df = performance_df[performance_df['execution_time'] < 10]

    execution_time = performance_df['execution_time']

    plot_connection_solver_execution_time_hist(execution_time) \
        .savefig(f'plots/connection_solver_execution_time_hist.{format}')
    plot_connection_solver_execution_time_ecdf(execution_time) \
        .savefig(f'plots/connection_solver_execution_time_ecdf.{format}')
    plot_connection_solver_execution_time_vs_distance(performance_df) \
        .savefig(f'plots/connection_solver_execution_time_vs_distance.{format}')


def generate_connection_solver_path_plots():
    pickle_path = Path(__file__).parent / 'data' / 'connection_solver_path_performance.pickle'
    performance_df = pd.read_pickle(pickle_path)
    performance_df = performance_df[performance_df['execution_time'] < 10]

    execution_time = performance_df['execution_time']

    plot_connection_solver_path_execution_time_hist(execution_time) \
        .savefig(f'plots/connection_solver_path_execution_time_hist.{format}')
    plot_connection_solver_path_execution_time_ecdf(execution_time) \
        .savefig(f'plots/connection_solver_path_execution_time_ecdf.{format}')



def generate_meeting_solver_plots():
    pickle_path = Path(__file__).parent / 'data' / 'meeting_solver_performance.pickle'
    performance_df = pd.read_pickle(pickle_path)

    plot_meeting_solver_execution_time_by_participants_count(performance_df) \
        .savefig(f'plots/meeting_solver_execution_time_by_participants_count.{format}')


def generate_sequence_solver_plots():
    pickle_path = Path(__file__).parent / 'data' / 'sequence_solver_performance.pickle'
    performance_df = pd.read_pickle(pickle_path)

    plot_sequence_solver_execution_time_by_stops_to_visit(performance_df) \
        .savefig(f'plots/sequence_solver_execution_time_by_stops_count.{format}')


if __name__ == '__main__':
    Path('plots').mkdir(parents=True, exist_ok=True)
    generate_connection_solver_plots()
    generate_connection_solver_path_plots()
    generate_meeting_solver_plots()
    generate_sequence_solver_plots()
