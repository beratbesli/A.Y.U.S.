# A.Y.U.S.

A.Y.U.S., EYBAL ekibinin TUA Astro Hackathon kapsamında geliştirdiği bir prototiptir. Bir girdi görselini işleyerek risk haritası oluşturur ve olası tahliye rotalarını görselleştirir.

## Kurulum

```bash
git clone https://github.com/beratbesli/A.Y.U.S..git
cd A.Y.U.S.
python -m venv .venv
```

Sanal ortamı etkinleştirdikten sonra bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

`depremfoto.png` varsayılan girdi görselidir ve depoda takip edilir.

## Çalıştırma

```bash
python A.Y.U.S..py
```

Program `afet_rota_sonuclari.png` ve `afet_risk_haritasi.png` dosyalarını oluşturabilir. Bu üretilen çıktılar Git tarafından yok sayılır. Görüntü işleme eşiklerini etkileşimli olarak ayarlamak için `kalibrasyon.py` dosyasını kullanabilirsiniz.

## Güvenlik notu

Bu proje statik bir görseli işleyen hackathon prototipidir. Acil müdahale, navigasyon, tıbbi kullanım, güvenlik açısından kritik senaryolar veya gerçek afet yönetimi kararları için doğrulanmış değildir. Her zaman yetkili acil durum hizmetlerini ve doğrulanmış operasyonel verileri kullanın.

## Lisans

[MIT Lisansı](LICENSE) ile sunulmaktadır.
