# Report 03 — KAN-assisted quantum detector tomography

**Subject:** Using a Kolmogorov-Arnold Network as a denoising interpolator in front of the
semidefinite-programming step of optical detector tomography.

**Source folder:** `KAN_assisted tomography/`
**Notebooks:** 7
**Data:** Supplementary files MOESM3, MOESM4, MOESM5 from Zhang et al., *Mapping coherence
in measurement via full quantum tomography of a hybrid optical detector*, Nature Photonics
6, 364 (2012)
**Filed:** 2026-09-09

---

## 1. The problem

Zhang et al. characterise a weak-homodyne optical detector by reconstructing its POVM
element `Π̂₁` — the operator linking an input coherent state to the probability the detector
registers one click. From measured click statistics they solve an ill-conditioned
semidefinite program to recover `Π̂₁`, after which the click probability for any probe
follows from the Born rule, `p₁ = ⟨α|Π̂₁|α⟩`.

The datasets are grids of `(|α|², θ)` probe settings with 0-click and 1-click counts over
roughly 128,000 laser shots per row. The label is the empirical probability
`p₁ = #1-click / (#0-click + #1-click)`.

| File | Rows | `|α|²` range | `p₁` range |
|---|---|---|---|
| MOESM3 | 4400 | 0.044 – 56.2 | 0.006 – 0.997 |
| MOESM4 | 3720 | 0.178 – 38.5 | 0.001 – 0.997 |
| MOESM5 | 4760 | 0.057 – 166.9 | 0.430 – 0.996 |

These are three physically different detector configurations from the paper's Figure 2,
differing in local-oscillator strength and mode overlap.

The folder asks three questions in sequence, and the third is where the contribution is.

---

## 2. Question one — can a KAN replace the SDP?

`KAN_assisted_tomography_MOESM3.ipynb` learns the direct map `(|α|², θ) → p₁` with a KAN,
skipping the POVM entirely, and puts it against a faithful reimplementation of the paper's
SDP on the same 80/20 split.

Model choices, all reported with reasons: architecture `[2,3,1]` (a single hidden node fails
because the fringe shape changes with brightness, an interaction one node cannot carry),
`log1p(|α|²)` compression then normalisation to [-1,1] using training statistics only, and a
sigmoid output to keep predictions in [0,1].

Tuning path:

| Stage | Train RMS | Test RMS |
|---|---|---|
| baseline, 100 steps, grid 5 | 0.0085 | 0.0087 |
| longer, 150 steps, grid 5 | 0.0079 | 0.0078 |
| refine to grid 10 | 0.0069 | 0.0071 |

The SDP side reconstructs `Π̂₁` at truncation d = 90 (max leakage 2.0 × 10⁻⁵), four leading
off-diagonal bands, quadratic smoothness regulariser at γ = 0.5, positivity as
`0 ⪯ Π̂₁ ⪯ I`. It solves to optimality in 11.5 s and reproduces the paper both numerically
and structurally: eigenvalues in [0.0061, 0.9996], diagonal rising 0.507 → 0.986 (number
sensitivity), leading off-diagonal peaking at 0.251 in magnitude (phase sensitivity). That
is the Figure 2a signature.

Head to head on the identical 880-point test set:

