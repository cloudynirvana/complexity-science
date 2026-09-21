---
title: "Complexity Science and NSTG-Guided In-Silico Pathology Dynamics for Biologics Pathway Exploration"
author: "Kelechi Emeka Ogbonna"
date: "20 September 2026"
subtitle: "Computational research thesis manuscript — not a clinical study"
keywords:
  - complexity science
  - in-silico pathology
  - NSTG
  - CaseCard
  - PathwaySketch
  - biologics pathway exploration
  - knowledge constraint
  - parameter smuggling
lang: en-GB
---

# Front matter {-}

**Thesis #2**

**Status.** Computational research thesis manuscript. This is not a clinical study, not a medical device dossier, not clinical decision support (CDS), not a dosing advisor, and not a claim of cure.

**Repository.** Implementation: `https://github.com/cloudynirvana/complexity-science`. Dedicated thesis deposit: `https://github.com/cloudynirvana/thesis-02-complexity-nstg`.

**Corresponding objects in this repository.** `pathology_cases/` (CaseCard schema and four seed cases); `pipeline/` (NSTG-gated PathwaySketch explorer); `docs/NSTG_PROVENANCE.md`; `DISCLAIMER.md`.

**Revision.** 21 September 2026: Problem Statement, Justification of the Study, and Significance of the Study added as headed sections (computational research framing; NSTG is a knowledge constraint, not ODE coefficients; this work is not a medical device).

**Relation to other work in this repository.** Pull request #1 explores a compact multi-scale host–burden ordinary differential equation (ODE) with numeric constraint *hints*. This manuscript describes the complementary **data-first** layer: YAML CaseCards, qualitative Nigeria Standard Treatment Guidelines (NSTG) constraints, and an evidence gate that **never** auto-translates NSTG into ODE coefficients. Numeric scales such as `x_cap_scale` and `infection_risk_weight` are treated here as smuggled non-parameters.

**How to read this document.** After the abstract, read the headed **Problem Statement**, **Justification of the Study**, and **Significance of the Study** (sections 1.3–1.5) before the aims. Official NSTG 2022, the Nigeria Essential Medicines List (2020), the National Cancer Control Plan 2018–2022, and the National Policy on Chemotherapy Safety (ChemoSafe, 2021) are **cited, not redistributed**. No guideline chapter, table, or dosing schedule is reproduced. If any line in this repository conflicts with official NSTG 2022, **NSTG wins**. Bibliographic style is Vancouver / NLM (`docs/CITATION_STYLE.md`).

\newpage

# Abstract {-}

Complex pathological systems sit in Warren Weaver's class of *organised complexity*: many interacting parts, nonlinear couplings, and host context that cannot be reduced to a single rate or a single target [1–3]. In oncology that organisation appears as metabolic competition, immune exclusion, hypoxic and invasive niches, stromal delivery barriers, and latent residual disease [18–26,45–48]. Biologics pathway exploration is therefore a **systemic control problem** — how a host–tumour system might be constrained — not a product-selection problem.

Computational oncology often collapses five distinct epistemic layers into one object. This manuscript treats that collapse as the central failure mode and states a non-negotiable boundary used throughout the accompanying software:

> Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction

The work reported here is an **architectural** computational thesis, not a clinical study. It specifies, implements, and tests a data-only in-silico pipeline in this repository. A contributor authors a YAML `CaseCard` — disease framing, systemic axes, research-only observables, candidate mechanisms, falsifiers, qualitative NSTG touchpoints, Vancouver citations, and a required honesty disclaimer. The card is refused if it carries doses, rate constants, ODE knobs, PK/PD tokens, numeric leaves, or NSTG-derived numeric scales. A stub `PathwaySketch` explorer then ranks bibliographic, falsifiable hypotheses, lists evidence still required, and emits an explicit `refused_non_parameters` record. The evidence gate **never opens**. NSTG 2022 is used only as a structured clinical-knowledge **constraint layer** [49,50]. It is never executed as a care protocol and never auto-translated into model parameters.

Four seed CaseCards were constructed from published knowledge and evidence pointers, not from patient records: triple-negative breast cancer (TNBC) framed as metabolic–immune exclusion [23,28–30]; glioblastoma (GBM) framed as an invasive hypoxic niche [31–34]; pancreatic ductal adenocarcinoma (PDAC) framed as a stromal barrier [37–41]; and dormant / occult residual disease framed explicitly as a research hypothesis space [45–48]. Each card validates against schema version 1.0.0. Across the four cards the explorer emits thirteen ranked hypotheses. Every hypothesis has `parameter_status = refused` and `prediction_status = not_emitted`. Infection- or immunosuppression-themed NSTG touchpoints down-rank immune-axis hypotheses as a qualitative heuristic; the software states that this is not a contraindication and not a parameter. Dedicated tests refuse `parameters`, `ode_params`, `x_cap_scale`, `infection_risk_weight`, dose-like strings, and bare numeric leaves.

Results are architectural. No ODE was integrated in this pipeline. No public dataset was analysed. No effect size, survival, response, or care pathway is claimed. Named public resources — The Cancer Genome Atlas (TCGA) breast, GBM, and pancreatic cohorts; the NCI Genomic Data Commons; cBioPortal; NCBI GEO; the Ivy Glioblastoma Atlas; and the Human Tumor Atlas Network — are listed only as **future binds** [54–63]. They are not used here.

Headed sections state the Problem Statement, Justification of the Study, and Significance of the Study in computational-research terms: NSTG is a knowledge constraint, not a source of ODE coefficients, and this work is not a medical device [65–69].

The contribution is a reusable research object and a closed gate: a CaseCard can be added in under fifteen minutes without editing explorer or ODE code, and NSTG knowledge cannot smuggle itself into a coefficient. That is a complexity-science result about *what must not be computed yet*, not a claim that a biologic pathway has been found.

\newpage

# Keywords {-}

complexity science; organised complexity; in-silico pathology; systemic control; Nigeria Standard Treatment Guidelines (NSTG); knowledge constraint; CaseCard; PathwaySketch; biologics pathway exploration; triple-negative breast cancer; glioblastoma; pancreatic ductal adenocarcinoma; cancer dormancy; parameter smuggling; evidence gate; falsifiability; computational research thesis

\newpage

# 1 Introduction

## 1.1 Complex pathology

A tumour is not a bag of mutated cells. It is a spatially structured, temporally evolving host–tumour system: metabolic sinks, excluded or exhausted lymphocytes, hypoxic niches, desmoplastic stroma, abnormal vasculature, and — after apparent control — occult residual populations [18–26,31,37,45]. Hanahan and Weinberg organised many of these behaviours as hallmarks [18,19]; Hanahan and Coussens, Quail and Joyce, and Junttila and de Sauvage emphasised that recruited stroma and immune context can dominate therapeutic response [20–22]. Joyce and Fearon named T-cell exclusion as a distinct privilege of the tumour microenvironment [23]. Chen and Mellman described the cancer-immunity cycle and the immune set point as systems properties rather than single-receptor facts [24,25]. Hegde and Chen listed exclusion, lack of infiltration, and host context among the practical obstacles to immunotherapy [26].

Those descriptions are knowledge. They are not automatically evidence in a new cohort, not automatically a mechanism in a named patient, not automatically a parameter in a differential equation, and not automatically a prediction of response. Conflating the five is how computational pathology becomes theatre.

## 1.2 The systemic control problem

Biologics pathway exploration is often narrated as target discovery: find the receptor, write the affinity, rank the product. In a complex host the relevant question is closer to **control under constraint**. Metabolic competition can starve effectors independently of checkpoint occupancy [27,28]. A desmoplastic gland can prevent a small molecule from arriving [37,38]. A hypoxic pseudopalisade can couple survival to migration [32,33]. A dormant disseminated cell can ignore therapies aimed at cycling compartments [45,46]. Infection, anaemia, HIV care continuity, chemotherapy-handling safety, and specialist referral are host and system constraints in the Nigerian guideline and policy environment [49–53]. They shape what may be *explored*. They do not, by themselves, supply a rate constant.

A control problem of this kind is a complexity-science problem. Weaver distinguished organised complexity from problems of simplicity and from disorganised complexity amenable to statistics alone [1]. Anderson's "more is different" warned that scale introduces new laws rather than larger versions of old ones [2]. Goldenfeld and Kadanoff, and Hartwell and colleagues, restated the lesson for condensed matter and for modular cell biology [3,4]. Kitano's systems-biology programme, and Barabási, Gulbahce and Loscalzo's network medicine, made the same claim for disease: the unit of analysis is a coupled system [5–7]. In health services, Plsek and Greenhalgh, Ahn and colleagues, and Lipsitz argued that reduction to a single protocol step misrepresents care [8–10]. None of those arguments licenses an unfitted ODE as a digital twin, and none licenses a guideline as a coefficient. May warned that mathematics in biology is easily abused when a model is treated as the organism [65]. Saltelli and colleagues argued that models must serve society by making limits inspectable, not by converting uncertainty into false precision [66].

