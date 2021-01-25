import PIL
import imageio
from math import cos
from copy import copy, deepcopy
from math import radians
from queue import PriorityQueue

from krk_meetings.config import WALKING_ROUTE_ID
from krk_meetings.solver import solver_utils
from krk_meetings.solver.ConnectionSolver import ConnectionSolver
from krk_meetings.solver.ConnectionSolverConfiguration import ConnectionSolverConfiguration

import matplotlib.pyplot as plt
from IPython import display

import io


class ConnectionVisualizer(ConnectionSolver):
    def get_visualization_paths(self, start_stop_name: str, end_stop_name: str):
        start_node_id = solver_utils.get_stop_id_by_name(start_stop_name, self.stops_df_by_name)
        if start_node_id is None:
            print(f"ConnectionSolver({id(self)}): Start stop not found({start_stop_name})")
            return None
        end_node_id = solver_utils.get_stop_id_by_name(end_stop_name, self.stops_df_by_name)
        if end_node_id is None:
            print(f"ConnectionSolver({id(self)}): End stop not found({end_stop_name})")
            return None


        def get_max_priority(prior):
            return prior * self.configuration.max_priority_multiplier + self.configuration.max_priority_cap

        def get_max_queue_priority(prior):
            return (prior * self.configuration.max_priority_multiplier
                    + self.configuration.max_priority_cap) * self.configuration.path_calculation_boost

        def resolve_neighbor(node_id, neighbor_id, weight, path, routes, graph):
            n_weight = weight + graph.edges[node_id, neighbor_id]['weight']
            n_queue_priority = n_weight + self.distances[neighbor_id][
                end_node_id] * self.configuration.path_calculation_boost
            n_priority = n_weight + self.distances[neighbor_id][
                end_node_id] * self.configuration.max_priority_multiplier
            n_path = copy(path)
            n_path.append(neighbor_id)
            n_routes = copy(routes)
            route = graph.edges[node_id, neighbor_id]['route_ids']
            if self.is_redundant(n_routes, route):
                return

            if n_queue_priority <= max_queue_priority and n_priority <= max_priority and len(
                n_path) <= self.configuration.max_path_len:
                n_routes.append(route)
                if (n_routes, neighbor_id) not in routes_dict:
                    routes_dict.append((n_routes, neighbor_id))
                    queue.put((n_queue_priority, n_weight, neighbor_id, n_path, n_routes))

        queue = PriorityQueue()
        paths = []
        visualization_paths = []
        routes_dict = []
        routes_to_node = {}
        priority_distance = float("inf")
        max_priority = float("inf")
        max_queue_priority = float("inf")

        last_hubs = []
        if end_node_id not in self.kernelized_graph.nodes:
            for neighbor_id in self.graph.predecessors(end_node_id):
                if neighbor_id in self.kernelized_graph.nodes:
                    last_hubs.append(neighbor_id)

        if start_node_id in self.kernelized_graph.nodes:
            queue.put((0, 0, start_node_id, [start_node_id], []))
        else:
            for neighbor_id in self.graph.neighbors(start_node_id):
                if neighbor_id in self.kernelized_graph.nodes:
                    resolve_neighbor(start_node_id, neighbor_id, 0, [start_node_id], [], self.graph)

        while not queue.empty() and len(paths) <= self.configuration.max_number_of_paths:
            priority, weight, node_id, path, routes = queue.get()

            visualization_path = [solver_utils.connection_stop_data(stop_id, self.stops_df) for stop_id in path]
            visualization_path = [(stop['longitude'], stop['latitude']) for stop in visualization_path]
            visualization_paths.append(visualization_path)
            subset_route = False
            current_route_set = set()
            for route in routes:
                current_route_set.update(set(route))
            if node_id in routes_to_node:
                for route_to_node in routes_to_node[node_id]:
                    if route_to_node.issubset(current_route_set):
                        subset_route = True
                        break
                if subset_route:
                    continue
            else:
                routes_to_node[node_id] = []
            routes_to_node[node_id].append(current_route_set)
            if node_id == end_node_id:
                if priority < max_priority:
                    paths.append(path)
                    if priority < priority_distance:
                        max_priority = get_max_priority(priority_distance)
                        max_queue_priority = get_max_queue_priority(priority_distance)
                        priority_distance = priority
                continue
            if node_id in last_hubs:
                resolve_neighbor(node_id, end_node_id, weight, path, routes, self.graph)
            for neighbor_id in self.kernelized_graph.neighbors(node_id):
                resolve_neighbor(node_id, neighbor_id, weight, path, routes, self.kernelized_graph)
        if [start_node_id, end_node_id] not in paths:
            paths.append([start_node_id, end_node_id])

        stop_ys = self.stops_df["stop_lat"].tolist()
        stop_xs = self.stops_df["stop_lon"].tolist()

        all_stops = [(stop_xs[it], stop_ys[it]) for it in range(len(stop_xs))]

        start_stop = solver_utils.connection_stop_data(start_node_id, self.stops_df)

        start_stop = (start_stop['longitude'], start_stop['latitude'])

        end_stop = solver_utils.connection_stop_data(end_node_id, self.stops_df)
        end_stop = (end_stop['longitude'], end_stop['latitude'])

        return visualization_paths, all_stops, start_stop, end_stop

    def create_pngs(self, paths, all_stops, start_stop, end_stop, markersize, all_stops_markersize, linewidth,
                    current_linewidth, dpi):
        self.plot_setup(paths, all_stops, all_stops_markersize)
        file_num = 1000
        paths_found = []
        paths_processed = []
        for path in paths:
            self.plot_setup(paths, all_stops, all_stops_markersize)
            for path_processed in paths_processed:
                self.draw_path(path_processed, colors["processed_paths"], markersize, linewidth)
            for path_found in paths_found:
                self.draw_path(path_found, colors["found_paths"], markersize, linewidth)
            if path[-1] == end_stop:
                paths_found.append(path)
            else:
                paths_processed.append(path)
            self.draw_path(path, colors["current_path"], markersize, current_linewidth)
            self.draw_path(path[-2:], colors["current_edge"], markersize, current_linewidth)
            self.draw_point(start_stop, colors["start"], markersize)
            self.draw_point(end_stop, colors["end"], markersize)
            # plt.savefig("visualization_images/" + str(file_num) + "_plot", format='svg', dpi=1200)
            #plt.savefig("visualization_images/" + str(file_num) + "_plot", dpi=dpi)
            file_num += 1

            buf = io.BytesIO()
            plt.savefig(buf, dpi=dpi)
            buf.seek(0)
            img = deepcopy(PIL.Image.open(buf))
            buf.close()
            yield img

    def draw_path(self, path, color, markersize, linewidth):
        for index in range(len(path) - 1):
            self.draw_line(path[index], path[index+1], color, markersize, linewidth)

    def plot_setup(self, paths, points, markersize):
        plt.cla()
        plt.axis('off')
        plt.tight_layout()
        plt.plot(*zip(*points), marker='o', ls='', color=colors["all"], markersize=markersize)
        display.clear_output(wait=True)
        display.display(plt.gcf())

        xmin = 1000
        xmax = 0
        ymin = 1000
        ymax = 0
        for point in points:
            # for point in path:
                y, x = point
                xmin = x if x < xmin else xmin
                xmax = x if x > xmax else xmax
                ymin = y if y < ymin else ymin
                ymax = y if y > ymax else ymax
        xrange = xmax - xmin
        yrange = ymax - ymin
        # xmin = xmin - xrange/10
        # xmax = xmax + xrange/10
        # ymin = ymin - yrange/10
        # ymax = ymax + yrange/10

        # plt.rcParams["figure.figsize"] = 50, 50
        # plt.xlim(xmin, xmax)
        # plt.ylim(ymin, ymax)
        plt.axes().set_aspect(1/cos(radians(50)))


    def draw_line(self, p_1, p_2, color, markersize, linewidth):
        plt.plot([p_1[0], p_2[0]], [p_1[1], p_2[1]], color=color, marker='o',markersize=markersize,
                 linewidth=linewidth)

    def draw_point(self, p, color, markersize):
        plt.plot([p[0]], [p[1]], marker='o', color=color, markersize=markersize)
        display.clear_output(wait=True)
        display.display(plt.gcf())

    def record(self):
        pass


