# Quantum detector tomography audit (2026-09-21)

This is a read-only audit of all seven committed tomography notebooks, all four local source spreadsheets, Report 03, relevant thesis/poster/slides text, the original Zhang article and supplement, and primary literature. No notebook training, full SDP run, package installation, checkpoint deserialization, or original-repository mutation was performed. Notebook cell references below are **zero-based JSON cell indices**, counting markdown and code; add one for a human cell ordinal. Saved numeric outputs are historical observations, not fresh reproductions. Fresh bounded checks are in [tomography_probes.py](probes/tomography_probes.py) and [recorded outputs](probes/tomography-results.txt); see the [verification record](verification.md) for commands.

## Scientific conclusion and viable target

The implemented inverse problem is **detector tomography**: known coherent probes and observed clicks estimate an unknown binary measurement `{Π0, Π1}`. It is not unknown-state density-matrix tomography. `p1(α)=<α|Π1|α>`, `Π1=Π1†`, `0≼Π1≼I`, and `Π0=I−Π1`. Trace-one is not a POVM-effect constraint. Negative real off-diagonal entries are compatible with positivity and encode phase response; negative eigenvalues are the relevant feasibility defect. For Fock input `|j>`, diagonal `Π1[j,j]` is a probability. An arbitrary matrix entry is not independently a probability.

KAN learns the forward scalar response `(mean photon number, phase)→click probability` for one detector setting. Learning a response surface does not identify a physically valid operator, and low probe error cannot certify poorly observed operator directions. The practical research question is narrower than replacing tomography: **at a fixed acquisition budget, does a KAN improve held-out count prediction and recovery of a known synthetic POVM over equally tuned physical estimators and simpler response smoothers?** Existing outputs motivate that experiment but do not establish its answer.

A binomial noise model applies to two-outcome rows conditional on their total count: `c1_i~Binomial(N_i,p_i)`, `N_i=c0_i+c1_i`. Poisson photon-number weights describe the coherent-state Fock expansion; they are not automatically the shot-count likelihood. For MOESM6, use all nine counts and a multinomial model, with nine PSD effects summing to identity. Applying the binary `c1/(c0+c1)` parser to MOESM6 would estimate a conditional probability and discard outcomes; the seven notebooks currently avoid this by using MOESM3–5 only.

## Data evidence

Fresh checks with existing environment: NumPy/SciPy/xlrd versions are in the probe output. Every count inspected was finite, integer-valued, nonnegative, with positive row totals.

| File | Rows | Outcomes | Mean photon number range | Phase range (radians) | Brightness levels | Approx. plug-in binomial RMS noise floor |
|---|---:|---:|---|---|---:|---:|
| MOESM3 | 4400 | 2 | 0.0440313–56.1885650 | 0.00303–6.28297 | 110 | 0.001005 |
| MOESM4 | 3720 | 2 | 0.1784984–38.5243384 | 0.00798–6.28170 | 93 | 0.001021 |
| MOESM5 | 4760 | 2 | 0.0566253–166.8649884 | −1.85697–6.28201 | 119 | 0.000994 |
| MOESM6 | 34600 | 9 | 0.1080408–610.7287847 | −3.14137–9.41757 | not used | multinomial |

The spreadsheet headers explicitly say `Probe photon number`, `Probe phase (radians)`, and `Number of ...-click event`. Around 128,000 shots per APD row are available; totals vary slightly. The noise floors are a **plug-in estimate under independent binomial sampling**, not a proof that systematic calibration/phase drift is absent. Calling the full experimental data "clean" or "no noise to remove" is false even at high counts.

Zhang Fig.2 distinguishes APD configurations by LO intensity and mode overlap (5.5/.99, .8/.99, 5.5/.16). The publisher lists MOESM3–5 as three APD-size supplementary XLS files and MOESM6 as the much larger nine-outcome dataset. The local filenames are consistent with those publisher links. I did not byte-compare online files because browser fetches for supplementary binaries failed; avoid claiming independent online hash verification.

