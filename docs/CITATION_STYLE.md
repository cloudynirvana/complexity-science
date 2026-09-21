# Citation style (Vancouver / NLM)

Shared policy for CaseCards, manuscripts, and Scholar landing pages in this
repository. Style follows the ICMJE / NLM *Citing Medicine* Vancouver system.
This is a bibliographic policy, not a care protocol.

```text
Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction
```

Do not invent DOIs. Do not paste copyrighted NSTG chapter text.

## In-text

- Use numbered citations in square brackets: `[12]`, `[18,19]`, `[49–53]`.
- Number in order of first appearance in the manuscript.
- Every in-text number must have a References entry, and every References
  entry must be cited at least once. No orphans.

## Journal article (required elements)

```text
Author AA, Author BB, Author CC, Author DD, Author EE, Author FF, et al.
Article title in sentence case. Nlm J Abbrev. YYYY;volume(issue):pages.
doi:10.xxxx/xxxxx. PMID: 12345678.
```

| Element | Rule |
| --- | --- |
| Authors | All authors up to 6; then `, et al.` (NLM `AU` / group `CN`) |
| Initials | No periods, no spaces between initials (`Hanahan D`) |
| Title | Full article title; keep the publisher/NLM wording; no invented subtitles |
| Journal | NLM title abbreviation (`Nat Rev Cancer`, not the full name) |
| Date/locator | `YYYY;volume(issue):pages` (NLM page elision: `1195-203`) |
| Article number | If there are no pages: `YYYY;volume:article-number` |
| DOI | Print only a Crossref-resolvable DOI. If Crossref/PubMed cannot verify it, omit the DOI and use a URL if one exists. Never invent a DOI. |
| PMID | Print when PubMed has one. Leave blank if none. |
| PMC / ISBN | Optional; do not invent. |

Group / consortium papers may use the collective name (`Cancer Genome Atlas
Network`) instead of a truncated personal-author list.

## Book

```text
Author AA. Title. Edition. Place: Publisher; Year.
```

No DOI unless Crossref verifies one. No invented ISBN.

## Government / guideline / policy (Internet)

```text
Organisation. Title [Internet]. Edition. Place: Publisher; Year Mon DD
[cited YYYY Mon DD]. Available from: https://...
```

For NSTG 2022 and sibling FMoH documents:

- Cite the official bibliographic identity.
- Give a stable public URL when one exists (WHO EML host, ICCP plan host,
  NICRAT ChemoSafe host, FMINO launch notice).
- If the official book is not freely hosted, say so and point to an official
  launch or distributor notice. **Do not** cite unofficial scrapes (Scribd,
  random mirrors) as the source of the guideline text.
- Do not redistribute guideline chapters, tables, or dosing schedules.
- If a line here conflicts with official NSTG 2022, **NSTG wins**.

## What a citation is allowed to be

A knowledge or evidence **pointer**. A CaseCard citation is not a parameter,
not a dose, and not a prediction.

## Verification checklist

1. Resolve every printed DOI at `https://api.crossref.org/works/{doi}`.
2. Resolve PMIDs at PubMed / NCBI E-utilities.
3. Prefer NLM MEDLINE `TA`, `VI`, `IP`, `PG`, `AU`/`CN` for journal items.
4. Reject placeholder DOIs (`10.0000/`, `fake`, `example.com`).
5. After edits, regenerate any committed PDF so the bibliography matches.

## Scholar packaging

Landing HTML (`scholar/*.html`) should carry Highwire `citation_reference`
meta tags whose `content` is the **full Vancouver string** of each reference,
in the same order as the manuscript.

## CaseCard YAML

Primary and review items require a real DOI. Guideline and policy items may
omit DOI and must use a Vancouver (or Vancouver-Internet) string. See
`pathology_cases/SCHEMA.md`.
