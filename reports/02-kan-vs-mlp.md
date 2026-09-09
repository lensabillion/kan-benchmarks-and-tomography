# Report 02 — KAN vs MLP

**Subject:** Head-to-head comparisons of KANs against standard MLPs on classification and
regression tasks, using from-scratch NumPy implementations and applied datasets.

**Source folder:** `KAN vs MLP /` (note the trailing space in the directory name)
**Notebooks:** 6
**Filed:** 2026-09-09

---

## 1. What this folder is

Two distinct things live here, and they should be read differently.

**Teaching notebooks.** `MLP_vs_KAN_Research_Demo.ipynb` and
`KAN_vs_NN_Planar_Classification (1).ipynb` build both an MLP and a KAN from scratch in
NumPy, on the flower-shaped planar dataset from the deeplearning.ai course assignment. They
are written as explained walkthroughs, with the maths spelled out, comprehension questions
after each section, and B-spline basis functions plotted for intuition. Their purpose is to
make the architectural difference concrete: an MLP learns weights on edges and applies a
fixed tanh at nodes, a KAN learns a curve on each edge and just sums at nodes.

**Applied notebooks.** `KAN_housing_prediction.ipynb`, `NN_housing_prediction.ipynb`, and
`NN__Heating_Cooling_Prediction.ipynb` run the two architectures on real regression
datasets — California housing and UCI energy efficiency.

`Example_1_function_fitting.ipynb` is a copy of the pykan tutorial and duplicates the
reference run analysed in [Report 01](01-kan-vs-bspline-mlp.md).

The headline outcome is easy to state and easy to over-read: **the MLP won every comparison
in this folder.** The rest of this report is about why none of those wins is yet a
controlled result.

---

## 2. Results as recorded

### 2.1 Planar flower classification, both from scratch

`KAN_vs_NN_Planar_Classification (1).ipynb`, 400 points, 2 features, 2 classes:

| Model | Training accuracy |
|---|---|
| Logistic regression | 47% |
| Neural network, n_h = 4 | 91% |
| KAN, n_h = 4, G = 5 | 82% |

Both non-linear models beat logistic regression by a wide margin, which is the pedagogical
point. Swept across hidden sizes:

| n_h | NN | KAN | Winner |
|---|---|---|---|
| 1 | 68% | 50% | NN |
| 2 | 67% | 64% | NN |
| 4 | 91% | 82% | NN |
| 8 | 91% | 76% | NN |
| 16 | 91% | 72% | NN |

The KAN peaks at n_h = 4 and then degrades as it gets wider, which is consistent with
overfitting on 400 points given that its parameter count grows about six times faster per
hidden unit than the MLP's.

`MLP_vs_KAN_Research_Demo.ipynb` runs the same comparison with a different implementation
and different hyperparameters (10,000 iterations at lr = 1.2 for the MLP, 15,000 at lr = 2.0
for the KAN in the sister notebook), and gets MLP 90.8% against KAN 77.2% at n_h = 4. The
two notebooks disagree by 5 percentage points on the same nominal KAN configuration, which
is itself a useful indication of how much the result moves with hyperparameters.

### 2.2 The parameter-matched experiment, and why it does not hold

`MLP_vs_KAN_Research_Demo.ipynb` correctly identifies that comparing at equal `n_h` is
unfair, because a KAN uses roughly `(G + degree + 1)` parameters per edge against the MLP's
one. Its Experiment 3 sizes each model to hit a shared parameter budget. The recorded
output:

| Budget | MLP shape | MLP params | MLP acc | KAN config | KAN params | KAN acc |
|---|---|---|---|---|---|---|
| 50 | [2,16,1] | 65 | 91.5% | G = 6 | 30 | 50.0% |
| 80 | [2,26,1] | 105 | 91.8% | G = 12 | 48 | 85.8% |
| 120 | [2,39,1] | 157 | 90.5% | G = 20 | 72 | 50.0% |
| 160 | [2,53,1] | 213 | 90.8% | G = 28 | 96 | 79.0% |
| 200 | [2,66,1] | 265 | 91.0% | G = 36 | 120 | 70.5% |
| 250 | [2,83,1] | — | 92.2% | G = 46 | — | 87.8% |