## Ranked findings and acceptance criteria

### T1 — P1, high confidence: test-label leakage invalidates main held-out comparison

**Evidence:** [KAN_assisted_tomography_MOESM4.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_assisted_tomography_MOESM4.ipynb) cells 8–9 explicitly give KAN a 60/20/20 split but give SDPs full data; cells 22, 28 use `X,y`, cell 32 scores on `Xte,yte`. [KAN_assisted_tomography_MOESM4_SDP_joint and recursive.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_assisted_tomography_MOESM4_SDP_joint%20and%20recursive.ipynb) cells 6–7 admit the same policy, cell 19 minimizes against `y` from full `X`, cell 21 phase-averages full `y`, and cells 25/28 evaluate `Xte`. [KAN_alone_vs_SDP.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_alone_vs_SDP.ipynb) cell 17 fits full `X,y` and evaluates `Xte`. Both bridge notebooks cell 1 execute every parent code cell and inherit that reference. The 0.00320 joint and 0.00602 raw-recursive "test" numbers are therefore resubstitution on a selected subset, whereas the KAN test uses unseen rows. MOESM3 cells 8/22 do fit only `Xtr,ytr`, so this particular defect does not apply there.

**Impact:** identical scored rows do not imply an equal-data generalization comparison. Refitting on full data is legitimate for a final calibration estimate but cannot be labeled out-of-sample evaluation. Low errors against the joint estimate likewise do not establish truth.

**Fix/acceptance:** serialize one train/validation/test split by physical acquisition groups before fitting; every candidate sees identical training counts only; choose all hyperparameters from validation; reserve test until decisions are frozen. Demonstrate that permuting test labels cannot alter any learned estimator. Label full-data results as fit diagnostics, not test performance.

### T2 — P1, high confidence: PSD certification and fitted forward model refer to different operators

**Evidence:** MOESM3 cell 22, MOESM4 cell 28, joint/recursive cell 19, and KAN-alone cell 17 allocate a full Hermitian `D×D` variable but include only `|j−k|≤4` entries in the fit and regularizer. They never constrain the remaining entries to zero. PSD constraints allow those free entries to participate in a completion. Joint/recursive `born_predict` cell 11 and KAN-alone cell 5 later evaluate the full returned matrix. MOESM3 cell 24 and original MOESM4 cell 32 instead evaluate only the fitted bands, while their eigenvalue checks certify the full matrix.

**Impact:** in later notebooks the training map can differ from the evaluation map; in earlier notebooks the scored band-masked operator is not the matrix whose physical validity was checked. A band mask need not preserve positivity. The size of the actual saved off-band contribution is **unknown** because numeric matrices were not preserved as safe arrays; this is a structural defect, not a claim that the published score changes by a particular amount.

**Fresh reproduction:** valid `Π=.5I_6+.2(|0><5|+|5><0|)` has eigenvalues .3–.7, yet full vs L=4 masked prediction at mean photon number 2 differs by 0.0279547. Thus PSD alone does not force ignored entries to zero.

**Fix/acceptance:** parameterize exactly the intended bands and constrain the same assembled operator, or use the complete forward map. Assert equality of the design-matrix prediction and independent coherent-state Born prediction on random complex feasible effects and all fitted probes. Record norm and predictive contribution of out-of-band entries.

### T3 — P1, high confidence: starvation advantage is confounded by regularization and representation

**Evidence:** stress notebook cell 11 uses unnormalized `sum_squares(Fx−P)+.5 sum_squares(diff(x))`. Cells 13/15/20 fit raw recursion on `n_train` measured levels, but KAN recursion on all 93 synthetic levels. At .25 fraction there are 23 measured raw levels versus 93 KAN-generated levels. No independent regularization selection or covariance weighting is performed. Joint regression has 3720 scalar data residuals whereas each reduced-band fit has 93, again with `.5`.

