---
type: is
id: is-01m32xa4mj10yn7033mpvynb66
title: Freeze source provenance and make a clean environment reproducible
kind: task
status: open
priority: 1
version: 4
spec_path: reports/04-project-restart-audit.md
labels: []
dependencies:
  - type: blocks
    target: is-01m32xa4sz783mpm2yp6rrvgb3
  - type: blocks
    target: is-01m32xa54nkscje5nk36mzcdsf
parent_id: is-01m32xa49096sft8k6t5vm55n5
created_at: 2026-09-21T21:17:50.610Z
updated_at: 2026-09-21T21:23:18.325Z
---
Inventory tracked and local assets; record KANbeFair upstream commit and local modifications, third-party attribution and data provenance; choose supported Python and pin tested direct/transitive dependencies; isolate installed pykan from vendored kan. Acceptance: clean checkout imports and bounded smoke command succeed without absolute paths or personal venvs; manifest includes code/data/version identity.
