# Repository and Local Asset Inventory

## Scope and provenance

- Review base: commit `5fc5a0524298b0f6904e5d8b461106d552356c85` (`origin/main`, merge of PR #1). The original checkout is on `9109d5dac7576afc2920a1395de7933e7beced48`, the merged report-branch parent; `git diff 5fc5a05..9109d5d` is empty, so the source trees are identical.
- Remote: `https://github.com/lensabillion/kan-benchmarks-and-tomography.git`.
- The original checkout has 164 tracked files, 23,562,219 bytes total, and no non-ignored untracked files. The complete size/path enumeration is [`tracked-files.txt`](tracked-files.txt); machine-readable sizes and categories are in [`inventory.json`](inventory.json).
- Ignored local state comprises `.DS_Store`, two virtual environments, and three `__pycache__` directories. Git reports 94,560 ignored paths because the environments are materialized. Their installed packages are local evidence, not a reproducible dependency declaration.
- The report and audit scaffolding (`AGENTS.md`, `.agents/`, `.tbd/`) are excluded from the baseline inventory; they were added during this audit.

## Tracked content coverage

| Category | Count | Bytes | Coverage |
| --- | ---: | ---: | --- |
| Jupyter notebooks | 23 | 10,871,354 | All parsed and extracted cell-by-cell |
| Python source | 20 | 204,723 | All are under vendored `KANbeFair/src`; all AST-parse |
| Legacy `.xls` datasets | 4 | 5,373,952 | All four have OLE Compound Document magic; not recalculated |
| Model state artifacts | 33 | 1,787,713 | Container integrity only; never deserialized |
| Model cache artifacts | 33 | 285,939 | Container integrity only; never deserialized |
| Model YAML configs | 33 | 17,256 | Counted as checkpoint metadata |
| PNG images | 3 | 1,071,529 | Two vendored paper figures plus one tomography plot |
| Vendored PDFs | 2 | 59,595 | KANbeFair FLOP/parameter plots |
| CSV | 1 | 3,467,911 | `KANbeFair/results/results.csv` |
| PyTorch dataset split | 1 | 369,728 | `KANbeFair/dataset/uciml_split_idx.pt`; not loaded |
| Markdown | 6 | 51,399 | Root README, four reports, KANbeFair README |

The repository contains no root `pyproject.toml`, requirements file, lockfile, setup file, or Makefile. Its only dependency manifest is `KAN vs BSpline_MLP/KANbeFair/environment.yml`, which requests Python 3.9.7 and pins matplotlib 3.6.2, NumPy 1.24.4, scikit-learn 1.1.3, setuptools 65.5.0, SymPy 1.11.1, Torch 2.2.2, torchvision 0.17.2, tqdm 4.66.2, pandas 2.2.2, ucimlrepo 0.0.7, torchaudio 2.2.2, torchtext 0.17.2, and torchdata 0.7.1; `fvcore` is unpinned.

## Notebook extraction

[`notebook-index.json`](notebook-index.json) inventories all 23 notebooks and 511 cells. The committed compact index records SHA-256, byte size, kernel metadata, cell counts, imports, execution counts, saved exceptions, source absolute paths and execution-order indicators. Exception cell ordinals in this inventory are one-based; the technical appendices explicitly use zero-based JSON indices. Full per-cell extracts were reviewed locally. This PR retains a compact notebook index and links to the original committed notebooks below, avoiding duplication of every saved output.

Saved outputs contain three exceptions:

- `KAN vs BSpline_MLP/symbolic_formula_representation_MLP_Spline.ipynb`, cell 39: `KeyboardInterrupt`.
- `KAN vs MLP /NN__Heating_Cooling_Prediction.ipynb`, cell 4: `NameError: name 'fetch_ucirepo' is not defined`.
- The same notebook, cell 8: `NameError: name 'y_train' is not defined`.

Five notebooks have non-monotonic saved execution counts: the two KANbeFair notebooks, `NN__Heating_Cooling_Prediction.ipynb`, `NN_housing_prediction.ipynb`, and `KAN_assisted_tomography_MOESM3.ipynb`. One source cell hard-codes `/Users/lensa/Term_3/Research/papers/Quantum Paper/KAN_assisted tomography/data`. The vendored `train.py` and `train_continual_learning.py` each call `os.chdir('/home/yurunpeng/Repos/KANBeFair/src')`. Saved outputs in nine notebooks retain `/Users/...` or `/var/folders/...` traceback paths; these are separately indexed and should not be confused with executable source paths.

Saved warnings are extensive: the planar-classification notebook retains 30 `RuntimeWarning`s, 5 `DeprecationWarning`s, and 2 `FutureWarning`s; tomography notebooks retain repeated divide-by-zero, overflow, invalid-matmul, CVXPY expression-size, and complex-casting warnings. These outputs are historical evidence and were not reproduced in this audit.

Static imports span Torch, KAN/pykan, NumPy, pandas, SciPy, scikit-learn, matplotlib, seaborn, SymPy, TensorFlow/Keras, CVXPY, xlrd, ucimlrepo, torchvision, torchaudio, torchtext, torchdata-adjacent code, tqdm, and fvcore. The tracked manifest does not declare the notebook-wide environment.

## Local environments

| Environment | Disk | Python | Selected installed packages | Provenance issue |
| --- | ---: | --- | --- | --- |
| `KAN vs BSpline_MLP/.venv` | 1.1 GB | 3.14.4 | Torch 2.12.0, pykan 0.2.8, NumPy 2.4.6, pandas 3.0.3, scikit-learn 1.8.0 | `pyvenv.cfg` says it was created at removed `KAN/Example Notebooks/.venv` |
| `KAN_assisted tomography/.venv` | 1.2 GB | 3.12.13 | Torch 2.12.0, pykan 0.2.8, CVXPY 1.9.1, xlrd 2.0.2, NumPy 2.4.6 | `pyvenv.cfg` points to sibling `papers/Quantum Paper/...` path |
| `papers/Quantum Paper/.venv` | 1.5 GB | 3.12.13 | Torch 2.12.0, pykan 0.2.8, CVXPY 1.9.1, pandas 2.2.2, transformers 5.9.0 | Broad research environment; untracked and unpinned |
| `papers/Quantum Paper/KAN_assisted tomography/.venv` | 1.2 GB | 3.12.13 | Same tomography core as repository environment | Duplicate environment tree |
| `kan-symbolic-regression/venv` | 1.1 GB | 3.14.4 | Torch 2.11.0, pykan 0.2.8, NumPy 2.4.4 | `pyvenv.cfg` creation path is an iCloud location |

The full KAN checkout occupies 2.3 GB mainly because of its two ignored environments; tracked content is only 23.56 MB.

## Vendored KANbeFair provenance

`KAN vs BSpline_MLP/KANbeFair` is ordinary tracked content, not a Git submodule and not a nested checkout: it has no `.git` file/directory, no `.gitmodules` entry, and therefore no recoverable upstream commit or remote. All files first appear in local commit `d60ba3911a005c263a0200727a63eb17f0d2a928` (“Initial commit: KAN research notebooks and experiments,” 2026-07-02). Its README identifies the paper “KAN or MLP: A Fairer Comparison” (arXiv:2407.16674) and acknowledges `https://github.com/KindXiaoming/pykan/tree/master`; that acknowledgment is not provenance for this entire copied tree. A future reproducibility pass should identify and record the exact KANbeFair upstream repository and commit.

## Sibling research material

The requested sibling comparison excludes environments, caches, `.git`, and `.DS_Store` from content hashes.

`papers/Quantum Paper` has 42 files byte-identical to repository files. This includes all seven tomography notebooks, the plot, both copies of all four `.xls` inputs, and one complete six-checkpoint model directory. Its 15 relevant unique files are:

- `Zhang_etal_2012a.pdf` (2,101,446 bytes) and `Zhang_etal_2012a_SM.pdf` (384,086 bytes).
- `try_construct_SDP.ipynb` (170,631 bytes).
- A second `model/` lineage: six states, five nonempty cache snapshots plus the zero-step cache already duplicated elsewhere, and `history.txt`; details and hashes are in [`quantum_sibling.json`](quantum_sibling.json).

`kan-symbolic-regression` has no byte-identical project files. Its relevant unique files are `notebooks/de_broglie.ipynb` (2,130 bytes) and `requirements.txt` (56 bytes), whose unpinned dependencies are Torch, pykan, NumPy, matplotlib, scikit-learn, SymPy, and Jupyter. Hashes are in [`symbolic_sibling.json`](symbolic_sibling.json).

## Thesis, poster, and presentation

All supplied text was extracted and reviewed locally; the documents are identified below. See the [writing and theory audit](writing-and-theory.md) for findings. The complete extracts and source binaries are not added to this public PR:

| Source | Size | SHA-256 | Extent | Notes |
| --- | ---: | --- | ---: | --- |
| `Thesis_ KAN Theoretical aspects and applications.pdf` | 2,163,207 | `a2783e4ea2ab3dbdbb2f3e52bc85b72d7863b28a1433300c1da0d99eedfe6af5` | 30 pages | Text extracted per page |
| `Scientific Poster.pdf` | 919,601 | `ba92c4538d268a1018ec1dd40f7bc6c54f44347827a71671dc12a8bfc0ee7011` | 1 page | Text extracted |
| `presentation_V3.pptx` | 10,453,031 | `e154f8ab5dbd0b0123e89c0d3f48d6d58f9b8e489eade535c284bcd81c867607` | 24 slides | Full slide XML text; zero notes-slide XML parts |

## Checks completed and remaining limits

Completed low-cost checks: parsed every notebook as JSON; parsed all 20 Python files with `ast`; extracted every text output and stored error; validated all 66 model state/cache ZIP containers with CRC checks without pickle deserialization; checked all four spreadsheet file signatures; parsed both PDFs with pypdf; parsed all 24 presentation slide XML parts; compared sibling content by SHA-256; and confirmed the original checkout has no relevant untracked files.

The tomography audit subsequently checked spreadsheet schemas and numeric ranges. CSV/YAML semantic validation and full notebook execution remain future work. Report links and JSON/Python syntax are checked in this PR. Full numerical reproduction has not been attempted; its prerequisites include resolving the absence of a repository-wide pinned environment, Python/Torch version divergence, missing exact KANbeFair source provenance, hard-coded paths, computationally expensive training/SDP cells, and saved outputs that already show numerical warnings. The mechanical inventory did not execute notebooks, install dependencies or deserialize `.pt`, `_state`, or `_cache_data` objects. Other parts of the audit used online primary sources and bounded numerical probes in existing environments.

## Notebook Coverage at the Audited Commit

All notebooks were parsed; source code and saved text outputs were reviewed. Cell references in findings count both markdown and code.

| Notebook | Cells | Saved exceptions | Execution order |
| --- | ---: | ---: | --- |
| [KAN vs BSpline_MLP/Example_1_MLP_Version.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/Example_1_MLP_Version.ipynb) | 8 | 0 | Monotonic recorded counts |
| [KAN vs BSpline_MLP/Example_1_function_fitting.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/Example_1_function_fitting.ipynb) | 16 | 0 | Monotonic recorded counts |
| [KAN vs BSpline_MLP/Example_1_function_fitting_MLP + BSpline.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/Example_1_function_fitting_MLP%20%2B%20BSpline.ipynb) | 9 | 0 | Monotonic recorded counts |
| [KAN vs BSpline_MLP/Example_1_function_fitting_MLP_BSpline_1.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/Example_1_function_fitting_MLP_BSpline_1.ipynb) | 51 | 0 | Monotonic recorded counts |
| [KAN vs BSpline_MLP/Example_3_deep_formula.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/Example_3_deep_formula.ipynb) | 13 | 0 | Monotonic recorded counts |
| [KAN vs BSpline_MLP/Example_3_deep_formula_MLP + BSPline.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/Example_3_deep_formula_MLP%20%2B%20BSPline.ipynb) | 12 | 0 | Monotonic recorded counts |
| [KAN vs BSpline_MLP/Feyman_dataset_fitting_KAN_and_Bspline_MLP.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/Feyman_dataset_fitting_KAN_and_Bspline_MLP.ipynb) | 27 | 0 | Monotonic recorded counts |
| [KAN vs BSpline_MLP/KANbeFair/notebooks/lbfgs_exploration.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/KANbeFair/notebooks/lbfgs_exploration.ipynb) | 29 | 0 | Non-monotonic recorded counts |
| [KAN vs BSpline_MLP/KANbeFair/notebooks/plot.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/KANbeFair/notebooks/plot.ipynb) | 10 | 0 | Non-monotonic recorded counts |
| [KAN vs BSpline_MLP/symbolic_formula_representation_MLP_Spline.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20BSpline_MLP/symbolic_formula_representation_MLP_Spline.ipynb) | 42 | 1 | Monotonic recorded counts |
| [KAN vs MLP /Example_1_function_fitting.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20MLP%20/Example_1_function_fitting.ipynb) | 17 | 0 | Monotonic recorded counts |
| [KAN vs MLP /KAN_housing_prediction.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20MLP%20/KAN_housing_prediction.ipynb) | 10 | 0 | Monotonic recorded counts |
| [KAN vs MLP /KAN_vs_NN_Planar_Classification (1).ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20MLP%20/KAN_vs_NN_Planar_Classification%20%281%29.ipynb) | 28 | 0 | Monotonic recorded counts |
| [KAN vs MLP /MLP_vs_KAN_Research_Demo.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20MLP%20/MLP_vs_KAN_Research_Demo.ipynb) | 24 | 0 | Monotonic recorded counts |
| [KAN vs MLP /NN__Heating_Cooling_Prediction.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20MLP%20/NN__Heating_Cooling_Prediction.ipynb) | 12 | 2 | Non-monotonic recorded counts |
| [KAN vs MLP /NN_housing_prediction.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN%20vs%20MLP%20/NN_housing_prediction.ipynb) | 16 | 0 | Non-monotonic recorded counts |
| [KAN_assisted tomography/KAN_alone_vs_SDP.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_alone_vs_SDP.ipynb) | 28 | 0 | Monotonic recorded counts |
| [KAN_assisted tomography/KAN_assisted_tomography_MOESM3.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_assisted_tomography_MOESM3.ipynb) | 30 | 0 | Non-monotonic recorded counts |
| [KAN_assisted tomography/KAN_assisted_tomography_MOESM4.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_assisted_tomography_MOESM4.ipynb) | 37 | 0 | Monotonic recorded counts |
| [KAN_assisted tomography/KAN_assisted_tomography_MOESM4_SDP_joint and recursive.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_assisted_tomography_MOESM4_SDP_joint%20and%20recursive.ipynb) | 35 | 0 | Monotonic recorded counts |
| [KAN_assisted tomography/KAN_crossfile_testing.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_crossfile_testing.ipynb) | 17 | 0 | Monotonic recorded counts |
| [KAN_assisted tomography/KAN_to_SDP_bridge.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_to_SDP_bridge.ipynb) | 12 | 0 | Monotonic recorded counts |
| [KAN_assisted tomography/KAN_to_SDP_bridge_with_stresstest.ipynb](https://github.com/lensabillion/kan-benchmarks-and-tomography/blob/5fc5a0524298b0f6904e5d8b461106d552356c85/KAN_assisted%20tomography/KAN_to_SDP_bridge_with_stresstest.ipynb) | 28 | 0 | Monotonic recorded counts |

The [unique local prototype and paper-library review](local-extra-assets.md) describes the two additional notebooks and identifies all six top-level paper PDFs. These assets are outside the versioned repository.
