"""Small command-line helpers for intel operations."""
from __future__ import annotations

import argparse
import json
from typing import Sequence

from .store import list_findings


def cmd_top(args: argparse.Namespace) -> None:
    rows = list_findings(limit=args.limit)
    for row in rows:
        print(f"{row['risk']:.2f}\t{row['source_url']}")
        print(json.dumps(row["iocs"], indent=2))
        print("-")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Intel helper CLI")
    sub = parser.add_subparsers(dest="command")

    top = sub.add_parser("top", help="Show the highest risk findings")
    top.add_argument("--limit", type=int, default=10, help="Number of findings to show")
    top.set_defaults(func=cmd_top)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
