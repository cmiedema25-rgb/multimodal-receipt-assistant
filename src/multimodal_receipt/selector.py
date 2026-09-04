"""Keyword-routed, scored answer selector over fused image + OCR evidence."""

from __future__ import annotations

import re

from multimodal_receipt.fusion import FusionContext
from multimodal_receipt.models import AskResult, CandidateAnswer
from multimodal_receipt.ocr_layer import first_item_desc

INTENT_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("vendor", ("vendor", "merchant", "store", "who sold", "company", "who issued")),
    ("time", ("what time", "time of day")),
    ("date", ("date", "when was", "what day")),
    ("subtotal", ("subtotal", "sub-total", "before tax")),
    ("tax", ("sales tax", "vat", " tax", "tax ", "tax?")),
    ("total", ("grand total", "amount due", "how much in all", " total", "total?", "total ")),
    ("payment", ("payment", "paid with", "paid", "card", "how did they pay")),
    ("item_count", ("how many", "number of items", "line items", "item count")),
    ("first_item", ("first item", "first line", "what did they buy first")),
    (
        "layout",
        (
            "thermal",
            "invoice or receipt",
            "document type",
            "layout",
            "what kind of document",
        ),
    ),
]


def _needle_match(needle: str, question: str) -> bool:
    """Prefer whole-word matches so 'total' does not hit inside 'subtotal'."""
    if " " in needle or any(ch in needle for ch in "?."):
        return needle in question
    return re.search(rf"(?<![a-z]){re.escape(needle)}(?![a-z])", question) is not None


def classify_intent(question: str) -> str:
    q = question.lower()
    for field, needles in INTENT_PATTERNS:
        if any(_needle_match(n, q) for n in needles):
            return field
    return "vendor"


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _candidates(ctx: FusionContext) -> list[CandidateAnswer]:
    ocr = ctx.ocr
    layout_answer = "thermal_receipt" if ctx.layout == "thermal_receipt" else "invoice"
    mapping = {
        "vendor": ocr.vendor,
        "date": ocr.date,
        "time": ocr.time or "",
        "total": f"{ocr.total:.2f}",
        "tax": f"{ocr.tax:.2f}",
        "subtotal": f"{ocr.subtotal:.2f}",
        "payment": ocr.payment,
        "item_count": str(len(ocr.line_items)),
        "first_item": first_item_desc(ocr),
        "layout": layout_answer,
        "doc_type": ocr.doc_type,
    }
    out: list[CandidateAnswer] = []
    for field, text in mapping.items():
        if text == "":
            continue
        score = 0.55
        reasons = [f"ocr field {field}={text}"]
        bonus, reason = ctx.region_support(field if field != "doc_type" else "vendor")
        score += bonus
        reasons.append(reason)
        if field == "layout":
            ocr_agrees = (ocr.doc_type == "receipt" and layout_answer == "thermal_receipt") or (
                ocr.doc_type == "invoice" and layout_answer == "invoice"
            )
            if ocr_agrees:
                score += 0.15
                reasons.append(f"ocr doc_type={ocr.doc_type} agrees with image layout")
        out.append(
            CandidateAnswer(
                field=field,
                text=str(text),
                score=round(min(score, 0.99), 3),
                reasons=reasons,
            )
        )
    return out


def select_answer(ctx: FusionContext, question: str) -> AskResult:
    intent = classify_intent(question)
    ranked = _candidates(ctx)
    intended = [c for c in ranked if c.field == intent]
    chosen = intended[0] if intended else max(ranked, key=lambda c: c.score)
    return AskResult(
        question=_normalize(question),
        answer=chosen.text,
        field=chosen.field,
        score=chosen.score,
        reasons=chosen.reasons,
        image=ctx.image.path,
        ocr_source=ctx.ocr.source,
        layout=ctx.layout,
    )
