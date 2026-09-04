"""CLI: multimodal-receipt ask | benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from multimodal_receipt.benchmark import run_benchmark, write_report
from multimodal_receipt.pipeline import ask


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="multimodal-receipt")
    sub = parser.add_subparsers(dest="command", required=True)

    ask_p = sub.add_parser("ask", help="Answer a question about one receipt image")
    ask_p.add_argument("--image", required=True)
    ask_p.add_argument("--ocr", required=True)
    ask_p.add_argument("--question", required=True)

    bench = sub.add_parser("benchmark", help="Run authored cases and write a JSON report")
    bench.add_argument("--cases", default=str(_repo_root() / "data" / "cases.jsonl"))
    bench.add_argument("--report", default=str(_repo_root() / "evidence" / "benchmark-report.json"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "ask":
        result = ask(args.image, args.ocr, args.question)
        print(json.dumps(result.to_dict(), indent=2))
        return 0
    report = run_benchmark(args.cases, repo_root=_repo_root())
    dest = write_report(report, args.report)
    print(
        json.dumps(
            {
                "cases": report.cases,
                "correct": report.correct,
                "precision": report.precision,
                "passed": report.passed,
                "report": str(dest),
            },
            indent=2,
        )
    )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