| Method | Test RMS | Encodes physics? |
|---|---|---|
| SDP / POVM (paper's method) | 0.00647 | yes — positivity, Born rule, coherent-state kernel |
| Tuned KAN | 0.00708 | no — two inputs and spline edges |
| Paper reported | ~0.005 | — |

**A KAN with no physics lands within 10% of the physics-constrained reconstruction.** Grid
refinement was the decisive lever, moving test RMS from 0.0074 to 0.0069 in one step, which
matches the finding in [Report 01](01-kan-vs-bspline-mlp.md) that refinement rather than
architecture carries most of pykan's accuracy.

The correct reading, which the notebook states: this is the *forward* problem, probe to
statistics, and it is well-posed. The paper's inverse problem, statistics to operator, is
not. Beating the SDP on forward prediction does not mean the operator is dispensable.

### Cross-file check

`KAN_crossfile_testing.ipynb` separates two claims that are easy to conflate.

| File | MOESM3-trained KAN | Retrained per file |
|---|---|---|
| MOESM3 | 0.00690 | 0.00706 |
| MOESM4 | 0.22360 | 0.00335 |
| MOESM5 | 0.21149 | 0.00183 |

The *method* transfers to every detector setting. The *trained model* does not transfer at
all — a 30-fold degradation, exactly as physics predicts, because these are different
detectors and the same probe gives a different response in each. This is the right control
to have run, and the result is clean.

---

## 3. Question two — what does the SDP actually contribute?

`KAN_alone_vs_SDP.ipynb` answers this directly, and it is the sharpest experiment in the
folder. It builds the POVM matrix three ways on MOESM4: the paper's SDP on raw data
(baseline), the KAN surface fed through the SDP, and — the new one — the KAN surface
inverted into a matrix by plain least squares with the positivity constraints removed.

| Method | Test RMS | Min eigenvalue | Max eigenvalue | Valid POVM? |
|---|---|---|---|---|
| Baseline (paper) | 0.00320 | +0.0007 | +1.0000 | yes |
| KAN → SDP | 0.00602 | +0.0042 | +0.9998 | yes |
| KAN alone, no SDP | 0.00407 | −3.59 × 10⁸ | +3.70 × 10⁸ | **no** |

The KAN-alone matrix has a competitive test RMS and is physically meaningless. Twenty-eight
eigenvalues exceed 1, and its largest diagonal entry is 1.3 × 10⁸ — a click probability of
130 million percent. Fidelity to the baseline cannot even be computed, because fidelity is
only defined for valid operators.

Notably, all three matrices recover the correct *structure*: rising diagonal, negative
decaying first off-diagonal. So the KAN's surface does contain the right physical
information. What it lacks is any mechanism to keep the inversion legal.

**Conclusion: the SDP is not a fitting step, it is the projection onto physical validity.**
The unconstrained inversion is ill-conditioned, so small surface errors get amplified
without bound. This is the justification for the pipeline being KAN → SDP rather than KAN
alone.

---

## 4. Question three — does routing through the KAN help? (the contribution)

`KAN_to_SDP_bridge.ipynb` and `KAN_to_SDP_bridge_with_stresstest.ipynb` implement the
pipeline:

```
raw noisy data → KAN → smooth surface → sample on a CLEAN uniform phase grid → SDP → Π̂₁
```

The argument for why this is more than a reshuffle is structural, and it is a good one. The
paper's recursive SDP needs an exact phase average (SI Eq. 1) to isolate each diagonal band.
The experiment's measured phase grid is offset, so the discrete average injects an artifact
and needs a trapezoid correction. Routing through the KAN removes that fragility by
construction: you choose the phases, so the grid is perfectly uniform and the phase average
is a plain mean. The notebook evaluates the trained KAN at the same 93 brightness levels but
64 uniform phases each, giving 5952 clean points.

On the full dataset, four-way on the same 744-point test set:

| Method | Test RMS |
|---|---|
| KAN alone (surface, no matrix) | 0.00320 |
| Joint SDP on raw data (reference) | 0.00320 |
| Recursive SDP on raw data | 0.00602 |
| KAN → recursive SDP | 0.00602 |

Fidelity between the KAN → SDP matrix and the joint reference is 0.9999. The reconstruction
routed through the network recovers the same physical operator.

But the tie proves nothing on its own, and the notebook says so plainly: with the full clean
dataset the KAN has no job to do. There is no noise to remove and no gaps to fill.

### The stress test

The centrepiece experiment starves the data. Whole brightness levels are held out — not
random rows — so the test genuinely measures interpolation across brightness, which is
precisely what the raw recursion cannot do without measurements. Both methods are then
scored on the held-out levels.

Single draw:

| Fraction of levels kept | Raw recursion | KAN → SDP |
|---|---|---|
| 1.00 | 0.00573 | 0.00572 |
| 0.60 | 0.00591 | 0.00500 |
| 0.40 | 0.00729 | 0.00552 |
| 0.25 | 0.01411 | 0.00588 |

Repeated over several random level subsets, mean ± standard deviation:

| Fraction | Raw recursion | KAN → SDP |
|---|---|---|
| 1.00 | 0.00573 ± 0.00000 | 0.00572 ± 0.00000 |
| 0.60 | 0.00754 ± 0.00135 | 0.00570 ± 0.00059 |
| 0.40 | 0.01097 ± 0.00206 | 0.01051 ± 0.00944 |
| 0.25 | 0.01546 ± 0.00239 | 0.00589 ± 0.00041 |

**At 25% of the brightness levels, raw recursion degrades 2.7× while KAN → SDP stays flat.**
The matrix-distance to the full-data truth at 25% is 0.0011 for raw recursion against 0.0006
for KAN → SDP, so the advantage shows in the operator as well as in predicted clicks.

The 40% row is the honest complication, and the notebook treats it well rather than
smoothing it over. KAN → SDP has a standard deviation of 0.00944 there, nearly as large as
its mean — some subsets excellent, some terrible. A follow-up experiment rebuilds the
subsets once and evaluates all three quantities on the *same* draws, which isolates the
failure: the worst subset had a KAN-alone RMS of 0.03202 against a final KAN → SDP RMS of
0.02506. **The KAN mis-fit that subset; the SDP stage was not at fault.** That is the right
diagnostic to have built, and it means the pipeline's weak point is identified rather than
hidden.

---

## 5. Discrepancies and issues found

**The recursive SDP's test RMS on MOESM4 differs by 7× between two notebooks.**
`KAN_assisted_tomography_MOESM4.ipynb` reports 0.04326.
`KAN_assisted_tomography_MOESM4_SDP_joint and recursive.ipynb` reports 0.00602. Same
dataset, same truncation d = 58, same four bands, same γ = 0.5. The likely cause is visible
in the first notebook's own warnings, which fire at every band:

```
[warn] l=1: P^(l) imag NOT negligible (|im|max=6.02e-02 vs |re|max=1.45e-01)
       -> real-only fit discards signal
```

The imaginary-to-real ratio climbs to 0.86 by l = 4, so the real-only fit is throwing away
most of the signal in the higher bands, and the per-band reduced-function fit RMS sits
around 0.019–0.024 rather than the 0.0006 the clean-grid version achieves. The second
notebook applies the trapezoid correction to the phase average. **This should be resolved
before either number is cited**, because the recursive SDP is the baseline the whole
contribution is measured against — and the 0.00602 figure happens to be the one that makes
KAN → SDP look like a tie rather than a win on full data.

**Prose disagrees with its own output.** The MOESM4 notebook's discussion says the recursive
SDP "fits less precisely here (~0.08 RMS)" while the cell above it printed 0.04326.

**Stale absolute paths.** `KAN_assisted_tomography_MOESM3.ipynb` hardcodes
`DATA_DIR = "/Users/lensa/Term_3/Research/papers/Quantum Paper/KAN_assisted tomography/data"`,
which is outside this repository. The cross-file notebook uses the relative `"data"` and is
correct. All execution warnings across the folder reference a virtualenv at
`/Users/lensa/Term_3/Research/papers/Quantum Paper/.venv`, so the folder was moved after the
runs and the MOESM3 notebook will not execute as committed.

**Bootstrap-by-notebook-import.** The bridge notebooks load upstream state by reading the
joint/recursive notebook file, which produces confusing tracebacks where the reported source
line is a line of JSON from the `.ipynb` (`"cells": [`). It works, but any failure in the
bootstrap will be very hard to diagnose. Extracting the shared setup into a small `.py`
module would fix this and would also remove the "run the three-way notebook first"
prerequisite.

**Pervasive matmul warnings.** `divide by zero`, `overflow`, and `invalid value encountered
in matmul` appear throughout, including inside CVXPY and inside matplotlib's 3D shading.
These are most likely the `np.log(absa + 1e-300)` guards in the log-magnitude computation
producing large negatives, and are probably benign, but they are frequent enough to mask a
real problem if one appeared.

---

## 6. What the folder establishes

1. **A KAN with no physics matches the paper's SDP on forward prediction** — 0.0071 against
   0.0065 test RMS on MOESM3, both near the paper's ~0.005 region. Grid refinement was the
   decisive tuning lever.

2. **The method generalises across detector settings; a trained model does not.** Per-file
   retraining gives 0.0018–0.0071; cross-file application gives 0.21–0.22.

3. **The SDP's contribution is physical validity, not accuracy.** Inverting the KAN surface
   without positivity constraints yields eigenvalues of order 10⁸ and a matrix for which
   fidelity is undefined, while still scoring a competitive test RMS. Low RMS is necessary
   but nowhere near sufficient.

4. **KAN → SDP recovers the same operator as the reference**, fidelity 0.9999.

5. **The KAN earns its place under data starvation.** At a quarter of the brightness levels,
   raw recursion degrades 2.7× while KAN → SDP holds flat, and its reconstructed matrix is
   closer to the full-data truth. This is a concrete, defensible meaning for
   "KAN-assisted tomography": the network supplies denoising and interpolation, the SDP
   supplies legality.

6. **Joint versus recursive SDP is an accuracy-tractability trade-off.** On a small APD the
   joint solve wins on accuracy because it uses the full 2-D statistics under one positivity
   constraint. The recursion is the paper's contribution because it drops the per-step cost
   from quadratic to linear in dimension, which is what makes their 1.8-million-parameter
   photon-number-resolving detector at d = 450 tractable at all. Fidelity between the two is
   0.9999, so they recover the same detector by different routes.

---

## 7. Recommended next steps

1. **Resolve the 0.04326 versus 0.00602 discrepancy** in the recursive SDP baseline on
   MOESM4. Everything downstream is measured against it. Determine whether the trapezoid
   correction is the whole difference, apply it consistently, and re-run both notebooks.

2. **Run the second starvation axis: noise.** The sparse-levels test exercises the KAN's
   interpolation. Keeping all levels but resampling the counts to fewer shots per point
   would exercise its denoising. Together they cover both of the KAN's contributions, and
   the denoising axis is the one the pipeline's motivation leans on most heavily.

3. **Report fidelity to the full-data reference at each starvation fraction**, not just RMS
   and matrix distance. That confirms the pipeline recovers the *right* detector under
   scarcity rather than a low-error impostor.

4. **Sweep the phase-grid density** (16, 32, 64, 128 phases) and show the result is stable
   once the grid is dense enough. This is direct evidence that the clean-gridding step is
   doing what the argument says it does.

5. **Investigate the 40% instability.** The diagnostic already points at KAN mis-fitting on
   particular subsets. More training steps, multiple seeds per subset, or a validation-based
   stopping rule would establish whether it is fixable or intrinsic.

6. **Fix the MOESM3 hardcoded path** and extract the shared bootstrap into a module so the
   folder runs from a clean checkout.

7. **Extract the symbolic formula.** Several notebooks flag `model.auto_symbolic()` as the
   natural next step — recovering a closed form for `p₁(|α|², θ)` would give
   interpretability without the operator, which is the one thing the SDP currently provides
   that the KAN does not.

---

## 8. References

- Zhang, L. et al. *Mapping coherence in measurement via full quantum tomography of a hybrid
  optical detector*. Nature Photonics 6, 364 (2012).
- Liu, Z. et al. *KAN: Kolmogorov-Arnold Networks*. arXiv:2404.19756 (2024).
- pykan: `github.com/KindXiaoming/pykan`. CVXPY with the SCS solver for all SDPs.
