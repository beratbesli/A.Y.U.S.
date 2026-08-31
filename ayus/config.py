from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PlannerConfig:
    """Validated, serializable configuration for the planner."""

    grid_rows: int = 40
    grid_cols: int = 40
    blur_kernel: int = 5
    canny_low: int = 50
    canny_high: int = 150
    edge_dilation: int = 1
    block_threshold: float = 0.10
    risk_threshold: float = 0.04
    buffer_radius: int = 2
    safe_zone_radius: int = 1
    risk_edge_weight: float = 18.0
    clearance_edge_weight: float = 4.5
    alternative_route_count: int = 3
    alternative_search_attempts: int = 30
    alternative_overlap_limit: float = 0.65
    aco_ants: int = 45
    aco_iterations: int = 30
    aco_alpha: float = 1.2
    aco_beta: float = 3.0
    aco_gamma: float = 2.0
    aco_evaporation: float = 0.35
    aco_deposit: float = 160.0
    seed: int = 42
    algorithm: str = "dijkstra"

    def validate(self) -> None:
        if self.grid_rows < 2 or self.grid_cols < 2:
            raise ValueError("grid_rows ve grid_cols en az 2 olmalıdır.")
        if self.blur_kernel < 1:
            raise ValueError("blur_kernel en az 1 olmalıdır.")
        if self.canny_low < 0 or self.canny_high < 0 or self.canny_low >= self.canny_high:
            raise ValueError("canny_low, canny_high'dan küçük ve geçerli olmalıdır.")
        if self.edge_dilation < 1:
            raise ValueError("edge_dilation en az 1 olmalıdır.")
        for name in ("block_threshold", "risk_threshold", "alternative_overlap_limit"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} 0 ile 1 arasında olmalıdır.")
        for name in ("buffer_radius", "safe_zone_radius"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} negatif olamaz.")
        if self.alternative_route_count < 1 or self.alternative_search_attempts < 1:
            raise ValueError("Rota sayısı ve arama denemesi en az 1 olmalıdır.")
        if self.aco_ants < 1 or self.aco_iterations < 1:
            raise ValueError("ACO ant ve iterasyon sayısı en az 1 olmalıdır.")
        for name in ("risk_edge_weight", "clearance_edge_weight", "aco_alpha", "aco_beta", "aco_gamma", "aco_deposit"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} geçerli ve negatif olmayan bir sayı olmalıdır.")
        if not 0.0 < self.aco_evaporation < 1.0:
            raise ValueError("aco_evaporation 0 ile 1 arasında olmalıdır.")
        if self.algorithm not in {"dijkstra", "aco"}:
            raise ValueError("algorithm yalnızca 'dijkstra' veya 'aco' olabilir.")

    def with_overrides(self, **overrides: Any) -> PlannerConfig:
        unknown = set(overrides) - {field.name for field in fields(self)}
        if unknown:
            raise ValueError(f"Bilinmeyen yapılandırma alanları: {', '.join(sorted(unknown))}")
        updated = replace(self, **overrides)
        updated.validate()
        return updated

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


def load_config(path: Path) -> PlannerConfig:
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Yapılandırma dosyası bulunamadı: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Yapılandırma JSON olarak okunamadı: {path}") from exc
    if not isinstance(data, dict):
        raise TypeError("Yapılandırma dosyasının kökü bir JSON nesnesi olmalıdır.")
    return PlannerConfig().with_overrides(**data)
