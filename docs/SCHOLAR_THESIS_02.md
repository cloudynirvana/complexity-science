# Scholar packaging — Thesis #2

Indexing checklist for

*Complexity Science and NSTG-Guided In-Silico Pathology Dynamics for Biologics Pathway Exploration*
(Kelechi Emeka Ogbonna, 2026-09-20).

This is a computational research manuscript. **Not** a medical device, CDS, dosing advisor, or cure.

## Files in this repository

| File | Role |
| --- | --- |
| `docs/manuscript/thesis_02_complexity_nstg_pathology.md` | Canonical Markdown manuscript |
| `docs/manuscript/thesis_02_complexity_nstg_pathology.pdf` | Committed PDF (Scholar full text) |
| `scholar/thesis_02.html` | Static landing page with Highwire `citation_*` meta |

## Two absolute URL schemes

Document both. Use Pages once the site is enabled; raw GitHub works without it.

### A. GitHub Pages (intended Scholar host)

Enable Pages on this repository (Settings → Pages → Deploy from branch `main`, site root `/` or `/docs` only if you also move the HTML). With a root deploy of `main`:

- HTML: `https://cloudynirvana.github.io/complexity-science/scholar/thesis_02.html`
- PDF: `https://cloudynirvana.github.io/complexity-science/docs/manuscript/thesis_02_complexity_nstg_pathology.pdf`

`scholar/thesis_02.html` already sets:

```html
<meta name="citation_fulltext_html_url" content="https://cloudynirvana.github.io/complexity-science/scholar/thesis_02.html">
<meta name="citation_pdf_url" content="https://cloudynirvana.github.io/complexity-science/docs/manuscript/thesis_02_complexity_nstg_pathology.pdf">
```

Google Scholar can read those Highwire tags when the HTML URL is crawlable.

### B. Raw GitHub (PDF without Pages)

- PDF: `https://raw.githubusercontent.com/cloudynirvana/complexity-science/main/docs/manuscript/thesis_02_complexity_nstg_pathology.pdf`

`raw.githubusercontent.com` serves the PDF bytes and is crawlable on a public repo. It does **not** serve `scholar/thesis_02.html` as HTML (`text/plain`), so do not use raw URLs as the HTML landing page.

Until Pages is on, a crawler can still be pointed at the raw PDF. After merge to `main`, replace any branch-specific raw URL with the `main` URL above. On this feature branch the equivalent raw path is:

`https://raw.githubusercontent.com/cloudynirvana/complexity-science/cursor/thesis-02-nstg-pathology-87a6/docs/manuscript/thesis_02_complexity_nstg_pathology.pdf`

## Highwire tags present

`scholar/thesis_02.html` includes: `citation_title`, `citation_author` (family, given), `citation_publication_date` (`2026/09/20`), `citation_date`, `citation_online_date`, `citation_year`, `citation_language`, `citation_technical_report_institution`, `citation_technical_report_number`, `citation_fulltext_html_url`, `citation_pdf_url`, `citation_abstract`, repeated `citation_keywords`, one `citation_reference` meta per bibliography entry (full Vancouver string), plus Dublin Core `dc.title` / `dc.creator` / `dc.date`.

Vancouver rules: `docs/CITATION_STYLE.md`.

No DOI is minted here. Do not invent one.

## Rebuild the PDF

From the repository root, with `pandoc` and XeLaTeX:

```bash
pandoc docs/manuscript/thesis_02_complexity_nstg_pathology.md \
  --from markdown \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=2 \
  -V documentclass=report \
  -V papersize=a4 \
  -V geometry:margin=25mm \
  -V fontsize=11pt \
  -V colorlinks=true \
  -V linkcolor=black \
  -V urlcolor=blue \
  -V toccolor=black \
  -V mainfont="TeX Gyre Termes" \
  -V monofont="DejaVu Sans Mono" \
  --variable=mainfontoptions:Ligatures=TeX \
  -o docs/manuscript/thesis_02_complexity_nstg_pathology.pdf
```

Commit the regenerated PDF when the Markdown changes.

## Indexing checklist

- [ ] Repository is **public**.
- [ ] PDF is committed (not Git-LFS-only, unless Scholar can follow LFS).
- [ ] `scholar/thesis_02.html` is on the default branch after merge.
- [ ] GitHub Pages is enabled **or** the raw PDF URL is used as the crawl target.
- [ ] `citation_pdf_url` is an **absolute** `https://` URL that returns `application/pdf` without a login wall.
- [ ] `robots` allows indexing (`index, follow` is set on the landing page).
- [ ] Title, author, and date on the PDF first page match the meta tags.
- [ ] No invented DOI; no pasted NSTG chapter text.
- [ ] Google Scholar inclusion is not guaranteed and is not peer review.

## Suggested citation

Ogbonna KE. Complexity science and NSTG-guided in-silico pathology dynamics for biologics pathway exploration. Computational research thesis manuscript. Complexity Science repository; 2026 Sep 20 (rev. 2026 Sep 21). Available from: https://github.com/cloudynirvana/complexity-science and https://github.com/cloudynirvana/thesis-02-complexity-nstg

Dedicated deposit (README, THESIS.md, THESIS.pdf, CITATION.cff, DISCLAIMER.md):
https://github.com/cloudynirvana/thesis-02-complexity-nstg

Copy-ready payload in this repository (for that dedicated root, pending GitHub App write access):
`docs/deposit/thesis-02-complexity-nstg/`
