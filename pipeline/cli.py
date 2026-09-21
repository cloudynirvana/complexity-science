"""Command-line entry for validation and PathwaySketch exploration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pathology_cases.loader import CaseCardError, iter_case_paths, load_case
from pipeline.explorer import explore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="complexity-science",
        description=(
            "In-silico CaseCard validator and NSTG-gated pathway explorer. "
            "Research software only — not a medical device."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    validate = sub.add_parser("validate", help="Validate CaseCard YAML")
    validate.add_argument("--case", type=Path, help="Single YAML path")
    validate.add_argument("--all", action="store_true", help="All seed cases")

    explore_p = sub.add_parser("explore", help="Emit a PathwaySketch JSON")
    explore_p.add_argument("--case", type=Path, help="Single YAML path")
    explore_p.add_argument("--all", action="store_true", help="All seed cases")
    explore_p.add_argument("--out", type=Path, help="Write JSON to this path")

    args = parser.parse_args(argv)
    paths = _resolve_paths(args)
    if not paths:
        print("Specify --case PATH or --all", file=sys.stderr)
        return 2

    if args.cmd == "validate":
        return _validate(paths)
    return _explore(paths, out=args.out)


def _resolve_paths(args: argparse.Namespace) -> list[Path]:
    if getattr(args, "all", False):
        return iter_case_paths()
    if getattr(args, "case", None):
        return [args.case]
    return []


def _validate(paths: list[Path]) -> int:
    failed = 0
    for path in paths:
        try:
            card = load_case(path)
        except CaseCardError as exc:
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failed += 1
            continue
        print(f"OK   {path} ({card.id})")
    return 1 if failed else 0


def _explore(paths: list[Path], *, out: Path | None) -> int:
    sketches = []
    for path in paths:
        try:
            sketches.append(explore(load_case(path)).to_dict())
        except CaseCardError as exc:
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            return 1
    payload: object = sketches[0] if len(sketches) == 1 else sketches
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if out:
        out.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
