# Repository review and roadmap

State as of 4 October 2026. This file is an honest internal assessment, not a
claim of quality. It exists so that a reader — or a future contributor — can see
what has been done, what has not, and what should happen next.

## What is here

| Object | Size | Figures | Status |
| --- | --- | --- | --- |
| Thesis #2 — NSTG-guided in-silico pathology | ~10,200 words, 69 refs | none | on `main`; unreviewed |
| Thesis #3 — identifiability as the evidence gate | ~6,800 words, 28 refs | 6 | on a feature branch; unreviewed |
| `pathology_cases/` + `pipeline/` | CaseCard schema, smuggling scanner, gated explorer | — | 30 tests |
| `glucose_competition/` | model, regimes, identifiability, gate, figures | — | 11 tests |

Neither manuscript has been peer reviewed. Neither has a DOI. Both are
single-author computational work with no experimental data.

## Honest assessment

**Strengths.** The epistemic boundary (*Knowledge ≠ Evidence ≠ Mechanism ≠
Parameter ≠ Prediction*) is unusual and defensible, and Thesis #3 turns it from
a slogan into a computation that anyone can rerun. Every reference in both
manuscripts was checked against PubMed records rather than recalled. Every
number and figure in Thesis #3 regenerates from one command. Negative results
and one withdrawn claim are reported rather than buried.

**Weaknesses, in order of how much they cost.**

1. **No external validation.** No peer review, no co-author, no data. The work
   is internally consistent, which is not the same as being right.
2. **Thesis #2 has no figures.** A reader cannot see the architecture it
   describes without reading 10,000 words. It is also repetitive: the
   non-claims are restated on nearly every page.
3. **Thesis #3 rests on one parameter point.** Bistability occurred in 1 of 400
   random draws, and the reference point was chosen because it was bistable.
   The identifiability results are reported at that point only.
4. **No real data anywhere.** Both theses are about what must *not* be computed
   yet. That is a real contribution, but a reviewer will ask what happens when
   the gate meets a measured time course.
5. **[PR #1](https://github.com/cloudynirvana/complexity-science/pull/1) is open
   and stale.** Both manuscripts cite it as the companion experiment they refuse.
   A visitor who follows that citation finds unmerged work.
6. **No ORCID, no DOI.** `CITATION.cff` and `.zenodo.json` are ready and a
   commented line marks where the ORCID goes.

## Recommendations, in priority order

1. **Close the loop on Thesis #3.** Review it, merge the branch, register an
   ORCID, connect Zenodo, cut a release. An archived DOI is worth more than a
   fourth manuscript.
2. **Resolve PR #1.** Merge it or close it with a note. A cited pull request
   should not stay open.
3. **Give Thesis #2 one figure** — the CaseCard-to-PathwaySketch flow, drawn the
   same way as Figure 1 of Thesis #3 — and cut its repetition by roughly a third.
4. **Widen Thesis #3's identifiability result** beyond the single reference
   point: repeat the Fisher and profile analysis across a sample of parameter
   sets and report how often the kill rate is refused.
5. **Apply the gate to published data.** Take one openly available time course,
   run the gate, and report the verdicts beside any estimate. This is the step
   that turns a method into a result.
6. **Then, and only then, a fourth manuscript.** The prepared candidate is
   artemisinin partial resistance: parasite clearance half-life is the standard
   phenotype, and what it can and cannot identify about stage-specific killing
   is the same question in a setting where the answer affects African malaria
   surveillance.

## Reproducing everything

```bash
python -m pip install -e ".[dev]"
python -m pytest                              # 41 tests
python -m glucose_competition.analysis        # all numbers + all six figures
docs/manuscript/src/build_pdf.sh              # Thesis #3 PDF
```
