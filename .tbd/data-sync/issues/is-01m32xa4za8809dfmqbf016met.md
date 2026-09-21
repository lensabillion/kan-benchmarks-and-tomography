---
type: is
id: is-01m32xa4za8809dfmqbf016met
title: Unify benchmark model definitions, splits, budgets and selection
kind: task
status: open
priority: 1
version: 5
spec_path: reports/04-project-restart-audit.md
labels: []
dependencies:
  - type: blocks
    target: is-01m32xb4bn1y56sq47mysy3tsb
  - type: blocks
    target: is-01m32xb4wfe7xvk8e65wwe5jk6
parent_id: is-01m32xa49096sft8k6t5vm55n5
created_at: 2026-09-21T21:17:50.953Z
updated_at: 2026-09-21T21:24:25.010Z
---
Separate train/validation/test, use shared seed/split manifests and preprocessing fit only to training data; select on validation, count active trainable versus stored parameters, equalize optimizer data/work/search budgets, include MLP in LBFGS sweeps. Acceptance: fresh run artifacts identify final models and units; no test-driven early stopping or lower-envelope selection; paired multi-seed estimates and explicit equivalence margins.

## Notes

Explicit acceptance additions from audit review: coefficient transport must preserve represented functions on grid updates; constructor must forward independent seeds; validate actual trainable/active parameter counts and RMSE aggregation. Fix current Heating/Cooling x/X NameError and train-only preprocessing in reused loaders.