**The budgets were not met.** Look at the two parameter columns: the MLP has roughly 2.2×
the KAN's parameters at every single budget. The experiment labelled "the research-valid
version" is the least fair comparison in the notebook.

The cause is a formula error that is checkable from the output. The notebook's markdown
states MLP parameters as `n_h*2 + n_h + n_h + 1 = 3*n_h + 1` and solves
`n_h = (budget - 1)/3`. But that arithmetic is wrong: `2·n_h + n_h + n_h + 1` is
`4·n_h + 1`, not `3·n_h + 1`. Every printed count confirms the model has `4·n_h + 1`
parameters — n_h = 16 gives 65, n_h = 26 gives 105, n_h = 39 gives 157, n_h = 53 gives 213,
n_h = 66 gives 265. So every MLP is about a third larger than intended, while the KAN side
lands under budget, and the two errors compound in the same direction.

The notebook's own interpretation text anticipates that "KAN wins at high budgets", and the
summary claims KAN "can overtake at high budgets". Neither happened — MLP won all six. The
prose was written from expectation rather than from the table.

Two accuracy values of exactly 50.0% (budgets 50 and 120) are a further warning: 50% on a
balanced 2-class problem is the chance floor, so those KAN runs did not train at all rather
than training and losing.

### 2.3 California housing regression

Two separate notebooks, same dataset (20,640 rows, 8 features), same 80/20 split with
`random_state=42`, same standardisation:

| Model | Framework | Setup | Test MAE | In dollars |
|---|---|---|---|---|
| MLP | Keras | [8,16,8,16,8,1] tanh, 569 params, Adam, 100 epochs, batch 32 | 0.3501 | $35,010 |
| KAN | pykan | [8,16,8,16,1], grid 5, k 3, Adam, 100 steps | 0.6087 | $60,874 |

The MLP is off by about half as much. But the KAN run should not be reported as a result:
its training log ends at `train_loss 1.06e+00 | test_loss 1.01e+01`. A test loss three
orders of magnitude above the training loss means the run diverged. A commented-out cell in
the same notebook records an earlier, smaller KAN `[8,16,8,1]` that ended at
`train 6.91e-01 | test 7.06e-01` — a healthy, converged run that was then replaced by the
deeper diverged one. The reported 0.6087 MAE comes from the diverged model.

The two runs are also not comparable on budget or schedule. The MLP had 569 parameters and
100 epochs over 413 mini-batches each, roughly 41,000 gradient steps. The KAN had 100 full
steps. These are different amounts of training by three orders of magnitude.

### 2.4 Energy efficiency (heating load)

`NN__Heating_Cooling_Prediction.ipynb` fits a Keras MLP `[8,8,10,8,4,1]` with tanh
activations to the UCI energy efficiency dataset (768 rows), predicting heating load Y1
only. Test MAE 0.7990 kWh/m².

**There is no KAN counterpart.** The notebook installs pykan in its first cell and never
uses it. Despite sitting in a folder named for the comparison, this notebook contains only
one of the two models.

The notebook also does not execute cleanly top to bottom. Cell 3 raises
`NameError: name 'fetch_ucirepo' is not defined` and cell 7 raises
`NameError: name 'y_train' is not defined`, yet later cells produce output — so it was run
out of order with state carried over from a previous session. The results are not
reproducible from the committed file as it stands.

---

## 3. What can and cannot be claimed

**Can claim.** On the planar flower dataset, with these implementations and these
hyperparameters, a small tanh MLP reaches higher accuracy than a from-scratch KAN across
every hidden size tried, and converges in fewer iterations. This is consistent with the
mechanism the notebooks describe: spline coefficients start near zero, so a KAN's edges
begin flat and produce no gradient signal until they develop shape, whereas tanh supplies
strong non-linearity from the first iteration.

