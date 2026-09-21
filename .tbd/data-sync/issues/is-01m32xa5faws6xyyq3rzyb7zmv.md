---
type: is
id: is-01m32xa5faws6xyyq3rzyb7zmv
title: Control phase quadrature and pseudodata regularization weight
kind: bug
status: open
priority: 1
version: 4
spec_path: reports/04-project-restart-audit.md
labels: []
dependencies:
  - type: blocks
    target: is-01m32xb521zavway5ercgbabc8
  - type: blocks
    target: is-01m32xb4ham2hynmrfn9bdn0ne
parent_id: is-01m32xa49096sft8k6t5vm55n5
created_at: 2026-09-21T21:17:51.465Z
updated_at: 2026-09-21T21:23:19.184Z
---
Compare naive and periodic weighted phase quadrature; account for imaginary Fourier coefficients and phase calibration; normalize data loss so duplicated or denser pseudodata do not change effective gamma. Acceptance: uniform offset circle has zero nonzero-mode DC leakage; grid convergence, complex calibration and duplicated-row invariance checks pass.
