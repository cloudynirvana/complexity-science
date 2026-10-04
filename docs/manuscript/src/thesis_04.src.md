---
title: "What the Blood Film Allows: Parasite Clearance Curves Identify Infection Staging, Not Ring-Stage Drug Killing"
author: "Kelechi Emeka Ogbonna"
date: "4 October 2026"
subtitle: "Computational research thesis manuscript — Thesis #4"
keywords:
  - malaria
  - Plasmodium falciparum
  - artemisinin partial resistance
  - parasite clearance half-life
  - sequestration
  - structural identifiability
  - practical identifiability
  - evidence gate
lang: en-GB
---

# Front matter {-}

**Thesis #4**

**Status.** Computational research thesis manuscript. It reports mathematical and numerical results on a within-host model of *Plasmodium falciparum*. It is not a clinical study, not a medical device, not clinical decision support, and not treatment guidance. No patient data were used. It has not been peer reviewed.

**Relation to the earlier work.** Thesis #2 built a pipeline whose evidence gate never opens [@thesis2]. Thesis #3 replaced that permanent refusal with a computable admission rule — structural rank, a Cramér–Rao bound, and a two-sided profile likelihood — and applied it to a tumour–immune model [@thesis3]. This thesis applies **the same gate, through the same code** (`evidence_gate/`), to a question in which the measurement is already standardised worldwide and the stakes are African.

**Reproducibility.** Every number and figure comes from `python -m malaria_clearance.analysis` in `https://github.com/cloudynirvana/complexity-science`. Tests: `python -m pytest`. Raw outputs: `docs/manuscript/thesis_04_figures/results.json`.

\newpage

# Abstract {-}

**Problem.** Artemisinin partial resistance is defined in practice by a *slow parasite clearance curve*: serial blood films after treatment, summarised as a clearance half-life [@white_curve; @flegg]. The biological claim attached to that phenotype is specific — that ring-stage parasites survive drug exposure [@saralamba]. Whether the measurement can support the claim has not been asked directly. The question matters now because the phenotype is being used for surveillance in Africa, where partial resistance has emerged independently [@uwimana].

**Approach.** An age-structured within-host model of the 48-hour asexual cycle was built with the features that make the measurement non-trivial: only young parasites circulate and are therefore visible on a film, mature stages sequester, killing is stage-specific, and the drug is eliminated within hours. The model has eight parameters. The evidence gate of Thesis #3 was applied unchanged to five measurement designs, from the routine protocol to one no field laboratory could run.

**Result 1 — the summary is degenerate.** A clearance half-life of 3.1 h is produced by a **50-fold range** of ring-stage killing rates (0.02–1.0 /h) once the mean parasite age at presentation is allowed to vary over a 3.5-hour window. The half-life is jointly determined by drug action and by when in its cycle the infection was sampled, and the two cannot be read apart from the summary.

**Result 2 — the curve measures staging, not killing.** Under the routine design (6-hourly films to 48 h, 20% counting error) **no parameter of the model is admissible**: the ring-stage killing rate has a coefficient-of-variation bound of 1.63. Under the best microscopy-only design examined (4-hourly films plus stage composition, to 72 h) the quantities that become admissible are the *sequestration age* (CV 0.035) and the *mean parasite age at presentation* (CV 0.073). The ring-stage killing rate remains refused (CV 0.56). What the clearance curve determines well is when the infection started and how parasites leave circulation.

**Result 3 — the limit is counting precision, not sampling effort.** Doubling sampling frequency and extending follow-up improves the bound on ring-stage killing by a factor of about 3; the bound scales as 1/σ in the film counting error. Admissibility requires σ ≈ 0.01–0.03, one to two orders of magnitude better than light microscopy. In the model, ring-stage killing becomes admissible only in an idealised design that also requires total parasite biomass, which is not observable in a patient.

**Result 4 — the curve cannot exclude full susceptibility.** Under the routine design the expected profile likelihood of the ring-stage killing rate is flat (Δχ² < 0.02) from the reference value up to a 3.5-fold increase, which approaches full mature-stage susceptibility. It rises on the resistant side only, giving a weak lower bound and no upper bound.