**Can claim.** A KAN's parameter count grows much faster with width than an MLP's, so
comparing at equal `n_h` systematically favours the KAN on capacity and the MLP on
efficiency. Both notebooks identify this correctly, which is the main thing they get right
methodologically.

**Cannot claim.** That MLPs outperform KANs on these tasks. No comparison in this folder
controls parameter count (Section 2.2), optimizer, or training budget (Section 2.3)
simultaneously. The one experiment that attempted parameter control got the arithmetic
wrong in the MLP's favour.

**Cannot claim.** Anything about the energy-efficiency task, since only one model was run.

**Cannot claim.** Anything about KAN's interpretability advantage in practice. Both
notebooks plot the learned φ curves and present this as KAN's unique strength, which is a
fair qualitative point, but no notebook here tests whether the recovered curves match a
known ground-truth function. That test does exist elsewhere in this repository — see the
symbolic-formula work covered in [Report 01](01-kan-vs-bspline-mlp.md).

---

## 4. Correctness issues found

**Numerical instability in the from-scratch implementations.** The planar classification
notebook emits `RuntimeWarning: divide by zero encountered in matmul`,
`overflow encountered in matmul`, and `invalid value encountered in matmul` repeatedly —
including inside the standard NN forward pass at `Z1 = W1 @ X + b1`. A two-layer tanh
network on 400 points with weights initialised at 0.01 scale should not overflow. Something
is producing infinities or NaNs in the parameters, most likely the learning rate of 1.2 over
10,000 iterations with no gradient clipping. The accuracies reported alongside these
warnings should be treated as provisional until the warnings are chased down.

**Deprecated NumPy conversion.** Both notebooks compute accuracy via
`float(np.dot(Y, preds.T) + ...)`, which raises `DeprecationWarning: Conversion of an array
with ndim > 0 to a scalar is deprecated, and will error in future`. This will break outright
on a future NumPy. Fix is to index the scalar out, `.item()` or `[0, 0]`.

**Stale absolute path.** The planar notebook's warnings reveal it was executed against a
virtualenv at `/Users/lensa/Term_3/Research/papers/Quantum Paper/.venv`, which is neither in
this repository nor related to this sub-project.

**Folder name.** The directory is `KAN vs MLP ` with a trailing space. This is legal on
macOS but causes quoting problems in shell scripts and is worth renaming.

---

## 5. Recommended next steps

Ranked by how much each would change what this folder can claim.

1. **Fix the parameter-matching arithmetic** in Experiment 3 of the research demo. Use
   `4·n_h + 1` for the MLP, and size the KAN's G so its count lands within a few percent of
   the same target rather than at half. This single fix determines whether the folder's
   headline finding survives. Cheapest change with the highest information value.

2. **Re-run the housing KAN.** Use the converged `[8,16,8,1]` configuration rather than the
   diverged one, match the parameter budget to the Keras MLP's 569, and equalise the
   training budget in gradient steps rather than in nominal iterations.

3. **Add the missing KAN to the energy-efficiency notebook**, and make it run top to bottom
   without NameErrors. Right now the file cannot be executed as committed.

4. **Add seeds.** Every accuracy in this folder is single-seed. Differences of 5–10
   percentage points on 400 points are well within seed variance for a small network; the
   two planar notebooks already disagree by 5 points on nominally the same model.

5. **Report a held-out test split for the planar task.** Accuracies are currently computed
   on the training set. That is standard for the original course assignment but is not
   adequate for a capacity comparison, which is precisely where train-set accuracy is most
   misleading.

---

## 6. References

- Liu, Z. et al. *KAN: Kolmogorov-Arnold Networks*. arXiv:2404.19756 (2024).
- pykan: `github.com/KindXiaoming/pykan`.
- Planar dataset and MLP scaffolding adapted from the deeplearning.ai "Planar data
  classification with one hidden layer" assignment.
- California housing: Pace, R. K. and Barry, R. *Sparse Spatial Autoregressions*,
  Statistics and Probability Letters 33 (1997), 291-297.
