# NSTG provenance

## Official source (cite this; do not copy it from this repo)

Federal Ministry of Health, Nigeria. *Nigeria Standard Treatment Guidelines*.
3rd edition. Abuja: Federal Ministry of Health; 2022.

Obtain the official book from FMoH or an authorised distributor.
**This repository does not bundle, scrape, or quote NSTG verbatim.**

Related public policy documents cited on CaseCards (also not redistributed
as body text):

- Federal Ministry of Health, Nigeria. *Nigeria Essential Medicines List*. 7th ed. 2020.
- Federal Ministry of Health, Nigeria. *Nigeria National Cancer Control Plan 2018–2022*. 2018.
- Federal Ministry of Health, Nigeria. *National Policy on Chemotherapy Safety (ChemoSafe)*. June 2021.

## What NSTG is allowed to be here

A **structured clinical-knowledge constraint layer** for in-silico pathway
exploration (themes such as infection, HIV, anaemia, supportive referral).

## What NSTG is not allowed to be here

A parameter source. The evidence gate refuses auto-translation of NSTG
touchpoints into doses, rate constants, ODE coefficients, or numeric
constraint scales (`x_cap`, infection-risk weights, and similar).

If a line in this repo conflicts with official NSTG 2022, **NSTG wins**.
