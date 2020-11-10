def test_extending(self):
    graph = self.generate_test_graph()
    df_data = {'stop_id': [0], 'route_id': [1]
               }
    first_hubs_df = pd.DataFrame(df_data, columns=['stop_id', 'route_id'])
    graph = self.extend_graph(graph, first_hubs_df)
    print(graph.edges)


def generate_test_graph(self):
    def edge_generator():
        for i in range(10):
            yield i, i + 1, 1, {
                'duration': 1,
                'period': 10,
                'route_id': 1
            }

    graph = nx.MultiDiGraph()
    graph.add_edges_from(edge_generator())
    return graph


def draw_graph(self, graph, stops_df):
    pos = dict(stops_df[['stop_lon', 'stop_lat']].iterrows())

    fig, ax = plt.subplots()
    ax.set_aspect(aspect=1 / cos(radians(50)))
    nx.draw(graph, pos, ax, node_size=8, width=2)

    fig.tight_layout()

    # fig.savefig('map.svg')
    plt.show()