**Interpretation.** These results reproduce, from the measurement alone, the historical difficulty that drove the field to new assays: slow clearance *in vivo* without a corresponding *in vitro* correlate [@dondorp], resolved only by a ring-stage survival assay [@witkowski] and a molecular marker [@ariey]. The gate says why that was necessary rather than unlucky. The practical reading is that clearance half-life is sound as a **population screening signal** and unsound as a **parameter estimate**, and that a cheap addition — recording ring/trophozoite composition, which a microscopist already sees — sharply improves what the curve determines about staging, though not about drug killing.

\newpage

# 1 Introduction

## 1.1 A phenotype defined by a curve

Artemisinin and its derivatives underpin first-line malaria treatment. Reduced susceptibility was first detected in western Cambodia not as a change in laboratory drug sensitivity but as a change in how quickly parasites disappeared from blood films: median clearance times of 84 h in Pailin against 48 h in north-western Thailand, with no corresponding difference on conventional *in vitro* testing [@dondorp]. A multi-site study then mapped clearance half-lives from 1.9 h in the Democratic Republic of the Congo to 7.0 h on the Thailand–Cambodia border and linked slow clearance to mutations in *kelch13* [@ashley; @ariey]. The phenotype has since been standardised: fit the log-linear segment of the parasitaemia–time curve and report its half-life [@white_curve; @flegg].

The mechanistic account of what that curve means is also specific. Modelling of the Cambodian and Thai cohorts concluded that the concentration–effect relationship is conserved for trophozoites and schizonts but variable for **rings**, so artemisinin partial resistance is reduced killing of young circulating parasites [@saralamba]. That account is now the textbook one, and it is supported independently by a ring-stage survival assay that distinguishes slow- from fast-clearing isolates [@witkowski].

The relevance has moved to Africa. In Rwanda, *kelch13* R561H was associated with day-3 parasitaemia in a therapeutic efficacy study [@uwimana]. Nigerian sites contributed to the multi-site clearance study [@ashley]. Surveillance across the continent now rests on clearance measurements made with light microscopy.

## 1.2 The question this thesis asks

A measurement that defines a phenotype carries an implicit claim: that the quantity of interest can be recovered from it. For parasite clearance that claim has not been tested directly. The question is one of identifiability, not of biology [@raue; @villaverde; @simpson]:

> Given serial counts of *circulating* parasites at the sampling frequency and counting precision a field study actually achieves, which parameters of a stage-structured within-host model can be determined — and is stage-specific killing among them?

Three features of the system make the answer non-obvious. First, **a blood film does not see the infection**: mature parasites sequester, so the observable is a shifting, age-filtered slice of the parasite population. Second, **the curve's shape depends on when the patient presented** within the 48-hour cycle, which is unknown and uncontrolled. Third, **counting precision is poor**: a film read is a noisy estimate, and the noise does not shrink with more films.

## 1.3 Problem Statement

Artemisinin partial resistance is surveilled by a scalar — the parasite clearance half-life — that is interpreted as a statement about stage-specific drug killing. Between the measurement and that interpretation sits an unexamined inference. A within-host model that generates a clearance curve contains killing parameters, staging parameters, sequestration parameters and pharmacokinetic parameters, all of which shape the observed decline. If several of these trade off against each other within the precision of a blood film, then the clearance half-life is not a measurement of drug killing; it is a measurement of a combination, and attributing it to the drug is an error of the kind Thesis #2 named: treating a *measurement* as though it were a *parameter* [@thesis2].

The specific gap is that no published analysis states, for the standard protocol, which parameters of a stage-structured clearance model are structurally identifiable, which are practically identifiable at realistic noise, and what measurement would be required to admit the ring-stage killing rate. Without that statement, a surveillance programme cannot know whether a slow curve in a Nigerian or Rwandan clinic reports a resistant parasite, a late-presenting patient, or a hard-to-read film.

## 1.4 Justification of the Study

The study is justified first because the inference is load-bearing. Clearance measurements inform national treatment policy. If the phenotype is a composite, that should be stated precisely, not suspected informally.

It is justified second because the history already contains the evidence. Dondorp and colleagues found slow clearance *in vivo* with no *in vitro* correlate [@dondorp]; Witkowski and colleagues opened their report by naming the "absence of *in-vitro* and *ex-vivo* correlates" as the obstacle to studying the phenotype [@witkowski]. An identifiability analysis can show whether that was an accident of assay technology or a property of the measurement, and the second explanation has different consequences: it predicts that no refinement of the clearance protocol would have closed the gap.

