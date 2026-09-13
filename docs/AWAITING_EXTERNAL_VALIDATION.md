# Awaiting external validation

This pipeline is a **computational sketch**. Nothing in the repository has been
externally validated against prospective clinical outcomes, independent
biobank time series, or a registered protocol.

## What exists today

| Layer | Status |
| --- | --- |
| NSTG knowledge index | Placeholder research summaries + provenance pointer. Official FMoH text is **not** redistributed. |
| Pathology ODE | Documented four-state toy model. Parameters are computational, not fitted to a named cohort. |
| Biologic effectors | Class-level caricatures (checkpoint-like, TGF-β-trap-like, cytokine-like, fusion-mAb-like). Not products. |
| Constrained search | Deterministic in-silico ranking under hand-set weights and caps. |
| Confluence adapter | JSON contract only. No live dependency. |

## What validation would actually require

External validation is **not** a software checkbox. A serious programme would
need, at minimum:

1. **Independent data** — longitudinal burden, immune, toxicity, and exposure
   series that the authors of this repo did not tune against.
2. **Pre-registered predictions** — which archetype, which observables, which
   rejection rules (see each report’s falsification checklist).
3. **Identifiability analysis** — which parameters can be recovered from
   sparse African-context lab panels, and which cannot.
4. **Ethics and governance** — IRB/REC review before any human data; no
   re-identification; no CDS deployment dressed up as “research UI”.
5. **Domain review** — oncology, infectious disease, haematology, and NSTG
   custodians reading the constraint map, not only the ODE.
6. **Negative controls** — effectors and archetypes the model should *not*
   rank well, to catch reward-hacking of the scalar score.

Until those exist, every ranked list is an **in-silico hypothesis generator**.

## Explicit non-claims

This work does **not** claim:

- clinical validation, clinical utility, or real-world evidence;
- Phase I/II/III readiness or any FDA / NAFDAC / EMA dossier status;
- that a faster path through biologics has been found for patients;
- that NSTG recommendations have been encoded as an executable protocol.

When validation results exist, they should live in a dated, citable report
with data access notes — not as adjectives in the README.