## 1.3 Problem Statement

Computational oncology routinely collapses five distinct epistemic layers — knowledge, evidence, mechanism, parameter, and prediction — into a single numeric object, so that a guideline sentence, a review article, or a qualitative host constraint is silently rewritten as an ordinary-differential-equation coefficient.

That collapse is the problem this thesis addresses. Complex pathology belongs to Weaver's class of organised complexity: a modest number of coupled host–tumour axes whose geometry and history matter [1–7,18–26]. Biologics pathway exploration in such a system is a **systemic control problem**, not a product-selection problem [23–30,37–41,45–48]. Two complementary errors follow when the five layers are fused.

**Guideline-as-coefficient.** Nigeria Standard Treatment Guidelines (NSTG 2022) and adjacent Nigerian policy documents are structured clinical **knowledge** [49–53]. Mapping them to numeric scales such as `x_cap_scale` or `infection_risk_weight` treats a constraint theme as a fitted — or, worse, unfitted — parameter. A parameter requires physicochemical identification that a YAML hypothesis and a guideline sentence do not supply [11,12,65,66]. NSTG is a knowledge constraint. It is not a source of ODE coefficients.

**Host-as-generic-trial-body.** Omitting NSTG themes — infection, immunosuppression, HIV care continuity, anaemia, chemotherapy-handling safety, specialist referral — writes the host as if Nigerian system-level knowledge did not exist [8–10,49–53]. Organised complexity includes that host. Honouring the host by inventing a weight is the first error; deleting the host is the second.

A third, quieter error is **software-as-care**. Research code that ranks bibliographic hypotheses is not a medical device, not clinical decision support (CDS), and not a dosing advisor. It does not have a medical purpose and it does not drive a clinical decision about a person. Presenting it as a care protocol, a digital twin of a Nigerian clinic, or a cure would be a category error of a different kind [13,14,65,66].

The specific computational gap is therefore this: there is no data-first research object in this setting that (i) lets a contributor author a complex pathological case without editing a solver; (ii) holds NSTG as a qualitative knowledge constraint that **cannot** auto-translate into ODE coefficients, doses, or predictions; and (iii) keeps the evidence gate closed so that parameterisation and prediction are refused rather than silently emitted. This is a problem in computational research architecture. It is not a clinical-care problem, not a device-engineering problem, and not a request for a cure.

## 1.4 Justification of the Study

The study is justified by the mismatch between what complexity science says a pathological system *is* and what computational pipelines usually *emit*.

Weaver, Anderson, Goldenfeld and Kadanoff, Hartwell and colleagues, Kitano, and network medicine locate disease in organised, scale-dependent, modular, interactome-level systems [1–7]. Hallmarks, accessory cells, exclusion, the immunity cycle, and immunotherapy's practical obstacles locate oncology in the same class [18–26]. May warned that mathematics in biology is easily abused when a model is treated as the organism [65]. Saltelli and colleagues argued that models must serve society by making assumptions and limits inspectable [66]. Wolkenhauer asked "why model?" and answered: to make assumptions inspectable [11]. Aldridge, Burke, Lauffenburger and Sorger stated what a physicochemical signalling model actually requires [12]. A CaseCard that has not met those requirements is not entitled to a rate constant.

Health-systems complexity supplies a second justification. Plsek and Greenhalgh, Ahn and colleagues, and Lipsitz treated care organisations as complex adaptive systems [8–10]. NSTG 2022 is system-level knowledge in that sense [49,50]. It is justified as a **constraint layer** because infection, HIV continuity, anaemia, ChemoSafe handling, and referral shape what may be *explored* in a Nigerian research framing [49–53]. It is not justified as a source of ODE coefficients, because a guideline sentence is not a calibrated parameter [12,65,66]. Pull request #1 in the companion modelling experiment explores numeric constraint hints; this thesis is justified as the complementary refusal at the data boundary, so that the two designs cannot launder numbers through YAML.

A third justification is honesty under publication pressure. Ioannidis, Begley and Ellis, and Popper's falsifiability requirement are used here as **negative** design constraints [13–15]: a ranked `research_score` must not be readable as an effect size, and every mechanism must name its own destruction. Peng, and Stodden and colleagues, argued that computational claims should travel with data, code, and explicit limits [68,69]. FAIR principles justify treating the CaseCard as a findable, reusable research object rather than as a slide figure [67]. Those arguments justify a schema that fails closed.

The study is **not** justified as a medical device programme, a Phase II protocol, a regulator-ready dossier, or a replacement for official NSTG. Those would be different objects, with different evidence, different licences, and different accountable authors. This manuscript does not claim them.

## 1.5 Significance of the Study

The significance of this work is architectural and epistemic, not clinical.

**For computational oncology and complexity science.** The thesis makes the five-layer boundary — knowledge, evidence, mechanism, parameter, prediction — machine-enforceable. A contributor cannot paste `ec50`, `10 mg/kg`, or `x_cap_scale` into a CaseCard and obtain a PathwaySketch. That refusal is the result. It operationalises organised complexity as a stop on a mis-specified controller rather than as another state in an ODE [1–7,65,66]. Four control motifs (metabolic–immune exclusion, invasive hypoxic niche, stromal barrier, dormancy) share one schema, showing that motif diversity need not imply solver diversity [23–26,31–34,37–41,45–48].

**For Nigerian guideline-aware research (not care).** NSTG 2022 is present as cited knowledge and as qualitative themes [49–53]. It is absent as a table dump, as an executable protocol, and as a coefficient. The significance is that a computational pipeline can honour Nigerian system context without impersonating the Federal Ministry of Health and without smuggling a weight. If a line in the repository conflicts with official NSTG 2022, NSTG wins.

**For reusable research objects.** A CaseCard can be added in under fifteen minutes without editing explorer or ODE code. Schema, tests, and a closed gate travel with the object [67–69]. Named public datasets (TCGA, GDC, GEO, Ivy GAP, HTAN) are listed only as future binds [54–64], so that a later worker cannot invent a silent analysis in the gap.

**What this significance is not.** This thesis does not diagnose, treat, prevent, or cure anyone. It is not a medical device and not CDS. It does not recommend a biologic product, dose, schedule, or combination. It does not claim that a pathway has been found. Ranked hypotheses are bibliographic starting points awaiting independent falsification. The honest next measurement is an orthogonal assay against a named falsifier — not a tighter toxicity cap, and not a clinic deployment.

## 1.6 What this thesis is

This thesis specifies an in-silico research architecture implemented in `complexity-science` (repository version 0.2.0, CaseCard schema 1.0.0):

1. a **CaseCard** data schema that holds knowledge, evidence pointers, candidate mechanisms, falsifiers, and qualitative NSTG constraints;
2. a **parameter-smuggling** scanner that refuses numeric and PK/PD/ODE content, including NSTG numeric scales used as constraint hints in a companion ODE pipeline;
3. an **evidence gate** that encodes `Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction` and never opens;
4. a stub **PathwaySketch** explorer that ranks hypotheses bibliographically and by falsifiability, applies NSTG theme flags, and records refusals;
5. four **seed cases** — TNBC, GBM, PDAC, dormancy — treated as research objects, not as validated models.

The manuscript reports what the software does on those objects. It does not analyse patient data, does not fit parameters, and does not bind public datasets. It is a thesis about honest computational structure for complex pathology.

## 1.7 What this thesis is not

This is not a medical device. It is not CDS. It is not dosing advice. It is not a cure. It is not Phase II. It is not regulator-ready. It is not an executable NSTG protocol. It does not speak for the Federal Ministry of Health, Nigeria, or for any manufacturer. Official NSTG text is not redistributed from this repository [49,50].

\newpage

# 2 Aims

The aims are computational and architectural.

**Aim 1 — Epistemic separation.** State and enforce a layered boundary — knowledge, evidence, mechanism, parameter, prediction — so that a biologics pathway hypothesis cannot be written as a coefficient by accident.

**Aim 2 — CaseCard as a research object.** Define a strict, extra-key-forbidding schema in which a complex pathological case is authored as YAML: disease framing, ≥2 systemic axes, research-only observables, ≥2 candidate mechanisms each with citations and ≥1 falsifier, ≥1 qualitative NSTG touchpoint, Vancouver citations with real DOIs for primary and review items, and a required honesty disclaimer.

**Aim 3 — NSTG as constraint, not parameter.** Use NSTG 2022 and adjacent Nigerian policy documents only as a structured clinical-knowledge constraint layer [49–53]. Cite them. Do not copy them. Do not map them to `x_cap`, infection-risk weights, doses, or rate constants.

**Aim 4 — Gated exploration.** Implement a PathwaySketch explorer that (i) ranks hypotheses from citations, falsifiers, and qualitative NSTG flags, (ii) lists evidence still required, and (iii) always refuses parameterisation and prediction.

