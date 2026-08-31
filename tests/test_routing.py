import networkx as nx
import numpy as np

from ayus.config import PlannerConfig
from ayus.image_processing import GridSpec
from ayus.metrics import path_length_pixels
from ayus.routing import build_graph, generate_backup_routes, path_overlap_ratio


def _grid(height=20, width=30, rows=4, cols=5):
    return GridSpec(
        height,
        width,
        rows,
        cols,
        np.linspace(0, height, rows + 1, dtype=np.int32),
        np.linspace(0, width, cols + 1, dtype=np.int32),
    )


def test_grid_metric_uses_real_pixel_geometry():
    grid = _grid()
    assert path_length_pixels([(0, 0), (0, 1)], grid) == 6.0
    assert path_length_pixels([(0, 0), (1, 0)], grid) == 5.0


def test_graph_does_not_allow_diagonal_corner_cutting():
    grid = _grid()
    blocked = np.zeros((4, 5), dtype=bool)
    blocked[0, 1] = True
    blocked[1, 0] = True
    graph = build_graph(
        blocked, np.zeros((4, 5), dtype=np.float32), np.ones((4, 5), dtype=np.float32), grid, PlannerConfig()
    )
    assert not graph.has_edge((0, 0), (1, 1))


def test_backup_routes_are_not_duplicate_paths():
    graph = nx.grid_2d_graph(4, 4)
    for u, v in graph.edges:
        graph.edges[u, v]["weight"] = 1.0
    config = PlannerConfig(alternative_route_count=3)
    primary = nx.shortest_path(graph, (0, 0), (3, 3))
    routes = generate_backup_routes(graph, (0, 0), (3, 3), primary, config)
    assert len({tuple(route) for route in routes}) == len(routes)
    assert all(path_overlap_ratio(route, primary) <= 1.0 for route in routes)
