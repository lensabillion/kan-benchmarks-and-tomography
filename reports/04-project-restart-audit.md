# 04 — Project Restart Audit

**Date:** 2026-09-21

**Scope:** Local research folder, current GitHub source, historical reports, supplied thesis/poster/slides, and relevant primary research.

**Code baseline:** `origin/main` at `5fc5a05` (merge of PR #1).

**Audit tracking:** `kan-1btb`. **Implementation restart:** `kan-lwtk`.

## Decision

**Restart by establishing a correct, reproducible baseline. The current repository is a valuable exploratory archive, but its strongest theoretical and experimental conclusions are not yet supported.** The immediate work is to repair the theorem, verify numerical implementations, enforce train/validation/test separation, and reproduce the physical reference objective. New KAN variants, large sweeps, and replacing the SDP should follow those steps.

The central theorem in the thesis is false for the model classes it defines: a single KAN layer is additive in its input coordinates, whereas a spline MLP can apply a nonlinear curve to a mixture of coordinates and therefore create interactions. The thesis's reverse proof changes the model to a generalized KAN. A correct routed inclusion and a qualified deeper-network construction can be retained.

There are also concrete implementation and evaluation defects. Both NumPy classification KANs divide parameter gradients by batch size twice. Their spline backward paths do not account for input clipping. Important benchmark sweeps select winners on the test set and do not match all of the claimed budgets. Several tomography SDPs fit the full measured dataset before being scored on a subset called a test set. The joint reconstruction fits a band-limited forward expression but predicts with an unrestricted matrix. These problems can change conclusions; they are not just documentation issues.

The most promising research question remains useful: **under a fixed measurement and computational budget, does KAN-based smoothing improve recovery of a detector's physically valid response more than ordinary spline/Fourier smoothing or a spline MLP?** The present sparse-data plots motivate that question. They do not yet answer it, because the raw and KAN branches use different effective regularization, the reference is not ground truth, and noise reduction is not isolated.

This PR records the evidence, corrections, research landscape, and implementation plan. It initializes the requested `tbd` workflow and creates the restart backlog. It does not silently replace historical notebook results with new training runs or claim that the underlying research defects have been fixed.

## Evidence and Coverage

The audit separates four types of statements:

- **Verified code/math:** directly established by reading the relevant implementation or deriving a counterexample.
- **Reproduced bounded check:** independently evaluated during this audit without launching a full training sweep.
- **Historical output:** present in a saved notebook, with no guarantee that executing the current notebook from a fresh kernel recreates it.
- **Proposed experiment or hypothesis:** a next step, not an established result.

The local checkout started at `9109d5d` on `docs/research-reports`; the local `main` branch was older. Fetching GitHub confirmed that PR #1 was merged and the remote default branch is `main`. The tracked trees at local `9109d5d` and remote `5fc5a05` are identical. An isolated `codex/project-restart-audit` worktree was used for this report; the original checkout's files and branch were preserved.

The source contains **164 tracked files and 23 notebooks**, including the two vendored KANbeFair notebooks. All notebook source cells and saved text outputs were extracted; the model/data/source inventory is in the appendix. All 30 thesis pages, the single-page poster, and all 24 slides were read as text. Selected mathematical and result figures were rendered for visual verification. The source binaries are identified by hashes and remain outside Git.

The appendices are part of this report:

| Appendix | Purpose |
| --- | --- |
| [Repository and local asset inventory](restart-audit/inventory.md) | File coverage, dependency and provenance gaps, local-only material, execution evidence |
| [Benchmark audit](restart-audit/benchmarks.md) | Notebook-level findings, numerical checks, parameter/compute fairness, benchmark literature |
| [Detector tomography audit](restart-audit/tomography.md) | Source-paper comparison, data and operator checks, leakage, reconstruction validity, tomography literature |
| [Writing and theory audit](restart-audit/writing-and-theory.md) | Counterexample, corrected mathematical scope, thesis/page/slide claim register |
| [Research landscape and experiment choices](restart-audit/research-landscape.md) | Primary-source reading map, alternatives, novelty boundaries |
| [Verification record](restart-audit/verification.md) | Checks performed and limits of what was reproduced |

Reports [01](01-kan-vs-bspline-mlp.md), [02](02-kan-vs-mlp.md), and [03](03-kan-assisted-tomography.md) remain historical records. This report supersedes their unqualified causal, equivalence, and validation conclusions where the appendices identify contradictions. A saved number may be transcribed correctly while the inference drawn from it is wrong.

## The Project From First Principles

### Three distinct questions

The repository mixes three questions that need separate evidence:

1. **Representation:** What functions can a precisely defined architecture represent, at what depth and parameter cost?
2. **Learning:** Which fitted model predicts unseen data better after specified optimization and model selection?
3. **Inverse inference:** Which reconstruction identifies a physical detector from limited, noisy observations, with what uncertainty?

A representation theorem does not prove a learning advantage. Low prediction error does not prove physical validity or unique inverse recovery. A valid physical matrix does not prove that a neural preprocessing step improves it. Treating these distinctions explicitly is the conceptual starting point.

### KANs, MLPs, and splines

An ordinary MLP layer maps $x$ to $\sigma(Wx+b)$. A pure-spline KAN layer maps it to $y_j=\sum_i\phi_{ji}(x_i)$, with $\phi_{ji}(t)=\sum_r c_{jir}B_r(t)$. A spline MLP instead places learned one-variable spline functions after linear mixing. These are different arrangements of linear and nonlinear operations.

A fixed spline basis gives a finite-dimensional linear space of one-variable functions. Grid size, polynomial degree, knot placement, domain/extrapolation convention, coefficient sharing, residual activation, and layer composition all matter. In common pykan notation, `k=3` denotes cubic degree; spline literature sometimes uses “order” for degree plus one. Declare the convention instead of interchanging the terms.

The classical Kolmogorov–Arnold representation theorem is an existence result about continuous one-variable functions and compositions. It does not say that a particular small cubic-grid network, a fixed optimization budget, or a noisy finite dataset will recover the desired function efficiently. The original [KAN paper](https://arxiv.org/abs/2404.19756) supplies specific models and experiments; use its exact assumptions and recipes when attempting a replication.

Two inputs already expose the false equivalence: $(x_1+x_2)^2$ is a one-unit spline-of-a-projection function, but cannot be written as $a(x_1)+b(x_2)$. Its four-corner alternating difference is 2; the difference for every additive function is 0. The [theory appendix](restart-audit/writing-and-theory.md) gives the construction, a lower error bound, and the valid inclusions.

For benchmarking, the estimand should be the expected loss on new observations under a stated data distribution after a stated model-selection procedure. Equal widths do not mean equal parameter counts. Equal optimizer steps do not mean equal computation: LBFGS can call the closure several times per step, and full-batch and subset training see different information. Equal stored parameter counts do not imply equal active trainable parameters. Those distinctions need to be measured, not inferred from model names.

### Detector tomography is not state tomography

The optical data concern **quantum detector tomography**. Known probe states $\rho_i$ are measured by an unknown detector with POVM elements $\{\Pi_n\}$. The Born rule is

$$p_{in}=\operatorname{Tr}(\rho_i\Pi_n),\qquad \Pi_n\succeq0,\qquad\sum_n\Pi_n=I.$$

For a binary click/no-click detector, estimating the click element $\Pi$ requires $0\preceq\Pi\preceq I$, with the other element $I-\Pi$. Quantum state tomography reverses which object is unknown: it estimates $\rho$ given known measurement operators. The repository README's state-tomography description is corrected in this PR; the distinction matters when evaluating relevant literature and novelty.

For a coherent probe $\alpha=\sqrt{\mu}e^{i\theta}$, its Fock coefficients have the form

$$a_j=e^{-\mu/2}\frac{\mu^{j/2}e^{ij\theta}}{\sqrt{j!}},\qquad p(\mu,\theta)=a^\dagger\Pi a.$$

The observed count $k_i$ out of $N_i$ shots is naturally binomial in the binary case, conditional on the probe and a stable detector. The empirical frequency $k_i/N_i$ has variance $p_i(1-p_i)/N_i$. A probability RMSE is useful, but it ignores heteroskedasticity and cannot by itself establish calibrated uncertainty. A multi-outcome detector requires a multinomial formulation and completeness across all outcomes; MOESM6 should not be passed through a binary APD parser without a separate schema.

After choosing a Fock cutoff, matrix representation, and probe calibration, the forward map is linear in the unknown matrix entries. The inverse is difficult because some entry combinations barely change the measured probabilities. In an SVD $A=U\Sigma V^*$, inversion divides by small singular values. Small measurement or smoothing errors can therefore create large operator errors. Positivity, completeness, regularization, and better probe design address different parts of that problem; none alone guarantees that the true operator is identified.

Fock truncation is part of the model. The omitted mass is $\Pr[\operatorname{Poisson}(\mu)\ge d]$ for coefficients $j=0,\ldots,d-1$. The observed MOESM4 cutoff has a maximum tail around $2.04\times10^{-3}$, on the scale of some reported prediction errors. Increase $d$ or explicitly model/bound the tail and demonstrate convergence. Renormalizing truncated probes changes the statistical model and must be justified.

### What a learned surface can and cannot contribute

A KAN can fit $\hat p(\mu,\theta)$ and supply values at unmeasured settings. This is a data-dependent prior or regularizer: it may reduce noise variance and may impose useful smoothness, but it can also introduce systematic bias. Thousands of predictions from one trained model are correlated pseudodata, not thousands of independent measurements. Their density must not silently increase the likelihood weight or shrink reported uncertainty.

If reconstruction minimizes $\sum_{i=1}^{M}r_i^2+\gamma R(\Pi)$, duplicating all points $c$ times produces $c\sum r_i^2+\gamma R$, equivalent to dividing the relative regularization strength by $c$. The sparse raw branch and dense KAN branch cannot be compared fairly by keeping the same numerical `gamma` under this loss. Use a documented normalized objective or statistical weighting and tune hyperparameters under the same validation protocol.

Uniform phases simplify Fourier extraction only under appropriate quadrature and bandlimit assumptions. An exactly uniform grid remains orthogonal after a global phase shift. Unequal spacings, missing phases, calibration error, aliasing, and nonperiodic learned surfaces are different phenomena and require different controls. Periodic spline or Fourier regression is therefore an essential baseline for this two-dimensional response surface.

## Findings That Determine the Restart Order

Priority **P1** means a blocker for reusing a scientific claim or running a meaningful comparison; **P2** means needed for defensible inference and reproducibility; **P3** means a later research extension. These priorities do not imply production-security severity.

| Finding | Evidence and consequence | Priority and action |
| --- | --- | --- |
| The stated function-class equality is false | Thesis pp. 15-18 changes from additive coordinate edges to mixed-coordinate edges in the reverse proof; explicit counterexample above | P1: `kan-rngu`; repair definitions and claims before building further theory on them |
| KAN classification gradients are scaled incorrectly | Both handwritten implementations apply `/m` in output loss differentiation and again in layer parameter gradients | P1: `kan-k44j`; verify against finite differences/autodiff and batch-duplication invariance |
| Clipped spline forward and backward disagree | Forward clipping is followed by an unmasked derivative outside the domain | P1: `kan-k44j`; differentiate the implemented function, then rerun comparisons |
| Benchmark winners are selected on test error | Per-step and per-configuration minima use the test set; model attribution and execution state are inconsistent in places | P1: `kan-sb42`; rebuild model selection around validation and a locked final test set |
| Claimed parameter/optimizer fairness is incomplete | Stored/frozen/dormant parameters are mixed; Feynman Adam/LBFGS use different sample counts and skip an MLP comparison | P1: `kan-sb42`; report active capacity, data exposure, evaluations, time and search budget |
| Full-data SDP fits contaminate purported test scores | Joint/recursive notebook uses full measurement labels before scoring `Xte`; downstream bootstrap reuses this state | P1: `kan-wg0b`; enforce estimator-level partition boundaries |
| Fitting and scoring can use different Born operators | Joint loss constrains a limited set of bands while full prediction reads all entries of the matrix | P1: `kan-xskn`; share one operator or explicitly constrain omitted entries |
| Reference objective is not the published one | Zhang Methods Eq. (5) uses an unsquared Frobenius residual plus smoothness; notebooks use squared residuals with the same numeric weight | P1: `kan-wg0b`; first reproduce the objective, then compare alternatives with separately tuned weights |
| Pseudogrid size confounds smoothing with regularization | Same unnormalized loss weight with different numbers of brightness-level residuals after Fourier reduction | P1: `kan-v42q`; normalize/tune consistently and test row-duplication invariance |
| Phase-average explanation is wrong and real-only treatment needs calibration | Actual phase gaps are uneven; a uniform offset alone does not create DC leakage; dropping imaginary terms needs a justified reference phase | P1: `kan-v42q`; verify weighted complex Fourier extraction and quadrature convergence |
| Good probability fit does not identify a unique physical POVM | Large unconstrained eigenvalues, reference-normalized fidelity, ill-conditioning and truncation all affect interpretation | P2: `kan-j3vs`; quantify identifiability, validity, uncertainty and operator error separately |
| Least-squares/SDP comparison changes regularization too | Unregularized inversion is compared with a regularized constrained estimator | P2/P3: isolate contributions before proposing `kan-5rcn` as a new solver project |
| Sparse-data benefit has not isolated KAN-specific or noise-specific value | Missing ordinary smoothers, shot-noise sweeps and consistent selection; full-fraction point is in-sample | P2: `kan-lz8l`; run synthetic truth and controlled ablations |
| Scientific artifact provenance is incomplete | No project-level reproducible environment, hidden notebook state, duplicate copies, imported implementation ambiguity and figure/run gaps | P1/P2: `kan-102g`, `kan-8kcj`, `kan-ayoi` |

The appendices distinguish confirmed defects from plausible mechanisms still requiring experiments. For example, the historical regularized KAN collapse is real as a saved observation, but “the coefficient penalty grows with grid size” is not established by the implemented default regularizer. Numerical warnings must be traced to finite values and solver diagnostics; they should not be declared harmless by speculation.

## The First Implementation Should Be Small

Build one runnable path per scientific question, then expand. Keep the old notebooks as an archive of the exploration. Extract shared logic into an importable package; use notebooks as thin figure/report clients.

```text
src/kan_research/
  models/             # explicit adapters: pykan, spline MLP, plain MLP
  benchmarks/         # named targets, domains, splits, metrics
  tomography/         # data schema, probe map, estimators, physical metrics
  experiments/        # configurations, run identity, orchestration
configs/              # small reviewed experiment configurations
tests/                # numerical and split-boundary regression checks
data/                 # documented immutable raw inputs or fetch manifest
results/              # compact run metadata/tables; large artifacts external
notebooks/            # read run outputs and make figures
reports/              # evidence and scientific conclusions
```

This is a proposed structure, not an implemented package. Prefer a modest extraction over a generalized experiment platform. Keep one supported Python version initially. Capture both the historical environment and a tested restart environment; an old vendored Conda file is evidence about upstream dependencies, not a validated lock for this repository. Resolve installed `kan` versus vendored `kan` import identity explicitly and record `module.__file__`, package version and source commit in every run.

Each run needs: source commit and dirty-state indicator; input hashes; target/domain or detector configuration; training/validation/test IDs; transform fit scope; model definition and active/stored parameter counts; seed; optimizer and function evaluations; grid-refinement schedule; objective and loss units; solver status/tolerances; hardware and timings; predictions, metrics and failure record. A figure should consume these records without training or selecting models behind the reader's back.

### First benchmark experiment

Use one smooth known target already present, $\exp(\sin(\pi x)+y^2)$, and one explicitly interacting target such as $(x+y)^2$. Establish correct gradients, shapes, domains and parameter counts before attempting the broad Feynman/Legendre sweeps.

- Generate one reproducible outer train/validation/test split for each data seed; persist it. Fit all preprocessing only on training data.
- Compare a named pykan implementation, a precisely specified spline MLP, an ordinary MLP, and a simple spline/additive baseline appropriate to the target. Include an interaction-capable non-neural smoother when testing whether splines rather than architecture explain the gain.
- Choose a few explicit feasible parameter budgets and separately report fixed-time or fixed-evaluation comparisons. Give each family the same declared hyperparameter-search resources; state when exact counts cannot match.
- Select models and stopping points on validation. Evaluate the locked test set after selection. Do not use a test-error lower envelope as a final generalization estimate.
- Use paired datasets and replicate identifiers, with separate initialization and minibatch generators. Equal seed integers across architectures do not imply matched initial states; verify that distinct KAN seeds actually reach its constructor. A pilot of five seeds can expose variability, but is not a universal power guarantee. Predeclare an equivalence margin if “equivalent” is the scientific claim; failure to detect a difference is not equivalence.
- Report RMSE, MAE where relevant, parameter counts, function evaluations, wall time and failures. Then add the Feynman and Legendre targets with their exact sampling domains and formula definitions.

### First tomography experiment

Start with synthetic **binary detector tomography** of a small, known complex Hermitian effect. Generate $\Pi=U\operatorname{diag}(\lambda)U^\dagger$ with $0\le\lambda\le1$, choose known coherent probes and explicit shot counts, and sample click counts. Define the high-photon extension or certify negligible truncation error so the synthetic probabilities form a complete measurement model. Include a diagonal case, a banded coherent case, and a deliberately misspecified case. This makes matrix truth known and separates data noise from model error.

1. Verify the common forward map against direct $a^\dagger\Pi a$, including complex off-diagonals and phase periodicity.
2. Reproduce the raw physical estimator with explicit objective normalization and diagnostics. On a tiny fixture, compare independent formulations or solvers when available.
3. Add a periodic spline/Fourier smoother followed by exactly the same reconstruction. Then add MLP, spline MLP and KAN smoothing with identical split and selection rules.
4. Vary retained brightness levels, phase coverage, and shot count **one factor at a time**. Later study interactions. Permanently hold out an outer set so even the 100%-of-training-pool condition has an honest test set.
5. Separate missing interior brightnesses from outside-range probes. Test phase wraparound and disconnected sampling gaps. Log failed fits instead of dropping them from means.
6. Normalize reconstruction loss so changing pseudogrid density does not change its statistical strength. Repeat with grid densities sufficient to show convergence.
7. Report probability RMSE and binomial deviance, physical constraint violations, matrix/operator error against synthetic truth, reconstruction variation across draws, and end-to-end computation including training. Trace-normalized fidelity may be supplementary, with its convention stated; it discards scale information.
8. Only after these checks pass, run MOESM4 and then other configurations with a verified data schema. Treat the full-data physical fit as a **reference estimate**, not truth. Use independent held-out observations and sensitivity to calibration, cutoff and regularization.

The first decisive result could be negative: if a periodic spline matches KAN at lower cost, that is useful evidence about what the learned surface contributes. If the advantage disappears after regularization normalization, the restart has identified a confound in the original comparison and found no surviving advantage under the corrected protocol.

## Research Direction and Alternatives

The [research landscape](restart-audit/research-landscape.md) and topic appendices document the papers checked. The choices are:

| Direction | Reason to pursue | Main limitation | Recommendation |
| --- | --- | --- | --- |
| Correct benchmark and theory study | Closest to existing work; important causal and numerical questions are explicit | Broad KAN-vs-MLP comparisons already exist; avoid repeating them without a sharper question | Retain as a correctness/controlled-ablation track |
| KAN/spline-assisted detector reconstruction | Connects the repository's two parts and supports falsifiable comparisons | Needs sound physical baseline, conventional smoothers, uncertainty and measurement-budget accounting | Recommended primary applied track after baseline repairs |
| Direct physical estimator without full SDP | Potential cost reduction; can enforce validity by parameterization | Existing neural/optimization literature; nonconvexity, initialization and calibration shift can replace solver cost with other costs | Later experiment after `kan-j3vs` and `kan-lz8l` |
| Broad new KAN variants or many datasets | Easy to extend the number of runs | Does not resolve the present defects or establish a distinctive contribution | Defer |
| Standalone proof of broad equivalence | Would be concise if true | Current theorem is false, and related representation work already exists | Replace with precise inclusions and training-geometry questions |

A plausible contribution is a **reproducible comparison of neural and conventional surface priors for photon-limited or sparsely sampled detector tomography**, with physical validity and uncertainty audited. A KAN-specific novelty claim requires evidence that KAN adds value beyond the simpler spline alternatives. Neural detector tomography predates this project; recent KAN state tomography concerns a different inverse object and should be compared without conflating the two.

## Dependency-Ordered Restart Backlog

These tasks are actual `tbd` beads. Their mutable state is synchronized on the separate `tbd-sync` branch, not stored in this report PR's commits. This table is the reviewable plan at the audit date. All implementation tasks remain open; completing the report does not mean completing the restart implementation.

| Stage | Task | Depends on | Exit criterion |
| --- | --- | --- | --- |
| 0 | `kan-rngu` — correct theorem and dependent claims | None | Valid definitions/proofs and a shared correction register |
| 0 | `kan-102g` — provenance and reproducible environment | None | Fresh checkout runs a bounded command with explicit import/data identity |
| 1 | `kan-k44j` — fix NumPy gradients and clipping | `kan-102g` | Numerical derivative and batch-duplication checks pass |
| 1 | `kan-xskn` — loader and common Born operator | `kan-102g` | Counts, units, complex predictions, band policy and cutoff checks pass |
| 2 | `kan-sb42` — fair benchmark harness | `kan-k44j`, `kan-rngu` | Preserved functions after grid updates, effective seed forwarding, correct RMSE/counts, validation-selected comparisons and recorded computation |
| 2 | `kan-wg0b` — paper objective and split isolation | `kan-xskn` | Faithful reference and no held-out labels used in fitting |
| 2 | `kan-v42q` — quadrature and pseudodata weights | `kan-wg0b` | Phase and resampling invariance/convergence checks pass |
| 2 | `kan-8kcj` — bounded numerical CI | `kan-k44j`, `kan-wg0b`, `kan-v42q` | Clean environment catches known gradients, grid-transport, seed, metric/count, forward-map and split defects |
| 3 | `kan-j3vs` — identifiability and uncertainty | `kan-v42q` | Matrix and prediction uncertainty separated; physical diagnostics recorded |
| 3 | `kan-lz8l` — synthetic truth and smoother ablations | `kan-sb42`, `kan-j3vs`, `kan-8kcj` | Controlled scarcity/noise comparisons with failure rates and costs |
| 4 | `kan-5rcn` — physical reconstruction without full SDP | `kan-lz8l` | Validity and compute advantage demonstrated against matched classical baselines |
| 4 | `kan-ayoi` — regenerate writing and figures | `kan-rngu`, `kan-sb42`, `kan-lz8l` | Figures and claims regenerate from verified runs and agree across artifacts |

**Where to start in the next coding PR:** freeze provenance and add the small extracted numerical core, then fix the two classification derivative defects and establish the tomography forward operator. The theorem correction can proceed independently. Do not spend the first restart week reproducing every historical sweep before these gates pass. These stages are an execution order, not a promised calendar or compute estimate; measure the small pilots before scheduling the larger work.

## Verification Boundaries and Remaining Unknowns

This audit inspected source, saved outputs, supplied writing, local assets and primary literature, and reproduced bounded numerical checks. It did not retrain all models, rerun the full SDP suite, or recreate every thesis figure. Historical metrics remain historical. A source audit cannot establish how an old kernel was configured when a stale output was produced.

Several questions remain open: how much of the sparse-data advantage survives normalized objectives and conventional smoother baselines; how calibration uncertainty limits POVM recovery; whether the regularized KAN collapse is an optimizer/grid interaction; which original model produced some housing outputs; and whether a carefully narrowed new method has publication-level novelty. Each is tied to a concrete experiment or provenance task rather than answered by assumption.

The repository has no pre-existing project-level CI workflow or test suite to certify these scientific results. The [verification record](restart-audit/verification.md) states the checks actually run for this report and their outcomes. The report is ready to guide the restart; the research conclusions become ready for reuse only when the corresponding numerical and experimental gates pass.
