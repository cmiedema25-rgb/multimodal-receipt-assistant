#!/usr/bin/env python3
"""Generate synthetic receipt PNG/JPEG fixtures and aligned OCR JSON (no copyrighted assets)."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "fixtures" / "receipts"
OCR = ROOT / "fixtures" / "ocr"
FONT_REG = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
FONT_MONO = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


class Drawer:
    def __init__(self, img: Image.Image) -> None:
        self.img = img
        self.draw = ImageDraw.Draw(img)
        self.blocks: list[dict] = []

    def text(
        self,
        xy: tuple[int, int],
        content: str,
        font: ImageFont.ImageFont,
        fill: tuple[int, int, int],
        role: str,
    ) -> None:
        self.draw.text(xy, content, font=font, fill=fill)
        box = self.draw.textbbox(xy, content, font=font)
        self.blocks.append(
            {
                "text": content,
                "bbox": [box[0], box[1], box[2] - box[0], box[3] - box[1]],
                "role": role,
                "confidence": 0.99,
            }
        )


def save_ocr(name: str, payload: dict) -> None:
    OCR.mkdir(parents=True, exist_ok=True)
    (OCR / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def coffee() -> None:
    img = Image.new("RGB", (420, 780), (248, 244, 232))
    d = Drawer(img)
    bold, reg, mono = _font(FONT_BOLD, 22), _font(FONT_REG, 16), _font(FONT_MONO, 15)
    d.text((70, 28), "NORTHSTAR COFFEE", bold, (30, 30, 30), "vendor")
    d.text((120, 58), "Portland, OR", reg, (50, 50, 50), "address")
    d.text((95, 88), "2026-08-12  08:41", mono, (40, 40, 40), "date")
    y = 140
    items = [("Latte 12oz", 1, 5.25), ("Blueberry muffin", 1, 3.75), ("Drip coffee", 2, 5.50)]
    for desc, qty, amount in items:
        d.text((28, y), f"{qty}  {desc}", mono, (25, 25, 25), "line_item")
        d.text((310, y), f"{amount:6.2f}", mono, (25, 25, 25), "line_amount")
        y += 32
    y += 24
    d.text((28, y), "Subtotal", reg, (30, 30, 30), "subtotal_label")
    d.text((310, y), "14.50", mono, (30, 30, 30), "subtotal")
    y += 28
    d.text((28, y), "Tax", reg, (30, 30, 30), "tax_label")
    d.text((318, y), "1.31", mono, (30, 30, 30), "tax")
    y += 32
    d.text((28, y), "TOTAL", bold, (10, 10, 10), "total_label")
    d.text((300, y), "15.81", bold, (10, 10, 10), "total")
    y += 50
    d.text((28, y), "VISA ****4242", mono, (30, 30, 30), "payment")
    d.text((90, y + 50), "THANK YOU", reg, (80, 80, 80), "footer")
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    dest = RECEIPTS / "northstar_coffee.png"
    img.save(dest)
    save_ocr(
        "northstar_coffee",
        {
            "source": "fixtures/receipts/northstar_coffee.png",
            "vendor": "NORTHSTAR COFFEE",
            "date": "2026-08-12",
            "time": "08:41",
            "currency": "USD",
            "subtotal": 14.50,
            "tax": 1.31,
            "total": 15.81,
            "payment": "VISA ****4242",
            "doc_type": "receipt",
            "line_items": [
                {"desc": "Latte 12oz", "qty": 1, "amount": 5.25},
                {"desc": "Blueberry muffin", "qty": 1, "amount": 3.75},
                {"desc": "Drip coffee", "qty": 2, "amount": 5.50},
            ],
            "blocks": d.blocks,
        },
    )


def hardware() -> None:
    img = Image.new("RGB", (640, 820), (255, 255, 255))
    d = Drawer(img)
    d.draw.rectangle((0, 0, 640, 110), fill=(18, 52, 98))
    bold_w, bold, reg, mono = (
        _font(FONT_BOLD, 24),
        _font(FONT_BOLD, 18),
        _font(FONT_REG, 15),
        _font(FONT_MONO, 14),
    )
    d.text((24, 28), "HARBOR HARDWARE", bold_w, (255, 255, 255), "vendor")
    d.text((24, 64), "INVOICE  INV-4419", reg, (220, 230, 245), "doc_type")
    d.text((24, 130), "Date: 2026-07-03", reg, (20, 20, 20), "date")
    d.text((24, 158), "Bill to: Cascadia Logistics", reg, (20, 20, 20), "bill_to")
    y = 210
    items = [
        ("Safety gloves (pair)", 12, 47.40),
        ("LED shop lamp", 4, 89.60),
        ("Cable ties 8in (100)", 6, 23.70),
    ]
    for desc, qty, amount in items:
        d.text((28, y), f"{qty:>3}  {desc}", mono, (25, 25, 25), "line_item")
        d.text((500, y), f"{amount:7.2f}", mono, (25, 25, 25), "line_amount")
        y += 30
    y += 30
    d.text((400, y), "Subtotal", reg, (20, 20, 20), "subtotal_label")
    d.text((520, y), "160.70", mono, (20, 20, 20), "subtotal")
    y += 26
    d.text((400, y), "Tax 8.5%", reg, (20, 20, 20), "tax_label")
    d.text((528, y), "13.66", mono, (20, 20, 20), "tax")
    y += 30
    d.draw.rectangle((380, y - 6, 620, y + 32), fill=(18, 52, 98))
    d.text((400, y), "TOTAL", bold, (255, 255, 255), "total_label")
    d.text((520, y), "174.36", bold, (255, 255, 255), "total")
    y += 60
    d.text((24, y), "NET 15   ACH ****9012", mono, (30, 30, 30), "payment")
    dest = RECEIPTS / "harbor_hardware.png"
    img.save(dest)
    save_ocr(
        "harbor_hardware",
        {
            "source": "fixtures/receipts/harbor_hardware.png",
            "vendor": "HARBOR HARDWARE",
            "date": "2026-07-03",
            "currency": "USD",
            "subtotal": 160.70,
            "tax": 13.66,
            "total": 174.36,
            "payment": "ACH ****9012",
            "doc_type": "invoice",
            "line_items": [
                {"desc": "Safety gloves (pair)", "qty": 12, "amount": 47.40},
                {"desc": "LED shop lamp", "qty": 4, "amount": 89.60},
                {"desc": "Cable ties 8in (100)", "qty": 6, "amount": 23.70},
            ],
            "blocks": d.blocks,
        },
    )


def grill() -> None:
    img = Image.new("RGB", (400, 720), (252, 248, 236))
    d = Drawer(img)
    bold, reg, mono = _font(FONT_BOLD, 20), _font(FONT_REG, 15), _font(FONT_MONO, 14)
    d.text((90, 24), "MESA GRILL", bold, (70, 28, 16), "vendor")
    d.text((70, 54), "Table 7   2026-09-01", reg, (40, 40, 40), "date")
    y = 110
    items = [("Street tacos", 2, 18.00), ("Iced tea", 2, 5.00), ("Flan", 1, 7.50)]
    for desc, qty, amount in items:
        d.text((24, y), f"{qty} {desc}", mono, (25, 25, 25), "line_item")
        d.text((300, y), f"{amount:6.2f}", mono, (25, 25, 25), "line_amount")
        y += 30
    y += 20
    d.text((24, y), "Subtotal", reg, (30, 30, 30), "subtotal_label")
    d.text((300, y), "30.50", mono, (30, 30, 30), "subtotal")
    y += 26
    d.text((24, y), "Tax", reg, (30, 30, 30), "tax_label")
    d.text((308, y), "2.59", mono, (30, 30, 30), "tax")
    y += 28
    d.text((24, y), "TOTAL", bold, (70, 28, 16), "total_label")
    d.text((292, y), "33.09", bold, (70, 28, 16), "total")
    y += 48
    d.text((24, y), "MASTERCARD ****5510", mono, (30, 30, 30), "payment")
    dest = RECEIPTS / "mesa_grill.png"
    img.save(dest)
    save_ocr(
        "mesa_grill",
        {
            "source": "fixtures/receipts/mesa_grill.png",
            "vendor": "MESA GRILL",
            "date": "2026-09-01",
            "currency": "USD",
            "subtotal": 30.50,
            "tax": 2.59,
            "total": 33.09,
            "payment": "MASTERCARD ****5510",
            "doc_type": "receipt",
            "line_items": [
                {"desc": "Street tacos", "qty": 2, "amount": 18.00},
                {"desc": "Iced tea", "qty": 2, "amount": 5.00},
                {"desc": "Flan", "qty": 1, "amount": 7.50},
            ],
            "blocks": d.blocks,
        },
    )


def office() -> None:
    img = Image.new("RGB", (700, 900), (255, 255, 255))
    d = Drawer(img)
    d.draw.rectangle((0, 0, 700, 96), fill=(12, 90, 78))
    bold_w, bold, reg, mono = (
        _font(FONT_BOLD, 24),
        _font(FONT_BOLD, 18),
        _font(FONT_REG, 15),
        _font(FONT_MONO, 14),
    )
    d.text((28, 30), "MILLER OFFICE SUPPLY", bold_w, (255, 255, 255), "vendor")
    d.text((28, 64), "INVOICE  INV-2207", reg, (210, 240, 230), "doc_type")
    d.text((28, 120), "Date: 2026-06-18", reg, (20, 20, 20), "date")
    y = 180
    items = [
        ("Copy paper 10-ream", 8, 239.60),
        ("Toner cartridge BK", 3, 186.00),
        ("Shipping labels", 10, 84.50),
        ("Binder clips mixed", 5, 22.25),
    ]
    for desc, qty, amount in items:
        d.text((32, y), f"{qty:>3}  {desc}", mono, (25, 25, 25), "line_item")
        d.text((560, y), f"{amount:7.2f}", mono, (25, 25, 25), "line_amount")
        y += 28
    y += 36
    d.text((460, y), "Subtotal", reg, (20, 20, 20), "subtotal_label")
    d.text((580, y), "532.35", mono, (20, 20, 20), "subtotal")
    y += 26
    d.text((460, y), "Tax", reg, (20, 20, 20), "tax_label")
    d.text((588, y), "47.91", mono, (20, 20, 20), "tax")
    y += 30
    d.draw.rectangle((440, y - 6, 680, y + 32), fill=(12, 90, 78))
    d.text((460, y), "TOTAL", bold, (255, 255, 255), "total_label")
    d.text((572, y), "580.26", bold, (255, 255, 255), "total")
    y += 56
    d.text((28, y), "Card on file  AMEX ****3003", mono, (30, 30, 30), "payment")
    dest = RECEIPTS / "miller_office.png"
    img.save(dest)
    save_ocr(
        "miller_office",
        {
            "source": "fixtures/receipts/miller_office.png",
            "vendor": "MILLER OFFICE SUPPLY",
            "date": "2026-06-18",
            "currency": "USD",
            "subtotal": 532.35,
            "tax": 47.91,
            "total": 580.26,
            "payment": "AMEX ****3003",
            "doc_type": "invoice",
            "line_items": [
                {"desc": "Copy paper 10-ream", "qty": 8, "amount": 239.60},
                {"desc": "Toner cartridge BK", "qty": 3, "amount": 186.00},
                {"desc": "Shipping labels", "qty": 10, "amount": 84.50},
                {"desc": "Binder clips mixed", "qty": 5, "amount": 22.25},
            ],
            "blocks": d.blocks,
        },
    )


def gas() -> None:
    img = Image.new("RGB", (380, 640), (245, 245, 240))
    d = Drawer(img)
    bold, reg, mono = _font(FONT_BOLD, 20), _font(FONT_REG, 15), _font(FONT_MONO, 14)
    d.text((90, 24), "PINE GAS #18", bold, (20, 20, 20), "vendor")
    d.text((70, 56), "2026-08-28  16:04", reg, (40, 40, 40), "date")
    y = 120
    d.text((24, y), "1 Regular 12.480 GAL", mono, (25, 25, 25), "line_item")
    d.text((270, y), "43.55", mono, (25, 25, 25), "line_amount")
    y += 40
    d.text((24, y), "Subtotal", reg, (30, 30, 30), "subtotal_label")
    d.text((270, y), "43.55", mono, (30, 30, 30), "subtotal")
    y += 26
    d.text((24, y), "Tax", reg, (30, 30, 30), "tax_label")
    d.text((286, y), "0.00", mono, (30, 30, 30), "tax")
    y += 28
    d.text((24, y), "TOTAL", bold, (10, 10, 10), "total_label")
    d.text((262, y), "43.55", bold, (10, 10, 10), "total")
    y += 48
    d.text((24, y), "DEBIT ****1188", mono, (30, 30, 30), "payment")
    dest = RECEIPTS / "pine_gas.jpg"
    img.save(dest, format="JPEG", quality=92)
    save_ocr(
        "pine_gas",
        {
            "source": "fixtures/receipts/pine_gas.jpg",
            "vendor": "PINE GAS #18",
            "date": "2026-08-28",
            "time": "16:04",
            "currency": "USD",
            "subtotal": 43.55,
            "tax": 0.00,
            "total": 43.55,
            "payment": "DEBIT ****1188",
            "doc_type": "receipt",
            "line_items": [
                {"desc": "Regular 12.480 GAL", "qty": 12.48, "amount": 43.55, "unit": "GAL"}
            ],
            "blocks": d.blocks,
        },
    )


def write_cases() -> None:
    cases = [
        {
            "id": "coffee-vendor",
            "image": "fixtures/receipts/northstar_coffee.png",
            "ocr": "fixtures/ocr/northstar_coffee.json",
            "question": "What is the vendor name?",
            "expected": "NORTHSTAR COFFEE",
            "field": "vendor",
        },
        {
            "id": "coffee-total",
            "image": "fixtures/receipts/northstar_coffee.png",
            "ocr": "fixtures/ocr/northstar_coffee.json",
            "question": "What is the grand total?",
            "expected": "15.81",
            "field": "total",
        },
        {
            "id": "coffee-date",
            "image": "fixtures/receipts/northstar_coffee.png",
            "ocr": "fixtures/ocr/northstar_coffee.json",
            "question": "What date is on the receipt?",
            "expected": "2026-08-12",
            "field": "date",
        },
        {
            "id": "coffee-items",
            "image": "fixtures/receipts/northstar_coffee.png",
            "ocr": "fixtures/ocr/northstar_coffee.json",
            "question": "How many line items are listed?",
            "expected": "3",
            "field": "item_count",
        },
        {
            "id": "coffee-first",
            "image": "fixtures/receipts/northstar_coffee.png",
            "ocr": "fixtures/ocr/northstar_coffee.json",
            "question": "What is the first item they bought?",
            "expected": "Latte 12oz",
            "field": "first_item",
        },
        {
            "id": "coffee-layout",
            "image": "fixtures/receipts/northstar_coffee.png",
            "ocr": "fixtures/ocr/northstar_coffee.json",
            "question": "Is this a thermal receipt or an invoice layout?",
            "expected": "thermal_receipt",
            "field": "layout",
        },
        {
            "id": "hardware-vendor",
            "image": "fixtures/receipts/harbor_hardware.png",
            "ocr": "fixtures/ocr/harbor_hardware.json",
            "question": "Which company issued this document?",
            "expected": "HARBOR HARDWARE",
            "field": "vendor",
        },
        {
            "id": "hardware-total",
            "image": "fixtures/receipts/harbor_hardware.png",
            "ocr": "fixtures/ocr/harbor_hardware.json",
            "question": "What is the amount due / total?",
            "expected": "174.36",
            "field": "total",
        },
        {
            "id": "hardware-layout",
            "image": "fixtures/receipts/harbor_hardware.png",
            "ocr": "fixtures/ocr/harbor_hardware.json",
            "question": "What kind of document layout is this (invoice or thermal)?",
            "expected": "invoice",
            "field": "layout",
        },
        {
            "id": "hardware-payment",
            "image": "fixtures/receipts/harbor_hardware.png",
            "ocr": "fixtures/ocr/harbor_hardware.json",
            "question": "How was this paid?",
            "expected": "ACH ****9012",
            "field": "payment",
        },
        {
            "id": "grill-tax",
            "image": "fixtures/receipts/mesa_grill.png",
            "ocr": "fixtures/ocr/mesa_grill.json",
            "question": "What is the tax amount?",
            "expected": "2.59",
            "field": "tax",
        },
        {
            "id": "grill-payment",
            "image": "fixtures/receipts/mesa_grill.png",
            "ocr": "fixtures/ocr/mesa_grill.json",
            "question": "What payment card was used?",
            "expected": "MASTERCARD ****5510",
            "field": "payment",
        },
        {
            "id": "office-subtotal",
            "image": "fixtures/receipts/miller_office.png",
            "ocr": "fixtures/ocr/miller_office.json",
            "question": "What is the subtotal before tax?",
            "expected": "532.35",
            "field": "subtotal",
        },
        {
            "id": "office-items",
            "image": "fixtures/receipts/miller_office.png",
            "ocr": "fixtures/ocr/miller_office.json",
            "question": "How many line items are on the invoice?",
            "expected": "4",
            "field": "item_count",
        },
        {
            "id": "gas-vendor",
            "image": "fixtures/receipts/pine_gas.jpg",
            "ocr": "fixtures/ocr/pine_gas.json",
            "question": "What is the store / vendor name?",
            "expected": "PINE GAS #18",
            "field": "vendor",
        },
        {
            "id": "gas-total",
            "image": "fixtures/receipts/pine_gas.jpg",
            "ocr": "fixtures/ocr/pine_gas.json",
            "question": "What is the total amount?",
            "expected": "43.55",
            "field": "total",
        },
    ]
    dest = ROOT / "data" / "cases.jsonl"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("".join(json.dumps(c) + "\n" for c in cases), encoding="utf-8")


def main() -> None:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    OCR.mkdir(parents=True, exist_ok=True)
    coffee()
    hardware()
    grill()
    office()
    gas()
    write_cases()
    print(f"wrote fixtures under {RECEIPTS} and {OCR}")


if __name__ == "__main__":
    main()
