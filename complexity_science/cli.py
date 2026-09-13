"""Command-line interface: ``python -m complexity_science run ...``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from complexity_science.version import __version__
from complexity_science.biologics.catalog import load_catalog
from complexity_science.dynamics.archetypes import list_archetypes
from complexity_science.honesty import DISCLAIMER_SHORT
from complexity_science.integration.confluence_adapter import (
    EXAMPLE_REQUEST,
    SCHEMA_ID,
    execute_request,
)
from complexity_science.nstg.retriever import NstgRetriever
from complexity_science.pipeline import run_pipeline
from complexity_science.reporting.report import write_report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="complexity_science",
        description=(
            "NSTG-guided in-silico complexity science pipeline. "
            "Research software only — not a medical device."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="run retrieval + dynamics + constrained search")
    run.add_argument(
        "--archetype",
        default="exhausted_high_burden",
        help="computational archetype id",
    )
    run.add_argument(
        "--conditions",
        default="oncology_supportive,malaria,anaemia",
        help="comma-separated research-index queries",
    )
    run.add_argument("--horizon", type=float, default=42.0, help="days")
    run.add_argument("--max-candidates", type=int, default=24)
    run.add_argument(
        "--no-combinations",
        action="store_true",
        help="search single classes only",
    )
    run.add_argument(
        "--out",
        default="reports/pathway_report.json",
        help="JSON path (Markdown written alongside)",
    )
    run.add_argument("--json-only", action="store_true")

    retrieve = sub.add_parser("retrieve", help="query the NSTG research index")
    retrieve.add_argument("--condition", required=True, help="id, name, or alias")

    sub.add_parser("list-archetypes", help="list computational basins")
    sub.add_parser("list-effectors", help="list class-level biologic caricatures")
    sub.add_parser("show-disclaimer", help="print the short disclaimer")
    sub.add_parser("show-confluence-contract", help="print the Confluence JSON seam")

    bridge = sub.add_parser(
        "confluence-bridge",
        help="execute a ConfluenceRequest JSON file (no Confluence import)",
    )
    bridge.add_argument("--request", required=True, help="path to request JSON")
    bridge.add_argument("--out", default="reports/confluence_response.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.cmd == "show-disclaimer":
        print(DISCLAIMER_SHORT)
        return 0
    if args.cmd == "list-archetypes":
        for item in list_archetypes():
            print(f"{item.id:28}  {item.name}")
        return 0
    if args.cmd == "list-effectors":
        for item in load_catalog():
            print(f"{item.id:24}  {item.class_label:14}  {item.name}")
        return 0
    if args.cmd == "retrieve":
        result = NstgRetriever().retrieve(args.condition)
        print(json.dumps(result.to_dict(), indent=2))
        return 0
    if args.cmd == "show-confluence-contract":
        print(
            json.dumps(
                {
                    "schema": SCHEMA_ID,
                    "example_request": EXAMPLE_REQUEST,
                    "notes": (
                        "Inputs/outputs only. See "
                        "complexity_science/integration/confluence_adapter.py"
                    ),
                },
                indent=2,
            )
        )
        return 0
    if args.cmd == "confluence-bridge":
        raw = json.loads(Path(args.request).read_text(encoding="utf-8"))
        payload = execute_request(raw)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(out)
        return 0 if payload.get("status") == "ok" else 2
    if args.cmd == "run":
        result = run_pipeline(
            archetype_id=args.archetype,
            conditions=args.conditions,
            horizon_days=args.horizon,
            allow_combinations=not args.no_combinations,
            max_candidates=args.max_candidates,
        )
        written = write_report(
            result,
            args.out,
            also_markdown=not args.json_only,
        )
        print(DISCLAIMER_SHORT, file=sys.stderr)
        for kind, path in written.items():
            print(f"{kind}: {path}")
        top = result.top()
        if top is not None:
            print(f"top_hypothesis: {top.label}  score={top.score:.3f}  feasible={top.feasible}")
        return 0
    return 1