configuration = ConnectionSolverConfiguration(
    max_searching_time=8*3600,  # sec
    partition_time=1800,  # sec
    max_travel_time=4*3600,  # sec
    number_of_connections_returned=25,
    max_priority_multiplier=1.2,
    max_priority_cap=2400,  # sec - cant be 0 due to ban of walking from stop to stop twice in a row
    path_calculation_boost=1.5,
    max_number_of_paths=20,
    max_path_len=6,
    max_path_calculation_time=3,  # sec
    walking_route_id=WALKING_ROUTE_ID,
    walking_index=(WALKING_ROUTE_ID, WALKING_ROUTE_ID, WALKING_ROUTE_ID)
)

colors = {
    "all": "black",
    "start": "#41c0ff",
    "end": "#35d985",
    "found_paths": "#35d985",
    "current_edge": "#ff3d67",
    "current_path": "#41c0ff",
    "processed_paths": "gray"
}


if __name__ == "__main__":
    visualizer = ConnectionVisualizer(configuration)
    visualizer.data_manager.update_data()
    visualizer.update_data()
    #start_stop_name, end_stop_name = "Czerwone Maki P+R", "Jerzmanowskiego"
    #start_stop_name, end_stop_name = "Krzeszowice Dworzec Autobusowy", "Chobot Leśniczówka" # this is good
    start_stop_name, end_stop_name = "Kamień Szkoła", "Chobot Leśniczówka" # this is good
    #start_stop_name, end_stop_name = "Bieżanowska", "Chobot Leśniczówka"
    visualization_paths, all_stops, start_stop, end_stop = visualizer.get_visualization_paths(start_stop_name, end_stop_name)
    # visualization_paths, all_stops, start_stop, end_stop = visualizer.get_visualization_paths("Biprostal", "Kurdwanów P+R")
    imgs = visualizer.create_pngs(visualization_paths, all_stops, start_stop, end_stop,
                           markersize=3,
                           all_stops_markersize=1,
                           linewidth=1,
                           current_linewidth=2,
                           dpi=300)
    #visualizer.record()

    imageio.mimwrite('animation.gif', imgs)

