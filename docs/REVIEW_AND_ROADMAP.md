# Repository review and roadmap

State as of 4 October 2026 (updated when Thesis #4 landed). This file is an honest internal assessment, not a
claim of quality. It exists so that a reader — or a future contributor — can see
what has been done, what has not, and what should happen next.

## What is here

| Object | Size | Figures | Status |
| --- | --- | --- | --- |
| Thesis #2 — NSTG-guided in-silico pathology | ~10,200 words, 69 refs | none | on `main`; unreviewed |
| Thesis #3 — identifiability as the evidence gate | ~6,800 words, 28 refs | 6 | on a feature branch; unreviewed |
| Thesis #4 — what a blood film allows (malaria) | ~5,800 words, 22 refs | 5 | on a feature branch; unreviewed |
| `pathology_cases/` + `pipeline/` | CaseCard schema, smuggling scanner, gated explorer | — | 30 tests |
| `glucose_competition/` | model, regimes, identifiability, figures | — | 11 tests |
| `evidence_gate/` | the shared gate, used by Theses #3 and #4 | — | 4 tests |
| `malaria_clearance/` | stage-structured model, analysis, figures | — | 7 tests |

None of the three manuscripts has been peer reviewed, and none has a DOI. All
are single-author computational work with no experimental data.

## Honest assessment

**Strengths.** The epistemic boundary (*Knowledge ≠ Evidence ≠ Mechanism ≠
Parameter ≠ Prediction*) is unusual and defensible, and Thesis #3 turns it from
a slogan into a computation that anyone can rerun, which Thesis #4 then applies
unchanged to a different field. Every reference in all three manuscripts was
checked against PubMed records rather than recalled. Every number and figure in
Theses #3 and #4 regenerates from one command. Negative results
and one withdrawn claim are reported rather than buried.

**Weaknesses, in order of how much they cost.**

1. **No external validation.** No peer review, no co-author, no data. The work
   is internally consistent, which is not the same as being right. Thesis #4 is
   the closest to a testable claim, because its prediction is about a protocol
   that thousands of studies already run.
2. **Thesis #2 has no figures of its own.** The framework schematic now covers
   its architecture on the README front page, but the manuscript itself still
   carries none, and it is repetitive: the non-claims are restated on nearly
   every page.
3. **Thesis #3 rests on one parameter point.** Bistability occurred in 1 of 400
   random draws, and the reference point was chosen because it was bistable.
   The identifiability results are reported at that point only.
4. **No real data anywhere.** All three theses are about what must *not* be
   computed yet. That is a real contribution, but a reviewer will ask what happens when
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
3. **Fold the framework schematic into Thesis #2** (panel B already draws its
   CaseCard-to-PathwaySketch flow) and cut the manuscript's repetition by about
   a third. Note that Thesis #2's PDF was built with pandoc + XeLaTeX, which is
   not installed here; rebuilding it would either need that toolchain or a
   switch to the HTML pipeline used by Theses #3 and #4.
4. **Widen Thesis #3's identifiability result** beyond the single reference
   point: repeat the Fisher and profile analysis across a sample of parameter
   sets and report how often the kill rate is refused.
5. **Apply the gate to published data.** Take one openly available clearance
   time course, run the gate, and report the verdicts beside any estimate. This
   is the step that turns a method into a result, and it is now the single most
   valuable thing left to do.
6. **Hierarchical extension of Thesis #4.** Across many patients, staging varies
   while drug parameters are shared, so a population model may identify killing
   where one curve cannot. This is the natural fifth manuscript — but only after
   step 1 and step 5.

## Reproducing everything

```bash
python -m pip install -e ".[dev]"
python -m pytest                              # 52 tests
python -m glucose_competition.analysis        # Thesis #3: all numbers + six figures
python -m malaria_clearance.analysis          # Thesis #4: all numbers + five figures
docs/manuscript/src/build_pdf.sh                                            # Thesis #3 PDF
docs/manuscript/src/build_pdf.sh thesis_04 thesis_04_clearance_identifiability  # Thesis #4 PDF
```
