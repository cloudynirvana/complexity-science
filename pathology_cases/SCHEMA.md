# CaseCard schema

A `CaseCard` is **data**. Contributors add one YAML file. They do not edit
ODE, PK/PD, or explorer ranking code.

```text
Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction
```

NSTG touchpoints are **constraints**. They are never numeric scales.

## Required fields

| Field | Layer | Notes |
| --- | --- | --- |
| `disease` | knowledge | Name, abbreviations, research framing |
| `systemic_axes` | knowledge | ≥2 host–tumour couplings (`driver` / `constraint` / `context`) |
| `observables` | evidence pointers | `research_only: true` always |
| `candidate_mechanisms` | mechanism | Hypothesis statements + citation ids + biologic axis |
| `falsifiers` | mechanism | Every mechanism needs ≥1 |
| `nstg_touchpoints` | knowledge constraint | Qualitative only; cite FMoH, do not paste NSTG text |
| `citations` | knowledge or evidence | Vancouver (`docs/CITATION_STYLE.md`); real DOI for primary/review (no fake DOIs) |
| `disclaimer` | honesty | Must include the hard non-claims |

Forbidden extra keys include `parameters`, `ode`, `dose`, `ec50`,
`x_cap_scale`, `infection_risk_weight`, and other PK/PD or ODE knobs.
Numeric leaves are refused. Dose-like strings are refused.

Machine-readable copy: `pathology_cases/schema/case_card.schema.json`.
