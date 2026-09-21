# KAN Research

Experiments exploring **Kolmogorov–Arnold Networks (KANs)** — comparing them against
conventional neural architectures and applying them to a real physics problem
(quantum detector tomography).

## Restart audit

The [September 2026 restart audit](reports/04-project-restart-audit.md) examines the
code, saved results, thesis, poster, slides, and prior literature. It identifies
mathematical, implementation, and evaluation defects and provides a tracked repair
plan. Treat the existing notebook results as exploratory until the corresponding
validation steps pass. The report links to detailed evidence and bounded probes.

Task tracking uses [tbd](https://github.com/jlevy/tbd), with the `kan` prefix.
The report audit is `kan-1btb`; the implementation restart is `kan-lwtk`.
Issue state lives on the separate `tbd-sync` branch. See [AGENTS.md](AGENTS.md)
for the research workflow and numerical validation requirements.

The work is organized into three self-contained sub-projects, each a collection of
Jupyter notebooks.

## Contents

### 1. `KAN vs BSpline_MLP/`
Compares KANs against **B-spline-augmented MLPs** to isolate how much of a KAN's
performance comes from its learnable spline activations versus its architecture.

- `Example_1_function_fitting*.ipynb` — 1D/2D function-fitting benchmarks
- `Example_3_deep_formula*.ipynb` — deeper compositional formulas
- `Feyman_dataset_fitting_KAN_and_Bspline_MLP.ipynb` — fits on the Feynman equations dataset
- `symbolic_formula_representation_MLP_Spline.ipynb` — symbolic regression / formula recovery
- `KANbeFair/` — the [KANbeFair](https://github.com/yu-rp/KANbeFair) benchmark suite used for fair comparisons
- `model/` — saved KAN checkpoints/configs

### 2. `KAN vs MLP/`
Head-to-head comparisons of KANs against standard **MLPs / neural networks** on a
mix of regression and classification tasks.

- `Example_1_function_fitting.ipynb` — function fitting
- `KAN_vs_NN_Planar_Classification (1).ipynb` — 2D planar classification
- `MLP_vs_KAN_Research_Demo.ipynb` — general comparison demo
- `KAN_housing_prediction.ipynb` / `NN_housing_prediction.ipynb` — housing price regression
- `NN__Heating_Cooling_Prediction.ipynb` — energy efficiency prediction

### 3. `KAN_assisted tomography/`
Applies KANs to **quantum detector tomography**, using a KAN as a proposed smoothing front-end
that feeds an SDP (semidefinite programming) reconstruction step.

- `KAN_to_SDP_bridge*.ipynb` — the KAN → SDP pipeline (denoise raw data, then reconstruct)
- `KAN_alone_vs_SDP.ipynb` — KAN-only vs SDP-only baselines
- `KAN_assisted_tomography_MOESM*.ipynb` — experiments on published photonics datasets
- `data/` — source measurement data (`.xls`)
- `model/` — saved KAN checkpoints/configs

## Getting started

Each sub-project uses its own Python virtual environment (not tracked in git).
To set one up:

```bash
cd "<sub-project folder>"
python3 -m venv .venv
source .venv/bin/activate
pip install pykan torch numpy scipy matplotlib jupyter
```

Additional per-project dependencies (e.g. `cvxpy` for the SDP tomography work) are
installed as needed from the notebooks.

Then launch Jupyter and open any notebook:

```bash
jupyter lab
```

## Notes

- Virtual environments (`.venv/`), notebook checkpoints, and OS/editor artifacts are
  excluded via `.gitignore`.
- `KANbeFair/` is vendored from an external benchmark repository for reproducibility.
