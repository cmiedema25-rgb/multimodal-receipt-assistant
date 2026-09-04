"""Typed records for the multimodal receipt pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class BoundingBox:
    x: int
    y: int
    w: int
    h: int

    @property
    def as_tuple(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)


@dataclass(frozen=True)
class TextBlock:
    text: str
    bbox: BoundingBox
    role: str
    confidence: float = 1.0


@dataclass(frozen=True)
class LineItem:
    desc: str
    qty: float
    amount: float
    unit: str | None = None


@dataclass
class OcrDocument:
    source: str
    vendor: str
    date: str
    currency: str
    subtotal: float
    tax: float
    total: float
    payment: str
    doc_type: str
    line_items: list[LineItem]
    blocks: list[TextBlock]
    time: str | None = None
    notes: str | None = None

    def field_map(self) -> dict[str, str]:
        return {
            "vendor": self.vendor,
            "date": self.date,
            "time": self.time or "",
            "currency": self.currency,
            "subtotal": f"{self.subtotal:.2f}",
            "tax": f"{self.tax:.2f}",
            "total": f"{self.total:.2f}",
            "payment": self.payment,
            "doc_type": self.doc_type,
            "item_count": str(len(self.line_items)),
        }


@dataclass(frozen=True)
class RegionStats:
    name: str
    bbox: tuple[int, int, int, int]
    mean_brightness: float
    contrast: float
    mean_r: float
    mean_g: float
    mean_b: float
    edge_density: float


@dataclass
class ImageFeatures:
    path: str
    width: int
    height: int
    aspect_ratio: float
    mean_brightness: float
    contrast: float
    is_grayscale_like: bool
    likely_thermal: bool
    likely_invoice: bool
    header_is_dark: bool
    regions: dict[str, RegionStats] = field(default_factory=dict)


@dataclass
class CandidateAnswer:
    field: str
    text: str
    score: float
    reasons: list[str]


@dataclass
class AskResult:
    question: str
    answer: str
    field: str
    score: float
    reasons: list[str]
    image: str
    ocr_source: str
    layout: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CaseResult:
    case_id: str
    question: str
    expected: str
    predicted: str
    field: str
    score: float
    correct: bool
    image: str


@dataclass
class BenchmarkReport:
    cases: int
    correct: int
    precision: float
    by_field: dict[str, dict[str, float]]
    passed: bool
    results: list[CaseResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "cases": self.cases,
            "correct": self.correct,
            "precision": self.precision,
            "by_field": self.by_field,
            "passed": self.passed,
            "results": [asdict(r) for r in self.results],
        }
