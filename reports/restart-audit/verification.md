# Verification Record

**Date:** 2026-09-21. **Audited source:** `5fc5a0524298b0f6904e5d8b461106d552356c85`. The report and its bounded probes were reviewed separately from the underlying historical experiments. No full training sweep or SDP reconstruction suite was rerun.

## Source and Artifact Checks

- Fetched the GitHub remote, confirmed default `main` and merged PR #1, and compared its tree with the clean original checkout. There were no tracked source differences between `9109d5d` and `5fc5a05`.
- Inventoried 164 tracked files (23,562,219 bytes), parsed all 23 notebooks / 511 cells, and inspected their source and saved text outputs. Parsed all 20 tracked Python files with `ast`.
- Checked ZIP/CRC integrity of 33 state and 33 cache artifacts without deserializing their pickle contents. Container integrity does not establish model provenance or numerical correctness.
- Inspected all four XLS headers and numeric count/range schemas. Compared duplicate local research assets by hash. The supplied documents and local-only prototypes are identified in the inventory.
- Read all thesis, poster and slide text. Rendered and inspected the poster, thesis proof page, and selected theorem/stress-test slides. Read the original Zhang article and supplement; visually checked the objective in the article's Methods page.
- Checked the report's local Markdown links, JSON syntax and new probe syntax, and inspected the Git diff. The detailed benchmark and tomography reviews include false-positive distinctions and confidence limits.
- Formatted the two diagnostic scripts with Black `24.10.0` and verified formatting; the formatter preserves their parsed behavior. No project dependency files were added for this one-off tool.

## Reproduced Bounded Numerical Evidence

The following checks ran once during specialist review and again from the isolated report checkout after adapting the benchmark script to accept a repository argument. The numerical results agreed. They are **diagnostic reproductions of defects and mathematical properties**, not assertions that the research implementation passes a corrected test suite.

| Check | Result | Meaning |
| --- | --- | --- |
| NumPy KAN mean-loss gradient, four samples | Finite-difference / implemented gradient = `3.9999998337513714` | Confirms the extra batch-size division |
| Spline derivative outside clipped domain | Reported `0.625`; finite difference `0` | Confirms missing clipping chain rule |
| Spline basis against SciPy and partition of unity | Maximum errors `2.22e-16` | The tested basis recurrence itself is consistent; do not blame it for the clipping defect |
| Grid update without coefficient transport | Maximum output jump `0.10763860006766168` | Grid replacement changes the represented function without training |
| Vendored spline MLP parameter counts | Formula `37`, actual trainable `31` | Formula includes an output activation absent from the model |
| Vendored KAN parameter counts | Formula `85`, requires-grad `112`, gradient-connected `76`, all stored `166` | Different counting conventions are not interchangeable |
| Different caller seeds | Identical KAN tensors | Constructor resets seeds, defeating nominal initialization replication |
| Feynman KAN anchor | `441` requires-grad versus `381` gradient-connected | Published local budget is not a matched active-parameter budget |
| MOESM4 first Fourier coefficient | Max imaginary component `0.06023925` with unweighted mean, `0.00375360` with periodic trapezoid | Confirms a quadrature problem on the actual irregular phases; does not independently attribute the entire final SDP error difference |
| Uniform phase grid plus constant offset | DC-to-band-1 leakage `1.82e-17` | Offset alone does not explain the nonzero leakage |
| MOESM4 Fock cutoff `d=58` | Maximum Poisson tail `0.002038774756583651` | Truncation must be assessed at the reported prediction precision |
| Reduced MOESM4 kernels | Numerical ranks `32–34` for `54–58` columns; condition estimates around `1e19` | Severe numerical ill-conditioning; exact tiny singular values are precision-sensitive |
| Normalized fidelity of `0.2 I` and `0.8 I` | `1.0`, with click-probability difference `0.6` | The normalized metric discards effect scale |
| Valid matrix with an omitted off-band element | Full-minus-band-limited prediction `0.0279547359` | PSD feasibility does not force unused entries to zero |
| Recreated stress-test split order | Some held-out levels lie outside training support; full fraction has zero held-out levels | Existing plots mix interpolation, extrapolation and an in-sample endpoint |

Exact outputs: [benchmark results](probes/benchmark-results.txt) and [tomography results](probes/tomography-results.txt). Floating-point last digits and singular-value estimates may vary by BLAS, platform and package versions. The parameter “active” diagnostic means parameters with a connected gradient in the probed numerical forward path, not a universal count of statistical degrees of freedom.

## Repeating the Probes

From the repository root, in an environment that provides the listed dependencies:

```bash
python reports/restart-audit/probes/benchmark_probes.py .
python reports/restart-audit/probes/tomography_probes.py .
```

The benchmark script requires NumPy, SciPy, PyTorch, matplotlib and installed pykan, and imports the reviewed vendored models as well. It extracts **only function/class definitions** from selected notebook cells and performs bounded forward/backward calculations; it never executes full notebook cells, trains models, fetches data or loads checkpoints. The tomography script requires NumPy, SciPy and xlrd; it reads the four local spreadsheets and evaluates kernels and small counterexamples. Neither script is a clean-environment installer or a comprehensive test harness. Review imports before rerunning against a changed or untrusted source tree.

Two existing environments were used, without installing packages or modifying their dependencies:

| Probe | Environment observed |
| --- | --- |
| Benchmark | Python `3.12.13`, NumPy `2.0.2`, Torch `2.12.0`, pykan `0.2.8`; existing `papers/Quantum Paper/.venv` |
| Tomography | Python `3.12.13`, NumPy `2.4.6`, SciPy `1.17.1`, xlrd `2.0.2`; existing `KAN_assisted tomography/.venv` |

In the audit session these were selected with `uv run --no-project --python <existing-environment-python> ...`, with bytecode writes disabled and caches redirected to temporary directories. The `uv` warning that no project was found is consistent with the missing project manifest. These versions document the checks performed **now**; they do not establish which versions produced historical notebook outputs.

## Checks Not Performed

- No full notebook run, broad hyperparameter sweep, model retraining, full SDP re-solve, original-paper benchmark replication or end-to-end timing comparison.
- No checkpoint deserialization, model-state lineage recovery or execution of the local prototype's install commands.
- No independent online hash verification of publisher supplementary XLS files; filenames and metadata were checked against publisher links, and local data were inspected.
- No claim that every plotted number is reproducible from its current cell source. Edited/commented cells and stale execution histories prevent that attribution in several cases.
- No systematic literature review proving first publication priority. The search is dated and scoped; abstracts and preprints are labeled where used.
- No validation of a fresh pinned project environment. That is the first restart engineering task.

## PR and Tracking Checks

The PR adds the report, evidence manifests/probes, report navigation, a corrected detector-tomography description, and tbd integration. Existing experiment notebooks, data and models are unchanged. GitHub check availability is inspected after publishing; no pre-existing CI workflow exists, so absence of checks must be reported as **no CI configured**, not a passing scientific test suite.

The audit work is tracked under `kan-1btb`. Future implementation is tracked under `kan-lwtk` with prerequisite dependencies and acceptance criteria. Task state is synchronized separately on `tbd-sync`; the report contains the reviewable task-ID map. Original research results remain provisional until those tasks are completed.
