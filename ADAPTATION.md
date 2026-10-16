# Adaptation map: upstream → this workflow

Source: Snippet-Digital-Agency/tech-seo-audit-skill, commit `8b5b5d5c776ec71a0d427bd6760dfeca058b404c`; `SKILL.md` and `LICENCE` are preserved unmodified under `upstream/snippet-digital/`. MIT, Copyright (c) 2026 Snippet Digital. This is an adapted workflow, not an original invention of technical SEO auditing. No upstream scripts or reference documents were copied or executed.

| Actual upstream section | Treatment here | Concrete artifact / reason |
|---|---|---|
| Phase 1, Path A: supplied crawl ingestion and normalization | Retained, narrowed to explicit JSON mapping | INPUT-CONTRACT.md and source/row locators; rejects ambiguity instead of assuming tool-column inference |
| Phase 1, Paths B/C: live APIs / multi-source merging | Removed in v0.2 supplied-data mode; distinct local public collector added in v0.4 | No upstream API integration, credentials or paid calls; the new bounded HTTP collector is locally authored |
| Phase 2: business model and revenue/lead-page context | Adapted into mandatory objective and per-page importance/intent | scripts/triage.py validation and gates; no inferred revenue data |
| Phase 3, Categories 1/2/3/4: status, redirects, indexability, canonical, titles, depth, inlinks | Eight limited evidence checks | RULES registry and triage function; zero-inlink and canonical differences always need corroboration |
| Phase 3, Categories 5–10 and other detailed checks | Omitted from v0.2 triage; selected new checks added separately in v0.4 | Six-dimension evidence report adds bounded observations and supplied-data comparisons, not a full audit or health score |
| Phase 4: 40% SEO impact + 40% business impact + 20% inverse effort | Formula retained; local scale calibration and action gates added | score_inputs makes estimates visible; freshness/intent/uncertainty override score priority |
| Phase 4: platform-specific fix instructions | Replaced by approval-dependent investigation steps | No platform is established from these limited observations; owner verifies actual configuration |
| Phase 5: Markdown report and XLSX, health scores | Replaced with JSON queue and reviewed human handoff | No unjustified full-site health denominator; reproducible artifact and review trace instead |
| Important Principles: specific evidence, business meaning, honest severity | Operationalized | Every finding includes locator, owner, rationale, verification, confidence and proposed status |

New local work: strict validated contract; provenance and missing-signal reporting; intentional-exclusion suppression; age/unknown-intent/manual-corroboration gates; deterministic sortable repair queue; owner roles and acceptance checks; fictional end-to-end case with actual execution and review; regression and source-integrity tests; bilingual practical documentation. Formula lineage is disclosed, not claimed as novel.

The shipped source snapshot is a reference document, not an instruction to install/run its broader workflow. Its linked dependencies are not vendored and not needed to run this adaptation. Snapshot contents may include upstream claims beyond this repository's verified scope; retaining the exact source does not endorse them.

## v0.3 local extension
Adaptive intake, source/status-bearing answers, report-level fallback, explicit separation of technical severity/business urgency, gated scores and root-path canonical equivalence are new local contributions. The upstream 40/40/20 formula is retained only for fully supported provisional rankings; upstream text/license are unchanged. No upstream claim of these new capabilities is made.

## v0.4 local extension: public sample and six-dimension review
The new `collect_public_site.py` and `six_dimension_report.py` are locally authored implementations. They are not copied upstream crawler code. The URL-first route extends the adapted evidence → business context → review → handoff sequence with safe public HTTP collection, six overlapping report dimensions, applicability/coverage separation, optional attributed evidence, root-cause deduplication and explicit pending semantic review. The existing supplied-data `triage.py`, old cases and upstream bytes remain unchanged.

The six-dimension framework is this project's organization, not a Google taxonomy or an upstream promise. Current official documentation informs factual boundaries (including FAQ rich-result removal); links are in docs/SIX-DIMENSION-METHOD.md. No Google documentation text is vendored. Security tests and fictional executions demonstrate bounded behavior, not a security certification or SEO results.

## v0.5 local extension: actionable final handoff
Locally authored four-bucket handoff and reviewed-decision validation extend the upstream principle of specific evidence, business meaning and practical reporting. Rule-specific action/verification guidance is informed by the existing adapted eight-rule triage; the six-dimension reporter does not copy the old numeric score or pretend every observation is a defect. Explicit review provenance, missing-evidence investigation tasks and synthetic false-positive/actionability tests are added. Earlier outputs remain preserved; upstream bytes/license are unchanged.

## 2026-10-16 — Local SEO evidence extension
Original local evidence validation/import and report integration add branch/date/source guards, conservative NAP normalization, scoped LocalBusiness checks and ethical review-rating/count warnings. Official Google guidance informs interpretation; no Google code or new upstream code copied. Pinned upstream notices are unchanged. Thresholds are project heuristics, not ranking requirements. Live GBP/Places access and writes are not implemented or implied.

## Maps and purpose-based applicability
Original bounded HTML signal parser and reporter integration now distinguish Maps embeds, JavaScript signals and links, without resolving shortlinks or using API credentials. Purpose/service/transaction answers feed applicability; independent domain form does not. These are local adaptation contributions with unchanged upstream attribution. No map-presence ranking claim is made.
