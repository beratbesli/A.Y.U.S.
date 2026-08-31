from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .config import PlannerConfig


@dataclass(frozen=True)
class GridSpec:
    """A grid whose boundaries cover every input pixel exactly once."""

    height: int
    width: int
    rows: int
    cols: int
    row_edges: np.ndarray
    col_edges: np.ndarray

    def bounds(self, node: tuple[int, int]) -> tuple[int, int, int, int]:
        row, col = node
        if not 0 <= row < self.rows or not 0 <= col < self.cols:
            raise ValueError(f"Grid düğümü sınır dışında: {node}")
        return (
            int(self.row_edges[row]),
            int(self.row_edges[row + 1]),
            int(self.col_edges[col]),
            int(self.col_edges[col + 1]),
        )

    def center(self, node: tuple[int, int]) -> tuple[float, float]:
        row_start, row_end, col_start, col_end = self.bounds(node)
        return ((col_start + col_end - 1) / 2.0, (row_start + row_end - 1) / 2.0)


@dataclass(frozen=True)
class RiskMaps:
    edges: np.ndarray
    grid: GridSpec
    raw_risk: np.ndarray
    buffered_risk: np.ndarray
    blocked_mask: np.ndarray
    clearance: np.ndarray


def load_image(path: Path, max_file_bytes: int = 100 * 1024 * 1024, max_pixels: int = 50_000_000) -> np.ndarray:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Girdi görüntüsü bulunamadı: {path}")
    if path.stat().st_size > max_file_bytes:
        raise ValueError(f"Girdi görüntüsü izin verilen dosya boyutunu aşıyor: {path}")
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"Girdi görüntüsü okunamadı veya BGR renkli görüntü değil: {path}")
    if image.shape[0] * image.shape[1] > max_pixels:
        raise ValueError(f"Girdi görüntüsü izin verilen piksel sayısını aşıyor: {path}")
    return image


def build_grid(image: np.ndarray, config: PlannerConfig) -> GridSpec:
    height, width = image.shape[:2]
    if height < config.grid_rows or width < config.grid_cols:
        raise ValueError("Grid boyutu görüntü boyutundan büyük olamaz.")
    row_edges = np.linspace(0, height, config.grid_rows + 1, dtype=np.int32)
    col_edges = np.linspace(0, width, config.grid_cols + 1, dtype=np.int32)
    return GridSpec(height, width, config.grid_rows, config.grid_cols, row_edges, col_edges)


def _odd(value: int) -> int:
    value = max(1, int(value))
    return value if value % 2 else value + 1


def compute_clearance_map(blocked_mask: np.ndarray) -> np.ndarray:
    if np.all(blocked_mask):
        return np.zeros_like(blocked_mask, dtype=np.float32)
    if not np.any(blocked_mask):
        return np.ones_like(blocked_mask, dtype=np.float32)
    free_mask = np.where(blocked_mask, 0, 255).astype(np.uint8)
    clearance = cv2.distanceTransform(free_mask, cv2.DIST_L2, 3)
    maximum = float(clearance.max())
    if maximum <= 0:
        return np.zeros_like(blocked_mask, dtype=np.float32)
    return (clearance / maximum).astype(np.float32)


def clear_safe_zone(blocked_mask: np.ndarray, center: tuple[int, int] | None, radius: int) -> None:
    if center is None:
        return
    center_row, center_col = center
    rows, cols = blocked_mask.shape
    for row in range(center_row - radius, center_row + radius + 1):
        for col in range(center_col - radius, center_col + radius + 1):
            if 0 <= row < rows and 0 <= col < cols:
                blocked_mask[row, col] = False


def build_risk_maps(image: np.ndarray, config: PlannerConfig) -> RiskMaps:
    config.validate()
    grid = build_grid(image, config)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (_odd(config.blur_kernel), _odd(config.blur_kernel)), 0)
    edges = cv2.Canny(blurred, config.canny_low, config.canny_high)
    dilation_size = _odd(config.edge_dilation)
    if dilation_size > 1:
        edges = cv2.dilate(edges, np.ones((dilation_size, dilation_size), np.uint8), iterations=1)

    raw_risk = np.zeros((grid.rows, grid.cols), dtype=np.float32)
    for row in range(grid.rows):
        for col in range(grid.cols):
            row_start, row_end, col_start, col_end = grid.bounds((row, col))
            raw_risk[row, col] = float(np.mean(edges[row_start:row_end, col_start:col_end] > 0))

    if config.buffer_radius:
        kernel_size = config.buffer_radius * 2 + 1
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        dilated = cv2.dilate(raw_risk, kernel, iterations=1)
        smoothed = cv2.GaussianBlur(raw_risk, (0, 0), sigmaX=1.1)
        buffered = np.maximum(dilated * 0.80, smoothed).astype(np.float32)
    else:
        buffered = raw_risk.copy()
    blocked = raw_risk >= config.block_threshold
    return RiskMaps(edges, grid, raw_risk, buffered, blocked, compute_clearance_map(blocked))
