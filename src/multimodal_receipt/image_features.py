"""Image-derived features via Pillow: size, brightness, contrast, region crops."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter, ImageStat

from multimodal_receipt.models import ImageFeatures, RegionStats

REGION_FRACTIONS = {
    "header": (0.00, 0.00, 1.00, 0.18),
    "vendor_band": (0.00, 0.00, 0.70, 0.22),
    "body": (0.00, 0.18, 1.00, 0.52),
    "footer": (0.00, 0.70, 1.00, 0.30),
    "total_band": (0.40, 0.72, 0.60, 0.28),
}


def _crop_box(
    width: int, height: int, frac: tuple[float, float, float, float]
) -> tuple[int, int, int, int]:
    x, y, w, h = frac
    left = int(width * x)
    top = int(height * y)
    right = min(width, left + int(width * w))
    bottom = min(height, top + int(height * h))
    return left, top, right, bottom


def _stats(region: Image.Image, name: str, box: tuple[int, int, int, int]) -> RegionStats:
    rgb = region.convert("RGB")
    gray = region.convert("L")
    st = ImageStat.Stat(rgb)
    gst = ImageStat.Stat(gray)
    mean_r, mean_g, mean_b = (float(v) for v in st.mean)
    brightness = float(gst.mean[0])
    contrast = float(gst.stddev[0]) if gst.stddev else 0.0
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_density = float(ImageStat.Stat(edges).mean[0]) / 255.0
    return RegionStats(
        name=name,
        bbox=box,
        mean_brightness=round(brightness, 3),
        contrast=round(contrast, 3),
        mean_r=round(mean_r, 3),
        mean_g=round(mean_g, 3),
        mean_b=round(mean_b, 3),
        edge_density=round(edge_density, 4),
    )


def extract_features(image_path: str | Path) -> ImageFeatures:
    path = Path(image_path)
    with Image.open(path) as img:
        img = img.convert("RGB")
        width, height = img.size
        full = _stats(img, "full", (0, 0, width, height))
        regions: dict[str, RegionStats] = {}
        for name, frac in REGION_FRACTIONS.items():
            box = _crop_box(width, height, frac)
            crop = img.crop(box)
            regions[name] = _stats(crop, name, box)

        grayscale_delta = max(
            abs(full.mean_r - full.mean_g),
            abs(full.mean_g - full.mean_b),
            abs(full.mean_r - full.mean_b),
        )
        is_grayscale_like = grayscale_delta < 18.0
        aspect = width / height if height else 0.0
        # Tall bright slips (coffee/gas/grill) read as thermal POS receipts.
        likely_thermal = aspect < 0.70 and full.mean_brightness > 200
        header = regions["header"]
        header_is_dark = header.mean_brightness < 160
        # Wider pages or darker branded headers read as invoices.
        likely_invoice = (aspect >= 0.70 or header_is_dark) and not likely_thermal

        return ImageFeatures(
            path=str(path),
            width=width,
            height=height,
            aspect_ratio=round(aspect, 4),
            mean_brightness=full.mean_brightness,
            contrast=full.contrast,
            is_grayscale_like=is_grayscale_like,
            likely_thermal=likely_thermal,
            likely_invoice=likely_invoice,
            header_is_dark=header_is_dark,
            regions=regions,
        )


def layout_label(features: ImageFeatures) -> str:
    if features.likely_thermal:
        return "thermal_receipt"
    if features.likely_invoice:
        return "invoice"
    return "unknown"
