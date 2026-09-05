# A.Y.U.S.

A.Y.U.S., görüntüden göreli risk haritası çıkarıp geçilebilir grid hücreleri üzerinden afet senaryoları için rota öneren bir prototiptir. Gerçek bir acil durum, navigasyon veya karar destek sistemi değildir; resmî kurum ve uzman yönlendirmeleri her zaman önceliklidir.

## Özellikler

- Canny kenar yoğunluğuna dayalı göreli risk haritası
- Dijkstra ile varsayılan rota, isteğe bağlı ACO denemesi
- Masaüstü arayüzü ve komut satırı kullanımı
- Rota/risk görselleri ile isteğe bağlı GeoJSON çıktısı
- Görüntüye özel eşik ayarı için kalibrasyon aracı

## Hızlı başlangıç

Python 3.10–3.13 gerekir.

```bash
git clone https://github.com/beratbesli/A.Y.U.S..git
cd A.Y.U.S.
python -m venv .venv
```

Windows'ta `\.venv\Scripts\Activate.ps1`, Linux/macOS'ta `source .venv/bin/activate` komutunu çalıştırın. Ardından:

```bash
python -m pip install -e ".[dev]"
python -m ayus
```

Komut satırından örnek kullanım:

```bash
python -m ayus --input depremfoto.png --output-dir outputs
```

## Platformlar ve sürümler

- **Windows:** `kurulum.bat` ve `baslat.bat` ile kolay kurulum/başlatma; yayınlanan Windows paketi de kullanılabilir.
- **Linux/macOS:** Python ortamında yukarıdaki kurulum adımlarıyla çalışır.
- İndirilebilir paketler için [GitHub Releases](https://github.com/beratbesli/A.Y.U.S./releases) sayfasına bakın.

## Kalibrasyon

Görüntü eşiklerini etkileşimli ayarlamak için:

```bash
python kalibrasyon.py --input depremfoto.png --output-config ayus_config.json
```

## Geliştirme

```bash
ruff check .
pytest -q
```

MIT lisansı ile sunulmaktadır. Ayrıntılar için [LICENSE](LICENSE) ve güvenlik bildirimleri için [SECURITY.md](SECURITY.md) dosyalarına bakın.