**Implication:** dividing an SSE objective by its number of observations gives effective mean-loss penalty `.5/n`. At 25%, raw receives approximately `93/23=4.04` times stronger regularization relative to the mean residual. This alone can change the sparsity curve. It does not prove the observed entire gain is caused by that confound. KAN pseudo-observations are correlated predictions, not 93 independent acquisitions; they add a learned prior and change weighting, not new information.

**Fix/acceptance:** normalize objectives consistently; tune each method's penalty using only validation groups; compare raw direct joint fit, raw recursion, periodic Fourier/spline smoother→same inversion, matched spline-MLP→same inversion, and KAN→same inversion. Include a resampled raw/spline arm with the same grid and the same normalized loss. Plot sensitivity to gamma, cutoff, bands, and pseudo-grid density. An advantage must survive equally tuned acquisition-budget comparisons, not just fixed copied `.5`.

### T4 — P1, high confidence: unregularized least-squares ablation does not isolate PSD constraints

**Evidence:** KAN-alone cell 11 calls `np.linalg.lstsq(Fl,P.real,rcond=None)` with no smoothness term; cell 15 adds **both** quadratic smoothness and PSD/upper-bound constraints. Cells 6/14 say the only difference is physics constraints. Historical eigenvalues are approximately −3.59e8 and +3.70e8, versus 0.00407 probe RMSE. Fresh SVD of MOESM4 kernels gives numerical rank 32–34 for 54–58 columns and condition numbers around 1.5e19–8.1e19 (these tiny singular values are precision-sensitive).

**Interpretation:** the saved output demonstrates failure of this unregularized inversion. It does not prove that the PSD constraint alone prevents that blow-up, that KAN inherently fails, or that an SDP is the only way to enforce a valid POVM. The original paper itself attributes instability control to regularization.

**Fix/acceptance:** a factorial ablation: same data, grid, loss and smoothness with constraints on/off; same constraints with penalty on/off; compare truncated SVD/ridge, spectral projection (with refit if desired), and a physical parameterization. For binary effects, `Π=U diag(sigmoid(s)) U†` or a matrix function of a Hermitian generator guarantees `0<Π<I`, though optimization may become nonconvex and speed is unproven. Keep negative-eigenvalue, max-eigenvalue and residual checks for every arm.

### T5 — P1/P2, high confidence: the implementation is not a literal paper reproduction

**Source:** Zhang main article p.368, Eq.(5), visually checked in the rendered original Methods page, defines the residual as the **unsquared Frobenius norm** `||P−FΠ||₂=sqrt(Tr M†M)` plus quadratic regularization. The notebooks use squared Euclidean/Frobenius residuals, and generally fit only one outcome. The paper reconstructs the POVM outcome set jointly under completeness. Carrying `.5` across different norm, residual count, outcome handling and phase compression is not a justified equivalence. The paper's Eq.(1) is the Fourier-reduced function; the SI Eq.(1) instead gives diagonal positivity/completeness. Notebooks incorrectly call their phase average "SI Eq.1".

**Optimization classification:** the diagonal-only stage with squared error and box constraints is a convex QP. The off-diagonal stages/joint matrices have PSD cone constraints; they are convex quadratic semidefinite/conic programs, representable as standard SDP using epigraph lifts. They are not ordinary box-constrained QPs just because the objective is quadratic. A call to CLARABEL is not evidence a problem is an SDP: inspect its constraint cones. In this code `M>>0`/`I−M>>0` are genuine semidefinite constraints.

**Fix/acceptance:** implement and label a faithful norm/outcome baseline or rename to a related squared-loss estimator. Independently tune gamma and verify agreement on controlled data. Do not claim reproduction of the paper's RMS: no approximately .005 RMS benchmark was located in the complete locally read main article or two-page SI. The paper reports >98% fidelity against a theoretical detector model, which differs from fidelity between two fitted estimates.

