"""Load authored OCR/text-layer fixtures aligned to receipt images."""

from __future__ import annotations

import json
from pathlib import Path

from multimodal_receipt.models import BoundingBox, LineItem, OcrDocument, TextBlock


def load_ocr(path: str | Path) -> OcrDocument:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    items = [
        LineItem(
            desc=str(item["desc"]),
            qty=float(item["qty"]),
            amount=float(item["amount"]),
            unit=item.get("unit"),
        )
        for item in raw.get("line_items", [])
    ]
    blocks = [
        TextBlock(
            text=str(block["text"]),
            bbox=BoundingBox(
                x=int(block["bbox"][0]),
                y=int(block["bbox"][1]),
                w=int(block["bbox"][2]),
                h=int(block["bbox"][3]),
            ),
            role=str(block.get("role", "text")),
            confidence=float(block.get("confidence", 1.0)),
        )
        for block in raw.get("blocks", [])
    ]
    return OcrDocument(
        source=str(raw["source"]),
        vendor=str(raw["vendor"]),
        date=str(raw["date"]),
        currency=str(raw.get("currency", "USD")),
        subtotal=float(raw["subtotal"]),
        tax=float(raw["tax"]),
        total=float(raw["total"]),
        payment=str(raw["payment"]),
        doc_type=str(raw["doc_type"]),
        line_items=items,
        blocks=blocks,
        time=raw.get("time"),
        notes=raw.get("notes"),
    )


def first_item_desc(doc: OcrDocument) -> str:
    if not doc.line_items:
        return ""
    return doc.line_items[0].desc
