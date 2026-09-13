# NSTG provenance

## Official source (cite this, do not copy it from this repo)

Federal Ministry of Health, Nigeria. *Nigeria Standard Treatment Guidelines*.
3rd edition. Abuja: Federal Ministry of Health; 2022. Officially launched
24 November 2022 (sometimes referred to in government communications as NTSG).

Obtain the official text from the Federal Ministry of Health (FMoH) or an
authorised distributor. **This repository does not bundle, scrape, or quote
the NSTG verbatim.**

## What we ship instead

`complexity_science/data/nstg_index.json` holds **placeholder research-index
summaries**: short, original theme / caution / comorbidity lists for
oncology-adjacent supportive care and Nigerian comorbidity contexts
(malaria, HIV, sickle cell disease, anaemia).

Each record is tagged:

```text
status: PLACEHOLDER_RESEARCH_INDEX
redistribution: official NSTG text not included
```

These summaries are **not** a substitute for the guideline. They exist so the
retriever and constraint mapper have a structured, testable index. If a
summary disagrees with NSTG 2022, **NSTG wins**.

## Intended use of the retriever

```text
condition → themes, cautions, comorbidities
```

The retriever is a research index, not a point-of-care lookup. It may be
used to *shape computational constraints* (for example, a tighter toxicity
cap when sickle cell disease and anaemia co-occur). It must not be used to
select drugs, doses, or referral pathways for a person.

## Updating the index

Replace placeholders only with:

1. permissioned, licence-clear structured extracts; or
2. new original summaries that remain clearly labelled and cite FMoH NSTG 2022.

Do not paste chapter text, tables, or dosing schedules from the official book.