### T6 — P2, high confidence: phase-average narrative is mathematically wrong/incomplete

**Evidence:** original MOESM4 cell 22 uses an unweighted mean on actual phases; joint/recursive cell 21 switches to periodic trapezoidal integration. Fresh data probe reproduces `max |Im P^(1)|=.06023925` for mean and `.00375360` for wrapped trapezoid, agreeing with stored warnings. MOESM4 circular phase gaps span .002814–.175934 radians; the grid is nonuniform. A merely offset *uniform full-circle grid* does not leak a constant into these low Fourier modes: 40 equally spaced phases offset by .123 have l=1 leakage 1.82e−17.

**Bridge issue:** bridge cells 3/5 and stress cells 3/5/15 call the 64-phase mean "exact". It is exact for appropriate finite Fourier content without aliasing. An unconstrained KAN on scalar theta, especially after clipping, has no such bandlimit or periodic-boundary guarantee. Uniform sampling improves quadrature but does not remove interpolation bias, miscalibration, or aliasing. Raw scalar theta also treats equivalent wrapped phases as different inputs; MOESM5 includes negative phases.

**Fix/acceptance:** use calibrated periodic phases; compare periodic trapezoid and Fourier weighted least-squares on irregular samples; retain complex Fourier coefficients unless phase gauge/reality is justified. Require phase-density convergence (32/64/128/256), seam consistency at theta and theta+2pi, and recovery of known complex effects from synthetic probes. The paper's Fig.2 p.366 explicitly assumes zero LO phase, making APD coefficients real, so the real-only assumption can be legitimate **for this calibrated dataset**, not for general detector tomography. Dropping imaginary residuals should be quantified, not automatically called noise.

### T7 — P2, high confidence: truncation error is not negligible at the advertised precision

**Evidence:** D=58 in joint/recursive cell 11 prints max coherent-state omitted probability 0.00203877, versus reported RMSE .00320. Fresh Poisson survival-function check confirms it. D=90 in MOESM3 prints about 2e−5. For worst-case MOESM4 brightness the smallest D satisfying Poisson tail≤1e−8 is 79; analogous values are 104 for MOESM3 and 245 for MOESM5. This is a conservative numerical target for a zero-tail basis model, not a claim those cutoffs are statistically identifiable.

**Interpretation:** finite coherent vectors are not normalized: with `Π0+Π1=I_D`, their Born probabilities sum to `1−tail`. Tail probability is not automatically a bound on general coherent off-diagonal operator error; cross-block coherences can matter. Renormalizing vectors silently changes the model to a conditional truncated probe. High cutoff alone worsens inversion unless coverage/regularization is handled. The source paper's detector-saturation cutoff argument for its d=450 PNRD is not interchangeable with this notebook's zero-tail approximation.

**Fix/acceptance:** state a tail/overflow or high-photon saturation model, derive a suitable error bound, and show predictions and identifiable low-photon operator blocks converge when D increases. Choose numerical approximation tolerance materially below acquisition noise and target differences. Never reuse D=58 on MOESM5.

### T8 — P2, high confidence: fidelity and matrix-distance metrics overstate operator recovery

**Evidence:** joint/recursive cells 29–30 and bridge cell 8 normalize Uhlmann overlap by `Tr(A)Tr(B)`, then interpret .9999 as the same physical POVM. Stress cell 26 calls a full-data estimate `Pi_truth`, takes its real part, and averages squared entry errors over all `D²` entries.

**Counterexample:** A=.2I and B=.8I are both valid binary effects; this normalized fidelity is exactly 1 while every normalized state's click probability differs by .6. The metric removes scale. Saturating high-photon diagonals also dominate the trace and can conceal low-photon differences. Averaging over a mostly zero banded D² matrix dilutes localized error, and `.real` ignores imaginary disagreement.

