"""Authored-case benchmark that retains precision metrics."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from multimodal_receipt.models import BenchmarkReport, CaseResult
from multimodal_receipt.pipeline import ask


def load_cases(path: str | Path) -> list[dict]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _norm(value: str) -> str:
    return " ".join(value.strip().lower().split())


def run_benchmark(cases_path: str | Path, repo_root: str | Path | None = None) -> BenchmarkReport:
    root = Path(repo_root) if repo_root else Path(cases_path).resolve().parents[1]
    results: list[CaseResult] = []
    by_field: dict[str, list[bool]] = defaultdict(list)
    for row in load_cases(cases_path):
        image = root / row["image"]
        ocr = root / row["ocr"]
        got = ask(image, ocr, row["question"])
        correct = _norm(got.answer) == _norm(str(row["expected"]))
        results.append(
            CaseResult(
                case_id=str(row["id"]),
                question=row["question"],
                expected=str(row["expected"]),
                predicted=got.answer,
                field=got.field,
                score=got.score,
                correct=correct,
                image=row["image"],
            )
        )
        by_field[got.field].append(correct)

    correct = sum(1 for r in results if r.correct)
    n = len(results)
    precision = round(correct / n, 4) if n else 0.0
    field_stats = {
        field: {
            "n": float(len(vals)),
            "correct": float(sum(vals)),
            "precision": round(sum(vals) / len(vals), 4) if vals else 0.0,
        }
        for field, vals in sorted(by_field.items())
    }
    return BenchmarkReport(
        cases=n,
        correct=correct,
        precision=precision,
        by_field=field_stats,
        passed=n > 0 and correct == n,
        results=results,
    )


def write_report(report: BenchmarkReport, dest: str | Path) -> Path:
    path = Path(dest)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path
