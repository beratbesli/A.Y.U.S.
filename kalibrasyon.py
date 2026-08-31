from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from ayus.config import PlannerConfig
from ayus.image_processing import load_image


def _odd(value: int) -> int:
    return max(1, value | 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="A.Y.U.S. Canny kalibrasyonu")
    parser.add_argument("--input", type=Path, default=Path("depremfoto.png"))
    parser.add_argument("--output-config", type=Path, default=Path("ayus_config.json"))
    args = parser.parse_args()
    try:
        image = load_image(args.input)
    except ValueError as exc:
        print(f"HATA: {exc}")
        return 2

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    window = "Enkaz Tespiti (Kenar Bulma)"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, 1200, 700)
    cv2.createTrackbar("Bulaniklik", window, 2, 20, lambda _: None)
    cv2.createTrackbar("Alt Esik", window, 50, 254, lambda _: None)
    cv2.createTrackbar("Ust Esik", window, 150, 255, lambda _: None)
    cv2.createTrackbar("Kalinlik", window, 1, 10, lambda _: None)
    print("S: ayarları JSON dosyasına kaydet | Q: çık")

    while True:
        blur = _odd(cv2.getTrackbarPos("Bulaniklik", window))
        low = cv2.getTrackbarPos("Alt Esik", window)
        high = max(low + 1, cv2.getTrackbarPos("Ust Esik", window))
        dilation = max(1, cv2.getTrackbarPos("Kalinlik", window))
        edges = cv2.Canny(cv2.GaussianBlur(gray, (blur, blur), 0), low, high)
        if dilation > 1:
            size = _odd(dilation)
            edges = cv2.dilate(edges, np.ones((size, size), np.uint8), iterations=1)
        cv2.imshow("Orijinal Fotograf", image)
        cv2.imshow(window, edges)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            config = PlannerConfig(blur_kernel=blur, canny_low=low, canny_high=high, edge_dilation=dilation)
            config.save(args.output_config)
            print(f"Kalibrasyon kaydedildi: {args.output_config}")
        elif key == ord("q"):
            break
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
