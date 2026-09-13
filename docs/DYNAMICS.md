# Pathology dynamics (MHBD-4)

The pipeline integrates a compact four-state nonlinear ODE, the
**multi-scale host–burden dynamics** model (MHBD-4). It is a *computational*
object: useful for attractor geometry, constraint trade-offs, and
falsification design. It is not a digital twin of a named disease.

## State

| Symbol | Meaning | Notes |
| --- | --- | --- |
| \(B\) | Pathological burden | Dimensionless; carrying capacity \(K = 1\) |
| \(I\) | Immune competence | Dimensionless; setpoint \(I^\star\) |
| \(X\) | Host toxicity / physiologic stress | Dimensionless proxy, not a lab analyte |
| \(E\) | Circulating biologic exposure | Concentration-like; driven by \(u(t)\) |

## Equations

\[
\begin{aligned}
\frac{dB}{dt} &= r B \left(1 - \frac{B}{K}\right)
  \frac{1}{1 + \alpha_I I}
  \left(1 + \alpha_X \frac{X}{X + h_X}\right)
  \frac{1}{1 + g_E E}
  - k_c \left(\varepsilon_E \frac{E}{E + h_E} + \varepsilon_I \frac{I}{I + h_I}\right) B \\
\frac{dI}{dt} &= \sigma \frac{I^\star - I}{1 + \gamma_B B}
  - \delta_I I (1 + \eta_X X)
  + \varphi \frac{E}{E + h_\varphi}
  - \psi E I \\
\frac{dX}{dt} &= \chi_E E + \chi_B B + \chi_{IE} \frac{I E}{1 + I} - \delta_X X \\
\frac{dE}{dt} &= -k_{el} E + u(t)
\end{aligned}
\]

- \(g_E\) is an optional growth-suppression gain (TGF-β-trap-like class).
- \(u(t)\) is a prescribed infusion: continuous or periodic pulses.
  Intensity is a **target exposure**; when the pump is on,
  \(u = k_{el} \times \text{intensity}\) so class comparisons are not
  dominated by half-life.
- Immune-mediated clearance (\(\varepsilon_I\)) is slower than direct
  clearance (\(\varepsilon_E\)) because \(I\) has its own timescale — this is
  how checkpoint-like delay appears **without** a fifth state.
- Immune stimulation saturates as \(I \to I_{\max}\) so \(I\) cannot run away.

## Attractors (qualitative)

With \(u \equiv 0\) the untreated system typically has:

1. A **high-burden endemic** equilibrium (large \(B\), suppressed \(I\)) when
   growth outruns immune clearance.
2. A **controlled** equilibrium (small \(B\), recovered \(I\)) if
   \(\varepsilon_I I^\star\) is large enough relative to \(r\).
3. A **toxic-stress** regime in which large \(X\) erodes \(I\) and can
   paradoxically support \(B\) via \(\alpha_X\).

Archetypes in `complexity_science/dynamics/archetypes.py` are different
parameter / initial-condition **basins**, not clinical diagnoses.

## Numerics

`scipy.integrate.solve_ivp` (RK45), `rtol=1e-6`, `max_step` short enough for
pulsed \(u(t)\). States are clipped to non-negative values after each
successful integration. Trajectories that leave a finite box are rejected.

## What the numbers are not

Parameters were chosen for qualitative, reproducible dynamics on a 6-week
horizon. They are **not** fitted to Nigerian or any other clinical cohort.
Changing \(r\) by 20% can reorder ranked effectors — treat rankings as
hypothesis orderings, not effect sizes.