It is justified third because the remedy may be cheap. Stage composition — what fraction of counted parasites are rings rather than trophozoites — is visible on the same film and is already recorded in some protocols. If it materially changes what the curve determines, that is an actionable finding for a laboratory in Awka or Kigali, requiring no new instrument.

It is justified fourth by method. Aldridge and colleagues set out what a physicochemical model needs before its parameters mean anything [@aldridge]; Wolkenhauer asked that models make assumptions inspectable [@wolkenhauer]; May warned against mistaking the model for the organism [@may]; Saltelli and colleagues asked that limits be made visible [@saltelli]. Applying a gate that fails closed is the operational form of those arguments.

## 1.5 Significance of the Study

**For malaria surveillance.** The thesis distinguishes two uses of the clearance half-life that are currently conflated. As a **screening signal** — a population-level flag that something has changed at a site — it is defensible, and its degeneracy does not matter much, because a shift in the distribution of half-lives across many patients is still informative. As a **parameter estimate** about an individual infection's drug susceptibility, it is not supported by the measurement.

**For African programmes specifically.** The result argues for pairing clearance surveillance with a stage-resolved readout and with the assays that do measure the phenotype directly [@witkowski; @ariey]. It also quantifies what extra microscopy buys, so that a programme with a fixed budget can see that more films do not substitute for a different observable.

**For the method.** It demonstrates that the gate of Thesis #3 is not specific to one model [@thesis3]. The same code, unchanged, judges a tumour–immune system and a parasite clearance protocol. In both, the parameter the field most wants to estimate is the one the measurement refuses.

**What this significance is not.** This is a model. It is not a clinical study, and it does not evaluate any drug, regimen or patient. No parameter is fitted to patient data, and no treatment recommendation follows from it.

\newpage

# 2 Aims

**Aim 1 — Build a minimal honest model.** Represent the 48-hour cycle, sequestration, stage-specific killing and fast drug elimination with the smallest model that reproduces published clearance half-lives.

**Aim 2 — Test the summary.** Determine whether the clearance half-life separates ring-stage killing from infection staging.

**Aim 3 — Apply the gate.** Determine, for five measurement designs, which parameters are structurally and practically identifiable.

**Aim 4 — Price the remedy.** Quantify how the bound on ring-stage killing depends on sampling frequency, follow-up length, added observables and counting precision.

**Non-aims.** Fitting to patient data; estimating resistance in any population; evaluating any drug or regimen; replacing *kelch13* genotyping or ring-stage survival assays.

\newpage

# 3 Model

## 3.1 Structure

The state is the parasite age distribution across 48 one-hour bins, in parasites/µL. Each hour, parasites are killed, then age by one bin; parasites leaving the last bin burst and re-invade, multiplied by the parasite multiplication rate.

| Symbol | Meaning | Role |
| --- | --- | --- |
| *k*~ring~ | maximum killing rate of ring stages (/h) | **the resistance parameter** |
| *k*~mature~ | maximum killing rate of mature stages (/h) | drug action |
| *EC*~50~ | concentration at half-maximal killing | drug action |
| PMR | parasite multiplication rate per cycle | parasite growth |
| *μ*~0~ | mean parasite age at presentation (h) | **staging** |
| *σ*~0~ | spread of the initial age distribution (h) | staging (synchronicity) |
| *a*~seq~ | age at which parasites sequester (h) | observation process |
| *k*~e~ | drug elimination rate (/h) | pharmacokinetics |

Three modelling choices carry the biology that makes the measurement hard.

**Sequestration.** The circulating fraction falls smoothly around *a*~seq~, so a blood film counts young parasites and misses mature ones. The observable is therefore an age-filtered projection of the state, not the state.

**Stage-specific killing.** The maximum killing rate rises smoothly from *k*~ring~ to *k*~mature~ across the ring-to-trophozoite transition, following the mechanism proposed for partial resistance [@saralamba].

**Fast elimination.** Drug concentration decays with rate *k*~e~ after each daily dose, so exposure is a series of short pulses. Which parasites are rings *during a pulse* therefore depends on *μ*~0~ — this is the coupling that produces the degeneracy reported below.

## 3.2 Calibration, and what it is not

Parameters were chosen so that the model spans published clearance half-lives, not fitted to any dataset. With full ring killing the model gives a half-life of **1.84 h**, matching the fastest site in the multi-site study (1.9 h, Democratic Republic of the Congo) [@ashley]. With strongly reduced ring killing it gives **3.77 h**. The reference phenotype used throughout — partial ring resistance — gives **3.12 h**.

