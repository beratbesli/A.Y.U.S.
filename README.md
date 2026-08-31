# A.Y.U.S.

A.Y.U.S., EYBAL ekibinin TUA Astro Hackathon kapsamında geliştirdiği, görüntü tabanlı afet rota planlama prototipidir. Görüntü kenar yoğunluğundan göreli bir risk haritası çıkarır ve geçilebilir grid hücreleri üzerinden rota önerir.

> **Güvenlik uyarısı:** Bu yazılım doğrulanmış bir afet yönetimi, navigasyon veya acil müdahale sistemi değildir. Gerçek hayatta resmi acil durum verileri, uzman doğrulaması ve yetkili kurumların talimatları her zaman önceliklidir.

## Kurulum

Python 3.10–3.13 ve `pip` gerekir.

```bash
git clone https://github.com/beratbesli/A.Y.U.S..git
cd A.Y.U.S.
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

```bash
python -m pip install -r requirements-dev.txt
```

## Çalıştırma

Varsayılan çalışma:

```bash
python A.Y.U.S..py --input depremfoto.png --output-dir outputs
```

Sunucu/CI gibi grafik arayüzü olmayan ortamlarda `--show` kullanmayın. Başlangıç ve bitiş hedefleri grid koordinatı olarak verilebilir:

```bash
python -m ayus --input depremfoto.png --start 2,3 --end 37,36 --no-save
```

Varsayılan ve önerilen rota algoritması Dijkstra’dır. Seed’li ACO denemek için:

```bash
python -m ayus --algorithm aco --seed 42
```

Çıktılar `outputs/afet_rota_sonuclari.png` ve `outputs/afet_risk_haritasi.png` olarak yazılır. Rota uzunluğu görüntünün gerçek piksel geometrisine göre hesaplanır; “açıklık” değeri grid içindeki göreli clearance ölçüsüdür.

## Kalibrasyon

```bash
python kalibrasyon.py --input depremfoto.png --output-config ayus_config.json
```

Pencerede ayarları değiştirip `S` tuşuna basınca değerler `ayus_config.json` dosyasına kaydedilir. Ana programda kullanmak için:

```bash
python -m ayus --config ayus_config.json
```

## Test ve kalite kontrolleri

```bash
ruff check .
python -m compileall -q .
pytest -q
```

GitHub Actions, CodeQL, Dependency Review ve Dependabot yapılandırmaları `.github/` altında bulunur.

## Sınırlamalar ve gelecek çalışmalar

Mevcut risk modeli Canny kenar yoğunluğuna dayalı bir heuristiktir; enkazı semantik olarak tanımaz, uydu görüntüsünü coğrafi koordinatlara bağlamaz ve gerçek güvenlik garantisi vermez. Üretim kullanımından önce etiketli afet görüntüleriyle doğrulanan bir hasar/engel segmentasyon modeli, gerçek yol/toplanma alanı verileri, koordinat dönüşümü, kullanıcı doğrulaması ve bağımsız saha testleri eklenmelidir.

## Lisans

[MIT Lisansı](LICENSE) ile sunulmaktadır.
