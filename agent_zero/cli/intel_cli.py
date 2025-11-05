"""Command line interface for the Agent Zero OSINT helpers."""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from agent_zero.intel.predict import classify_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify OSINT-related text")
    parser.add_argument("--text", required=True, help="Text snippet to classify")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of human readable text",
    )
    return parser


def format_output(result: Dict[str, Any], as_json: bool) -> str:
    if as_json:
        return json.dumps(result, indent=2)

    keywords = ", ".join(result.get("keywords", [])) or "(none)"
    return (
        f"Label: {result.get('label')}\n"
        f"Confidence: {result.get('confidence'):.2f}\n"
        f"Keywords: {keywords}"
    )


def main(args: list[str] | None = None) -> int:
    parser = build_parser()
    parsed = parser.parse_args(args=args)
    result = classify_text(parsed.text)
    print(format_output(result, parsed.json))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
