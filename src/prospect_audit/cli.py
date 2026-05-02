"""Offline command-line interface for inspecting supplied evidence."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from .line_type import classify_provider_payload
from .site_health import analyse_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prospect-audit")
    commands = parser.add_subparsers(dest="command", required=True)

    html = commands.add_parser("html", help="Inspect a saved HTML response without network access")
    html.add_argument("input", type=Path)
    html.add_argument("--url", default="https://example.test/")
    html.add_argument("--status", type=int, default=200)
    html.add_argument("--elapsed-ms", type=int, default=0)

    line = commands.add_parser("line", help="Classify a supplied provider-response fixture")
    line.add_argument("number", help="An E.164 phone number")
    line.add_argument("payload", type=Path, help="A local JSON response fixture")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "html":
        body = args.input.read_text(encoding="utf-8", errors="replace")
        result = analyse_html(
            args.url,
            args.url,
            args.status,
            body,
            body_bytes=len(body.encode("utf-8")),
            elapsed_ms=args.elapsed_ms,
        )
    else:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
        result = classify_provider_payload(args.number, payload)
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0
