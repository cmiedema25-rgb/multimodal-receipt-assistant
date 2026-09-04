from pathlib import Path

from multimodal_receipt.ocr_layer import load_ocr
from multimodal_receipt.pipeline import ask
from multimodal_receipt.selector import classify_intent

ROOT = Path(__file__).resolve().parents[1]


def test_ocr_loads_line_items() -> None:
    doc = load_ocr(ROOT / "fixtures/ocr/northstar_coffee.json")
    assert doc.vendor == "NORTHSTAR COFFEE"
    assert len(doc.line_items) == 3
    assert doc.total == 15.81
    assert doc.blocks


def test_ask_vendor_and_total() -> None:
    image = ROOT / "fixtures/receipts/northstar_coffee.png"
    ocr = ROOT / "fixtures/ocr/northstar_coffee.json"
    vendor = ask(image, ocr, "What is the vendor name?")
    assert vendor.answer == "NORTHSTAR COFFEE"
    assert vendor.score > 0.5
    total = ask(image, ocr, "What is the grand total?")
    assert total.answer == "15.81"


def test_intent_routing() -> None:
    assert classify_intent("How was this paid?") == "payment"
    assert classify_intent("Is this a thermal receipt or an invoice layout?") == "layout"


def test_invoice_layout_question() -> None:
    result = ask(
        ROOT / "fixtures/receipts/harbor_hardware.png",
        ROOT / "fixtures/ocr/harbor_hardware.json",
        "What kind of document layout is this (invoice or thermal)?",
    )
    assert result.answer == "invoice"
