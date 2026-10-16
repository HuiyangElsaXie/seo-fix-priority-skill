# Independent synthetic recommendation-truth outcome matrix

Final execution: 24 independent truth tests passed; full repository suite 119 tests passed. All inputs and reviewed assertions are synthetic. This measures the implemented bounded workflow, not live-site accuracy or SEO outcomes.

| Dimension / scenario | Expected | Actual | Source, date and locator |
|---|---|---|---|
| technical / JSONLD_SHAPE | confirmed_fix | confirmed_fix | snapshot / 2026-10-16T00:00:00Z / fictional-inline-fixture |
| onpage_content / EMPTY_TITLE | confirmed_fix | confirmed_fix | snapshot / 2026-10-16T00:00:00Z / fictional-inline-fixture |
| local / FIELD_MISMATCH_PHONE | confirmed_fix | confirmed_fix | Fictional manual export; no API connection / 2026-10-16 / local:Fictional business-profile snapshot |
| ecommerce / FIELD_MISMATCH_PRICE | confirmed_fix | confirmed_fix | Fictional manual export; no API connection / 2026-10-16 / products:Fictional supplied Offer extraction |
| international / HREFLANG_RETURN | confirmed_fix | confirmed_fix | snapshot / 2026-10-16T00:00:00Z / hreflang |
| onpage_content / EMPTY_META_DESCRIPTION | optional_improvement | optional_improvement | snapshot / 2026-10-16T00:00:00Z / fictional-inline-fixture |
| technical / NOINDEX_REVIEW | keep_or_not_applicable | keep_or_not_applicable | snapshot / 2026-10-16T00:00:00Z / fictional-inline-fixture |
| technical / CANONICAL_REVIEW | keep_or_not_applicable | keep_or_not_applicable | snapshot / 2026-10-16T00:00:00Z / fictional-inline-fixture |
| technical / HTTP_ERROR | keep_or_not_applicable | keep_or_not_applicable | snapshot / 2026-10-16T00:00:00Z / fictional-inline-fixture |
| offpage / OFFPAGE_SCOPED_SAMPLE | keep_or_not_applicable | keep_or_not_applicable | Fictional manual export; no API connection / 2026-10-16 / backlinks:data |

## Adversarial and exception outcomes

| Case | Expected | Actual |
|---|---|---|
| Invalid/future local or product observed_at | No supported mismatch | Skipped with unknown; pass |
| Future supplemental evidence date | No current defect support | No mismatch or CWV finding; pass |
| Review predating evidence, malformed or future review date | Reject confirmation | ValueError; pass |
| Missing / unrelated / other-entity review evidence | Reject confirmation | ValueError; pass |
| Fingerprint-bound review with edited same-date product value | Reject stale review | ValueError; pass |
| Noindex exclusion + claimed removal fix | Retain verification | Needs verification; original safe conditional steps retained |
| Price conflict without authoritative source | Do not choose value | Needs verification |
| Missing product variant / mismatched currency | Do not infer price defect | No price mismatch; investigation remains |
| Lab CWV / uncollected alternate target | Unknown, not field/reciprocity defect | No CWV or return-reference finding |
| Explicit local/ecommerce/international non-applicability | Keep scope reason | Only keep tasks; no findings in those dimensions |
| Offpage missing export | Missing evidence, not zero backlinks | Investigation; no invented fault |
| Section keep with unreviewed technical findings | Do not clear outstanding issues | Existing finding still needs verification; semantic review pending |

## Actionability inspection of the actual report

- Technical JSON-LD fix identifies the second malformed block, proposes a web-engineer/technical-SEO role, and requires successful parsing plus visible-content comparison. It does not promise rich-result eligibility.
- On-page fix has a descriptive approved title, editor role, and raw/rendered before-after acceptance. Optional description work is explicitly separate from defects and makes no ranking or click-rate promise.
- Local fix identifies branch and dated authoritative synthetic phone source; ecommerce identifies product, blue variant, CAD and the authoritative synthetic price. Each requires fresh paired evidence, not blindly copying the reference.
- International fix names the English/French reciprocal cluster, with target status/canonical checks. The supplied review explicitly addresses header/sitemap alternatives; without it, the HTML-only signal stays verification.
- Noindex, cross-page canonical and retired 404 are preserved under explicit supplied intentions. Offpage keep covers one supplied sample and retains liveness/completeness/reputation unknowns.
- All tasks carry concrete steps, proposed role, dependencies and acceptance. Finding-backed tasks link evidence source/date/scope/locator. Missing-evidence tasks explicitly request those materials instead of inventing them.
- The output remains industry_general with missing essential business context. Reviewed workflow states are qualitative and provisional; they are not ranked urgency, promised impact, estimated effort, named assignees or authorization to execute changes.

## Corrections and preserved evidence

1. run-00-original records the earlier generic acceptance/unassigned-owner output. run-00-truth-tests ran after the initial handoff implementation appeared: 11 of 12 tests passed, with two failing subcases for bad/future comparison dates.
2. run-02 passed 17 tests after chronology gates for comparisons and review support arrived. run-03 added review chronology and exposed a pre-observation reviewer date wrongly confirming a fix; that gate was then corrected.
3. run-04 had one obsolete assertion expecting all reviewed priorities to stay pending. The requested API now uses reviewed_fix_sequence / verify_before_change / optional / retain while remaining provisional. The assertion was updated to require those exact semantics, supplied rationale and no unreviewed promotion; the failed log is preserved.
4. run-05-final uses exact input_fingerprint binding. The additional stale-content test verifies that changing a same-date product value rejects the old review. Final logs are run-05-truth-tests.txt and run-05-full-suite.txt.

## Unsupported capabilities and remaining boundaries

- Reviewer prose is a supplied assertion. Structural evidence/date/intent validation cannot prove that a person actually performed the stated semantic review or that an asserted authority is truthful.
- Without optional input_fingerprint, a review binds to evidence locators, not exact content; the report explicitly warns such assertions may be stale. The final example uses fingerprint binding.
- No live crawl, Search Console/index coverage, complete graph, backlinks/reputation audit, real-world business-profile eligibility, rendered parity or official validator execution occurred here.
- No automated offpage defect detector exists; reporting offpage “defect recall” would be fabricated. A section keep note cannot clear unrelated findings or unresolved unknowns.
- Synthetic fixes and thresholds do not establish real ranking, revenue, conversion, or accessibility outcomes.

## Final freeze verification

`run-06-freeze/` is the last CLI rerun against frozen reporter SHA-256 `51340e158ade55feb749bc4e3df7f50f9e59d690cb5217d61c50b2a7e38609a2`. Its complete JSON and handoff decisions are identical to run-05-final. Fresh run-06 logs confirm 24 truth tests and all 119 repository tests pass. Bucket counts remain 5 confirmed-fix claims / 8 needs-verification tasks / 1 optional improvement / 4 scoped keep decisions. All earlier artifacts are preserved. See `run-06-manifest.json` for final hashes.