**Fix/acceptance:** name the full-data operator a reference estimate. On synthetic truth report Frobenius error on explicitly identified blocks, spectral/operator norm (worst-case probability difference for a binary effect), both outcome errors, and predictive risk. On real data use held-out counts, uncertainty bands, regularizer/cutoff sensitivity, and bounded identifiable functionals; retain trace mismatch and both effects beside any fidelity. Demonstrate the .2I/.8I counterexample is detected by the selected metric suite.

**Additional metric implementation defect:** KAN-alone cell 19 computes `sqrt(mean((A−B)**2))` for potentially complex matrices, rather than `sqrt(mean(abs(A−B)**2))`; its saved output raises `ComplexWarning` when formatting the result. Complex squares can cancel, so this is not a valid Frobenius/RMS distance. Use the conjugate-magnitude definition and verify a purely imaginary perturbation yields a positive distance.

### T9 — P2, high confidence: stress tests mix in-sample fit, interpolation, extrapolation and limited randomness

**Evidence:** stress cells 15/20 switch to all rows if there are no held-out levels, so the 100% point is in-sample while 25–60% points are held-out. Five outer seeds vary subsets; `train_kan_on_levels` cell 13 hardcodes model `seed=0`. The diagnostic cell 24 creates a *different* set of eight 40% draws and uses an ad hoc .009 threshold to assign blame. Fresh reproduction of the five-seed sampling order finds some test levels outside training min/max; seed 2 at 40% has 13 such brightnesses. Thus neither estimator is evaluated on pure interpolation in every draw.

**Interpretation:** the Born map can predict at any brightness once a POVM is fitted. Missing an interior measured level does not make raw tomography intrinsically "extrapolate blindly" while a KAN alone interpolates. A high KAN error on one bad run identifies an upstream contribution, but does not establish the inversion has no fragility, that more training fixes it, or that the pipeline is bug-free. Five subsets do not estimate optimizer-seed robustness or acquisition-noise robustness. np.std here is spread, not confidence interval.

**Fix/acceptance:** freeze a common independent test set for all budget fractions; acquire/subsample only the training pool; keep endpoint levels when claiming interpolation and evaluate extrapolation separately. Use nested subset sets for learning curves, paired repeated splits, several optimizer seeds, finite-shot noise seeds, failed-run accounting, and uncertainty for paired method differences. Reproduce the exact failing split before attributing its cause; compare KAN approximation error, quadrature error, inversion residual and physical feasibility separately.

### T10 — P2, high confidence: smoothing is not demonstrated denoising; simpler controls are missing

**Evidence:** the bridge evaluates a KAN fitted to empirical frequencies and treats its smoothed predictions as clean. Only brightness deletion is implemented as a systematic stress axis. There is no low-shot resampling/independent repeated acquisition experiment, no learned pseudo-data covariance, and no generic smoother or direct physical fit with a tuned regularizer as a sparse-data comparator.

**Fix/acceptance:** simulate known physical effects with binomial/multinomial counts or thin real counts with a documented hypergeometric procedure. Keep original high-count frequencies as noisy evaluation references, not truth. Distinguish parametric binomial bootstrap from genuinely independent data. Evaluate bias and variance, including sharp/complex phase structure where smoothing can suppress legitimate coherence. Compare periodic spline/Fourier, RBF/GP or a simple calibrated weak-homodyne response model; do not introduce every model, but include at least a strong inexpensive periodic baseline. A KAN-specific contribution requires an advantage over such baselines or independently validated interpretability.

### T11 — P2, high confidence: cross-file checks combine detector shift and input-domain shift

**Evidence:** cross-file cells 6/8 correctly reuse MOESM3 training normalization at inference. Cell 10 evaluates all 4400 MOESM3 rows (including training) for .00690, whereas cell 8's true MOESM3 held-out sanity RMS is .00706. Cell 14 retrains per file but retains the original MOESM3 normalization closure. MOESM5 brightness extends to 166.9 rather than 56.2 and includes negative phases; those inputs also shift outside the source domain. Detector parameters (LO strength, overlap) are absent as inputs.

