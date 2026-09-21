# Complexity Science

Efficient **in-silico** pipeline for **complex pathological cases** aimed at
systemic personalized-medicine **research**.

**Not a medical device. Not CDS. Not dosing. Not a cure.**

```text
Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction
```

Nigeria Standard Treatment Guidelines (NSTG) are a **structured
clinical-knowledge constraint layer** for pathway exploration. They are
**never** auto-translated into model parameters without an evidence gate.
This stub **never opens that gate**.

## What you get

| Input | Output |
| --- | --- |
| A `CaseCard` YAML in `pathology_cases/cases/` | A gated `PathwaySketch` (ranked hypotheses + required evidence + refused non-parameters) |

No patient data. No ODE edit when adding a case. No product, dose, or
schedule recommendations.

## Add a case in under 15 minutes

1. Copy any seed file in `pathology_cases/cases/` to
   `pathology_cases/cases/<your_id>.yaml`.
2. Fill the schema fields only: `disease`, `systemic_axes`, `observables`,
   `candidate_mechanisms`, `falsifiers`, `nstg_touchpoints`, `citations`,
   `disclaimer`. See `pathology_cases/SCHEMA.md`.
3. Use **real** Vancouver citations (see `docs/CITATION_STYLE.md`).
   Primary/review items need a real DOI. Do not invent DOIs. Do not paste
   NSTG chapter text.
4. Do **not** add parameters, doses, rates, ODE knobs, or numeric NSTG scales.
5. Validate and sketch:

```bash
python -m pip install -e ".[dev]"
python -m pipeline validate --case pathology_cases/cases/<your_id>.yaml
python -m pipeline explore --case pathology_cases/cases/<your_id>.yaml
python -m pytest
```

You should not open `pipeline/` or any ODE file. If the YAML is honest, the
explorer emits a `PathwaySketch` on its own.

## Efficiency

| Task | What you edit | What you do not edit | Typical local cost |
| --- | --- | --- | --- |
| Add a complex case | one YAML | `pipeline/`, ODE (none required) | <15 minutes |
| Validate schema + honesty | nothing | nothing | seconds |
| Emit PathwaySketch | nothing | nothing | seconds |
| Turn NSTG into a coefficient | refused | n/a | n/a |
| Fit an ODE from the card | refused | n/a | n/a |

Four seed cards (TNBC metabolic–immune exclusion, GBM invasive niche /
hypoxia, PDAC stromal barrier, dormant/occult disease) are data. They are
starting hypotheses with falsifiers, not validated models.

## Hard non-claims

| This repo | This repo does not |
| --- | --- |
| Validates research CaseCards | Treat, diagnose, or manage anyone |
| Ranks bibliographic, falsifiable hypotheses | Emit predictions or effect sizes |
| Applies NSTG as qualitative constraints | Execute NSTG as a protocol |
| Lists evidence still required | Auto-translate knowledge into parameters |
| Refuses parameter smuggling | Claim a cure, Phase II, or regulator-ready dossier |
| Stays in silico | Ingest patient records |

Read `DISCLAIMER.md` and `docs/NSTG_PROVENANCE.md`. Official NSTG 2022 is
cited, not redistributed. If a line here conflicts with NSTG, **NSTG wins**.

## Thesis #2 (manuscript)

Full thesis-format computational manuscript (not a clinical study). Headed
sections include **Problem Statement**, **Justification of the Study**, and
**Significance of the Study**. NSTG is a knowledge constraint, not a source
of ODE coefficients. Not a medical device.

- Markdown: `docs/manuscript/thesis_02_complexity_nstg_pathology.md`
- PDF: `docs/manuscript/thesis_02_complexity_nstg_pathology.pdf`
- Scholar landing page: `scholar/thesis_02.html`
- Indexing checklist: `docs/SCHOLAR_THESIS_02.md`
- Dedicated deposit: `https://github.com/cloudynirvana/thesis-02-complexity-nstg`

Author: Kelechi Emeka Ogbonna. Date: 2026-09-20. Revision: 2026-09-21.

## Seed cases

| ID | Research framing |
| --- | --- |
| `tnbc_metabolic_immune_exclusion` | Metabolic competition + T-cell exclusion in TNBC |
| `gbm_invasive_niche_hypoxia` | Hypoxic / infiltrative GBM niches |
| `pdac_stromal_barrier` | Desmoplastic delivery and immune barrier |
| `dormant_occult_disease` | Quiescent, angiogenic, or immune-held residual disease |

## License

MIT. Computational research software. Not a care product.
