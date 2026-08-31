from __future__ import annotations

import cv2
import numpy as np

from .config import PlannerConfig
from .image_processing import GridSpec
from .routing import Node

ROUTE_COLORS = ((0, 255, 0), (255, 200, 0), (255, 0, 255))


def _draw_text_block(image, lines, top_left, line_height=24):
    x, y = top_left
    width = max((cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)[0][0] for line in lines), default=0)
    height = len(lines) * line_height + 18
    overlay = image.copy()
    cv2.rectangle(overlay, (x, y), (x + width + 24, y + height), (18, 18, 18), -1)
    cv2.addWeighted(overlay, 0.72, image, 0.28, 0, image)
    for index, line in enumerate(lines):
        cv2.putText(
            image,
            line,
            (x + 12, y + 24 + index * line_height),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )


def _cell_rectangle(grid: GridSpec, node: Node):
    row_start, row_end, col_start, col_end = grid.bounds(node)
    return (col_start, row_start), (max(col_start, col_end - 1), max(row_start, row_end - 1))


def draw_result(
    image, routes, metrics, grid: GridSpec, risk_map, blocked_mask, start: Node, end: Node, config: PlannerConfig
):
    result = image.copy()
    overlay = image.copy()
    for row in range(grid.rows):
        for col in range(grid.cols):
            rectangle = _cell_rectangle(grid, (row, col))
            if blocked_mask[row, col]:
                cv2.rectangle(overlay, *rectangle, (0, 0, 255), -1)
            elif risk_map[row, col] >= config.risk_threshold:
                cv2.rectangle(overlay, *rectangle, (0, 165, 255), -1)
    cv2.addWeighted(overlay, 0.35, result, 0.65, 0, result)
    for route_index in range(min(len(routes), len(ROUTE_COLORS)) - 1, -1, -1):
        path = routes[route_index]
        points = np.asarray([[int(grid.center(node)[0]), int(grid.center(node)[1])] for node in path], dtype=np.int32)
        cv2.polylines(result, [points], False, ROUTE_COLORS[route_index], 4 if route_index == 0 else 2, cv2.LINE_AA)
    for node, color in ((start, (255, 255, 255)), (end, (0, 255, 0))):
        x, y = grid.center(node)
        radius = max(5, int(min(grid.width / grid.cols, grid.height / grid.rows) / 3))
        cv2.circle(result, (int(x), int(y)), radius, color, -1, cv2.LINE_AA)
        cv2.circle(result, (int(x), int(y)), radius + 2, (0, 0, 0), 2, cv2.LINE_AA)
    first = metrics[0] if metrics else None
    lines = [
        "Afet rota planlayici",
        f"Birincil skor: {float(first['safety_score']):.1f}/100" if first else "Birincil rota yok",
        f"Rota uzunlugu: {float(first['length_px']):.0f} px" if first else "Rota uzunlugu: -",
        f"Min aciklik: %{float(first['min_clearance']) * 100:.0f}" if first else "Min aciklik: -",
        f"Alternatif rota: {max(0, len(routes) - 1)}",
    ]
    _draw_text_block(result, lines, (18, 18))
    legend = ["Kirmizi: kapali alan", "Turuncu: riskli koridor", "Yesil: birincil rota"]
    if len(routes) > 1:
        legend.append("Mavi/mor: alternatif rotalar")
    _draw_text_block(result, legend, (18, 170))
    return result


def draw_risk_heatmap(image, risk_map, blocked_mask, grid: GridSpec, start: Node, end: Node):
    risk_8bit = np.clip(risk_map * 255.0 * 2.5, 0, 255).astype(np.uint8)
    heat_small = cv2.applyColorMap(risk_8bit, cv2.COLORMAP_JET)
    heatmap = cv2.resize(heat_small, (grid.width, grid.height), interpolation=cv2.INTER_NEAREST)
    result = cv2.addWeighted(image, 0.40, heatmap, 0.60, 0)
    for row in range(grid.rows):
        for col in range(grid.cols):
            if blocked_mask[row, col]:
                cv2.rectangle(result, *_cell_rectangle(grid, (row, col)), (0, 0, 255), 1)
    for node, color in ((start, (255, 255, 255)), (end, (0, 255, 0))):
        x, y = grid.center(node)
        cv2.circle(result, (int(x), int(y)), 6, color, -1, cv2.LINE_AA)
        cv2.circle(result, (int(x), int(y)), 8, (0, 0, 0), 2, cv2.LINE_AA)
    _draw_text_block(result, ["Risk isi haritasi", "Mavi: daha dusuk risk", "Kirmizi: daha yuksek risk"], (18, 18))
    return result


def show_results(result_image, risk_image):
    cv2.imshow("Afet Yonetim - Guvenli Rotalar", result_image)
    cv2.imshow("Afet Yonetim - Risk Haritasi", risk_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