**Interpretation/fix:** per-file retraining is repeated fitting of the method, not cross-detector generalization by a trained model. The failure of a detector-specific map on a different detector is expected, but its magnitude cannot be attributed solely to configuration shift without a common-support periodic-phase check. Fit per-file normalizers for standalone retraining; report common-domain transfer separately; supply known detector configuration covariates for a genuine cross-configuration model and hold out entire configurations. Treat current results as response-regression sanity checks, not established tomographic transfer.

### T12 — P2/P3, high confidence: reproducibility, numerical status and writing discrepancies

- MOESM3 cell 4 hardcodes an old absolute directory; that directory exists on this host, so "will not execute" is too categorical locally, but it is not checkout-portable.
- Bridge/stress cell 1 executes all upstream notebook code, including training, plots and checkpoint writes. Replace reusable functions with importable modules and immutable run configs, not notebook `exec`.
- All pykan instances share `./model` default checkpoint names; avoid cross-run overwrites and store normalization/model/dtype/training split together. Do not trust a found checkpoint without matching configuration provenance.
- MOESM3 cell 26 executed after cell 28 (counts 16 vs 15); more generally saved execution histories are not clean-run evidence. Preserve outputs as historical and regenerate from frozen scripts in the restart.
- Most solver calls immediately consume `.value`; retain `problem.status`, primal/dual residuals, objective components, iterations, setup/solve time and explicit finite checks. Accepting eigenvalues to ±1e−3 can hide errors comparable to the reported .003 RMS. Symmetrization does not fix a failed solve or guarantee PSD.
- Pervasive `divide by zero/overflow/invalid in matmul` warnings are **unexplained**. Small, nonzero probe magnitudes and log-stabilized bounded kernels do not establish the report's proposed cause. Reproduce in a small isolated matrix multiplication with versions and finite checks; do not call warnings cosmetic without evidence.
- The original MOESM4 code prints recursive RMS .04326 while prose says about .08; later trapezoid notebook prints .00602. The quadrature defect is independently reproduced, but the complete seven-fold score change was not re-solved here and should not be claimed solely attributed by a fresh experiment.
- A `[2,1,1]` KAN is not generically incapable of brightness–phase interactions: outer nonlinear composition of summed univariate features already creates interactions. Restrict claims to an empirically tested architecture/optimization result.
- MOESM3 uses sigmoid loss; later joint/recursive and stress notebooks train unconstrained outputs then clip at inference. These are different probability models and should be explicit.
- The reduced `F_matrix` helpers (joint/recursive cell 21, KAN-alone cell 5, stress cell 11) explicitly return zero for every column when probe amplitude is zero. At vacuum the correct diagonal-band coefficient is `F[0,0]=1` for l=0. Existing measured probes are strictly positive, so this is a latent vacuum-probe bug rather than the cause of saved scores; include vacuum in the restart kernel tests.
- Historical timing is not an end-to-end speed benchmark. The source paper reduces the **number of fitted coefficients per recursion** from O(d²) to O(d), not total runtime to linear. Current recursion still handles full D×D PSD constraints. Compare data prep, network training, compilation, solving, repeated hyperparameter search, and total time at a matched quality target.

## Minimal restart experiment and decision gate

