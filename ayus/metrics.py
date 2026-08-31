from __future__ import annotations

import math

import networkx as nx
import numpy as np

from .image_processing import GridSpec
from .routing import Node, path_cost


def path_length_pixels(path: list[Node], grid: GridSpec) -> float:
    length = 0.0
    for index in range(len(path) - 1):
        x1, y1 = grid.center(path[index])
        x2, y2 = grid.center(path[index + 1])
        length += math.hypot(x2 - x1, y2 - y1)
    return length


def compute_route_metrics(graph: nx.Graph, path: list[Node], risk_map, clearance_map, grid: GridSpec, label: str):
    if not path:
        return {
            "label": label,
            "cost": float("inf"),
            "length_px": 0.0,
            "avg_risk": 1.0,
            "max_risk": 1.0,
            "mean_clearance": 0.0,
            "min_clearance": 0.0,
            "safety_score": 0.0,
        }
    risk_values = np.asarray([risk_map[node] for node in path], dtype=np.float32)
    clearance_values = np.asarray([clearance_map[node] for node in path], dtype=np.float32)
    length_px = path_length_pixels(path, grid)
    normalized_length = length_px / max(grid.width + grid.height, 1)
    avg_risk = float(risk_values.mean())
    max_risk = float(risk_values.max())
    mean_clearance = float(clearance_values.mean())
    min_clearance = float(clearance_values.min())
    safety_score = (
        100.0
        - avg_risk * 220.0
        - max_risk * 70.0
        - normalized_length * 10.0
        + mean_clearance * 28.0
        + min_clearance * 18.0
    )
    return {
        "label": label,
        "cost": path_cost(graph, path),
        "length_px": length_px,
        "avg_risk": avg_risk,
        "max_risk": max_risk,
        "mean_clearance": mean_clearance,
        "min_clearance": min_clearance,
        "safety_score": float(np.clip(safety_score, 1.0, 99.0)),
    }
