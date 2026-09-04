"""Fuse image features with the OCR/text layer into a scoring context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from multimodal_receipt.image_features import extract_features, layout_label
from multimodal_receipt.models import ImageFeatures, OcrDocument
from multimodal_receipt.ocr_layer import load_ocr


@dataclass
class FusionContext:
    image: ImageFeatures
    ocr: OcrDocument
    layout: str

    def region_support(self, role: str) -> tuple[float, str]:
        """Return a bonus and reason if the image region agrees with a field role."""
        regions = self.image.regions
        if role in {"vendor", "doc_type"}:
            band = regions.get("header") or regions.get("vendor_band")
            if band and band.edge_density > 0.04:
                return 0.12, f"header/vendor region edge_density={band.edge_density}"
        if role in {"total", "tax", "subtotal", "payment"}:
            band = regions.get("total_band") or regions.get("footer")
            if band and band.contrast > 15:
                return 0.12, f"footer/total region contrast={band.contrast}"
        if role in {"item_count", "first_item"}:
            band = regions.get("body")
            if band and band.edge_density > 0.03:
                return 0.08, f"body region edge_density={band.edge_density}"
        if role == "layout":
            return 0.20, f"image layout classifier={self.layout}"
        return 0.0, "no matching region bonus"


def fuse(image_path: str | Path, ocr_path: str | Path) -> FusionContext:
    features = extract_features(image_path)
    ocr = load_ocr(ocr_path)
    return FusionContext(image=features, ocr=ocr, layout=layout_label(features))
