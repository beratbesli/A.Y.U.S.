from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import PlannerConfig, load_config
from .geospatial import GeoBounds, write_geojson
from .image_processing import load_image
from .planner import RoutePlan, generate_route_plan, write_image
from .visualization import show_results


def _node(value: str) -> tuple[int, int]:
    try:
        row, col = (int(part.strip()) for part in value.split(",", 1))
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("Koordinat 'satır,sütun' biçiminde olmalıdır.") from exc
    if row < 0 or col < 0:
        raise argparse.ArgumentTypeError("Koordinatlar negatif olamaz.")
    return row, col


def build_parser():
    parser = argparse.ArgumentParser(description="A.Y.U.S. görüntü tabanlı rota planlayıcı")
    parser.add_argument("--gui", action="store_true", help="Kolay kullanımlı masaüstü arayüzünü aç")
    parser.add_argument("--input", type=Path, default=Path("depremfoto.png"), help="İşlenecek görüntü")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Çıktı klasörü")
    parser.add_argument("--config", type=Path, help="Kalibrasyon JSON dosyası")
    parser.add_argument("--grid", type=int, help="Kare grid satır/sütun sayısı")
    parser.add_argument("--start", type=_node, help="Başlangıç hedefi: satır,sütun")
    parser.add_argument("--end", type=_node, help="Bitiş hedefi: satır,sütun")
    parser.add_argument("--algorithm", choices=("dijkstra", "aco"), help="Rota algoritması; varsayılan dijkstra")
    parser.add_argument("--seed", type=int, help="ACO için deterministik seed")
    parser.add_argument("--bounds", type=GeoBounds.from_csv, help="GeoJSON sınırları: min_lon,min_lat,max_lon,max_lat")
    parser.add_argument("--no-save", action="store_true", help="Görüntü çıktısı kaydetme")
    parser.add_argument("--show", action="store_true", help="Sonuç pencerelerini göster")
    return parser


def _config_from_args(args):
    config = load_config(args.config) if args.config else PlannerConfig()
    overrides = {}
    if args.grid is not None:
        overrides.update(grid_rows=args.grid, grid_cols=args.grid)
    if args.algorithm:
        overrides["algorithm"] = args.algorithm
    if args.seed is not None:
        overrides["seed"] = args.seed
    return config.with_overrides(**overrides) if overrides else config


def _print_plan(plan: RoutePlan) -> None:
    print(f"Başlangıç düğümü: {plan.start_node}")
    print(f"Bitiş düğümü: {plan.end_node}")
    if plan.used_fallback:
        print("ACO rota üretemedi; deterministik en kısa yol yedek olarak kullanıldı.")
    for metric in plan.route_metrics:
        print(
            f"{metric['label']}: skor={float(metric['safety_score']):.1f}/100 | "
            f"uzunluk={float(metric['length_px']):.1f} px | "
            f"ortalama risk=%{float(metric['avg_risk']) * 100:.1f} | "
            f"min göreli açıklık=%{float(metric['min_clearance']) * 100:.1f}"
        )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.gui:
        from .gui import launch_gui

        return launch_gui(args.input)
    try:
        config = _config_from_args(args)
        image = load_image(args.input)
        plan = generate_route_plan(image, config, args.start, args.end)
        if not args.no_save:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            write_image(args.output_dir / "afet_rota_sonuclari.png", plan.result_image)
            write_image(args.output_dir / "afet_risk_haritasi.png", plan.risk_image)
            if args.bounds:
                write_geojson(args.output_dir / "routes.geojson", plan.routes, plan.grid, args.bounds)
            print(f"Çıktılar kaydedildi: {args.output_dir.resolve()}")
        if args.show:
            show_results(plan.result_image, plan.risk_image)
        _print_plan(plan)
        return 0
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
