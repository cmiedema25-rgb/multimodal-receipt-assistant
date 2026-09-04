"""Public ask() helper used by the CLI and examples."""

from __future__ import annotations

from pathlib import Path

from multimodal_receipt.fusion import fuse
from multimodal_receipt.models import AskResult
from multimodal_receipt.selector import select_answer


def ask(image: str | Path, ocr: str | Path, question: str) -> AskResult:
    ctx = fuse(image, ocr)
    return select_answer(ctx, question)