1. Package pure loading, phase handling, forward kernels, physical assembly, metrics and inversion functions. Unit-check known binary effects, a genuinely complex effect, identity/completeness, kernel/Born agreement, Fourier recovery on uniform/irregular grids, and truncation convergence. Numerical diagnostics must fail loudly for nonfinite arrays/failed solves. No full notebooks as dependencies.
2. Begin with a low-dimensional synthetic binary detector (e.g. D=8–12) with known complex banded Π and eigenvalues safely in (0,1). Use coherent probes with a controlled tail and both uniform and actual irregular phase geometries. Generate at least two effect families, including a phase-shifted case; avoid validating only a truth tailored to the regularizer.
3. Freeze a test grid/count draw and independent validation groups. Compare raw physical squared-loss and/or binomial-likelihood fit, periodic Fourier/spline smoother→same fit, and KAN→same fit. Add the intended spline-MLP for the thesis's cross-part hypothesis if feasible. Tune each arm on the same training/validation acquisition budget. Use normalized losses and identify pseudo-point correlation as a model property.
4. Vary number of training brightness levels and shots per setting separately; retain endpoints for interpolation-only results. Start with a modest prespecified paired run count and report uncertainty; expand only if uncertainty spans the practical decision threshold. Repeat initialization within data draws rather than relabeling subset seeds as model seeds.
5. Report held-out binomial deviance/log score and RMSE, synthetic-truth operator norm/block error, positivity/completeness residuals, phase seam/cutoff sensitivity, convergence failures, and total wall time. On MOESM4 real data, drop "truth" and evaluate held-out acquisition groups with count uncertainty. Repeat on MOESM3/5 only after the pipeline passes.
6. **Continue KAN-assisted research only if** it improves the prespecified accuracy/stability/time criterion against an equally tuned inexpensive smoother and raw physical baseline, with feasible effects and consistent gains across paired draws. A negative result still supports a defensible conclusion: generic smoothing/regularization helped, with no evidence yet of a KAN-specific benefit. Do not prioritize symbolic extraction over valid evaluation.

## Writing corrections with concrete anchors

- Thesis PDF p.25 (printed p.24), Fig.2.7–2.8: replace "same held-out test set", "trusted reference", "preserves the real physics", and "bug-free" by the precise split/feasibility evidence. A fitted reference and normalized fidelity cannot certify correctness.
- Thesis PDF p.26 (printed p.25): replace the raw-SDP "extrapolating blindly" causal story; both learned maps predict at unseen probes, and the experiment mixes interpolation and extrapolation.
- Thesis PDF pp.27–28: five subset draws and a different eight-draw diagnostic do not establish general stability or a uniquely fixable KAN failure.
- Thesis PDF p.29, poster conclusion, slides 16–19: remove categorical "first", "entirely unexplored", "no prior work" and "must be KAN→SDP" claims pending a properly delimited review. Existing likelihood, neural detector, and physical-parameterization literature already supplies alternatives to this particular SDP.
- Poster and thesis call smoothed data denoised and claim sparse/noisy robustness; qualify as an unvalidated smoothing interpretation until a noise-axis experiment separates bias and variance.
- Slides 13: a POVM is a collection of effects; effects sum to identity, not their entries summing to one. Distinguish positivity of matrices from entrywise positivity.
- Report 03: preserve historical numbers only with qualification above; remove explanatory speculation about warnings; remove claim full-data reference is truth; correct scale-insensitive fidelity interpretation and positivity-only ablation attribution.

## Literature verified online (primary sources; accessed 2026-09-21)

**Zhang et al. (2012), Mapping coherence in measurement via full quantum tomography of a hybrid optical detector.** https://www.nature.com/articles/nphoton.2012.107 ; DOI https://doi.org/10.1038/nphoton.2012.107 . Main paper local PDF read in full; Eq.(1) Fourier reduction p.365, Fig.2 real LO gauge and model-comparison fidelity p.366, Fig.3 bands/d=450 p.367, Eq.(5)/(6) residual/regularization p.368. The online article verifies publication/date and supplementary attachments. The recursive coefficient reduction is established; the notebook's claimed held-out .005 RMS is not located. Supplement https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnphoton.2012.107/MediaObjects/41566_2012_BFnphoton2012107_MOESM2_ESM.pdf (online binary fetch failed; matching locally named `Zhang_etal_2012a_SM.pdf` read). SI pp.1–2 supplies recursive positivity, mode mismatch and detector-saturation estimate; it does not contain the claimed phase-integral SI Eq.1.

