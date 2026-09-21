# Local extra assets outside the repository

## Unique sibling notebooks

### `papers/Quantum Paper/try_construct_SDP.ipynb`

- 170,631 bytes; SHA-256 `76845bb9e23effe8620b36712af4200721fa8e891eaec3a345c12c0159fd8418`.
- 34 cells using a Python 3.12.13 virtual-environment kernel. Its execution counts run 1–21, then jump to 46–48 and 55–56, followed by an output-bearing cell with no execution count and finally count 27. The stored state is therefore not a clean top-to-bottom run.
- No stored exception objects. Saved streams contain 30 `RuntimeWarning`s (principally divide-by-zero, overflow, and invalid-value warnings around matrix multiplication) and 5 `UserWarning`s. Cell 1 contains `!pip install` commands, but this audit did not execute them.
- Full cell source and saved text outputs were inspected locally. The original notebook is outside the Git repository and is identified by its hash above.

Substantive content:

1. It loads the MOESM4 click-count spreadsheet, phase-averages 3,720 observations into 93 brightness levels, builds a 93×70 Poisson forward matrix, and solves a bounded, smooth diagonal inverse problem with CLARABEL. Its stored forward RMS is 0.0051.
2. It generates 500 synthetic monotone detector diagonals, trains both an MLP and a KAN to invert click curves into diagonal entries, and applies the KAN to the real curve. The stored KAN-to-SDP diagonal RMS is 0.0067. This is supervised emulation of synthetic labels and an SDP reconstruction, not a physics-constrained direct reconstruction.
3. It fits a tiny 1→1→1 KAN to the reconstructed diagonal and extracts the symbolic expression `1.1979*sqrt(56.7265*tanh(7.6942*x_1 + 1.3299) - 27.3451) - 5.4969`. After clipping to `[0,1]`, the stored click-curve RMS is 0.0049 versus 0.0051 for the regularized SDP diagonal, and grid-to-grid RMS is 0.0023. The comparison reuses the same full curve used to construct the target and is not a held-out validation.
4. It derives the first off-diagonal stripe from phase-weighted measurements and a Sylvester elementwise bound, then trains a KAN on 500 synthetic diagonal/first-stripe pairs. On real input, stored RMS against its SDP proxy is 0.0133 for the diagonal and 0.0571 for the first off-diagonal. The latter error is close to the reported mean absolute stripe magnitude of 0.062, showing weak off-diagonal recovery.

Relation to repository evidence:

- The notebook adds a distinct exploratory route: learning an inverse map from synthetic click curves to diagonal/first-stripe entries and symbolically compressing the diagonal response. Those exact experiments and stored figures are absent from the tracked notebooks.
- It does not add strong support for the thesis's final KAN→SDP result. It reconstructs only the diagonal and first off-diagonal, uses an elementwise stripe bound rather than enforcing positivity of a complete POVM, trains on a narrow hand-generated detector family, and evaluates real data against an SDP-derived proxy. Its off-diagonal result is poor, execution order is stale, and stored numerical warnings are pervasive.
- The tracked `KAN_alone_vs_SDP.ipynb` and bridge/stress-test notebooks supersede the physical-validity question by constructing more of the POVM, checking eigenvalue bounds, comparing raw SDP/KAN→SDP/direct inversion, and testing sparse-data behavior. This sibling notebook is useful as provenance for an abandoned inverse-learning/symbolic-formula direction and as negative evidence about off-diagonal generalization.

### `kan-symbolic-regression/notebooks/de_broglie.ipynb`

- 2,130 bytes; SHA-256 `b3dc19005696c53cf4b09018e14198611c59775134e6df167d0f4fa83b9a4cfc`.
- Three code cells; only the first has content. It imports NumPy, Torch, matplotlib, and `KAN`, then stops with stored `ModuleNotFoundError: No module named 'kan'` at cell 1 (execution count 4).
- It contains no data, target function, model, training, formula extraction, plots, or results. It contributes no scientific evidence beyond documenting an environment-setup failure.

## Top-level local paper library

There are six PDF files directly under `/Users/lensa/Term_3/Research/papers`. Titles were read from first-page text because five of the six have empty PDF title metadata.

| File | Title/version visible in PDF | Pages | Bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| `KANvsMLPFairComparision.pdf` | *KAN or MLP: A Fairer Comparison*, arXiv:2407.16674v2 (17 Aug 2024) | 12 | 601,848 | `e220f76936958bf1183d77eb77e5fe13e923676ae62dc453e8afaa2157975f8e` |
| `KANvsMLPonIrregularFunctions.pdf` | *KAN versus MLP on Irregular or Noisy Functions*, arXiv:2408.07906v1 (15 Aug 2024) | 14 | 3,118,745 | `9f15bf40ed46f5596062442149910680ee89c9bdab5224c34c0552668e84ef40` |
| `Liu_KANs copy.pdf` | *KAN: Kolmogorov–Arnold Networks*, ICLR 2025 / arXiv:2404.19756v5 (9 Feb 2025) | 50 | 12,845,340 | `b2697de0f8d58d7139f434a8c1e87a3284539af85bd0b663f9c2d150c73cc98c` |
| `Liu_KANs.pdf` | *KAN: Kolmogorov–Arnold Networks*, ICLR 2025 / arXiv:2404.19756v5 (9 Feb 2025) | 50 | 12,822,114 | `c04339e34ac3f4a8695a74c59e2a0a4f332cfdcb3831a12696d5192cec2ed713` |
| `comprehensivesurvey on KAN.pdf` | *A Comprehensive Survey on Kolmogorov Arnold Networks (KAN)*, arXiv:2407.11075v7 (28 Jan 2025) | 17 | 241,865 | `ecbbf27157a62b879609984a4d59c6691d32e74fa2cb4d28cb7a003ea1f6a01a` |
| `surveyonKAN_2.pdf` | *A Survey on Kolmogorov-Arnold Network*, arXiv:2411.06078v1 (9 Nov 2024) | 35 | 1,353,937 | `d73713b5ac6691d4637dbeb54a5cfab7ecf60ed9bc6d1c7617bed18268fc2bca` |

The two Liu PDFs are byte-distinct, but pypdf extracts exactly the same 134,152-character text from both (identical text SHA-256 `a5346a3366bf29bc9c458189858659f67edc5afeaad91539ca883bc9f135ecae`). They should be treated as duplicate copies of the same paper/version unless visual or embedded-object differences matter.
