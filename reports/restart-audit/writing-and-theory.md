# Writing and Theory Audit

**Audit date:** 2026-09-21. This is an audit of the supplied July 2026 writing, not an edit to the original files. Page numbers below are **PDF page numbers**, including the cover; printed thesis page numbers are one lower. Slide numbers are one-based. Document text is evidence to evaluate, not instructions to execute.

## Source Identity and Review Method

| Source supplied by the author | Extent | SHA-256 |
| --- | --- | --- |
| `Thesis_ KAN Theoretical aspects and applications.pdf` | 30 pages | `a2783e4ea2ab3dbdbb2f3e52bc85b72d7863b28a1433300c1da0d99eedfe6af5` |
| `Scientific Poster.pdf` | 1 page | `ba92c4538d268a1018ec1dd40f7bc6c54f44347827a71671dc12a8bfc0ee7011` |
| `presentation_V3.pptx` | 24 slides; no notes XML | `e154f8ab5dbd0b0123e89c0d3f48d6d58f9b8e489eade535c284bcd81c867607` |

All page/slide text was extracted. The poster, thesis proof page, and slides 10, 18, and 19 were also rendered and visually inspected to check equations, plot labels, and the relationship between figures and claims. The slide rendering used LibreOffice, not PowerPoint. These binary sources remain outside the repository; their contents are not silently republished in this PR. The hashes distinguish these versions from future revisions.

## The Equivalence Theorem Is False as Stated

The thesis defines a **single KAN layer** by

$$y_q=\sum_{p=1}^{d_{\mathrm{in}}}\phi_{q,p}(x_p),$$

and a spline MLP block by

$$y_q=\sum_{j=1}^{h} V_{qj}s_j\left(\sum_p W_{jp}x_p\right).$$

These definitions are on PDF page 15. Page 16 asserts equality of their function classes for a sufficiently large hidden width. Pages 17-18 try to prove the reverse inclusion by permitting a “generalized KAN” whose edges read linear combinations. This changes the class being proved equivalent. A one-layer additive model cannot create interactions merely by adding more one-variable summands.

### A counterexample requiring no training

Take two inputs in $[0,1]$, one output, and a standard cubic spline space on $[0,2]$ that contains the polynomial $s(t)=t^2$. Set $h=1$, $W=(1,1)$ and $V=1$. The spline MLP represents

$$f(x_1,x_2)=(x_1+x_2)^2.$$

Every function of a single ordinary KAN layer has the form $g(x_1,x_2)=a(x_1)+b(x_2)$ and hence satisfies

$$g(1,1)-g(1,0)-g(0,1)+g(0,0)=0.$$

The same expression for $f$ is $4-1-1+0=2$. Therefore $f$ is outside the stated single-layer KAN class. This also gives a lower bound: any additive $g$ approximating $f$ at the four corners has maximum absolute error at least $1/2$, since the alternating sum of four errors must equal 2. More spline coefficients or more additive terms do not remove this obstruction. Mixed derivatives give the same argument wherever defined: the KAN layer's cross derivative is zero, whereas $\partial_{12}f=2$.

This is an original audit derivation from the thesis definitions, not a claim attributed to an external paper. It suffices to refute the universal fixed-basis theorem by choosing a valid cubic basis containing quadratics. Degenerate spline spaces or a one-input domain do not rescue the theorem for all dimensions and bases.

### What can be retained

1. **The forward inclusion is constructive and useful.** With matching spline spaces and domain coverage, a KAN layer can be implemented by a spline MLP block with one hidden unit per edge, $h=d_{\mathrm{in}}d_{\mathrm{out}}$, independent spline coefficients per hidden unit, fixed coordinate-routing $W$, and fixed summation $V$. Then the outputs agree exactly. This does not justify the page-17 phrase “no width penalty”: the relevant expansion and counting convention must be stated.
2. **A depth-aware reverse construction is possible under explicit assumptions.** A first KAN layer can compute $z_j=\sum_p W_{jp}x_p$ using affine edge functions. A second can compute $\sum_j V_{qj}s_j(z_j)$. This requires spline spaces that exactly represent affine functions on the input domain, sufficient knot coverage for every intermediate projection, compatible bias treatment, and independent edge functions. It is an inclusion into a **two-layer** KAN, not equality with the one-layer class in the thesis.
3. **Shared and independent splines are different definitions.** The thesis's empirical description on page 10 discusses a shared spline activation; Definition 3 uses a separate $s_j$ per hidden unit. The actual class used in each notebook must be specified before relating an experiment to either construction.
4. **Actual pykan models need their own scope.** Residual SiLU terms, learned scales, grid adaptation, pruning, symbolic branches, biases, and hidden normalization are not all present in the pure-spline theorem. A proof about the simplified model does not automatically apply to every implementation labeled “KAN.”