**Aim 5 — Seed the hypothesis space.** Instantiate four complex cases — TNBC metabolic–immune exclusion, GBM invasive hypoxic niche, PDAC stromal barrier, dormant/occult residual disease — as starting research objects with falsifiers.

**Aim 6 — Efficiency without ODE edits.** Show that adding a case is a data-only act (typical local cost: under fifteen minutes plus validation) and that the `pathology_cases` and `pipeline` packages do not import `numpy`, `scipy`, or any ODE module.

**Non-aims.** Fitting ODEs; analysing TCGA, GEO, Ivy GAP, HTAN, or any other public cohort; recommending a product, dose, or schedule; claiming clinical validation; executing NSTG; ingesting patient records.

\newpage

# 3 Background

## 3.1 Complexity science and organised complexity

Weaver's 1948 essay remains the cleanest statement of the problem this thesis inherits [1]. Problems of *simplicity* have few variables. Problems of *disorganised complexity* have so many weakly coupled parts that averages work. Problems of *organised complexity* have an intermediate number of parts whose interrelations matter. Pathology of the kind encoded in the seed cards is organised: a handful of systemic axes (metabolism, immunity, stroma, hypoxia, invasion, vasculature, dormancy, host) coupled by geometry and history, not by a single stochastic ensemble.

Anderson's argument that new scales produce new laws [2], and Goldenfeld and Kadanoff's "simple lessons from complexity" [3], caution against writing a tissue-scale coefficient by renaming a molecule-scale fact. Hartwell, Hopfield, Leibler and Murray recast cell biology in modules rather than lists of genes [4]. Kitano defined systems biology as both a modelling practice and a computational one [5,6]. Barabási, Gulbahce and Loscalzo's network medicine treats disease as a perturbation of a interactome, not as a one-gene lesion [7]. Holland's hidden-order programme and Mitchell's survey of complexity [16,17] add the adaptive piece: the host and the tumour both change the rules while the "experiment" runs.

None of these citations is used here as a licence to simulate a Nigerian patient. They justify a **schema** that keeps host–tumour couplings visible and keeps numbers out until an evidence record — which this stub does not accept — opens a gate.

## 3.2 Complexity in health systems

Plsek and Greenhalgh described health care itself as a complex adaptive system [8]. Ahn and colleagues asked whether systems biology could discipline medical reductionism [9]. Lipsitz treated health care as a complex system with implications for safety and policy [10]. Those papers are about clinics and organisations. They are relevant here only as a reminder that Nigerian guideline and policy documents are **system-level knowledge**. Referral, handling safety, infection, HIV continuity, anaemia, and palliation are not tumour-cell parameters. A computational pipeline that "implements NSTG" by multiplying a toxicity cap has already made a category error. Pull request #1 in this repository explores numeric constraint hints of that kind as a modelling experiment. This thesis refuses them at the CaseCard boundary so that the data layer cannot be used to launder the error.

## 3.3 Why model — and when not to

Wolkenhauer asked "why model?" and answered: to make assumptions inspectable [11]. Aldridge, Burke, Lauffenburger and Sorger set out what a physicochemical model of signalling actually requires: a stated network, conservation laws, and parameters with physical meaning, calibrated on targeted experiments [12]. The CaseCard pipeline does not meet those requirements, and it does not pretend to. A YAML hypothesis with two review citations is knowledge-plus-pointer, not a mass-action system.

Ioannidis's argument that most published findings are false [13] and Begley and Ellis's demand for higher preclinical standards [14] are used here as **negative** design constraints. A ranked `research_score` that rewards citation count and the presence of a falsifier must not be read as an effect size. Popper's requirement that a claim name its own destruction [15] is implemented as a schema rule: every candidate mechanism needs at least one falsifier, or the card is rejected.

## 3.4 Complex pathology as coupled niches

The seed cases are not a convenience sample of "hard cancers." They are four recurring **control motifs**.

**Metabolic–immune exclusion (TNBC).** Bianchini and colleagues reviewed TNBC as a heterogeneous disease with immune and residual-disease axes [29]. Li and colleagues reviewed metabolic pathways that exclude or exhaust antitumour immunity [28]. Gatenby and Gillies restated aerobic glycolysis as a population-level strategy, not a single-cell curiosity [27]. Joyce and Fearon separated exclusion from checkpoint occupancy [23]. Schmid and colleagues reported a randomised evaluation of a checkpoint-class antibody plus chemotherapy in advanced TNBC [30]. That trial is **evidence** in its own protocol population. On a CaseCard it is a citation with `epistemic: evidence`. It is not a coefficient, not a schedule, and not a licence to write `10 mg/kg` into YAML — a string the smuggling scanner refuses.

**Invasive hypoxic niche (GBM).** Hambardzumyan and Bergers defined GBM niches rather than a uniform mass [31]. Brat and colleagues showed that pseudopalisades are hypoxic, protease-expressing, and formed by a migrating population [32]. Giese and colleagues named the migration–proliferation trade-off as a treatment-relevant cost [33]. Semenza reviewed hypoxia-inducible factors as physiology, not as an oncology product class [34]. Bertout, Patel and Simon reviewed oxygen availability in human cancer [35]. Friedl and Wolf reviewed invasion as escape diversity [36]. Vessel count is not delivery; microvascular proliferation can coexist with poor perfusion. That distinction is a hypothesis on the GBM card, not a fitted transport term.

**Stromal barrier (PDAC).** Kleeff and colleagues reviewed pancreatic cancer as a system-level disease [41]. Feig, Neesse and colleagues reviewed the pancreas-cancer microenvironment and stromal biology [39,40]. Olive and colleagues showed, in a mouse model, that Hedgehog-dependent stroma can limit chemotherapeutic delivery [37]. Provenzano and colleagues showed that enzymatic targeting of hyaluronan-rich stroma can ablate a physical barrier in PDAC models [38]. Kalluri, Sahai and colleagues, and Butcher, Alliston and Weaver extended the stromal and mechanical picture [42–44]. Mouse delivery rescue is **animal evidence**. It is not a human parameter and not an NSTG instruction. The PDAC card says so in its disease notes.

**Dormancy / occult residual disease.** Aguirre-Ghiso reviewed models and clinical evidence for cancer dormancy [45]. Sosa, Bragado and Aguirre-Ghiso reviewed disseminated-cell dormancy as an awakening field [46]. Massagué and Obenauf reviewed metastatic colonisation [47]. Giancotti reviewed dormancy and reactivation [48]. Occult means below a detection threshold in a given assay. It does not mean absent, and it does not mean a hidden parameter. Awakening cues are research objects. They are not a reason to provoke residual disease in a person. The dormancy card is written so that a future contributor cannot turn "awakening" into a protocol without first failing the honesty and smuggling checks.

## 3.5 NSTG 2022 as knowledge constraint

The Federal Ministry of Health, Nigeria, published the third edition of the *Nigeria Standard Treatment Guidelines* in 2022 [49]. A Federal Ministry of Information and National Orientation release records an official launch on 24 November 2022 at the Ministry headquarters in Abuja and notes that government communications sometimes use the abbreviation NTSG [50]. This manuscript cites that bibliographic fact. It does **not** quote guideline chapters, tables, or dosing schedules. Official text must be obtained from FMoH or an authorised distributor [49].

Adjacent public policy documents cited on the seed cards, also not redistributed as body text, are:

- Federal Ministry of Health, Nigeria. *Nigeria Essential Medicines List*. 7th edition. 2020 [51].
- Federal Ministry of Health, Nigeria. *Nigeria National Cancer Control Plan 2018–2022*. 2018 [52].
- Federal Ministry of Health, Nigeria. *National Policy on Chemotherapy Safety (ChemoSafe)*. June 2021 [53].

In this architecture NSTG and those adjacent documents are allowed to be **themes**: infection, immunosuppression, HIV, malaria, tuberculosis, anaemia, sickle cell disease, supportive referral, ChemoSafe handling, palliation. The in-repo qualitative catalog (`pipeline/data/nstg_constraint_catalog.yaml`) stores original flags such as `do_not_map_to_rate`, `not_a_dose_cap`, `art_continuity_unmodelled`, `haemoglobin_unobserved`, `referral_not_triage`. It does not store official prose. It does not store `constraint_hints`. If a catalog line disagrees with NSTG 2022, NSTG wins.

What NSTG is not allowed to be here: a parameter source; an executable care protocol; a digital twin of a Nigerian clinic; a reason to withhold or give any product.

## 3.6 Complementary objects in this repository

Pull request #1 (`complexity_science`) integrates a four-state ODE (burden, immune competence, toxicity, exposure) and uses placeholder research-index summaries with numeric constraint hints (`x_cap_scale`, `infection_risk_weight`, `max_immune_depletion_scale`). That design is a different thesis-shaped experiment: *what happens if* guideline-shaped numbers are allowed inside a toy dynamical system, while still disclaiming clinical use.

