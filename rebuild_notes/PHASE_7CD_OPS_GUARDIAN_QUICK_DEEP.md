# Phase 7C-D: Ops Guardian Quick/Deep Split

Changed:
- `hermes_ops_healthcheck` now supports `--quick`, `--deep`, and `--help`.
- Default mode is quick.
- Startup wrapper now runs `hermes_ops_healthcheck --quick`.
- Deep mode keeps reminder regression tests and heavier diagnostics.
- BOOT.md and Hermes Ops Guardian skill updated.

Quick mode is startup-safe and avoids reminder regression tests, real Telegram tests, and artifact generation.
Deep mode is for manual diagnostics and includes reminder create/delivery regressions.

No default model changed. No Gmail/YouTube/private_data changes.
