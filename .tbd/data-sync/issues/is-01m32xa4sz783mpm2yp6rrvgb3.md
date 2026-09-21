---
type: is
id: is-01m32xa4sz783mpm2yp6rrvgb3
title: Fix NumPy KAN gradient normalization and clipped derivatives
kind: bug
status: open
priority: 1
version: 4
spec_path: reports/04-project-restart-audit.md
labels: []
dependencies:
  - type: blocks
    target: is-01m32xa4za8809dfmqbf016met
  - type: blocks
    target: is-01m32xb521zavway5ercgbabc8
parent_id: is-01m32xa49096sft8k6t5vm55n5
created_at: 2026-09-21T21:17:50.783Z
updated_at: 2026-09-21T21:23:18.983Z
---
Evidence: both planar classification implementations divide by batch size twice; clipped forwards have unmasked derivatives. Acceptance: finite-difference or autodiff checks for inputs and parameters, in-domain and clipped inputs; duplicating a batch leaves mean-loss gradients unchanged; rerun paired classifier comparison after correction.
