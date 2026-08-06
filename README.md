# A.Y.U.S.

A.Y.U.S. is a prototype developed by the EYBAL team during the TUA Astro Hackathon. It uses an input image to build a risk map and visualise candidate evacuation routes.

## Setup

```bash
git clone https://github.com/beratbesli/A.Y.U.S..git
cd A.Y.U.S.
python -m venv .venv
```

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

`depremfoto.png` is the default input image and is tracked in the repository.

## Run

```bash
python A.Y.U.S..py
```

The program can create `afet_rota_sonuclari.png` and `afet_risk_haritasi.png`. These generated outputs are ignored by Git. Use `kalibrasyon.py` to interactively tune image-processing thresholds.

## Safety notice

This is a hackathon prototype that processes a static image. It is not validated for emergency response, navigation, medical, safety-critical or real-world disaster-management decisions. Always use authorised emergency services and verified operational data.

## License

Released under the [MIT License](LICENSE).
