"""Command line interface for the Agent Zero OSINT helpers."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from agent_zero.intel.predict import classify_text
from agent_zero.intel.pipelines.osint import classify_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify OSINT-related text or URLs")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text snippet to classify")
    group.add_argument("--url", help="URL to fetch and classify")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--user", help="User initiating the classification")
    parser.add_argument("--justification", help="Business justification for the fetch")
    return parser


def format_output(result: Dict[str, Any], as_json: bool) -> str:
    if as_json:
        return json.dumps(result, indent=2)

    lines = [
        f"Label: {result.get('label')} ({result.get('label_name')})",
        f"Risk: {result.get('risk', 0.0):.3f}",
        "Probabilities: " + ", ".join(f"{p:.3f}" for p in result.get("probs", [])),
    ]
    source = result.get("source_url")
    if source:
        lines.append(f"Source: {source}")

    iocs = result.get("iocs") or {}
    if iocs:
        lines.append("IOCs:")
        for kind, values in sorted(iocs.items()):
            pretty = ", ".join(values) if values else "(none)"
            lines.append(f"  {kind}: {pretty}")
    else:
        lines.append("IOCs: (none)")
    return "\n".join(lines)


def main(args: list[str] | None = None) -> int:
    parser = build_parser()
    parsed = parser.parse_args(args=args)

    try:
        if parsed.text:
            result = classify_text(parsed.text)
        else:
            result = classify_url(
                parsed.url,
                user=parsed.user,
                justification=parsed.justification,
            )
    except Exception as exc:  # pragma: no cover - CLI entry point error path
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(format_output(result, parsed.json))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
