import json
from pathlib import Path

from multimodal_receipt.benchmark import run_benchmark, write_report
from multimodal_receipt.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_authored_benchmark_is_perfect() -> None:
    report = run_benchmark(ROOT / "data/cases.jsonl", repo_root=ROOT)
    misses = [r.case_id for r in report.results if not r.correct]
    assert misses == []
    assert report.cases == 16
    assert report.precision == 1.0
    assert report.passed


def test_write_report(tmp_path: Path) -> None:
    report = run_benchmark(ROOT / "data/cases.jsonl", repo_root=ROOT)
    dest = write_report(report, tmp_path / "benchmark-report.json")
    payload = json.loads(dest.read_text(encoding="utf-8"))
    assert payload["correct"] == 16


def test_cli_ask(capsys) -> None:
    image = str(ROOT / "fixtures/receipts/mesa_grill.png")
    ocr = str(ROOT / "fixtures/ocr/mesa_grill.json")
    code = main(["ask", "--image", image, "--ocr", ocr, "--question", "What is the tax amount?"])
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["answer"] == "2.59"
