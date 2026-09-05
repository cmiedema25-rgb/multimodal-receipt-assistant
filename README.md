# Multimodal Receipt Assistant

[![CI](https://github.com/cmiedema25-rgb/multimodal-receipt-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/cmiedema25-rgb/multimodal-receipt-assistant/actions/workflows/ci.yml)

Answer questions over receipt/invoice images by fusing Pillow image features with an OCR text layer and a scored answer selector. Offline and deterministic — no API keys.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e '.[dev]'
make verify
```

## Usage

```bash
multimodal-receipt ask \
  --image fixtures/receipts/northstar_coffee.png \
  --ocr fixtures/ocr/northstar_coffee.json \
  --question "What is the grand total?"

multimodal-receipt benchmark --report evidence/benchmark-report.json
```

## Notes

OCR layers are authored fixtures (not live Tesseract). Selector is keyword/region scoring, not a trained VLM. Fixtures are synthetic PNGs drawn with Pillow.

## License

MIT
