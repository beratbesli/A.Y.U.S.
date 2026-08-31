from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import networkx as nx
import numpy as np

from .config import PlannerConfig
from .image_processing import build_risk_maps, clear_safe_zone, compute_clearance_map
from .metrics import compute_route_metrics
from .routing import Node, build_graph, choose_endpoints, find_corner_anchor, generate_backup_routes, run_aco
from .visualization import draw_result, draw_risk_heatmap


@dataclass(frozen=True)
class RoutePlan:
    start_node: Node
    end_node: Node
    primary_cost: float
    used_fallback: bool
    routes: list[list[Node]]
    route_metrics: list[dict]
    result_image: np.ndarray
    risk_image: np.ndarray


def write_image(path: Path, image: np.ndarray) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise OSError(f"Çıktı görüntüsü yazılamadı: {path}")


def generate_route_plan(
    image: np.ndarray, config: PlannerConfig, start_target: Node | None = None, end_target: Node | None = None
) -> RoutePlan:
    config.validate()
    maps = build_risk_maps(image, config)
    for name, target in (("başlangıç", start_target), ("bitiş", end_target)):
        if target is not None and not (0 <= target[0] < maps.grid.rows and 0 <= target[1] < maps.grid.cols):
            raise ValueError(f"{name} grid koordinatı sınır dışında: {target}")
    start_anchor = start_target or find_corner_anchor(maps.blocked_mask, maps.buffered_risk, maps.clearance, "top_left")
    end_anchor = end_target or find_corner_anchor(maps.blocked_mask, maps.buffered_risk, maps.clearance, "bottom_right")
    if start_anchor is None or end_anchor is None:
        raise RuntimeError("Başlangıç veya bitiş bölgesinde geçilebilir hücre bulunamadı.")
    blocked_mask = maps.blocked_mask.copy()
    clear_safe_zone(blocked_mask, start_anchor, config.safe_zone_radius)
    clear_safe_zone(blocked_mask, end_anchor, config.safe_zone_radius)
    clearance = compute_clearance_map(blocked_mask)
    graph = build_graph(blocked_mask, maps.buffered_risk, clearance, maps.grid, config)
    start_node, end_node = choose_endpoints(graph, maps.buffered_risk, clearance, start_anchor, end_anchor)
    if start_node is None or end_node is None:
        raise RuntimeError("Aynı geçilebilir koridorda başlangıç ve bitiş noktası bulunamadı.")

    used_fallback = False
    primary_path, primary_cost = (
        run_aco(graph, start_node, end_node, config) if config.algorithm == "aco" else ([], float("inf"))
    )
    if not primary_path:
        try:
            primary_path = nx.shortest_path(graph, start_node, end_node, weight="weight")
        except nx.NetworkXNoPath as exc:
            raise RuntimeError("Hedefe giden geçilebilir rota bulunamadı.") from exc
        primary_cost = sum(
            graph.edges[primary_path[i], primary_path[i + 1]]["weight"] for i in range(len(primary_path) - 1)
        )
        used_fallback = config.algorithm == "aco"

    routes = generate_backup_routes(graph, start_node, end_node, primary_path, config)
    metrics = [
        compute_route_metrics(
            graph,
            route,
            maps.buffered_risk,
            clearance,
            maps.grid,
            "Birincil Rota" if index == 0 else f"Alternatif {index}",
        )
        for index, route in enumerate(routes)
    ]
    result_image = draw_result(
        image, routes, metrics, maps.grid, maps.buffered_risk, blocked_mask, start_node, end_node, config
    )
    risk_image = draw_risk_heatmap(image, maps.buffered_risk, blocked_mask, maps.grid, start_node, end_node)
    return RoutePlan(
        start_node, end_node, float(primary_cost), used_fallback, routes, metrics, result_image, risk_image
    )
