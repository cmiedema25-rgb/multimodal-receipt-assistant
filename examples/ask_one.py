"""Ask one authored question about the coffee receipt."""

from pathlib import Path

from multimodal_receipt.pipeline import ask

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    result = ask(
        ROOT / "fixtures/receipts/northstar_coffee.png",
        ROOT / "fixtures/ocr/northstar_coffee.json",
        "What is the grand total?",
    )
    print(f"{result.answer} (score={result.score}, layout={result.layout})")


if __name__ == "__main__":
    main()
