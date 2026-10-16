# Local verification — 2026-10-16

Command: `python -m unittest discover -s tests -v`

Result: 29 tests passed. Full captured stdout/stderr: [results/unittest-20261016.txt](results/unittest-20261016.txt). Also ran `python -m py_compile scripts/triage.py tests/test_triage.py` successfully.

Coverage: all eight signal families; explicit excluded/unknown intent; stale/future observations; default/unassigned owners; missing values versus observed emptiness; invalid input types; duplicate URL rejection; business-sensitive ordering and score; deterministic, nonmutating output; CLI failure contract; required finding fields; exact Git blob and SHA-256 matching of the pinned upstream source and license.

This is local decision/contract verification, not a live SEO audit, independent human review, production integration test, performance benchmark, or evidence of ranking/revenue improvement. No external service or customer dataset was used. The agent-executed fictional case has its own raw commands, artifact checks and review under cases/fictional-harbor/.

Limits not automatically tested: source truth; authoritative page intent; suitability of a real platform fix; implemented changes; target-site rendering; complete graph coverage; queue interpretation by other agents. The human handoff explicitly strengthens the investigation gate where partial-crawl depth and inlink signals overlap.

## v0.3 intake execution, 2026-10-16
44 unittest tests pass; log: results/unittest-intake-v03-20261016.txt. Four fictional context variants executed by cases/fictional-context-intake/run_case.py; outputs and verification preserved there. Tests cover fallback value, assumptions, conversion branches, intent protection, missing effort, stale context and narrow root URL equivalence. Historic v0.2 results remain historical and are not overwritten. Tests establish bounded code behavior, not client/SEO effectiveness.


## v0.5 actionable handoff verification (2026-10-16)
119 unit/regression tests pass, including 24 independently authored truthfulness tests. Synthetic end-to-end evidence, failed initial probes, reviewed decisions and expected/actual matrix are preserved in [cases/actionable-handoff](../cases/actionable-handoff/). These are fictional inputs, not client data. Tests cover unsupported confirmations, evidence/date conflicts, intentional exclusions, missing data and concrete action fields.

A separate private real-site sample was used only to test the workflow; no real audit input or raw page content is shipped here. The validation preserved prior source bytes and distinguished raw generated reports from analyst commentary. No new network-success claim follows from these offline tests. Collector/triage behavior remains separately scoped; human or agent review assertions are not automatically authenticated. Tests do not establish ranking, traffic, revenue, full SEO coverage or a security certification.

## Local SEO evidence extension — 2026-10-16
180 final tests passed, including 28 independent local truth checks. Skill format validation passed. Actual offline exporter/importer → six-dimension report examples cover low rating, explicit zero and missing aggregate; missing remains unknown. See cases/local-evidence/INDEPENDENT-REVIEW.md and final-* outputs. No live GBP/Places account or paid API was exercised. Existing bounded collector and prior test evidence remain preserved.

## Google Maps and business applicability — 2026-10-16

Full regression: **228 tests passed** (`results/maps-applicability-final-20261016.txt`); independent Maps truth review: **30 tests passed**. Skill metadata validation passed. Four real offline CLI runs and the reviewer’s findings are preserved in [cases/google-maps/REVIEW.md](../cases/google-maps/REVIEW.md). They verify portfolio local/ecommerce N/A, a clinic’s optional map-navigation suggestion, contact-map suppression of per-blog suggestions, and wrong-branch verification without a fabricated confirmed defect. These fictional fixtures establish bounded behavior, not live Maps/API/rendering or ranking outcomes.
