from __future__ import annotations

import base64
import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import cv2

from .config import PlannerConfig, load_config
from .image_processing import load_image
from .planner import RoutePlan, generate_route_plan, write_image


def _application_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _default_input_path() -> Path:
    candidates = [_application_dir() / "depremfoto.png"]
    if hasattr(sys, "_MEIPASS"):
        candidates.append(Path(sys._MEIPASS) / "depremfoto.png")
    candidates.append(Path("depremfoto.png"))
    return next((path for path in candidates if path.is_file()), candidates[0])


def _default_icon_path() -> Path | None:
    candidates = [
        _application_dir() / "assets" / "ayus.png",
        _application_dir() / "ayus.png",
    ]
    if hasattr(sys, "_MEIPASS"):
        candidates.append(Path(sys._MEIPASS) / "assets" / "ayus.png")
        candidates.append(Path(sys._MEIPASS) / "ayus.png")
    candidates.append(Path("assets/ayus.png"))
    return next((path for path in candidates if path.is_file()), None)


class AyusApp:
    """Small desktop interface for exploring route and risk images."""

    def __init__(self, root: tk.Tk, initial_input: Path | None = None) -> None:
        self.root = root
        self.root.title("A.Y.U.S. - Afet Rota Planlayıcı")
        self.root.geometry("1280x820")
        self.root.minsize(900, 650)

        icon_path = _default_icon_path()
        if icon_path:
            try:
                self._app_icon = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(False, self._app_icon)
            except tk.TclError:
                self._app_icon = None

        default_input = initial_input or _default_input_path()
        default_output = _application_dir() / "outputs" if getattr(sys, "frozen", False) else Path("outputs")
        self.input_var = tk.StringVar(value=str(default_input))
        self.config_var = tk.StringVar()
        self.output_var = tk.StringVar(value=str(default_output))
        self.algorithm_var = tk.StringVar(value="Dijkstra (önerilen)")
        self.status_var = tk.StringVar(value="Hazır. Bir görüntü seçip rota oluşturabilirsiniz.")
        self.summary_var = tk.StringVar(value="Henüz rota oluşturulmadı.")
        self.run_button: ttk.Button | None = None
        self.open_output_button: ttk.Button | None = None
        self.route_canvas: tk.Canvas | None = None
        self.risk_canvas: tk.Canvas | None = None
        self.plan: RoutePlan | None = None
        self._display_images: dict[str, object] = {}
        self._image_arrays: dict[str, object] = {}

        self._build_layout()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        header = ttk.Frame(self.root, padding=(18, 14, 18, 4))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="A.Y.U.S.", font=("Segoe UI", 22, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Görüntü üzerinden göreli risk alanlarını ve güvenli rota önerilerini inceleyin.",
            foreground="#555555",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        controls = ttk.LabelFrame(self.root, text="Çalışma ayarları", padding=12)
        controls.grid(row=1, column=0, padx=18, pady=8, sticky="ew")
        controls.columnconfigure(1, weight=1)

        self._add_path_row(controls, 0, "Görüntü", self.input_var, self._choose_input, "Görüntü dosyası seç")
        self._add_path_row(controls, 1, "Kalibrasyon", self.config_var, self._choose_config, "JSON seç (isteğe bağlı)")
        self._add_path_row(controls, 2, "Çıktı klasörü", self.output_var, self._choose_output, "Klasör seç")

        ttk.Label(controls, text="Algoritma").grid(row=3, column=0, padx=(0, 8), pady=(8, 0), sticky="w")
        algorithm_box = ttk.Combobox(
            controls,
            textvariable=self.algorithm_var,
            values=("Dijkstra (önerilen)", "ACO (deneysel)"),
            state="readonly",
            width=24,
        )
        algorithm_box.grid(row=3, column=1, pady=(8, 0), sticky="w")

        buttons = ttk.Frame(controls)
        buttons.grid(row=3, column=2, padx=(12, 0), pady=(8, 0), sticky="e")
        self.run_button = ttk.Button(buttons, text="Rota oluştur", command=self._start_run)
        self.run_button.pack(side="left")
        self.open_output_button = ttk.Button(
            buttons, text="Çıktı klasörünü aç", command=self._open_output, state="disabled"
        )
        self.open_output_button.pack(side="left", padx=(8, 0))

        ttk.Label(self.root, textvariable=self.status_var, padding=(18, 0, 18, 4)).grid(
            row=2, column=0, sticky="new"
        )

        content = ttk.Frame(self.root, padding=(18, 0, 18, 12))
        content.grid(row=3, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        summary = ttk.Label(
            content,
            textvariable=self.summary_var,
            justify="left",
            anchor="w",
            padding=(10, 8),
            relief="groove",
        )
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        notebook = ttk.Notebook(content)
        notebook.grid(row=1, column=0, sticky="nsew")
        route_tab = ttk.Frame(notebook)
        risk_tab = ttk.Frame(notebook)
        notebook.add(route_tab, text="Rotalar")
        notebook.add(risk_tab, text="Risk haritası")
        self.route_canvas = self._image_canvas(route_tab)
        self.risk_canvas = self._image_canvas(risk_tab)

        ttk.Label(
            self.root,
            text="Yeşil: birincil rota  |  Mavi/mor: alternatif rotalar  |  Kırmızı: kapalı alan  |  Turuncu: riskli alan",
            foreground="#555555",
            padding=(18, 0, 18, 12),
        ).grid(row=4, column=0, sticky="w")

    @staticmethod
    def _image_canvas(parent: ttk.Frame) -> tk.Canvas:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        canvas = tk.Canvas(parent, background="#202124", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        canvas.bind("<Configure>", lambda _event: None)
        return canvas

    def _add_path_row(
        self,
        parent: ttk.LabelFrame,
        row: int,
        label: str,
        variable: tk.StringVar,
        command,
        button_text: str,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, padx=(0, 8), pady=3, sticky="w")
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, pady=3, sticky="ew")
        ttk.Button(parent, text=button_text, command=command).grid(row=row, column=2, padx=(12, 0), pady=3)

    def _choose_input(self) -> None:
        path = filedialog.askopenfilename(
            title="İşlenecek görüntüyü seçin",
            filetypes=(
                ("Görüntüler", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                ("Tüm dosyalar", "*.*"),
            ),
        )
        if path:
            self.input_var.set(path)

    def _choose_config(self) -> None:
        path = filedialog.askopenfilename(
            title="Kalibrasyon dosyasını seçin",
            filetypes=(("JSON dosyası", "*.json"), ("Tüm dosyalar", "*.*")),
        )
        if path:
            self.config_var.set(path)

    def _choose_output(self) -> None:
        path = filedialog.askdirectory(title="Çıktı klasörünü seçin")
        if path:
            self.output_var.set(path)

    def _set_busy(self, busy: bool) -> None:
        if self.run_button:
            self.run_button.configure(state="disabled" if busy else "normal")
        self.root.configure(cursor="watch" if busy else "")

    def _start_run(self) -> None:
        input_path = Path(self.input_var.get().strip())
        output_path = Path(self.output_var.get().strip() or "outputs")
        if not input_path.is_file():
            messagebox.showerror("Görüntü bulunamadı", f"Görüntü dosyası bulunamadı:\n{input_path}")
            return
        try:
            config = load_config(Path(self.config_var.get().strip())) if self.config_var.get().strip() else PlannerConfig()
            algorithm = "aco" if self.algorithm_var.get().startswith("ACO") else "dijkstra"
            config = config.with_overrides(algorithm=algorithm)
        except (OSError, TypeError, ValueError) as exc:
            messagebox.showerror("Ayar hatası", str(exc))
            return

        self._set_busy(True)
        self.status_var.set("Görüntü işleniyor ve rotalar hesaplanıyor…")
        if self.open_output_button:
            self.open_output_button.configure(state="disabled")
        threading.Thread(
            target=self._run_worker,
            args=(input_path, output_path, config),
            daemon=True,
        ).start()

    def _run_worker(self, input_path: Path, output_path: Path, config: PlannerConfig) -> None:
        try:
            plan = generate_route_plan(load_image(input_path), config)
            output_path.mkdir(parents=True, exist_ok=True)
            write_image(output_path / "afet_rota_sonuclari.png", plan.result_image)
            write_image(output_path / "afet_risk_haritasi.png", plan.risk_image)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            self.root.after(0, self._run_failed, str(exc))
            return
        self.root.after(0, self._run_finished, plan, output_path)

    def _run_failed(self, error: str) -> None:
        self._set_busy(False)
        self.status_var.set("İşlem başarısız.")
        messagebox.showerror("Rota oluşturulamadı", error)

    def _run_finished(self, plan: RoutePlan, output_path: Path) -> None:
        self._set_busy(False)
        self.plan = plan
        self.status_var.set(f"Rota hazır. Görseller kaydedildi: {output_path.resolve()}")
        if self.open_output_button:
            self.open_output_button.configure(state="normal")
        primary = plan.route_metrics[0] if plan.route_metrics else None
        if primary:
            summary = (
                f"Başlangıç: {plan.start_node}    Bitiş: {plan.end_node}\n"
                f"Birincil rota güvenlik skoru: {float(primary['safety_score']):.1f}/100    "
                f"Uzunluk: {float(primary['length_px']):.1f} px    "
                f"Ortalama risk: %{float(primary['avg_risk']) * 100:.1f}\n"
                f"Alternatif rota sayısı: {max(0, len(plan.routes) - 1)}    "
                f"Minimum göreli açıklık: %{float(primary['min_clearance']) * 100:.1f}"
            )
            if plan.used_fallback:
                summary += "\nACO rota üretemedi; deterministik Dijkstra yedeği kullanıldı."
            self.summary_var.set(summary)
        self._image_arrays = {"route": plan.result_image, "risk": plan.risk_image}
        self._display_image("route", self.route_canvas)
        self._display_image("risk", self.risk_canvas)

    def _display_image(self, name: str, canvas: tk.Canvas | None) -> None:
        if canvas is None or name not in self._image_arrays:
            return
        image = self._image_arrays[name]
        height, width = image.shape[:2]
        available_width = max(canvas.winfo_width() - 20, 400)
        available_height = max(canvas.winfo_height() - 20, 300)
        scale = min(available_width / width, available_height / height, 1.0)
        if scale < 1.0:
            image = cv2.resize(image, (max(1, int(width * scale)), max(1, int(height * scale))))
        success, encoded = cv2.imencode(".png", image)
        if not success:
            return
        data = base64.b64encode(encoded.tobytes()).decode("ascii")
        photo = tk.PhotoImage(data=data)
        self._display_images[name] = photo
        canvas.delete("all")
        canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, image=photo, anchor="center")

    def _open_output(self) -> None:
        output_path = Path(self.output_var.get().strip() or "outputs").resolve()
        if not output_path.is_dir():
            return
        if hasattr(os, "startfile"):
            os.startfile(str(output_path))


def launch_gui(initial_input: Path | None = None) -> int:
    root = tk.Tk()
    AyusApp(root, initial_input=initial_input)
    root.mainloop()
    return 0
