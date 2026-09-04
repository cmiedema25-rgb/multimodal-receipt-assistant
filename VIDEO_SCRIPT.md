# Multimodal Receipt Assistant — Loom script (~2 minutes)

**Repo:** https://github.com/cmiedema25-rgb/multimodal-receipt-assistant  
**Suggested title:** Multimodal Receipt Assistant — 16/16 offline Q&A (synthetic)

---

## Hook (0:00–0:20)
Expense and AP teams still re-key vendor, tax, and total from receipt photos.
I built an offline multimodal pipeline that answers questions by fusing image
features with an OCR text layer — no API key.

## What you built (0:20–0:35)
Pillow extracts brightness, contrast, and region crops. Authored OCR JSON
supplies fields. A scored selector picks the answer. Five synthetic receipts
(PNG/JPEG) — no copyrighted assets.

## Live demo beats (0:35–1:40)

**Install + ask:**
```bash
cd multimodal-receipt-assistant
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"
multimodal-receipt ask \
  --image fixtures/receipts/northstar_coffee.png \
  --ocr fixtures/ocr/northstar_coffee.json \
  --question "What is the grand total?"
```

**On-screen:** answer `15.81`, layout `thermal_receipt`.

**Benchmark:**
```bash
multimodal-receipt benchmark --report evidence/benchmark-report.json
```

**Demo numbers (synthetic / authored — honest):**
- Cases: **16**
- Correct: **16/16**
- Precision: **1.0000**
- Layout field: thermal vs invoice separation retained in the report

**ROI framing:** On these 16 fixtures, every vendor/total/tax/layout question
is answered without re-keying — hours saved = fewer manual spot-checks on the
same authored set each change. Not customer ROI.

**Verify:**
```bash
make verify
```

## Close (1:40–2:05)
Reproduce with `make verify`.  
GitHub: https://github.com/cmiedema25-rgb/multimodal-receipt-assistant  
Results prove the fusion pipeline on checked-in synthetic fixtures — not a
production VLM or live OCR deployment.
