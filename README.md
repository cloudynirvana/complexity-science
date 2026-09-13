# Complexity Science

NSTG-guided **in-silico** study of **pathology dynamics** and **constrained
biologic pathway search**. Attractors and trade-offs — not a care product.

**Not a medical device. Not CDS. Not dosing advice. Not externally validated.**

```text
problem  →  faster *computational* paths through class-level biologics
            under Nigerian comorbidity context (research question only)
method   →  NSTG research index  +  MHBD-4 ODE  +  constrained search
outputs  →  ranked in-silico hypotheses + falsification checklist
non-claims → no cure, no Phase II, no FDA-ready, no clinical validation
```

## Problem

Oncology-relevant host dynamics sit inside Nigerian comorbidity reality
(malaria, HIV, sickle cell disease, anaemia). The scientific question this
repo can *pose* — not answer in patients — is whether a compact dynamical
system plus guideline-shaped **constraints** can surface **falsifiable**
pathway hypotheses for later work.

## Method

1. **NSTG knowledge layer** — placeholder structured summaries
   (themes / cautions / comorbidities). Official FMoH *Nigeria Standard
   Treatment Guidelines* (3rd ed., 2022) is cited, **not redistributed**.
2. **Pathology dynamics** — documented four-state nonlinear ODE
   (burden \(B\), immune competence \(I\), toxicity \(X\), exposure \(E\)).
   Three computational archetypes (basins), not diagnoses.
   See `docs/DYNAMICS.md`.
3. **Biologics explorer** — class-level effectors (anti-PD-1–like,
   TGF-β trap–like, cytokine-like, fusion-mAb–like) with PK/PD-style knobs
   and provenance tags. Multi-objective / constrained search under toxicity
   caps and index-informed comorbidity flags.

Later **Project Confluence** calls should use
`complexity_science/integration/confluence_adapter.py` (JSON in/out only).
This codebase does not copy Confluence UI or connectome code.

## Outputs

```bash
python -m pip install -e ".[dev]"
python -m complexity_science run \
  --archetype comorbidity_constrained \
  --conditions "malaria,hiv,sickle_cell,anaemia" \
  --out reports/pathway_report.json
python -m pytest
```

Writes JSON + Markdown: ranked hypotheses, constraint rationale, falsification
checklist. Optional explainer: open `web/index.html`.

## Non-claims

| This repo | This repo does not |
| --- | --- |
| Generates in-silico rankings | Treat, diagnose, or manage anyone |
| Tightens model caps from an index | Execute NSTG as a protocol |
| Documents attractors | Claim a faster therapeutic path in patients |
| Awaits external validation | Phase II / FDA-ready / clinically validated |

Read `DISCLAIMER.md`, `docs/AWAITING_EXTERNAL_VALIDATION.md`,
`docs/NSTG_PROVENANCE.md`. Professor email blurb: `docs/PROFESSOR_EMAIL.md`.

## License

MIT. Parameters are computational caricatures. If a line conflicts with
NSTG 2022, **NSTG wins**.