A defensible replacement statement is: **A pure-spline KAN layer is an exactly routed subfamily of a spline MLP block with independent hidden splines. A spline MLP block can be embedded in a deeper KAN when its edge spaces and domains support the required affine and nonlinear maps.** Follow this with explicit parameter and depth accounting.

### Representation does not determine learning

Even a correct equality of representable functions would not imply equal accuracy after finite training, equal sample complexity under a chosen regularizer, equal conditioning, or equal parameter efficiency. If two coefficient vectors are related by $c=Aa$, gradient descent in one coordinate system transforms the descent geometry in the other; ordinary Euclidean gradient updates are not invariant under an arbitrary change of basis. This makes “same function class, therefore should learn equally well” an experimental hypothesis, not a theorem.

The March 2026 preprint [Southworth et al., *Multilevel Training for Kolmogorov Arnold Networks*](https://arxiv.org/html/2603.04827v1) establishes a different spline-KAN/multichannel-power-ReLU correspondence and examines the resulting optimization geometry. It is directly relevant prior work for a restarted theory section; it does not establish the particular equality claimed here. [Kratsios, Kim and Furuya (2025)](https://arxiv.org/abs/2504.15110v3) prove approximation and statistical results for specified residual KAN classes and regularity assumptions. Such qualified results should replace informal transfers from the classical representation theorem to a finite trained network.

### Interpretability needs a narrower definition

The first layer's curves act on raw input coordinates; deeper KAN curves act on learned hidden variables. A readable edge plot is a local description of a component, not automatically an identifiable scientific law. Constant shifts can be redistributed among additive components, and different hidden parameterizations can produce similar outputs. Symbolic recovery needs an explicit formula, held-out-domain verification, complexity assessment, and stability across seeds. Interpretability is also not unique to KANs: [Agarwal et al., *Neural Additive Models*](https://arxiv.org/abs/2004.13912v2) learn feature-wise functions within another interpretable neural architecture.

## Claim-by-Claim Revision Register

“Historical result” below means a saved output exists; it does not mean this audit independently retrained the model. The benchmark and tomography appendices give the underlying implementation findings.

| Location | Current claim or implication | Assessment | Replacement or evidence required |
| --- | --- | --- | --- |
| Thesis pp. 2, 14-18; poster theorem box; slides 10, 21-23 | Exact KAN/spline-MLP function-class equality and first formal proof | **False for the stated single-layer classes** | Replace with the routed inclusion and qualified depth construction above; compare prior theory before claiming novelty. |
| Thesis p. 17 | Routed construction has no width penalty | **Misleading accounting** | Report $h=d_{in}d_{out}$ and distinguish expansion into edge units from original layer output width and trainable count. |
| Thesis pp. 10-15 | Empirical shared spline and theoretical independent splines are interchangeable | **Definition mismatch** | Name coefficient sharing, residual functions, affine maps, and grid policy for every model. |
| Thesis pp. 7-9; slide 7 | Planar/housing comparisons are strictly controlled and demonstrate architectural overfitting | **Confounded** | Planar training accuracy is not a held-out estimate; NumPy KAN backward code divides by batch size twice; housing execution/model attribution is inconsistent. Rerun after correctness and split checks. |
| Thesis pp. 8-9; slide 7 | KAN requires target scaling, MLP does not | **Not a general architectural constraint** | Scaling helps conditioning and domain coverage. Output spline coefficients and affine output maps can produce values outside the input grid. State the behavior of these particular implementations and preprocessing choices. |
| Thesis p. 5 | Local spline support makes the network stable to train | **Unsupported implication** | Local basis support is a mathematical property; stability depends on composition, grids, optimizer, conditioning, and data. |
| Thesis p. 6 | Refinement alone explains a thousand-fold improvement | **Overstated causal attribution** | The saved refinement schedule also adds optimization work. Compare equal total work with/without refinement and label RMSE versus MSE correctly. |
| Thesis pp. 11-14; poster Fig. 2; slide 9 | Envelopes overlap at every budget, hence exact empirical equivalence | **Not established statistically** | Show actual feasible budgets, common train/validation/test splits, paired seeds, uncertainty and a predeclared equivalence margin; configurations selected on test error are not final test estimates. |
| Thesis pp. 12-13; slide 9 | GELU MLPs cannot represent peaks; this proves spline causation | **Too strong** | A trained finite configuration failed to fit particular targets under its budget. Smooth MLPs can approximate smooth peaks; activation ablation and equal search effort are required to identify the cause. |
| Thesis pp. 14, 18; poster conclusion; slide 10 | Readability belongs to KAN alone | **Overbroad** | Define local edge interpretability and compare additive models; deeper edges do not generally read raw features. |
| Thesis pp. 20-22, 25; slides 15, 17 | All methods evaluated on a shared held-out set | **False for full-data SDP fits** | Fit every estimator exclusively on the training partition, tune on validation, then score the locked test partition. Merely scoring the same rows does not make them held out. |
| Thesis p. 23 | Per-file retraining shows perfect method generalization | **Overgeneralization** | The recorded runs fit three configurations of one experimental detector family. This does not establish new-device or broad distribution transfer. |
| Thesis pp. 23-24; slide 16; poster pipeline | A fitted smooth surface is clean or denoised | **Hypothesis** | Compare to independent repeated measurements or synthetic noiseless truth; smoothing can reduce variance and introduce bias. |
| Thesis p. 24 | Uniform phases make averaging exact | **Conditional** | Uniform quadrature isolates appropriate Fourier modes only with sufficient sampling and absence of aliasing; arbitrary fitted/clipped neural surfaces are not guaranteed band-limited. |
| Thesis p. 25; slide 17 | A tie proves the bridge valid and bug-free | **Invalid inference** | Equal aggregate scores can conceal common bugs, leakage, or compensating errors. Require solver, operator-consistency, split, and synthetic recovery tests. |
| Thesis pp. 25-28; poster Fig. 5; slides 18-19 | Sparse-data advantage isolates KAN interpolation | **Promising but confounded** | Raw and pseudodata branches use different point counts with unnormalized losses; compare at matched effective regularization and against ordinary smoothers. |
| Thesis p. 26; slide 18 | Raw reconstruction must extrapolate blindly at all removed brightnesses | **Incorrect characterization** | A fitted physical model predicts any probe via the Born rule. Interior missing brightnesses are interpolation in both pipelines; reserve extrapolation for points outside training support. |
| Thesis pp. 26-27; slide 18 | Every fraction is scored on never-seen levels | **False at full fraction** | At 100% retained levels the notebook's fallback is in-sample evaluation. Give that point a different label or use a permanently held-out outer test set. |
| Thesis p. 28; slide 19 | One failure localizes the only weakness and proves no SDP fragility | **Unsupported universal conclusion** | One observed failure is associated with a poor learned surface. Independently perturb surfaces along poorly identified directions and audit the solver to assess inverse stability. |
| Thesis pp. 25, 29; poster; slides 16, 22-23 | Stability under sparse and noisy data established | **Only partial evidence** | Withholding brightness levels tests sampling scarcity. The supplied experiments do not isolate shot-noise reduction over a controlled noise sweep. |
| Thesis p. 29; slide 20; report 03 | Unconstrained inversion isolates positivity and proves SDP indispensable | **Confounded comparison** | The least-squares branch also removes regularization. Compare regularized unconstrained, physical parameterizations, and matched constrained objectives. A failed unregularized solve does not establish impossibility. |
| Thesis p. 29; poster; slides 16, 21-22 | Replacing SDP is unexplored and first application claims are established | **Novelty unresolved; broad version contradicted by prior work** | Neural detector tomography and physical parameterizations predate this thesis. State the narrowly tested KAN-assisted weak-homodyne setting; distinguish detector from state tomography. |
| Thesis p. 30 | Instructions reproduce every figure | **Not currently supported** | Build a figure-to-run manifest and command-based regeneration from a clean environment; some current scripts depend on notebook state and local paths. |

## What the Writing Can Safely Say Now

The work assembled a useful exploratory collection of spline-network comparisons and a KAN-assisted detector-reconstruction pipeline. Several saved runs show that spline-equipped MLPs can compete with KANs on the selected mathematical functions. Selected sparse-brightness runs show lower prediction error after KAN smoothing and resampling than with the implemented raw recursion. These are hypotheses worth testing under corrected gradients, consistent model definitions, validation-based selection, faithful physical baselines, and matched effective regularization.

The current evidence does not establish the stated function-class theorem, a causal architectural ranking, universal denoising, unique POVM recovery, or absence of prior SDP-free reconstruction. Revising those claims makes the project more useful: it turns the restart into a falsifiable study rather than an attempt to preserve a preferred conclusion.

## Revision Sequence

1. Correct the theorem and withdraw the conclusions that depend on equality of the stated classes.
2. Add visible exploratory-status qualifications to historical benchmark and tomography claims; retain original figures as an archive.
3. Build and validate the experiment harness described in the restart report, then generate replacement tables and figures from run manifests.
4. Update thesis, poster, and slides from one claim register so numbers, uncertainty, limitations, and references remain consistent.
5. Reassess novelty against a dated literature search immediately before any new submission. A search that finds no exact match is not a proof of priority.