Publisher supplementary file endpoints (links present on article, downloads not independently fetched):
- MOESM3: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnphoton.2012.107/MediaObjects/41566_2012_BFnphoton2012107_MOESM3_ESM.xls
- MOESM4: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnphoton.2012.107/MediaObjects/41566_2012_BFnphoton2012107_MOESM4_ESM.xls
- MOESM5: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnphoton.2012.107/MediaObjects/41566_2012_BFnphoton2012107_MOESM5_ESM.xls
- MOESM6: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnphoton.2012.107/MediaObjects/41566_2012_BFnphoton2012107_MOESM6_ESM.xls

**Fiurášek (2001), Maximum-likelihood estimation of quantum measurement.** https://arxiv.org/abs/quant-ph/0101027 ; DOI https://doi.org/10.1103/PhysRevA.64.024102 . Infers POVMs from known probe states using likelihood and yields physically sensible estimates, unlike unrestricted inversion. This is long-standing evidence against claiming physical reconstruction requires this particular SDP; it is not direct evidence of a KAN speedup.

**Feito et al. (2009), Measuring Measurement: Theory and Practice.** https://arxiv.org/abs/0906.3440 ; DOI https://doi.org/10.1088/1367-2630/11/9/093038 . General detector tomography theory and experiments; discusses ill-conditioning and smoothing regularization, including sensitivity to smoothing strength. Supports regularized physical and noise-aware baselines, not a transferable universal `.5` parameter or a new KAN result.

**Lundeen et al. (2009), Tomography of quantum detectors.** https://www.nature.com/articles/nphys1133 . Experimental POVM identification for APD and photon-number-resolving detectors. Clarifies detector/state/process distinction and why reconstructing probabilities only is not full detector characterization.

**Palmieri et al. (2020), Experimental neural network enhanced quantum tomography.** https://www.nature.com/articles/s41534-020-0248-6 . Supervised neural data filtering addresses SPAM and augments experimental tomography; paper discusses state and detector calibration. Establishes prior neural preprocessing of tomography data. Its trained noisy→ideal probability correction differs from this repository's self-fitted low-dimensional response smoother; do not conflate them.

**Tomography of quantum detectors using neural networks (2023), IFAC-PapersOnLine 56(2), 5875–5880.** https://www.sciencedirect.com/science/article/pii/S2405896323004317 ; DOI https://doi.org/10.1016/j.ifacol.2023.10.088 . Publisher abstract explicitly proposes neural reconstruction of detectors and numerical tests of phase-insensitive detectors. This is relevant prior neural detector work; abstract alone does not establish its exact positivity enforcement, runtime comparison or applicability to phase-sensitive APDs.

**Wu et al. (2026), Sparsified Kolmogorov-Arnold Networks for Interpretable Quantum State Tomography.** https://arxiv.org/abs/2606.11814 . Submitted 10 June 2026, preprint. Uses all 63 nonidentity Pauli expectations in a controlled three-qubit GHZ-family benchmark to reconstruct three subspace variables; probes sparse pathways and recovered Pauli structure. Authors position contribution as structural interpretability, not superior sparse regression. This is **state**, not detector, tomography and does not directly anticipate this exact KAN→optical-detector pipeline. It nevertheless prevents an unqualified claim of first KAN quantum tomography as of September 2026.

**Search boundary:** targeted primary-source searches for KAN quantum detector/state tomography located the works above but no directly matching KAN smoother→Zhang APD pipeline. Absence in this bounded search is not proof of novelty. A defensible current description is "an exploratory application of KAN response smoothing before constrained optical detector reconstruction". Establish a novel contribution by controlled benefit or verified interpretable structure, not the label alone.
