"""Resolve [@key] citations in a thesis source file into Vancouver numbering.

Numbers follow order of first appearance; adjacent runs collapse (e.g. [3-5]).
Fails if a key is missing from the reference file or a reference is never cited.

    python docs/manuscript/src/build_thesis.py thesis_03 thesis_03_identifiability_gate
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
STEM = sys.argv[1] if len(sys.argv) > 1 else "thesis_03"
OUT_NAME = sys.argv[2] if len(sys.argv) > 2 else "thesis_03_identifiability_gate"
SRC = HERE / f"{STEM}.src.md"
REFS = HERE / f"{STEM}_refs.yaml"
OUT = HERE.parent / f"{OUT_NAME}.md"

CITE = re.compile(r"\[(@[\w-]+(?:;\s*@[\w-]+)*)\]")


def compress(nums):
    nums = sorted(set(nums))
    runs, start, prev = [], nums[0], nums[0]
    for n in nums[1:] + [None]:
        if n is not None and n == prev + 1:
            prev = n
            continue
        runs.append(f"{start}" if start == prev else (f"{start},{prev}" if prev == start + 1 else f"{start}–{prev}"))
        if n is not None:
            start = prev = n
    return ",".join(runs)


def main():
    text = SRC.read_text()
    refs = yaml.safe_load(REFS.read_text())
    order: list[str] = []
    for m in CITE.finditer(text):
        for key in re.findall(r"@([\w-]+)", m.group(1)):
            if key not in refs:
                sys.exit(f"unknown citation key: {key}")
            if key not in order:
                order.append(key)
    unused = set(refs) - set(order)
    if unused:
        sys.exit(f"references never cited: {sorted(unused)}")
    num = {k: i + 1 for i, k in enumerate(order)}
    body = CITE.sub(lambda m: "[" + compress([num[k] for k in re.findall(r"@([\w-]+)", m.group(1))]) + "]", text)
    reflist = "\n\n".join(f"{num[k]}. {refs[k]}" for k in order)
    body = body.replace("<!-- REFERENCES -->", reflist)
    OUT.write_text(body)
    print(f"wrote {OUT.relative_to(HERE.parents[2])}: {len(order)} references")


if __name__ == "__main__":
    main()
