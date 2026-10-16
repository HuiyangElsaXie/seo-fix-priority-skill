# Frozen v0.2 implementation

Saved before v0.3 intake changes. Original Harbor inputs, executed outputs and review remain in ../../cases/fictional-harbor. From the current repository root, run:

python legacy/v0.2/scripts/triage.py cases/fictional-harbor/input.v1.json

Verified 2026-10-16: parsed output exactly equals the historical output.v2.json, which contains the v0.2 clarification of confidence semantics. It intentionally differs from the earlier output.v1.json. Neither historical output was overwritten. Archived tests are source snapshots, not the current v0.3 test entry point; use root tests for current behavior and source-integrity checks.
