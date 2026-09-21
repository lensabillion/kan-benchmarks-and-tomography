---
type: is
id: is-01m32xa54nkscje5nk36mzcdsf
title: Extract a tested tomography data loader and common forward operator
kind: task
status: open
priority: 1
version: 3
spec_path: reports/04-project-restart-audit.md
labels: []
dependencies:
  - type: blocks
    target: is-01m32xa59yh4f8b79w6kew0q26
parent_id: is-01m32xa49096sft8k6t5vm55n5
created_at: 2026-09-21T21:17:51.124Z
updated_at: 2026-09-21T21:23:18.659Z
---
Parse MOESM3-6 headers, counts, phases and calibration explicitly; make a single Born operator for fitting and scoring, with a consistent band restriction and controlled Fock tail. Acceptance: synthetic complex POVM probabilities, phase periodicity, count validation, band/full equivalence where intended, and dimension convergence checks pass.
