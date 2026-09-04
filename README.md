# Multimodal Receipt Assistant

[![CI](https://github.com/cmiedema25-rgb/multimodal-receipt-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/cmiedema25-rgb/multimodal-receipt-assistant/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Deterministic multimodal Q&A over **synthetic** receipt/invoice images. The
pipeline fuses (a) Pillow image features, (b) an authored OCR/text layer, and
(c) a scored answer selector. Offline CI — no API keys.

## Reviewer proof in 60 seconds

| Verifiable outcome | Retained evidence | Reproduce |
| --- | --- | --- |
| 16/16 authored cases correct (precision 1.0) | [`evidence/benchmark-report.json`](evidence/benchmark-report.json) | `make benchmark` |
| Layout classifier separates thermal vs invoice | same report `by_field.layout` | `make benchmark` |
| Tests + Ruff green | [`evidence/VERIFICATION.md`](evidence/VERIFICATION.md) | `make verify` |

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e '.[dev]'
make verify
```

## Problem → measurable demo

AP and expense teams re-key totals, vendors, and payment method from receipt
photos. This lab shows a **inspectable fusion path** on five synthetic fixtures
(PNG/JPEG drawn with Pillow — no copyrighted assets) and sixteen authored
questions with expected answer keys.

## Skills demonstrated

- **Multimodal AI:** image region stats + text-layer fusion into one answer.
- **Generative AI / Document AI adjacency:** receipt/invoice field answering
  without a live VLM.
- **Python:** typed pipeline, CLI, pytest, Ruff, GitHub Actions.
- **Prompt Engineering (light):** intent routing over natural-language questions.

## Architecture

```text
image PNG/JPEG ──► Pillow features (size, brightness, crops)
                         │
OCR JSON fixture ───────► fusion context ──► scored selector ──► answer
```

## CLI

```bash
multimodal-receipt ask \
  --image fixtures/receipts/northstar_coffee.png \
  --ocr fixtures/ocr/northstar_coffee.json \
  --question "What is the grand total?"

multimodal-receipt benchmark --report evidence/benchmark-report.json
```

## Limitations (honest)

- OCR is an authored fixture layer, not live Tesseract/cloud OCR.
- The answer selector is deterministic keyword + region scoring, not a trained VLM.
- Precision 1.0 is on sixteen curated cases — not a production claim or ROI.
- See [`docs/PROOF_OF_SKILLS.md`](docs/PROOF_OF_SKILLS.md) and [`VIDEO_SCRIPT.md`](VIDEO_SCRIPT.md).
