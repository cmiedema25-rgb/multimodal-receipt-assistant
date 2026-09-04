from pathlib import Path

from multimodal_receipt.image_features import extract_features, layout_label

ROOT = Path(__file__).resolve().parents[1]


def test_coffee_is_thermal_like() -> None:
    feats = extract_features(ROOT / "fixtures/receipts/northstar_coffee.png")
    assert feats.width == 420
    assert feats.height == 780
    assert feats.aspect_ratio < 0.72
    assert feats.mean_brightness > 180
    assert layout_label(feats) == "thermal_receipt"


def test_hardware_is_invoice_like() -> None:
    feats = extract_features(ROOT / "fixtures/receipts/harbor_hardware.png")
    assert feats.header_is_dark
    assert layout_label(feats) == "invoice"
    assert "header" in feats.regions
    assert "total_band" in feats.regions


def test_jpeg_gas_receipt_loads() -> None:
    feats = extract_features(ROOT / "fixtures/receipts/pine_gas.jpg")
    assert feats.width == 380
    assert feats.regions["body"].edge_density >= 0