This thesis (pull request #2 and the present manuscript) is the complementary refusal. The data-first layer cannot carry those keys. A contributor who pastes `x_cap_scale: 0.8` into a CaseCard is rejected before Pydantic validation finishes. The two designs can coexist in one organisation only if the boundary between them is explicit. The evidence gate is that boundary.

\newpage

# 4 Methods

## 4.1 Study design

This is a computational methods and architecture study. There is no human-subjects protocol, no animal protocol, and no chart review. Inputs are YAML research cards and published bibliographic identifiers. Outputs are validation results, PathwaySketch JSON objects, and this manuscript. The analysis unit is the **card**, not the patient.

Reproducible commands, as shipped:

```bash
python -m pip install -e ".[dev]"
python -m pipeline validate --all
python -m pipeline explore --case pathology_cases/cases/tnbc_metabolic_immune_exclusion.yaml
python -m pytest
```

Software identity: Python ≥3.10; `pydantic` ≥2.6; `pyyaml` ≥6.0; `pytest` ≥7.4 for tests. Package version 0.2.0. Schema version 1.0.0. Sketch version 1.0.0. Licence: MIT. The `pathology_cases` and `pipeline` packages are statically checked not to import `numpy`, `scipy`, `ode`, or `dynamics`.

## 4.2 CaseCard schema

A CaseCard is the only object a contributor must author. Machine-readable copies live at `pathology_cases/schema.py` (Pydantic) and `pathology_cases/schema/case_card.schema.json` (JSON Schema). Extra keys are forbidden (`extra = "forbid"`). Required fields and their epistemic layer are:

| Field | Layer | Constraint |
| --- | --- | --- |
| `disease` | knowledge | Name, optional abbreviations, research framing (≥12 characters) |
| `systemic_axes` | knowledge | ≥2 host–tumour couplings; layer in {metabolism, immunity, stroma, hypoxia, vasculature, invasion, dormancy, host}; role in {driver, constraint, context} |
| `observables` | evidence pointers | ≥2; `research_only` must be `true` |
| `candidate_mechanisms` | mechanism | ≥2; each has a hypothesis statement (≥24 characters), a class-level `biologic_axis`, ≥1 citation id, optional NSTG touchpoint ids; `status` is locked to `hypothesis` |
| `falsifiers` | mechanism | ≥2; every mechanism must be covered by ≥1 falsifier (`if_observed` / `then_reject`) |
| `nstg_touchpoints` | knowledge constraint | ≥1; `role` locked to `constraint`; qualitative `constraint_statement` only |
| `citations` | knowledge or evidence | ≥3; Vancouver text; primary/review items require a real DOI (`10.` prefix, no `fake` / `placeholder` / `example.com`); guideline/policy items may omit DOI |
| `disclaimer` | honesty | Must contain "not a medical device", "not dosing", "not a cure", and a CDS/clinical-decision-support negation |

Identifiers are snake_case. Cross-links are checked: mechanism citation ids and NSTG ids must exist; each NSTG touchpoint must point at a citation; falsifier mechanism ids must exist; every mechanism must have a falsifier. Duplicate ids are refused.

Class-level biologic axes (`pipeline/data/biologic_axes.yaml`) are families, not products: `metabolic_checkpoint`, `immune_exclusion`, `immune_checkpoint`, `stromal_barrier`, `hypoxia_adaptation`, `invasive_niche`, `vascular_delivery`, `dormancy_maintenance`, `dormancy_awakening`, `host_comorbidity`.

## 4.3 Parameter-smuggling refusal

`pathology_cases/smuggling.py` walks raw YAML before schema validation. Forbidden keys include, among others: `parameters`, `params`, `ode`, `ode_params`, `dose`, `doses`, `dosing`, `dosage`, `regimen`, `schedule`, `pk`, `pd`, `ec50`, `ic50`, `ed50`, `kcat`, `km`, `kd`, `kon`, `koff`, `clearance`, `half_life`, `cmax`, `cmin`, `auc`, `tmax`, `vmax`, `y0`, `dt`, `solver`, `rhs`, `theta`, `constraint_hints`, `x_cap`, `x_cap_scale`, `infection_risk_weight`, `max_immune_depletion`, `max_immune_depletion_scale`. The last cluster is the explicit refusal of PR #1-style numeric NSTG hints.

String leaves are scanned for dose-like quantities (`10 mg/kg`), PK/PD tokens, and schedule tokens (`q3w`). Citation fields (`vancouver`, `doi`, `pmid`) are exempt from the value scan so that years, volumes, and DOIs remain legal. Any other numeric leaf (integer or float) is refused. The error class is `ParameterSmugglingError`, wrapped as `CaseCardError` by the loader.

This is a documentation and schema control, not a legal device.

## 4.4 NSTG constraint layer

`pipeline/nstg_layer.py` attaches qualitative statements and catalog flags to a card. It does not emit numbers. Infection-ish themes (`infection`, `hiv`, `malaria`, `tb`, `febrile_neutropenia`, `immunosuppression`) plus immune-class axes (`immune_exclusion`, `immune_checkpoint`, `dormancy_awakening`) produce a ranking **penalty of 2**. The function docstring and the emitted note state that the penalty is not a contraindication and not a parameter.

The catalog loader refuses a file that contains `constraint_hints` or `parameters`, or whose `role` is not `constraint_catalog`.

Touchpoint `constraint_statement` fields on the seed cards are original research-index sentences. They name themes (immunosuppression, referral, ChemoSafe, palliation, anaemia, HIV). They do not quote NSTG.

## 4.5 Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction

`pipeline/evidence_gate.py` implements a permanently closed gate. `refuse_parameterization` always returns at least three `RefusedNonParameter` records:

1. source `nstg_touchpoints`, attempted kind `nstg_scale` — NSTG will not emit `x_cap`, infection-risk weights, doses, or other numeric scales;
2. source `candidate_mechanisms`, attempted kind `parameter` — hypotheses are not rate constants, EC50-like knobs, or ODE coefficients;
3. source `explorer`, attempted kind `prediction` — a PathwaySketch does not predict response, survival, or a care pathway for a person.

A fourth refusal is appended if any touchpoint `role` is not `constraint`.

`required_evidence_for` lists, for each mechanism: independent measurement of named observables that can separate the mechanism from its neighbours; an orthogonal assay before any rate, dose, or ODE coefficient is proposed; the closed-gate reason string; and a concrete test of each linked falsifier. This list is a **debt register**, not a completed analysis.

## 4.6 PathwaySketch explorer

`pipeline/explorer.py` is a stub. For each mechanism it computes an integer `research_score`:

- +2 per supporting citation (labelled "knowledge pointers");
- +3 if at least one falsifier is linked;
- −2 if the NSTG infection/immunosuppression heuristic applies;
- +1 for validated CaseCard membership, explicitly "not an efficacy credit".

Blocked mechanisms (no falsifier or no citations) are sorted below hypotheses. Rank is the sort order, not a clinical priority. Each `RankedHypothesis` locks `parameter_status` to `refused` and `prediction_status` to `not_emitted`. Sketch notes state: ranking is bibliographic plus falsifiability plus NSTG flags; no ODE was integrated; `research_score` is not an effect size; no patient record was read.

The explorer never opens the evidence gate. There is no API in this stub that could open it.

## 4.7 Seed-case construction

Four YAML files were authored in `pathology_cases/cases/`. Construction rules:

1. Frame a **systemic** motif, not a person and not a care pathway.
2. Use only published reviews and primaries with Crossref-resolvable DOIs for `kind: primary` and `kind: review`.
3. Cite FMoH documents as `kind: guideline` or `kind: policy` without DOI and without pasting their text [49–53].
4. Write falsifiers as observations that would *reject* the mechanism, not as endpoints that would "prove efficacy."
5. Mark every observable `research_only: true`.
6. Include the standard honesty disclaimer.

DOIs on the seed cards were checked against the Crossref Works API while preparing this manuscript (20 September 2026). All sixteen primary/review DOIs resolved. PMIDs on the cards are digits-only and match the articles as recorded on the cards. No DOI was invented. Guideline and policy items have no DOI field.

No patient-level information was used. No unpublished cohort was used.

## 4.8 Honesty controls

`pathology_cases/honesty.py` ships the epistemic-boundary string, a short disclaimer, and a non-claims list. Schema validation calls `disclaimer_gaps`. Repository tests assert that README, DISCLAIMER, seed cards, and this manuscript contain "not a medical device", "not dosing" / "not a cure" language. The explorer copies the short disclaimer, the boundary, and the non-claims onto every sketch.

## 4.9 What was not done

The following were **not** performed and must not be inferred from the Results:

- numerical integration of any ODE, including the MHBD-4 system in pull request #1;
- parameter estimation, identifiability analysis, or sensitivity analysis;
- survival, response, or receiver-operating-characteristic statistics;
- download or analysis of TCGA, GDC, GEO, cBioPortal, Ivy GAP, HTAN, ICGC, CPTAC, or any other public dataset;
- use of electronic health records or any Nigerian hospital dataset;
- extraction of official NSTG tables;
- recommendation of a biologic product, combination, dose, or schedule;
- a claim of external, prospective, or regulatory validation.

\newpage

# 5 Results

Results are **architectural**. They describe research objects and gate behaviour. They do not describe patients, effect sizes, or predicted benefit.

## 5.1 Four CaseCards validate as research objects

All four seed files load as `CaseCard` schema 1.0.0. Field counts:

| Case id | Systemic axes | Observables | Mechanisms | Falsifiers | NSTG touchpoints | Citations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `tnbc_metabolic_immune_exclusion` | 3 | 2 | 3 | 3 | 3 | 7 |
| `gbm_invasive_niche_hypoxia` | 4 | 2 | 3 | 3 | 3 | 7 |
| `pdac_stromal_barrier` | 4 | 2 | 3 | 3 | 3 | 8 |
| `dormant_occult_disease` | 4 | 2 | 4 | 4 | 4 | 7 |

Every observable has `research_only: true`. Every mechanism has `status: hypothesis`. Every NSTG touchpoint has `role: constraint`. Every primary/review citation has a Crossref-resolvable DOI. Guideline and policy citations name FMoH documents without embedding their text [49–53].

**TNBC axes.** Glycolytic competition (driver), T-cell exclusion (driver), host infection context (constraint). Mechanisms: nutrient starvation of effectors; stromal T-cell privilege; checkpoint pathway as a *research class* (explicitly not a product or coefficient). Falsifiers include metabolically competent intra-nest lymphocytes despite a harsh metabolite niche, intra-nest cytotoxic contact despite intact stroma, and persistent exclusion when the relevant coinhibitory pair is absent.

**GBM axes.** Hypoxic niche (driver), infiltrative front (driver), angiogenic compartment (context), host supportive context (constraint). Mechanisms: hypoxia-coupled adaptive invasion; migration–proliferation trade-off; vessel count is not delivery. Falsifiers include hypoxic but non-migratory palisades, bulk reduction that also clears infiltrate without a motility change, and microvascular density that tracks tracer delivery even under host anaemia.

**PDAC axes.** Desmoplastic matrix (driver), hypoperfusion (driver), immune access (context), host infection/anaemia (constraint). Mechanisms: Hedgehog-dependent stroma limits delivery; hyaluronan raises a transport barrier; the same barrier excludes immunity. Falsifiers include stromal depletion without a delivery change, hyaluronan-low tumours that remain as impermeable as hyaluronan-high tumours, and intra-nest T cells despite intact desmoplasia.

**Dormancy axes.** Cellular quiescence (driver), angiogenic pause (context), immune equilibrium (context), host HIV/infection (constraint). Mechanisms: G0/G1-like pause; angiogenic population pause; immune control without clearance; awakening as a research object that is not a protocol. Falsifiers include uniformly cycling residual cells that die under proliferation-targeted pressure, avascular expansion, immune depletion without outgrowth, and a hypothesized awakening cue that leaves cells occult.

These are starting hypotheses with named destruction conditions. They are not validated models.

## 5.2 PathwaySketch ranking is bibliographic, not predictive

`explore_all()` emitted four sketches. On every sketch the refusal set contained `nstg_scale`, `parameter`, and `prediction`. Every ranked hypothesis had `parameter_status = refused` and `prediction_status = not_emitted`. Sketch notes stated that no ODE was integrated, that `research_score` is not an effect size, and that no patient record was read.

**TNBC sketch.** `nutrient_starvation_excludes_effectors` ranked 1 (`research_score` 8). `checkpoint_axis_as_research_class` and `stromal_tcell_privilege` ranked 2 and 3 (score 6). The two immune-axis items received the NSTG infection/immunosuppression down-rank. Six required-evidence items were listed (union across mechanisms).

**GBM sketch.** `hypoxia_drives_adaptive_invasion` ranked 1 (score 10: three supporting citations). `invasion_proliferation_tradeoff` and `vessel_count_is_not_delivery` ranked 2 and 3 (score 8). No immune-axis penalty applied. Six required-evidence items.

**PDAC sketch.** The two stromal-barrier mechanisms tied on score 8 and sorted by id: `hedgehog_stroma_limits_delivery` then `hyaluronan_raises_transport_barrier`. `barrier_also_excludes_immunity` ranked 3 (score 6) after the NSTG immune-axis penalty. Six required-evidence items.

**Dormancy sketch.** `angiogenic_population_pause` and `cellular_g0_pause` ranked 1 and 2 (score 8). `awakening_is_not_a_protocol` and `immune_control_without_clearance` ranked 3 and 4 (score 6) after the infection/immunosuppression penalty. Seven required-evidence items; eight NSTG constraint strings after catalog flags were appended.

Tied scores are broken by mechanism id. That is a deterministic stub rule, not a claim that angiogenic dormancy is "more true" than cellular quiescence.

The immune-axis penalty did what it was designed to do: it kept the hypotheses in the list and marked them. It did not drop them, did not emit a contraindication, and did not write a weight into an equation.

## 5.3 Parameter-smuggling refusal

Automated tests (`tests/test_parameter_smuggling.py`) demonstrate that clean cards are not the only thing the gate can do. The following mutations of a minimal valid payload are refused:

| Mutation | Refused as |
| --- | --- |
| top-level `parameters: {k: 0.2}` | forbidden key / non-parameter |
| `candidate_mechanisms[0].ode_params` | forbidden key `ode_params` |
| `nstg_touchpoints[0].constraint_hints` with `x_cap_scale` and `infection_risk_weight` | forbidden key `constraint_hints` |
| mechanism statement containing `10 mg/kg` and `q3w` | dose-like / schedule token |
| `disease.notes` set to the float `0.42` | numeric leaf |
| statement containing `EC50` | PK/PD token |
| YAML file containing `x_cap: 1.15` | forbidden key `x_cap` |
| unknown extra key `secret_score` | extra-key forbid |

A card missing a falsifier for a mechanism is rejected by the schema, not by the smuggler. A fake DOI `10.0000/fake-doi` is rejected. A disclaimer that omits the hard non-claims is rejected. An unknown citation id is rejected.

These are positive results about **refusal**. They are the results this thesis is willing to claim.

## 5.4 The evidence gate stays closed on clean cards

On unmodified seed cards — cards that already contain no numbers — `refuse_parameterization` still emits the three standing refusals (NSTG scale, mechanism-as-parameter, explorer-as-prediction). The gate is therefore doing work even when the author is honest. That is deliberate. A clean card is not a licence to parameterise. Required-evidence strings still name orthogonal assays and the named falsifiers. The closed-gate sentence is attached to every mechanism:

> Evidence gate closed: NSTG and CaseCard content are not auto-translated into model parameters. A mechanism is not a coefficient.

No code path in `pipeline/` assigns a float to a rate, a dose, or an initial condition.

## 5.5 Packages do not import an ODE stack

An AST walk of `pathology_cases/` and `pipeline/` finds no import of `numpy`, `scipy`, `ode`, or `dynamics`. A contributor can add a fifth complex case by copying a seed YAML and filling schema fields. They are instructed not to open `pipeline/` or any ODE file. Local cost, as documented: schema authoring under fifteen minutes; validation in seconds; sketch emission in seconds. Turning NSTG into a coefficient is listed as `n/a` — refused.

## 5.6 What the scores are not

If `research_score` were an efficacy credit, TNBC's metabolic hypothesis would be "better" than its checkpoint hypothesis because it avoided an infection-theme penalty. That reading is forbidden by the sketch notes, the honesty module, this Results section, and the disclaimer. The penalty is a visibility flag for host-context themes. The citation bonus is a completeness flag for bibliographic pointers. The +1 membership bonus exists so that a validated card is distinguishable from an ad-hoc string, not so that a disease is awarded a point of benefit.

\newpage

# 6 Discussion

## 6.1 An architectural answer to a complexity problem

The organised-complexity diagnosis [1–7] is easy to recite and hard to operationalise. The usual operationalisation in computational oncology is to add more states to an ODE or more layers to a network and then to decorate the figure with a guideline logo. This thesis operationalises the diagnosis as a **refusal structure**. The system is allowed to see couplings (systemic axes), allowed to see competing explanations (mechanisms), allowed to see what would kill those explanations (falsifiers), allowed to see host-context themes (NSTG touchpoints), and forbidden to emit the one object everyone wants: a number that looks like a dose or a rate.

That is a control-theoretic move. In a poorly identified system the first job is to stop the controller from acting on a mis-specified plant. The evidence gate is that stop.

## 6.2 Why NSTG belongs here at all

A complexity-science project that ignored Nigerian guideline and policy context would treat the host as a generic Western trial body. Infection, anaemia, HIV continuity, sickle-cell comorbidity, chemotherapy-handling safety, and specialist referral are not optional decorations on a TNBC or PDAC card written in this repository [49–53]. They are part of the organised complexity.

The failure mode is to honour that context by inventing `infection_risk_weight = 0.4`. A weight is a parameter. A parameter requires evidence that this stub will not pretend to have [12–14]. Qualitative flags — `hiv_theme`, `art_continuity_unmodelled`, `haemoglobin_unobserved` — keep the theme in the sketch and keep the number out. Down-ranking an immune-axis hypothesis under an immunosuppression theme is a way of saying "this coupling is sensitive; do not skip the host." It is not a way of saying "do not give immunotherapy in Nigeria." The software is not licensed to say the latter, and the cards are written so that a contributor cannot smuggle the former into an equation.

## 6.3 Four motifs, one schema

TNBC, GBM, PDAC, and dormancy look like different specialties. Under the schema they are the same kind of object: a small set of systemic axes, a pair of research-only observables, a handful of mutually criticisable mechanisms, and host constraints. That sameness is the efficiency claim. A fifth case — for example another stromal or exclusion motif — does not require a new explorer. It requires a new YAML file that survives smuggling and honesty checks.

The motifs were chosen because they are **control failures of different kinds**. Metabolic exclusion is a resource-competition failure. GBM invasion is a spatial-escape failure. PDAC stroma is a delivery failure. Dormancy is a detection-and-timing failure. A biologics pathway exploration that only knows how to rank targets will miss all four. A pathway exploration that only knows how to integrate an ODE will be tempted to encode all four as the same four states. The CaseCard keeps the motifs distinct until someone opens a gate this stub does not open.

## 6.4 Relation to hallmarks, cycles, and set points

Hallmarks [18,19], accessory cells [20], microenvironmental regulation [21,22], exclusion [23], the immunity cycle and set point [24,25], and immunotherapy's practical challenges [26] are the knowledge background of the seed cards. The cards do not re-derive those reviews. They point at them and then ask for a falsifier. Schmid et al. [30], Brat et al. [32], Olive et al. [37], and Provenzano et al. [38] are the primary-evidence pointers. They remain pointed-at. They are not re-analysed. They are not meta-analysed. A future worker who wants to parameterise any mechanism is told, in the sketch, to bring an orthogonal assay that is not the paper that suggested the mechanism.

## 6.5 Honesty as a scientific result

It is unfashionable to treat a disclaimer as a result. In this domain the disclaimer is doing scientific work. Ioannidis and Begley–Ellis described environments in which a figure is treated as a fact [13,14]. A PathwaySketch that omitted `refused_non_parameters` would invite that treatment. A CaseCard that accepted `ec50` in a note field would invite it. A catalog that shipped `x_cap_scale` would invite it. The standing refusals on clean cards exist so that a reader of the JSON cannot say "the gate was silent, therefore I may fit." Silence is not consent.

\newpage

# 7 Limitations

**Architectural, not empirical.** No wet-lab measurement, no imaging study, and no clinical cohort was performed. Seed mechanisms may be incomplete, outdated, or wrong. The falsifiers are design prompts, not executed tests.

**Stub ranking.** `research_score` is a small integer heuristic. It is sensitive to how many citations an author attached, not to citation quality beyond "has a real DOI." A poorly conceived mechanism with two reviews outranks a better one with one primary. That is acceptable only because the score is not an effect size and not a care ranking.

**NSTG is not ingested.** The constraint layer is a short original catalog plus author-written touchpoint sentences. It is not a structured extract of NSTG 2022. It is not complete. It may omit themes that a clinician using the official book would consider essential. Completeness belongs to FMoH, not to this repository [49,50].

**Theme matching is lexical.** Infection-ish detection is substring matching on touchpoint `theme` and `id`. A mistyped theme silently avoids the penalty. A future catalog with richer identifiers would still be qualitative.

**No identifiability path.** Even if the gate were opened — it is not — the cards do not contain the measurements Aldridge et al. required for a physicochemical model [12]. Observables are named, not quantified.

**English-language, oncology-weighted seeds.** The four cases are solid-tumour research framings common in the English literature. They are not a map of Nigerian cancer incidence, and they are not a map of infectious-disease complexity except as host constraints.

**Companion ODE is out of scope.** Results here cannot be read as a validation or a refutation of the MHBD-4 model in pull request #1. They only show that the data layer will not feed that model automatically.

**Scholar and indexing limitations.** This manuscript is deposited in a public GitHub repository with a PDF and Highwire meta tags. Indexing by Google Scholar or any other service is not guaranteed and is not a claim of peer review.

**Single author, computational setting.** This is a sole-author computational manuscript. It has not undergone journal peer review at the time of deposit (20 September 2026).

\newpage

# 8 Future work

Future work is stated as **binds**, not as analyses performed here. No result in this manuscript depends on the resources below.

## 8.1 Public datasets as future binds (not analysed)

If a later study opens an evidence record — a new object, not a CaseCard field — the following **named public** resources are the intended first binds. They are listed so that a future author cannot invent a private cohort in the gap. They are not used in Results.

| Intended bind | Why it matches a seed motif | Citation for the resource |
| --- | --- | --- |
| TCGA breast cohort (TCGA-BRCA) molecular portraits | TNBC heterogeneity as published knowledge, not as a re-analysis here | [54] |
| TCGA glioblastoma genomic characterisation | GBM core pathways and later atlas work | [55] |
| TCGA / ICGC pancreatic ductal adenocarcinoma | PDAC genomic context for stromal hypotheses | [56] |
| TCGA Pan-Cancer project | Cross-tumour comparison of axes, still future | [57] |
| NCI Genomic Data Commons | Access layer for TCGA and related programs | [58] |
| cBioPortal | Open exploration of multidimensional cancer genomics | [59] |
| NCBI Gene Expression Omnibus | Functional-genomics archive for orthogonal expression studies | [60,61] |
| Ivy Glioblastoma Atlas Project | Anatomic transcriptional atlas of human GBM niches | [62] |
| Human Tumor Atlas Network | Spatial and temporal tumour transitions at high resolution | [63] |
| ICGC/TCGA Pan-Cancer Analysis of Whole Genomes | Whole-genome context if a future evidence record needs it | [64] |

Rules for any future bind, to be enforced before this repository accepts a parameter object:

1. The bind is a separate evidence record with its own provenance, licence, and split.
2. A CaseCard may *point* at a dataset accession. It may not contain a fitted number from that dataset.
3. NSTG still does not become a coefficient.
4. Negative assays remain detection limits, not proof of clearance (dormancy card).
5. Animal delivery studies remain animal evidence (PDAC card).

No CPTAC, METABRIC, Single Cell Portal, or hospital EHR analysis is claimed. If those resources are used later, they should be named with the same honesty.

## 8.2 Evidence records and a still-closed default

A future schema may introduce an `EvidenceRecord` with measured observables, assay identifiers, and an explicit `gate: still_closed` default. Opening the gate should require a human-signed statement that the record is orthogonal to the papers that suggested the mechanism, that no NSTG sentence was parsed into a float, and that no care recommendation will be emitted. Until that object exists, the stub is the specification.

## 8.3 Richer qualitative constraints

The catalog can grow as original theme lists — malaria, sickle cell, tuberculosis, febrile neutropenia — without becoming a shadow NSTG. Any growth that copies official tables is out of scope and out of licence.

## 8.4 Explorer versions that remain stubs until identified

Ranking can be replaced by a documented multi-criteria rule (coverage of axes, independence of falsifiers, recency of primaries) without introducing units of mg or h−1. If an ODE is ever coupled, it should consume an EvidenceRecord, not a CaseCard. The AST import ban can remain on `pathology_cases/` even if a sibling package integrates equations.

## 8.5 More cases, same schema

Additional organised-complexity motifs — for example myeloid exclusion, tertiary lymphoid structure failure, or treatment-induced dormancy — should be new YAML files. They should not be new Python packages.

\newpage

# 9 Conclusions

Complex pathology is a systemic control problem in Weaver's sense of organised complexity [1]. Biologics pathway exploration that jumps from a review article to a rate constant has skipped the problem.

Problem Statement, Justification of the Study, and Significance of the Study are stated as computational-research sections: the failure mode is epistemic collapse and guideline-as-coefficient; NSTG 2022 is a knowledge constraint, not a source of ODE coefficients; the work is not a medical device [49,50,65–69].

This thesis contributes a data-first in-silico architecture, implemented and tested in this repository, in which:

- a CaseCard holds knowledge, evidence pointers, mechanisms, falsifiers, and qualitative NSTG constraints;
- NSTG 2022 is cited as a knowledge constraint and is never auto-translated into ODE coefficients [49,50];
- four seed cases (TNBC, GBM, PDAC, dormancy) stand as research objects with real, Crossref-checked citations;
- a PathwaySketch explorer ranks bibliographic hypotheses and always refuses parameters and predictions;
- parameter smuggling, including PR #1 numeric scales, is a failing test rather than a hidden feature.

The work is computational research. It is not a medical device, not CDS, not dosing, and not a cure. Named public datasets are future binds, not silent analyses. Official guideline text remains with its publisher.

The honest next measurement is an orthogonal assay against a named falsifier — not a tighter toxicity cap.

\newpage

# References

Vancouver / NLM. Policy: `docs/CITATION_STYLE.md`. Journal items 1–64 were completed from PubMed MEDLINE (authors, NLM abbreviation, volume, issue, pages, PMID) on 20 September 2026; items 65–69 were completed the same way on 21 September 2026. Printed DOIs were resolved on the Crossref Works API on those dates; unverified DOIs are not printed. Guideline and policy items are Internet citations with a cited date. Books have no DOI. No DOI was invented.

1. Weaver W. Science and complexity. Am Sci. 1948;36(4):536-44. PMID: 18882675. Available from: https://www.jstor.org/stable/27826254

2. Anderson PW. More is different. Science. 1972;177(4047):393-6. doi:10.1126/science.177.4047.393. PMID: 17796623

3. Goldenfeld N, Kadanoff LP. Simple lessons from complexity. Science. 1999;284(5411):87-9. doi:10.1126/science.284.5411.87. PMID: 10102823

4. Hartwell LH, Hopfield JJ, Leibler S, Murray AW. From molecular to modular cell biology. Nature. 1999;402(6761 Suppl):C47-52. doi:10.1038/35011540. PMID: 10591225

5. Kitano H. Systems biology: a brief overview. Science. 2002;295(5560):1662-4. doi:10.1126/science.1069492. PMID: 11872829

6. Kitano H. Computational systems biology. Nature. 2002;420(6912):206-10. doi:10.1038/nature01254. PMID: 12432404

7. Barabási AL, Gulbahce N, Loscalzo J. Network medicine: a network-based approach to human disease. Nat Rev Genet. 2011;12(1):56-68. doi:10.1038/nrg2918. PMID: 21164525

8. Plsek PE, Greenhalgh T. Complexity science: The challenge of complexity in health care. BMJ. 2001;323(7313):625-8. doi:10.1136/bmj.323.7313.625. PMID: 11557716

9. Ahn AC, Tewari M, Poon CS, Phillips RS. The limits of reductionism in medicine: could systems biology offer an alternative? PLoS Med. 2006;3(6):e208. doi:10.1371/journal.pmed.0030208. PMID: 16681415

10. Lipsitz LA. Understanding health care as a complex system: the foundation for unintended consequences. JAMA. 2012;308(3):243-4. doi:10.1001/jama.2012.7551. PMID: 22797640

11. Wolkenhauer O. Why model? Front Physiol. 2014;5:21. doi:10.3389/fphys.2014.00021. PMID: 24478728

12. Aldridge BB, Burke JM, Lauffenburger DA, Sorger PK. Physicochemical modelling of cell signalling pathways. Nat Cell Biol. 2006;8(11):1195-203. doi:10.1038/ncb1497. PMID: 17060902

13. Ioannidis JP. Why most published research findings are false. PLoS Med. 2005;2(8):e124. doi:10.1371/journal.pmed.0020124. PMID: 16060722

14. Begley CG, Ellis LM. Drug development: Raise standards for preclinical cancer research. Nature. 2012;483(7391):531-3. doi:10.1038/483531a. PMID: 22460880

15. Popper KR. The logic of scientific discovery. London: Hutchinson; 1959.

16. Holland JH. Hidden order: how adaptation builds complexity. Reading (MA): Addison-Wesley; 1995.

17. Mitchell M. Complexity: a guided tour. Oxford: Oxford University Press; 2009.

18. Hanahan D, Weinberg RA. The hallmarks of cancer. Cell. 2000;100(1):57-70. doi:10.1016/S0092-8674(00)81683-9. PMID: 10647931

19. Hanahan D, Weinberg RA. Hallmarks of cancer: the next generation. Cell. 2011;144(5):646-74. doi:10.1016/j.cell.2011.02.013. PMID: 21376230

20. Hanahan D, Coussens LM. Accessories to the crime: functions of cells recruited to the tumor microenvironment. Cancer Cell. 2012;21(3):309-22. doi:10.1016/j.ccr.2012.02.022. PMID: 22439926

21. Junttila MR, de Sauvage FJ. Influence of tumour micro-environment heterogeneity on therapeutic response. Nature. 2013;501(7467):346-54. doi:10.1038/nature12626. PMID: 24048067

22. Quail DF, Joyce JA. Microenvironmental regulation of tumor progression and metastasis. Nat Med. 2013;19(11):1423-37. doi:10.1038/nm.3394. PMID: 24202395

23. Joyce JA, Fearon DT. T cell exclusion, immune privilege, and the tumor microenvironment. Science. 2015;348(6230):74-80. doi:10.1126/science.aaa6204. PMID: 25838376

24. Chen DS, Mellman I. Oncology meets immunology: the cancer-immunity cycle. Immunity. 2013;39(1):1-10. doi:10.1016/j.immuni.2013.07.012. PMID: 23890059

25. Chen DS, Mellman I. Elements of cancer immunity and the cancer-immune set point. Nature. 2017;541(7637):321-330. doi:10.1038/nature21349. PMID: 28102259

26. Hegde PS, Chen DS. Top 10 Challenges in Cancer Immunotherapy. Immunity. 2020;52(1):17-35. doi:10.1016/j.immuni.2019.12.011. PMID: 31940268

27. Gatenby RA, Gillies RJ. Why do cancers have high aerobic glycolysis? Nat Rev Cancer. 2004;4(11):891-9. doi:10.1038/nrc1478. PMID: 15516961

28. Li X, Wenes M, Romero P, Huang SC, Fendt SM, Ho PC. Navigating metabolic pathways to enhance antitumour immunity and immunotherapy. Nat Rev Clin Oncol. 2019;16(7):425-441. doi:10.1038/s41571-019-0203-7. PMID: 30914826

29. Bianchini G, Balko JM, Mayer IA, Sanders ME, Gianni L. Triple-negative breast cancer: challenges and opportunities of a heterogeneous disease. Nat Rev Clin Oncol. 2016;13(11):674-690. doi:10.1038/nrclinonc.2016.66. PMID: 27184417

30. Schmid P, Adams S, Rugo HS, Schneeweiss A, Barrios CH, Iwata H, et al. Atezolizumab and Nab-Paclitaxel in Advanced Triple-Negative Breast Cancer. N Engl J Med. 2018;379(22):2108-2121. doi:10.1056/NEJMoa1809615. PMID: 30345906

31. Hambardzumyan D, Bergers G. Glioblastoma: Defining Tumor Niches. Trends Cancer. 2015;1(4):252-265. doi:10.1016/j.trecan.2015.10.009. PMID: 27088132

32. Brat DJ, Castellano-Sanchez AA, Hunter SB, Pecot M, Cohen C, Hammond EH, et al. Pseudopalisades in glioblastoma are hypoxic, express extracellular matrix proteases, and are formed by an actively migrating cell population. Cancer Res. 2004;64(3):920-7. doi:10.1158/0008-5472.CAN-03-2073. PMID: 14871821

33. Giese A, Bjerkvig R, Berens ME, Westphal M. Cost of migration: invasion of malignant gliomas and implications for treatment. J Clin Oncol. 2003;21(8):1624-36. doi:10.1200/JCO.2003.05.063. PMID: 12697889

34. Semenza GL. Hypoxia-inducible factors in physiology and medicine. Cell. 2012;148(3):399-408. doi:10.1016/j.cell.2012.01.021. PMID: 22304911

35. Bertout JA, Patel SA, Simon MC. The impact of O2 availability on human cancer. Nat Rev Cancer. 2008;8(12):967-75. doi:10.1038/nrc2540. PMID: 18987634

36. Friedl P, Wolf K. Tumour-cell invasion and migration: diversity and escape mechanisms. Nat Rev Cancer. 2003;3(5):362-74. doi:10.1038/nrc1075. PMID: 12724734

37. Olive KP, Jacobetz MA, Davidson CJ, Gopinathan A, McIntyre D, Honess D, et al. Inhibition of Hedgehog signaling enhances delivery of chemotherapy in a mouse model of pancreatic cancer. Science. 2009;324(5933):1457-61. doi:10.1126/science.1171362. PMID: 19460966

38. Provenzano PP, Cuevas C, Chang AE, Goel VK, Von Hoff DD, Hingorani SR. Enzymatic targeting of the stroma ablates physical barriers to treatment of pancreatic ductal adenocarcinoma. Cancer Cell. 2012;21(3):418-29. doi:10.1016/j.ccr.2012.01.007. PMID: 22439937

39. Feig C, Gopinathan A, Neesse A, Chan DS, Cook N, Tuveson DA. The pancreas cancer microenvironment. Clin Cancer Res. 2012;18(16):4266-76. doi:10.1158/1078-0432.CCR-11-3114. PMID: 22896693

40. Neesse A, Michl P, Frese KK, Feig C, Cook N, Jacobetz MA, et al. Stromal biology and therapy in pancreatic cancer. Gut. 2011;60(6):861-8. doi:10.1136/gut.2010.226092. PMID: 20966025

41. Kleeff J, Korc M, Apte M, La Vecchia C, Johnson CD, Biankin AV, et al. Pancreatic cancer. Nat Rev Dis Primers. 2016;2:16022. doi:10.1038/nrdp.2016.22. PMID: 27158978

42. Kalluri R. The biology and function of fibroblasts in cancer. Nat Rev Cancer. 2016;16(9):582-98. doi:10.1038/nrc.2016.73. PMID: 27550820

43. Sahai E, Astsaturov I, Cukierman E, DeNardo DG, Egeblad M, Evans RM, et al. A framework for advancing our understanding of cancer-associated fibroblasts. Nat Rev Cancer. 2020;20(3):174-186. doi:10.1038/s41568-019-0238-1. PMID: 31980749

44. Butcher DT, Alliston T, Weaver VM. A tense situation: forcing tumour progression. Nat Rev Cancer. 2009;9(2):108-22. doi:10.1038/nrc2544. PMID: 19165226

45. Aguirre-Ghiso JA. Models, mechanisms and clinical evidence for cancer dormancy. Nat Rev Cancer. 2007;7(11):834-46. doi:10.1038/nrc2256. PMID: 17957189

46. Sosa MS, Bragado P, Aguirre-Ghiso JA. Mechanisms of disseminated cancer cell dormancy: an awakening field. Nat Rev Cancer. 2014;14(9):611-22. doi:10.1038/nrc3793. PMID: 25118602

47. Massagué J, Obenauf AC. Metastatic colonization by circulating tumour cells. Nature. 2016;529(7586):298-306. doi:10.1038/nature17038. PMID: 26791720

48. Giancotti FG. Mechanisms governing metastatic dormancy and reactivation. Cell. 2013;155(4):750-64. doi:10.1016/j.cell.2013.10.029. PMID: 24209616

49. Federal Ministry of Health (NG). Nigeria Standard Treatment Guidelines [Internet]. 3rd ed. Abuja: Federal Ministry of Health; 2022 [cited 2026 Sep 20]. Official text is not redistributed by this repository; obtain it from FMoH or an authorised distributor. Launch notice available from: https://fmino.gov.ng/fg-harps-on-effective-use-of-nigeria-standard-treatment-guidelines/

50. Federal Ministry of Information and National Orientation (NG). FG harps on effective use of Nigeria Standard Treatment Guidelines [Internet]. Abuja: Federal Ministry of Information and National Orientation; 2022 Nov 25 [cited 2026 Sep 20]. Available from: https://fmino.gov.ng/fg-harps-on-effective-use-of-nigeria-standard-treatment-guidelines/

51. Federal Ministry of Health (NG). Nigeria Essential Medicines List [Internet]. 7th ed. Abuja: Federal Ministry of Health; 2020 [cited 2026 Sep 20]. Available from: https://cdn.who.int/media/docs/default-source/essential-medicines/national-essential-medicines-lists-(neml)/afro_neml/nigeria-2020.pdf

52. Federal Ministry of Health (NG). Nigeria National Cancer Control Plan 2018-2022 [Internet]. Abuja: Federal Ministry of Health; 2018 [cited 2026 Sep 20]. Available from: https://www.iccp-portal.org/sites/default/files/plans/NCCP_Final%20%5B1%5D.pdf

53. Federal Ministry of Health (NG). National Policy on Chemotherapy Safety (ChemoSafe) [Internet]. Abuja: Federal Ministry of Health; 2021 Jun [cited 2026 Sep 20]. Available from: https://www.nicrat.gov.ng/wp-content/uploads/2023/08/National-Chemosafe-Policy-29-June.pdf

54. Cancer Genome Atlas Network. Comprehensive molecular portraits of human breast tumours. Nature. 2012;490(7418):61-70. doi:10.1038/nature11412. PMID: 23000897

55. Cancer Genome Atlas Research Network. Comprehensive genomic characterization defines human glioblastoma genes and core pathways. Nature. 2008;455(7216):1061-8. doi:10.1038/nature07385. PMID: 18772890

56. Cancer Genome Atlas Research Network. Integrated Genomic Characterization of Pancreatic Ductal Adenocarcinoma. Cancer Cell. 2017;32(2):185-203.e13. doi:10.1016/j.ccell.2017.07.007. PMID: 28810144

57. Weinstein JN, Collisson EA, Mills GB, Shaw KR, Ozenberger BA, Ellrott K, et al. The Cancer Genome Atlas Pan-Cancer analysis project. Nat Genet. 2013;45(10):1113-20. doi:10.1038/ng.2764. PMID: 24071849

58. Grossman RL, Heath AP, Ferretti V, Varmus HE, Lowy DR, Kibbe WA, et al. Toward a Shared Vision for Cancer Genomic Data. N Engl J Med. 2016;375(12):1109-12. doi:10.1056/NEJMp1607591. PMID: 27653561

59. Cerami E, Gao J, Dogrusoz U, Gross BE, Sumer SO, Aksoy BA, et al. The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data. Cancer Discov. 2012;2(5):401-4. doi:10.1158/2159-8290.CD-12-0095. PMID: 22588877

60. Edgar R, Domrachev M, Lash AE. Gene Expression Omnibus: NCBI gene expression and hybridization array data repository. Nucleic Acids Res. 2002;30(1):207-10. doi:10.1093/nar/30.1.207. PMID: 11752295

61. Barrett T, Wilhite SE, Ledoux P, Evangelista C, Kim IF, Tomashevsky M, et al. NCBI GEO: archive for functional genomics data sets--update. Nucleic Acids Res. 2013;41(Database issue):D991-5. doi:10.1093/nar/gks1193. PMID: 23193258

62. Puchalski RB, Shah N, Miller J, Dalley R, Nomura SR, Yoon JG, et al. An anatomic transcriptional atlas of human glioblastoma. Science. 2018;360(6389):660-663. doi:10.1126/science.aaf2666. PMID: 29748285

63. Rozenblatt-Rosen O, Regev A, Oberdoerffer P, Nawy T, Hupalowska A, Rood JE, et al. The Human Tumor Atlas Network: Charting Tumor Transitions across Space and Time at Single-Cell Resolution. Cell. 2020;181(2):236-249. doi:10.1016/j.cell.2020.03.053. PMID: 32302568

64. ICGC/TCGA Pan-Cancer Analysis of Whole Genomes Consortium. Pan-cancer analysis of whole genomes. Nature. 2020;578(7793):82-93. doi:10.1038/s41586-020-1969-6. PMID: 32025007

65. May RM. Uses and abuses of mathematics in biology. Science. 2004;303(5659):790-3. doi:10.1126/science.1094442. PMID: 14764866

66. Saltelli A, Bammer G, Bruno I, Charters E, Di Fiore M, Didier E, et al. Five ways to ensure that models serve society: a manifesto. Nature. 2020;582(7813):482-484. doi:10.1038/d41586-020-01812-9. PMID: 32581374

67. Wilkinson MD, Dumontier M, Aalbersberg IJ, Appleton G, Axton M, Baak A, et al. The FAIR Guiding Principles for scientific data management and stewardship. Sci Data. 2016;3:160018. doi:10.1038/sdata.2016.18. PMID: 26978244

68. Peng RD. Reproducible research in computational science. Science. 2011;334(6060):1226-7. doi:10.1126/science.1213847. PMID: 22144613

69. Stodden V, McNutt M, Bailey DH, Deelman E, Gil Y, Hanson B, et al. Enhancing reproducibility for computational methods. Science. 2016;354(6317):1240-1241. doi:10.1126/science.aah6168. PMID: 27940837


# Disclaimer

**Complexity Science — Thesis #2** is an in-silico / computational research manuscript describing software and research objects in a public repository. It is **not** a medical device, **not** clinical decision support (CDS), **not** a dosing advisor, and **not** a cure.

```text
Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction
```

Nigeria Standard Treatment Guidelines (NSTG, 3rd edition, 2022) appear here only as a structured clinical-knowledge **constraint layer** for pathway exploration. Official NSTG text, the Nigeria Essential Medicines List, the National Cancer Control Plan 2018–2022, and the National ChemoSafe policy are **cited, not redistributed**. NSTG statements are **never** auto-translated into model parameters, doses, rate constants, ODE coefficients, or predictions. If a line in this repository conflicts with official NSTG 2022, NSTG wins.

This work does not diagnose, treat, prevent, cure, or manage any person. It does not recommend a biologic product, dose, schedule, or combination. It does not claim clinical validation, Phase II status, or regulator readiness. It does not encode NSTG as an executable care protocol. It does not emit ODE, PK, or PD parameters from a CaseCard. Ranked items are computational hypotheses awaiting independent falsification.

No patient data were used. Public datasets named in Future work were not analysed. Use is at your own risk. If you are a patient or caregiver, consult a licensed clinician and the official NSTG. If you are a researcher, treat every sketch as a hypothesis awaiting independent falsification.

The author does not speak for the Federal Ministry of Health, Nigeria, or for any manufacturer or regulator.