The model therefore covers the lower and middle part of the published 1.9–7.0 h range and does **not** reach the extreme Thailand–Cambodia values. That is a limitation, stated here rather than hidden: the degeneracy and identifiability results below are properties of this model over this range, and the extreme slow-clearing phenotype is outside it.

![**Figure 1.** What a parasite clearance curve can and cannot measure. **A**, the 48-hour cycle: rings circulate and are visible on a film, mature stages sequester and are not. **B**, the standard protocol and the phenotype it reports. **C**, the evidence gate, applied through the same code as Thesis #3. The verdict strip gives the coefficient-of-variation bound on the ring-stage killing rate under each design; the panel is generated from `results.json`.](thesis_04_figures/fig1_overview.png)

\newpage

# 4 Methods

## 4.1 Simulation

The age distribution is marched hourly. Within each hour the drug effect is averaged over twelve sub-samples, because concentration changes rapidly relative to the hour. Killing is applied as exponential decay at the age-specific maximum rate scaled by the saturating concentration–effect term; parasites then age by one bin, and the oldest bin re-invades multiplied by PMR. The initial age distribution is Gaussian in age, computed with a shifted exponent so that narrow or displaced distributions cannot underflow during a fit.

## 4.2 Observables

Three observables are distinguished:

- **circ** — circulating parasitaemia: what a blood film counts;
- **stage** — mean age of circulating parasites: a proxy for ring/trophozoite composition, which a microscopist reads from the same film;
- **total** — total parasite biomass including sequestered parasites: **not observable in a patient**, included only to price what it would buy.

## 4.3 Clearance half-life

The half-life is the slope of the log-linear decline, fitted between the peak of the observed curve (excluding any initial lag) and the earlier of the curve's nadir or the detection limit. This follows the intent of the standard estimator [@flegg; @white_curve], not its implementation.

## 4.4 Measurement designs

| Design | Observables | Sampling | Follow-up | σ | Observations |
| --- | --- | --- | --- | --- | ---: |
| standard | circ | 6-hourly | 48 h | 0.20 | 9 |
| intensive | circ | 4-hourly | 72 h | 0.20 | 19 |
| + stage | circ, stage | 6-hourly | 48 h | 0.20 | 18 |
| + stage, intensive | circ, stage | 4-hourly | 72 h | 0.20 | 38 |
| idealised | circ, stage, total | 2-hourly | 96 h | 0.05 | 147 |

σ is the multiplicative counting error of a film on the log scale. **0.20 is generous** for light microscopy at the densities concerned; 0.05 is better than any field laboratory, and is used only to show what would be required.

## 4.5 The gate

The gate is applied through `evidence_gate/`, the same module used in Thesis #3 [@thesis3]. Sensitivities of log-observations to log-parameters are taken by central differences; the Fisher information is *S*ᵀ*S*/σ²; rank is computed with a relative singular-value tolerance of 10⁻⁶, and any parameter loading on the null space receives an infinite bound. A parameter is admissible only if it is off the null space (**structural**), its Cramér–Rao coefficient-of-variation bound is below 0.10 (**practical**), and its expected profile likelihood crosses 3.84 on both sides (**shape**) [@raue; @villaverde; @simpson]. Profiles were computed on noise-free synthetic data with the other seven parameters refitted in log space.

## 4.6 Software

Python ≥ 3.10, NumPy, SciPy [@scipy], Matplotlib, cairosvg. Fixed grids and fixed designs; the full analysis takes about a minute. Twelve automated tests cover the model, the degeneracy, and the gate verdicts, and four more test the gate itself on two analytically known models — one identifiable, one deliberately degenerate.

\newpage

# 5 Results

## 5.1 One half-life, many biologies

Ring-stage killing and infection staging trade off against each other in the half-life. Searching a grid of ring-stage killing rates and mean presentation ages for parameter sets whose half-life falls within 0.05 h of 3.1 h returns 194 matches. The extremes differ 50-fold in the parameter of interest:

| | *k*~ring~ (/h) | *μ*~0~ (h) | half-life (h) |
| --- | ---: | ---: | ---: |
| strongly resistant, late presentation | 0.020 | 21.5 | 3.12 |
| fully susceptible, slightly earlier presentation | 1.000 | 18.0 | 3.14 |

A 3.5-hour difference in when the patient presented absorbs a 50-fold difference in ring-stage drug killing. The two infections are biologically opposite and clinically identical on this summary.

![**Figure 2.** Clearance curves at three levels of ring-stage killing. Reduced ring killing prolongs clearance, as reported, but the curves differ in shape as well as slope.](thesis_04_figures/fig2_curves.png)

![**Figure 3.** Clearance half-life over ring-stage killing and mean parasite age at presentation. Contours are iso-half-life curves; the marked pair has the same half-life across a 50-fold range of ring-stage killing.](thesis_04_figures/fig3_surface.png)

## 5.2 The standard protocol admits nothing

Under the routine design — 6-hourly films to 48 h at 20% counting error — the sensitivity matrix is full rank, so nothing is *structurally* unidentifiable. Practically, every bound is far too wide:

| Parameter | standard | intensive | + stage | + stage, intensive | idealised |
| --- | ---: | ---: | ---: | ---: | ---: |
| *k*~ring~ | 1.63 | 0.66 | 1.24 | 0.56 | **0.033** |
| *k*~mature~ | 3.73 | 0.62 | 1.97 | 0.58 | **0.034** |
| *EC*~50~ | 10.6 | 4.00 | 7.09 | 3.35 | 0.188 |
| PMR | 25.5 | 2.55 | 6.61 | 1.61 | **0.025** |
| *μ*~0~ | 0.384 | 0.143 | 0.110 | **0.073** | **0.007** |
| *σ*~0~ | 1.86 | 0.247 | 0.250 | 0.118 | **0.011** |
| *a*~seq~ | 0.392 | **0.057** | **0.066** | **0.035** | **0.004** |
| *k*~e~ | 2.55 | 1.01 | 1.63 | 0.807 | **0.041** |
| **admissible** | **0 of 8** | 1 of 8 | 1 of 8 | 2 of 8 | 7 of 8 |

*Table 1. Cramér–Rao coefficient-of-variation bounds. Bold: below the 0.10 gate threshold.*

Three readings follow.

**The routine protocol determines nothing to 10%.** Its best bound is the sequestration age at 0.392, and the ring-stage killing rate sits at 1.63 — an uncertainty larger than the quantity.

**What the curve does determine is the observation process and the staging.** The first parameters to become admissible as the design improves are *a*~seq~ (sequestration age) and *μ*~0~ (mean age at presentation). Both describe *when parasites are visible*, not *how well the drug works*. This is the formal counterpart of Section 5.1.

**Drug parameters remain refused across every microscopy-only design.** Ring-stage killing improves from 1.63 to 0.56 — a factor of about three for a four-fold increase in observations — and never reaches the threshold. The pharmacological parameters fare worst of all: *EC*~50~ stays above 3 in every microscopy-only design, and the parameter vector shows the wide spread of sensitivities that Gutenkunst and colleagues described as sloppiness, in which most directions in parameter space are nearly invisible to the data [@gutenkunst].

![**Figure 4.** Coefficient-of-variation bound per parameter and design. A tick marks bounds below the gate threshold.](thesis_04_figures/fig4_gate.png)

## 5.3 The binding constraint is counting precision

Bounds scale as 1/σ in the film counting error, so the question of what would admit the ring-stage killing rate has a direct answer:

| σ (counting error) | standard | + stage, intensive |
| ---: | ---: | ---: |
| 0.40 | 3.26 | 1.13 |
| 0.20 | 1.63 | 0.56 |
| 0.10 | 0.81 | 0.28 |
| 0.05 | 0.41 | 0.14 |
| 0.03 | 0.24 | 0.08 |
| 0.01 | 0.08 | 0.03 |

*Table 2. CV bound on the ring-stage killing rate against counting error.*

The threshold is crossed at σ ≈ 0.01 for the routine design and σ ≈ 0.03 for the best microscopy-only design — one to two orders of magnitude better than light microscopy, which operates around σ ≈ 0.15–0.45. Sampling effort cannot substitute: quadrupling observations bought a factor of three, while reaching the threshold requires a factor of five to twenty in precision.

In the model, the ring-stage killing rate becomes admissible only in the idealised design, which additionally requires **total parasite biomass**. That quantity includes sequestered parasites and is not observable in a patient.

![**Figure 5.** What it would take to measure ring-stage killing. The shaded band marks where light microscopy operates.](thesis_04_figures/fig5_noise.png)

## 5.4 The curve cannot exclude a fully susceptible parasite

Under the routine design the expected profile likelihood of the ring-stage killing rate is asymmetric. Moving *down* from the reference, Δχ² reaches 8.3 at a 4.5-fold reduction, so the data exclude very strong resistance. Moving *up*, Δχ² stays below 0.02 across the whole grid to a 3.5-fold increase — a ring-stage killing rate of 0.87 /h against a mature-stage rate of 1.0 /h, which is near-complete susceptibility. The profile rises only beyond that, where ring killing would have to exceed mature-stage killing and the model becomes implausible.

The clearance curve from a single slow-clearing patient therefore supports a weak lower bound on susceptibility and no upper bound. It cannot, on its own, rule out that the parasite is fully artemisinin-sensitive and the patient simply presented late.

## 5.5 Negative and limiting results

- **No structural degeneracy was found.** All five designs are full rank. The failure is practical, not structural — which matters, because practical failures can in principle be fixed by better measurement, and this one would require precision beyond the instrument.
- **Stage composition does not rescue the drug parameters.** Adding it at routine sampling improves the ring-stage bound only from 1.63 to 1.24, while improving *μ*~0~ from 0.384 to 0.110. It buys staging, not killing.
- **The model does not reach the slowest published half-lives.** Its range is roughly 1.8–3.8 h against a published 1.9–7.0 h [@ashley]. Results are claimed only over the range the model covers.

\newpage

# 6 Discussion

## 6.1 Why the field needed a different assay

The historical sequence is now legible as a measurement problem rather than an accident. Slow clearance was observed *in vivo* with no corresponding *in vitro* signal [@dondorp]. A ring-stage survival assay, applied to 0–3 h ring-stage parasites, then separated slow- from fast-clearing isolates and correlated with *in vivo* half-life [@witkowski]. A molecular marker followed [@ariey].

The analysis here says that the first step could not have succeeded by refinement. The clearance curve, at achievable precision, does not determine ring-stage killing; it determines when parasites become invisible and when the infection was sampled. An assay that exposes *synchronised ring-stage parasites to drug directly* removes the staging nuisance by construction — it fixes *μ*~0~ and *σ*~0~ experimentally. From an identifiability standpoint that is exactly the right move, and it explains why the clearance curve and the survival assay are complements rather than alternatives.

## 6.2 What the half-life is good for

Nothing here argues against measuring clearance. It argues against one reading of it.

As a **screening signal**, the half-life is sound. Staging varies between patients but there is no reason for it to shift systematically at a site between surveys, so a change in the distribution of half-lives across many patients remains informative about a change in parasites. That is how the multi-site mapping was used [@ashley], and that use survives this analysis intact.

As a **parameter estimate** for an individual infection — "this parasite has reduced ring-stage susceptibility" — it is not supported. Section 5.4 makes the point sharply: the routine measurement cannot exclude full susceptibility in a slow-clearing patient.

## 6.3 What a programme in Awka or Kigali could do

Three things follow that cost little.

1. **Record stage composition.** It is visible on the same film and sharply improves what the curve determines about staging (*μ*~0~ from 0.384 to 0.073, *a*~seq~ from 0.392 to 0.035 under intensive sampling). It will not measure drug killing, and should not be advertised as doing so.
2. **Report time since fever onset.** The degeneracy in Section 5.1 runs through *μ*~0~. Any covariate that constrains staging reduces it.
3. **Pair clearance with a direct phenotype or genotype** where feasible [@witkowski; @ariey; @uwimana]. The gate says these are not redundant with clearance; they measure what clearance cannot.

## 6.4 Relation to the earlier theses

Thesis #2 refused all parameterisation by rule [@thesis2]. Thesis #3 replaced the rule with a computation and found that in a tumour–immune model the kill rate was refused under every design [@thesis3]. Here, in an unrelated system with a worldwide-standardised measurement, the pattern repeats: the parameter the field most wants — the drug-killing rate — is the one the measurement refuses, while nuisance quantities are determined well. That both cases came out the same way is not proof of a general law, and this thesis does not claim one. It does suggest where to look: in systems where the observable is a filtered projection of the state, the filter's parameters are easier to identify than the dynamics behind it.

\newpage

# 7 Limitations

- **One model, one reference point.** Eight parameters, one reference phenotype. The bounds are local and reported at that point.
- **Range.** The model does not reach the slowest published half-lives (Section 3.2), so conclusions are confined to the 1.8–3.8 h range it covers.
- **Simplifications.** One parasite population, no host immunity, no partner drug, no pyrogenic or splenic clearance, no inter-patient variation, instantaneous drug input, and sequestration as a deterministic function of age. Real infections are less synchronous and less tidy.
- **Idealised noise.** Independent log-normal counting error. Real film reading has density-dependent error, reader effects, and a detection limit that censors the tail — all of which make the measurement worse, not better, so the direction of the conclusion is conservative.
- **Local methods.** Fisher bounds are linearisations; profiles were refitted from the true values and may miss distant optima.
- **No data.** Nothing here is fitted to or validated against a patient cohort. The next honest step is to run the gate alongside a published clearance dataset and report verdicts next to any estimate.
- **Single author, unreviewed.**

\newpage

# 8 Future work and falsifiers

## 8.1 Falsifiers

| Claim | Would be falsified by |
| --- | --- |
| The half-life conflates ring killing with staging | a demonstration that half-life is insensitive to presentation time once realistic synchronicity is imposed |
| Routine protocols cannot identify ring-stage killing | an estimator recovering *k*~ring~ to 10% from 6-hourly films at realistic noise |
| Stage composition buys staging, not killing | stage data materially tightening the ring-stage bound in a richer model |
| Precision, not effort, is binding | sampling schedules reaching the threshold without improving σ |

## 8.2 Next steps

1. **Run the gate against a published clearance dataset**, reporting verdicts beside any fitted value.
2. **Hierarchical extension.** Across many patients, staging varies randomly while drug parameters are shared; a population model may identify killing where a single curve cannot. This is the most promising route and the natural next thesis.
3. **Optimal design.** Choose sampling times to maximise information on *k*~ring~ specifically, and report the best achievable bound at feasible σ.
4. **Model enrichment.** Host immunity, partner drug, asynchronous infections — each adds parameters, so each must re-enter the gate.
5. **Link to Thesis #2's CaseCards** so that a card may point at a gate verdict without containing a number [@thesis2].

\newpage

# 9 Conclusions

A phenotype is only as good as the measurement that defines it. Parasite clearance half-life is used worldwide to track artemisinin partial resistance, and the biological claim attached to it is that ring-stage parasites survive drug exposure.

In a stage-structured within-host model, that claim is not recoverable from the measurement. The same half-life arises from a 50-fold range of ring-stage killing rates once presentation time is free. Under the routine protocol no parameter is admissible, and the first quantities that become admissible under richer designs are the sequestration age and the mean parasite age at presentation — the observation process, not the drug. The binding constraint is counting precision, which would have to improve by one to two orders of magnitude, and the routine curve cannot even exclude a fully susceptible parasite.

This does not devalue clearance surveillance; it locates its strength. The half-life is a population screening signal. The phenotype itself requires a ring-stage survival assay or a molecular marker — which is what the field, by a harder route, already discovered.

The epistemic point is the one carried through this series: *Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction*, and the step from Evidence to Parameter is decided by what was measured [@thesis2; @thesis3; @popper].

\newpage

# Data and code availability {-}

All code, outputs and figures are in `https://github.com/cloudynirvana/complexity-science` under the MIT licence. Reproduce with `python -m pip install -e ".[dev]"`, then `python -m malaria_clearance.analysis` and `python -m pytest`. Raw numerical outputs: `docs/manuscript/thesis_04_figures/results.json`. In keeping with reproducible-research and FAIR practice [@peng; @fair], the manuscript is generated from a keyed source file by `docs/manuscript/src/build_thesis.py`.

# References {-}

Vancouver / NLM. Journal items were checked against PubMed MEDLINE records (authors, NLM abbreviation, volume, issue, pages, DOI, PMID) on 4 October 2026. Where PubMed records an electronic-publication date preceding the print issue, the print issue year is used. No DOI was invented.

<!-- REFERENCES -->

# Disclaimer {-}

This is a computational research manuscript about a mathematical model. It is **not** a medical device, **not** clinical decision support, and **not** treatment guidance. No patient, cohort or clinical data were used, and no parameter corresponds to a measured clinical quantity. Nothing here recommends or discourages any antimalarial drug, dose, regimen or surveillance decision. Malaria is a life-threatening illness; diagnosis and treatment are matters for qualified clinicians following national guidelines.
