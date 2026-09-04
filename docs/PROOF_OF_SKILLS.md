# Proof of Skills

## Multimodal AI

- `src/multimodal_receipt/image_features.py` extracts size, brightness, contrast,
  grayscale-likeness, and region crops (header/body/footer/total band).
- `src/multimodal_receipt/fusion.py` merges image features with the OCR document.
- Layout label (`thermal_receipt` vs `invoice`) is driven by aspect ratio and
  header darkness — then fused with OCR `doc_type`.

## Generative AI / Document AI adjacency

- `src/multimodal_receipt/selector.py` answers natural-language questions about
  vendor, totals, tax, payment, item count, and layout.
- Fixtures under `fixtures/receipts/` are synthetic Pillow drawings; OCR JSON
  under `fixtures/ocr/` is the text layer a Document AI stack would produce.

## Python

- Typed dataclasses in `models.py`, CLI entry point, pytest suite, Ruff, Actions.

## Prompt Engineering (light)

- Intent classification maps free-form questions onto field keys with
  whole-word matching so `subtotal` does not collide with `total`.

## Reproduce

```bash
python -m pip install -e '.[dev]'
make verify
```

Expected: 16/16 cases, precision 1.0, Ruff clean, ≥85% coverage.
