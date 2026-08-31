from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .image_processing import GridSpec
from .routing import Node


@dataclass(frozen=True)
class GeoBounds:
    """North-up geographic extent of the input image in WGS84 degrees."""

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    def validate(self) -> None:
        if not self.min_lon < self.max_lon or not self.min_lat < self.max_lat:
            raise ValueError("Coğrafi sınırlar min_lon/min_lat < max_lon/max_lat olmalıdır.")
        if not -180.0 <= self.min_lon <= 180.0 or not -180.0 <= self.max_lon <= 180.0:
            raise ValueError("Boylamlar -180 ile 180 arasında olmalıdır.")
        if not -90.0 <= self.min_lat <= 90.0 or not -90.0 <= self.max_lat <= 90.0:
            raise ValueError("Enlemler -90 ile 90 arasında olmalıdır.")

    @classmethod
    def from_csv(cls, value: str) -> GeoBounds:
        try:
            min_lon, min_lat, max_lon, max_lat = (float(part.strip()) for part in value.split(","))
        except (TypeError, ValueError) as exc:
            raise ValueError("Sınırlar 'min_lon,min_lat,max_lon,max_lat' biçiminde olmalıdır.") from exc
        bounds = cls(min_lon, min_lat, max_lon, max_lat)
        bounds.validate()
        return bounds


def pixel_to_lonlat(x: float, y: float, width: int, height: int, bounds: GeoBounds) -> tuple[float, float]:
    bounds.validate()
    if width < 1 or height < 1:
        raise ValueError("Görüntü boyutları pozitif olmalıdır.")
    x_ratio = min(1.0, max(0.0, x / max(width - 1, 1)))
    y_ratio = min(1.0, max(0.0, y / max(height - 1, 1)))
    longitude = bounds.min_lon + x_ratio * (bounds.max_lon - bounds.min_lon)
    latitude = bounds.max_lat - y_ratio * (bounds.max_lat - bounds.min_lat)
    return longitude, latitude


def routes_to_geojson(routes: list[list[Node]], grid: GridSpec, bounds: GeoBounds) -> dict:
    features = []
    for index, route in enumerate(routes):
        coordinates = [list(pixel_to_lonlat(*grid.center(node), grid.width, grid.height, bounds)) for node in route]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "label": "Birincil Rota" if index == 0 else f"Alternatif {index}",
                    "vertex_count": len(route),
                },
                "geometry": {"type": "LineString", "coordinates": coordinates},
            }
        )
    return {"type": "FeatureCollection", "features": features}


def write_geojson(path: Path, routes: list[list[Node]], grid: GridSpec, bounds: GeoBounds) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(routes_to_geojson(routes, grid, bounds), indent=2) + "\n", encoding="utf-8")
