"""Write JSON + Markdown in-silico pathway reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from complexity_science.honesty import assert_honest
from complexity_science.pipeline import PipelineResult


def _md_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- (none)"


def render_markdown(result: PipelineResult) -> str:
    data = result.to_dict()
    top = result.top()
    top_lines = []
    if top is not None:
        top_lines = [
            f"**Label:** {top.label}",
            f"**Feasible (in-model):** {'yes' if top.feasible else 'no'}",
            f"**Score (scalar, not utility):** {top.score:.3f}",
            (
                f"**B_final / I_final / X_peak:** "
                f"{top.metrics['b_final']:.3f} / "
                f"{top.metrics['i_final']:.3f} / "
                f"{top.metrics['x_peak']:.3f}"
            ),
        ]
        if top.violations:
            top_lines.append("**Violations:** " + "; ".join(top.violations))

    nstg_lines = []
    for hit in result.retrieval.hits:
        nstg_lines.append(f"### {hit.entry.name} (`{hit.entry.id}`)")
        nstg_lines.append("Themes:")
        nstg_lines.append(_md_list(list(hit.entry.themes)))
        nstg_lines.append("Cautions:")
        nstg_lines.append(_md_list(list(hit.entry.cautions)))
        nstg_lines.append("")

    table = [
        "| Rank | Label | Feasible | Score | B_final | I_final | X_peak |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for hyp in result.hypotheses:
        table.append(
            f"| {hyp.rank} | {hyp.label} | "
            f"{'yes' if hyp.feasible else 'no'} | {hyp.score:.3f} | "
            f"{hyp.metrics['b_final']:.3f} | {hyp.metrics['i_final']:.3f} | "
            f"{hyp.metrics['x_peak']:.3f} |"
        )

    cite = result.retrieval.provenance.get("cite", "FMoH NSTG 2022")
    body = f"""# In-silico pathway report

_{data['created_at']} · complexity_science {data['version']}_

## Disclaimer

{result.disclaimer}

## Non-claims

{_md_list(result.non_claims)}

## Problem (this run)

Explore **computational** paths that reduce modelled burden under toxicity
caps shaped by an NSTG *research index* — not faster cures, not a care plan.

- **Archetype:** {result.archetype.name} (`{result.archetype.id}`)
- **Horizon:** {result.horizon_days:.0f} days
- **Index query:** {', '.join(result.retrieval.query) or '(default)'}

{result.archetype.summary}

## Method

1. Retrieve placeholder NSTG themes / cautions / comorbidities.
2. Build a conservative constraint profile (min cap scales, max infection weight).
3. Integrate MHBD-4 (burden, immune competence, toxicity, exposure).
4. Rank class-level biologic caricatures (single and optional pairs).

Cite the official book, not this index: {cite}

## NSTG research index hits

{chr(10).join(nstg_lines) if nstg_lines else '_No index hits._'}

Unmatched queries: {', '.join(result.retrieval.unmatched) or 'none'}

### Constraint profile

- `x_cap` = {result.constraints.x_cap:.3f}
- `max_immune_depletion` = {result.constraints.max_immune_depletion:.3f}
- `infection_risk_weight` = {result.constraints.infection_risk_weight:.3f}
- flags: {', '.join(result.constraints.flags) or 'none'}

{_md_list(list(result.constraints.rationale))}

## Leading in-silico hypothesis

{chr(10).join(top_lines) if top_lines else '_No hypotheses._'}

This is a model artefact. It is not a biologic prescription.

## Ranked hypotheses

{chr(10).join(table)}

## Falsification checklist

{_md_list(result.falsification)}

## Notes

{_md_list(result.notes)}

## Outputs

JSON sibling of this file carries full trajectories (downsampled) and effector
provenance tags. See also `DISCLAIMER.md` and `docs/AWAITING_EXTERNAL_VALIDATION.md`.
"""
    assert_honest(body, label="markdown_report")
    return body


def write_report(
    result: PipelineResult,
    path: str | Path,
    *,
    also_markdown: bool = True,
) -> dict[str, Path]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = result.to_dict()
    text = json.dumps(payload, indent=2, sort_keys=False)
    assert_honest(text, label="json_report")
    path.write_text(text + "\n", encoding="utf-8")
    written = {"json": path}
    if also_markdown:
        md_path = path.with_suffix(".md")
        md_path.write_text(render_markdown(result), encoding="utf-8")
        written["markdown"] = md_path
    return written
