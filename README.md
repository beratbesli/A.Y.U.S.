![A.Y.U.S.](assets/ayus-header.png)

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

## Kolay kullanım (Windows)

Projeyi indirdikten sonra `kurulum.bat` dosyasına çift tıklayın. Kurulum bitince `baslat.bat` dosyasına çift tıklayarak görsel uygulamayı açabilirsiniz. Uygulamayı Python olmadan kullanmak için `paketle.bat` dosyasını çalıştırın; oluşan `dist/A.Y.U.S.exe` dosyası tek başına açılabilir.

Uygulamada görüntüyü seçin, isterseniz kalibrasyon JSON dosyanızı yükleyin ve `Rota oluştur` düğmesine basın. `Rotalar` sekmesinde birincil ve alternatif yolları, `Risk haritası` sekmesinde göreli risk alanlarını görebilirsiniz. Çıktılar ayrıca seçtiğiniz klasöre PNG olarak kaydedilir.

GitHub’daki `Windows application` iş akışı elle çalıştırıldığında Windows için `A.Y.U.S.-windows.zip` artefaktı üretir. `v*` etiketi gönderildiğinde aynı ZIP otomatik olarak GitHub Release asset’i olarak da yayınlanır. Paket, uygulamayı ve örnek görüntüyü içerir.

## Kolay kullanım (Linux - AppImage ve .deb)

Linux ortamında uygulamayı Python bağımlılığı olmadan doğrudan çalıştırmak veya sisteme kurmak için paketleme yapabilirsiniz:

### Paketleme (`paketle.sh`)
Linux terminalinde tek komutla hem `.deb` hem de `.AppImage` paketlerini üretmek için:

```bash
./paketle.sh
```

Bu betik otomatik olarak:
1. PyInstaller ile tek dosyalı çalıştırılabilir ikiliyi (`dist/A.Y.U.S`) üretir.
2. Debian/Ubuntu için doğrudan kurulabilir `dist/ayus_0.3.0_amd64.deb` paketini hazırlar.
3. Herhangi bir Linux dağıtımında taşınabilir çalışabilen `dist/A.Y.U.S-0.3.0-x86_64.AppImage` paketini oluşturur.

### AppImage ile Çalıştırma
Hiçbir kurulum yapmadan doğrudan çalıştırmak için:

```bash
chmod +x dist/A.Y.U.S-0.3.0-x86_64.AppImage
./dist/A.Y.U.S-0.3.0-x86_64.AppImage
```

Veya dosya yöneticisinden çift tıklayarak doğrudan başlatabilirsiniz.

### Debian / Ubuntu (.deb) Kurulumu
Uygulamayı sisteme, masaüstü uygulama menüsüne ve komut satırına entegre etmek için:

```bash
sudo apt install ./dist/ayus_0.3.0_amd64.deb
# veya
sudo dpkg -i ./dist/ayus_0.3.0_amd64.deb
```

Kurulduktan sonra:
- Uygulama menüsünden **A.Y.U.S.** simgesine tıklayarak görsel arayüzü açabilirsiniz.
- Terminalden doğrudan `ayus` komutuyla arayüzü veya `ayus --help` komutuyla CLI aracını çalıştırabilirsiniz.

Kaldırmak için:
```bash
sudo apt remove ayus
```

### Hızlı Başlatma Betikleri (Linux)
Geliştirme ortamında çalıştırmak için:
- `./kurulum.sh`: Sanal ortamı oluşturur ve geliştirme bağımlılıklarını kurar.
- `./baslat.sh`: Uygulamayı doğrudan başlatır.

GitHub Actions üzerindeki `Linux application` iş akışı ile `v*` etiketlerinde `.deb` ve `.AppImage` paketleri otomatik olarak derlenip Release varlıklarına eklenir.

## Çalıştırma

Parametre vermeden çalıştırmak görsel arayüzü açar:

```bash
python -m ayus
```

Varsayılan çalışma:

```bash
python A.Y.U.S..py --input depremfoto.png --output-dir outputs
```

Sunucu/CI gibi grafik arayüzü olmayan ortamlarda `--show` kullanmayın. Başlangıç ve bitiş hedefleri grid koordinatı olarak verilebilir:

```bash
python -m ayus --input depremfoto.png --start 2,3 --end 37,36 --no-save
```

Görsel arayüzü açıkça başlatmak için `--gui` kullanılabilir:

```bash
python -m ayus --gui
```

Varsayılan ve önerilen rota algoritması Dijkstra’dır. Seed’li ACO denemek için:

```bash
python -m ayus --algorithm aco --seed 42
```

Çıktılar `outputs/afet_rota_sonuclari.png` ve `outputs/afet_risk_haritasi.png` olarak yazılır. Rota uzunluğu görüntünün gerçek piksel geometrisine göre hesaplanır; “açıklık” değeri grid içindeki göreli clearance ölçüsüdür.

Görüntünün kuzey-yukarı olduğunu biliyorsanız rota çizgilerini WGS84 GeoJSON olarak da dışa aktarabilirsiniz:

```bash
python -m ayus --bounds 36.80,36.55,36.90,36.65
```

Bu seçenek `outputs/routes.geojson` üretir. Koordinat dönüşümü yalnızca verilen görüntü sınırları için doğrusal bir eşlemedir; gerçek ortofoto/uydu projeksiyonu, datum ve yol ağı doğrulaması sağlamaz.

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
