---
type: is
id: is-01m32xb521zavway5ercgbabc8
title: Add bounded numerical smoke checks and CI for the extracted package
kind: chore
status: open
priority: 2
version: 3
labels: []
dependencies:
  - type: blocks
    target: is-01m32xb4bn1y56sq47mysy3tsb
parent_id: is-01m32xa49096sft8k6t5vm55n5
created_at: 2026-09-21T21:18:23.809Z
updated_at: 2026-09-21T21:24:25.176Z
---
Add only failure-directed checks after core extraction: gradients, shapes, train-only transforms, import source, Born map consistency, quadrature, PSD, solver status and one tiny synthetic pipeline. Acceptance: clean-checkout CI fails on known defects and passes corrected paths; full sweeps remain explicit opt-in research jobs.

## Notes

Include regression checks for grid-function preservation, caller seed forwarding, true RMSE reduction and analytic versus active parameter accounting, in addition to gradients, Born map and split boundaries.
