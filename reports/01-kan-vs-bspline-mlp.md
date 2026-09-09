# Report 01 — KAN vs B-spline MLP

**Subject:** Does a Kolmogorov-Arnold Network beat a plain MLP because of its learnable
B-spline activation, or because of its edge-based architecture?

**Source folder:** `KAN vs BSpline_MLP/`
**Notebooks:** 8, plus a vendored copy of the KANbeFair benchmark suite
**Filed:** 2026-09-09

---

## 1. The question

Liu et al. (2024, arXiv:2404.19756) introduced KANs and reported large accuracy advantages
over MLPs on symbolic-regression benchmarks. Yu et al. (2024, arXiv:2407.16674, "KAN or MLP:
A Fairer Comparison", code at `github.com/yu-rp/KANbeFair`) pushed back: they argue the
advantage comes from the learnable B-spline activation, not from putting activations on
edges. Swap ReLU or GELU for a learnable spline in an ordinary MLP, they claim, and you
recover essentially all of KAN's benefit.

This folder tests that claim on four targets, under matched conditions:

| Target | Where | Character |
|---|---|---|
| `exp(sin(πx₀) + x₁²)` | Example 1 notebooks | smooth, separable, 2 inputs |
| `exp((sin(π(x₁²+x₂²)) + sin(π(x₃²+x₄²)))/2)` | Example 3 notebooks | deep composition, 4 inputs |
| Feynman I.30.3, `sin²(nθ/2)/sin²(θ/2)` | Feynman notebook | sharply peaked, 2 inputs |
| `scipy.special.lpmv(0, v, x)` | symbolic-formula notebook | associated Legendre, 2 inputs |

Three model classes appear throughout, all taken from KANbeFair's published source rather
than reimplemented:

- **KAN** — pykan's KAN wrapped by KANbeFair, splines on edges, with a SiLU shortcut branch.
- **BSpline_MLP** — `Linear → BSpline → Linear`, splines applied element-wise on hidden
  neurons, no shortcut branch.
- **Plain MLP** — `Linear → GELU/ReLU → Linear`.

---

## 2. Headline finding

**The answer depends on the target function, and the deciding factor is where the splines
sit relative to the raw inputs.**

On the sharply-peaked and special-function targets, KANbeFair's claim holds: KAN and
BSpline_MLP land within a small constant factor of each other, and the direction flips with
the optimizer. On the smooth separable target, it does not hold: when both models get the
full pykan training protocol, KAN wins by roughly 100×, and the notebooks isolate why.

A second finding runs through every notebook: **neither of the original KAN paper's headline
numbers could be reproduced from public pykan.** Not on Feynman I.30.3, not on `lpmv(0)`.

---

## 3. Results by target

### 3.1 Smooth separable target — `exp(sin(πx₀) + x₁²)`

The pykan reference, `Example_1_function_fitting.ipynb`, runs KAN `[2,1,1]` with LBFGS and
progressive grid refinement over G = 3 → 5 → 10 → 20 → 50 → 100, 200 steps per level:

| G | params | test RMSE |
|---|---|---|
| 3 | 36 | 1.39 × 10⁻² |
| 5 | 42 | 7.23 × 10⁻³ |
| 10 | 57 | 5.13 × 10⁻⁴ |
| 20 | 87 | 6.12 × 10⁻⁵ |
| 50 | 177 | 3.12 × 10⁻⁵ |
| 100 | 327 | 3.48 × 10⁻⁵ |

`Example_1_function_fitting_MLP_BSpline_1.ipynb` re-ran this live in the same notebook on
the same dataset object and matched every value to four significant figures, so the
reference is not a lucky run.

`Example_1_function_fitting_MLP + BSpline.ipynb` builds a strictly parameter-matched
BSpline_MLP. Solving `h(G+7) + 1 = 3G + 20` gives h = 3 at every G in the sweep, so the
model is `[2, 3, 1]` throughout:

| G | params | test RMSE | KAN at same G |
|---|---|---|---|
| 3 | 31 | 1.85 × 10⁻¹ | 1.39 × 10⁻² |
| 10 | 52 | 1.04 × 10⁻¹ | 5.13 × 10⁻⁴ |
| 50 | 172 | 1.07 × 10⁻¹ | 3.12 × 10⁻⁵ |
| 100 | 322 | 1.22 × 10⁻¹ | 3.48 × 10⁻⁵ |

BSpline_MLP plateaus around 10⁻¹ and starts overfitting from G = 10 onward. The gap widens
from 13× at G = 3 to roughly 3500× at G = 100.

**Why.** With 2 inputs and strict parameter matching, h collapses to 3. The
`Linear(2 → 3)` projection is the only thing the splines ever see, so they act on mixtures
like `0.7·x₀ + 0.3·x₁`. KAN `[2,1,1]` puts a spline directly on each raw input. Since the
target is separable, refining KAN's grid sharpens the approximations of `sin(πx₀)` and
`x₁²` independently, while refining BSpline_MLP's grid only sharpens resolution over
mixtures the upstream linear layer already scrambled.

The paper's own ablation used higher-dimensional inputs where parameter matching gives
h = 10–20, so this notebook is testing a stricter regime than the paper tested. That is
stated explicitly in the notebook and is the right framing: this identifies a boundary
condition, not a refutation.

### 3.2 The factor decomposition

`Example_1_function_fitting_MLP_BSpline_1.ipynb` runs the cleanest experiment in the
folder — five conditions that separate architecture, optimizer, and grid refinement:

| Condition | Best test RMSE | Gap to pykan reference |
|---|---|---|
| Adam, no refinement, KAN width 5 | 4.60 × 10⁻² | ~1000× |
| Adam, no refinement, BSpline_MLP width 10–20 | 5.45 × 10⁻² | ~1000× |
| Adam, no refinement, KAN `[2,1,1]` | 9.09 × 10⁻¹ | worst of all |
| LBFGS, no refinement, KAN width 5 | 8.65 × 10⁻⁴ | ~28× |
| LBFGS, no refinement, BSpline_MLP | 1.70 × 10⁻³ | ~55× |
| LBFGS, no refinement, KAN `[2,1,1]` | 6.23 × 10⁻³ | ~200× |
| LBFGS + fixed-grid refinement, BSpline_MLP | 1.49 × 10⁻³ | ~48× |
| LBFGS + adaptive refinement, BSpline_MLP | 1.23 × 10⁻³ | ~39× |
| LBFGS + refinement, pykan KAN `[2,1,1]` | 3.12 × 10⁻⁵ | reference |

Read down the column and the decomposition is clean:

1. **Under Adam with no refinement, KAN and BSpline_MLP tie.** KANbeFair's core claim is
   confirmed. If the edge architecture were intrinsically better, it would show here. It
   does not — and the exact pykan architecture `[2,1,1]` is the *worst* performer in this
   condition, because it is a small model with no capacity to fall back on.
2. **Switching to LBFGS buys roughly 10×** for both models. Necessary, not sufficient.
3. **Grid refinement is the remaining ~100×**, and it only works for KAN. BSpline_MLP given
   the identical refinement schedule barely moves, whether the grid is fixed to [-1,1] or
   made adaptive to match pykan's `update_grid_from_samples` logic exactly.

The conclusion the notebook draws is worth repeating: the architecture is not the *source*
of the advantage, it is the structural precondition that lets grid refinement land on
something useful.

### 3.3 Deep composition — Example 3

`Example_3_deep_formula.ipynb` confirms the depth argument from the original paper. A
3-layer KAN `[4,2,1,1]` reaches test RMSE 3.78 × 10⁻⁵ at G = 50. A 2-layer KAN `[4,9,1]`
on the same target bottoms out at 8.05 × 10⁻³ (G = 20) and then gets *worse* at G = 50
(9.89 × 10⁻³) while training loss keeps falling — textbook overfitting.

`Example_3_deep_formula_MLP + BSPline.ipynb` runs BSpline_MLP against the 3-layer KAN
reference at matched parameter counts:

| Approach | Best test RMSE | vs KAN |
|---|---|---|
| KAN `[4,2,1,1]`, G = 50, 620 params | 3.79 × 10⁻⁵ | reference |
| BSpline_MLP, parameter-matched, best | 1.38 × 10⁻¹ | ~3600× worse |
| BSpline_MLP, progressive refinement, G = 50, 591 params | 6.71 × 10⁻² | ~1800× worse |
| BSpline_MLP `[4,2,1,1]` same shape as KAN, G = 50, 174 params | 4.17 × 10⁻¹ | ~11000× worse |

Same story as Example 1, larger magnitude. Several BSpline_MLP configurations are stuck at
RMSE ≈ 0.58 across multiple grid sizes, meaning they did not learn at all.

### 3.4 Feynman I.30.3 — sharply peaked

`Feyman_dataset_fitting_KAN_and_Bspline_MLP.ipynb` is the strongest evidence *for*
KANbeFair. Target `sin²(nθ/2)/sin²(θ/2)`, 100,000 samples on `[1,5]²`, 80/10/10 split,
inputs min-max normalised to [-1,1].

At a matched budget of 441 trainable parameters, Adam, 50 epochs, 3 seeds:

| Model | params | test RMSE | Paper Table 2 |
|---|---|---|---|
| KAN | 441 | 4.08 × 10⁻² | 1.03 × 10⁻³ |
| BSpline_MLP | 433 | 3.18 × 10⁻² | — |
| MLP (GELU) | 441 | 4.67 × 10⁻¹ | 1.50 × 10⁻² |

KAN and BSpline_MLP are 1.28× apart, within noise. Both are an order of magnitude below
plain MLP. The paper's ~15× MLP-to-KAN gap survives when KAN is replaced by an MLP that
merely has spline activations, which is exactly the KANbeFair prediction.

An unconstrained sweep taking the lower envelope over 40 configurations agrees: KAN best
2.33 × 10⁻² at 465 parameters, BSpline_MLP best 2.04 × 10⁻² at 865 parameters, plain
ReLU MLP stuck at 2.50 × 10⁻¹ even with 2049 parameters.

The depth-and-optimizer sweep is the most interesting result in the notebook:

| depth | KAN Adam | KAN LBFGS | BSpline_MLP Adam | BSpline_MLP LBFGS |
|---|---|---|---|---|
| 1 | 2.33 × 10⁻² | 5.93 × 10⁻³ | 2.04 × 10⁻² | 9.62 × 10⁻³ |
| 2 | 7.38 × 10⁻³ | **1.62 × 10⁻³** | 6.45 × 10⁻³ | 2.63 × 10⁻³ |
| 3 | 8.58 × 10⁻³ | 2.15 × 10⁻³ | 3.84 × 10⁻³ | 7.56 × 10⁻¹ (diverged) |

Three things fall out. LBFGS beats Adam by 3–4× everywhere. Depth 2 is the sweet spot. And
KAN at depth 2 under LBFGS reaches 1.62 × 10⁻³, within 60% of the paper's 1.03 × 10⁻³ by
direct training with no prune-and-retrain pipeline.

The BSpline_MLP failure at depth 3 under LBFGS is real, not a fluke: the run terminated in
8 seconds instead of the expected ~150 because the strong-Wolfe line search could not find
a descent direction. KAN at the same depth and optimizer did not fail. That is a small but
genuine robustness point in KAN's favour, plausibly attributable to the SiLU shortcut
smoothing the loss landscape.

One more number settles the fairness argument: plain MLP at depth 3 with 132,609
parameters reaches 1.61 × 10⁻², essentially matching the paper's 1.50 × 10⁻². The paper's
MLP number is reproducible. It only looks bad when the budget is controlled.

### 3.5 Associated Legendre — `lpmv(0, v, x)`

`symbolic_formula_representation_MLP_Spline.ipynb` is the longest investigation in the
folder, eleven parts. The original paper's Table 1 reports a 330× KAN-to-MLP gap on this
function, the largest in its 15-function table.

**The paper's number is not reproducible.** Three independent protocols were tried:

| Protocol | Best KAN test RMSE | vs paper's 5.25 × 10⁻⁵ |
|---|---|---|
| Direct LBFGS training of `[2,2,1]` on `[-1,1]²` | 1.09 × 10⁻² | ~207× worse |
| KANbeFair-style Adam sweep on `[0,1]²` | 4.53 × 10⁻⁴ | ~8.6× worse |
| Paper's Section 3.2 sparsify → prune pipeline | 4.00 × 10⁻¹ post-prune | ~7600× worse |

The third result deserves emphasis. Running the paper's own protocol end-to-end, with the
full depth sweep {2..6} and both λ values, the pipeline collapses past G ≈ 5 in every run.
Inside a representative run the test loss goes 1.45 × 10⁻² at G = 5, then 3.64 × 10⁻²,
7.65 × 10⁻², 9.43 × 10⁻², 1.21 × 10⁻¹, and finally 9.30 × 10⁻¹ at G = 200 — the model has
collapsed to predicting the mean. The mechanism is identified: as the grid grows, spline
coefficient count goes from O(100) to O(10⁴) while the L1-plus-entropy penalty stays at
λ × O(params), so LBFGS minimises it the cheap way by driving every spline to zero. None
of the completed runs produced the paper's reported `[2,2,1]` pruned shape.

**KAN and BSpline_MLP are effectively tied**, with the winner set by the optimizer:

| Protocol | KAN | BSpline_MLP | Plain MLP | Winner |
|---|---|---|---|---|
| KANbeFair Adam, `[0,1]²` | 4.53 × 10⁻⁴ | 2.78 × 10⁻⁴ | 1.36 × 10⁻³ | BSpline_MLP by 1.6× |
| Unified LBFGS, `[0,1]²` | 4.28 × 10⁻⁴ | 5.40 × 10⁻⁴ | 7.42 × 10⁻⁴ | KAN by 1.3× |
| Unified LBFGS, `[-1,1]²` | 3.65 × 10⁻² | 3.78 × 10⁻² | 3.37 × 10⁻² | plain MLP by 1.08× |

**The paper's 330× gap collapses to single-digit factors in every controlled comparison.**

The notebook also settles where the paper's gap came from. A range-controlled plain-MLP run
on `[-1,1]²` lands at 4.78 × 10⁻², within ~3× of the paper's reported 1.74 × 10⁻². So the
paper's MLP baseline is plausibly honest, and the 330× gap is most likely driven by
undisclosed dataset details on the KAN side rather than by an under-tuned MLP.

KANbeFair's own published numbers, by contrast, reproduce within a factor of 2 from their
public code.

---

## 4. What the folder establishes

1. **KANbeFair's core claim is correct in the regime they measured.** On sharply-peaked
   symbolic targets (I.30.3) and special functions (`lpmv(0)`), KAN and BSpline_MLP are
   interchangeable at matched budget. The advantage over plain MLP is an activation-function
   property.

2. **The claim breaks on smooth separable targets under the full pykan protocol.** There
   the gap is ~100×, and it is attributable to grid refinement being useful only when
   splines sit on raw inputs. This is a genuinely new boundary condition, tested more
   strictly than the paper tested it.

3. **Strict parameter matching can make BSpline_MLP unable to learn at all.** On 2-input
   targets, matching against a small KAN forces h = 2–3, and the model gets stuck. Reported
   parity between the two architectures usually rests on BSpline_MLP having 10–20× more
   parameters.

4. **Neither of the original KAN paper's headline numbers reproduces from public pykan.**
   5.25 × 10⁻⁵ on `lpmv(0)` and 1.03 × 10⁻³ on I.30.3 both fall short by between 8× and
   7600× depending on protocol. The paper's own tutorial notebook flags library
   regression: "For some reason, this got worse than pykan 0.0."

5. **Optimizer choice dominates architecture choice.** LBFGS beats Adam by 3–4× across
   architectures and depths. Any Adam-only comparison of these models is leaving a larger
   effect on the table than the effect it is trying to measure.

---

## 5. Weaknesses and open items

**Seeds.** Most results are single-seed. Where seeds were swept in the Feynman notebook,
all three KAN seeds returned the identical RMSE of 4.084 × 10⁻², because KANbeFair's
wrapper does not forward a `seed` kwarg into pykan's `KAN` constructor. The error bar
reported for KAN there is meaningless. Fix is a one-line edit to
`KANbeFair/src/models/kanbefair.py`.

**FLOPs are never matched.** KAN and BSpline_MLP cost roughly 5× more per forward pass than
plain MLP at equal parameter count, because De Boor-Cox spline evaluation is expensive.
Every comparison in this folder controls trainable parameters. Under FLOP matching, plain
MLP gets a much wider hidden layer. The Feynman notebook already prints `total_flops()`
per model, so the change is small.

**The SiLU shortcut is uncontrolled.** pykan's KAN layer includes a shortcut branch
`φ(x) = w_b·silu(x) + w_s·spline(x)`. BSpline_MLP has no equivalent. Every KAN-versus-
BSpline_MLP comparison here is therefore "spline plus shortcut" against "spline alone", not
a clean architectural ablation. pykan supports `base_fun = nn.Identity()` to remove it;
a 2×2 factorial would isolate its contribution.

**Under-training of plain MLP.** In the Feynman matched-budget run, plain MLP's validation
curve was still descending at epoch 50. Its absolute number is conservative, though the
ordering at depth 1 would not change.

**Single functions.** Each conclusion rests on one target. The I.30.3 result is one Feynman
formula; the `lpmv(0)` result is one special function. Both notebooks are structured so the
target is a one-line swap.

### Ranked next steps

1. Match FLOPs instead of parameters on the 2D smooth target. This directly tests whether
   the `Linear(2→3)` bottleneck is the cause of BSpline_MLP's failure there, without
   changing the problem. Most diagnostic single experiment available.
2. Fix seed forwarding in the KANbeFair wrapper and re-run the Feynman matched-budget point
   with 5 real seeds.
3. Run the 2×2 shortcut ablation (KAN ± SiLU shortcut, BSpline_MLP ± shortcut).
4. Replicate the I.30.3 comparison on 2–3 more Feynman formulas. If KAN ≈ BSpline_MLP holds
   across several, the claim is on much firmer ground than one data point.
5. Recover the canonical `lpmv` input domain and sample count from pykan's `experiments/`
   scripts. The residual gap to 5.25 × 10⁻⁵ may be a dataset artifact.

---

## 6. References

- Liu, Z. et al. *KAN: Kolmogorov-Arnold Networks*. arXiv:2404.19756 (2024).
- Yu, R., Yu, W., Wang, X. *KAN or MLP: A Fairer Comparison*. arXiv:2407.16674 (2024).
  Code: `github.com/yu-rp/KANbeFair`.
- pykan: `github.com/KindXiaoming/pykan`.
