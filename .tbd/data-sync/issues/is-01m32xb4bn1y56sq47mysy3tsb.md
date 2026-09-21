---
type: is
id: is-01m32xb4bn1y56sq47mysy3tsb
title: Run synthetic truth and matched smoother tomography ablations
kind: task
status: open
priority: 2
version: 3
labels: []
dependencies:
  - type: blocks
    target: is-01m32xb4pv50nz6kxevzm1e9p6
  - type: blocks
    target: is-01m32xb4wfe7xvk8e65wwe5jk6
parent_id: is-01m32xa49096sft8k6t5vm55n5
created_at: 2026-09-21T21:18:23.093Z
updated_at: 2026-09-21T21:23:19.737Z
---
After baseline repairs, compare raw joint/recursive reconstruction, periodic spline or Fourier smoother, MLP, spline MLP and KAN using the same locked splits and objective scaling. Vary retained levels, shot noise and phase gaps separately, then jointly; separate interpolation from extrapolation. Acceptance: physical ground-truth POVMs for synthetic data, paired seeds, uncertainty, failure rate and total compute; full-data real-data estimates labeled references, not truth.
