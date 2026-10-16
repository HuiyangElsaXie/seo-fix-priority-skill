# Synthetic actionable-handoff truth cases

Every URL, entity, business assertion, reviewer, date and metric in this directory is fictional. No live requests were made. These are deliberately constructed supplied observations, not discovered bugs on a real site, client work, or proof of real SEO outcomes.

## Source ledger

- `snapshot.json`: synthetic HTTP/HTML observations, dated 2026-10-16; the JSON page records themselves are the reproducible source. `fictional-inline-fixture` is a logical fixture locator, not a claim that a fetched HTML file exists.
- `context.json`: synthetic retail brief and explicit local/ecommerce/international applicability, as of 2026-10-16. Only industry is supplied in essential business context, so business prioritization must stay provisional.
- `supplement.json`: synthetic field-p75 LCP window 2026-09-18–2026-10-15, backlink sample, same-identity branch phone comparison and product/variant price comparison, dated 2026-10-16. The paired values deliberately conflict; neither value is authoritative without review.
- Tests in `tests/test_handoff_truth.py` also construct missing evidence, invalid/future dates, cross-currency comparisons, lab metrics, missing target samples, explicit non-applicability and reviewed intent contradictions.

## Truth oracle and limits

The five deterministic positive dimensions are technical (JSON-LD parse signal; field LCP above threshold), on-page (empty title), local (paired phone disagreement), ecommerce (same-currency variant price disagreement), and international (collected HTML return-reference omission). These are observed candidates, not automatically confirmed business defects.

Offpage has no implemented automated fault detector. The honest oracle is “supplied sample, completeness/reputation/liveness unknown” or “missing evidence”; no offpage precision/recall or fake defect count is claimed.

`/private` has deliberate noindex and a cross-page canonical. `/deleted` is deliberately retired. Without a supplied review asserting those intentions, verification is correct; automatically removing exclusions or restoring a retired URL is incorrect. With a valid intentional-exception review, keep is correct. Missing business context is never permission to infer P0/P1 urgency, ROI or ranking damage.

## Preserved runs

- `run-00-original/`: original reporter output before the actionable implementation landed. It demonstrates generic acceptance and unassigned owners.
- `run-00-invalid-time-probe.json`: original malformed/future `observed_at` values accepted as two mismatch findings each.
- `run-00-truth-tests.txt`: first independent 12-test execution. The implementer's initial handoff was already present by execution; 11 tests passed and two subcases in one test failed for invalid/future dates. This is not a zero-pass baseline and does not pretend tests ran before code existed.
- `run-01-handoff/`: first four-bucket output, before review-led decisions and timestamp correction.

Run from repository root:

    python -m unittest discover -s tests -p test_handoff_truth.py -v

CLI results are always written to a fresh directory. Earlier reports and failure evidence are retained, not overwritten.

## Final reviewed example and matrix

The final inspected CLI output is `run-05-final/report.md` / `report.json`. `OUTCOME-MATRIX.md` records expected versus actual decisions, source identity/date/locator, actionability inspection, failures/corrections and unsupported capabilities. `run-05-manifest.json` records exact tested file hashes.

The full synthetic review is `review.json`, including exact `input_fingerprint` binding. It makes five supplied-review fix claims, one optional editorial improvement, and four scoped keep decisions; eight verification tasks remain. This does not independently verify reviewer assertions.

Reproduce to a NEW output path:

    python scripts/six_dimension_report.py cases/actionable-handoff/snapshot.json --context cases/actionable-handoff/context.json --supplement cases/actionable-handoff/supplement.json --review cases/actionable-handoff/review.json --out cases/actionable-handoff/reproduced-final
    python -m unittest discover -s tests -p test_handoff_truth.py -v
    python -m unittest discover -s tests -v

Final results: 24 independent truth tests pass; 119 repository tests pass. `make_review_fixture.py` regenerates the synthetic review IDs/fingerprint when intentionally changing synthetic inputs; do not use it to silently reapprove real changed evidence.

## Final freeze verification

`run-06-freeze/` is the last CLI rerun against frozen reporter SHA-256 `51340e158ade55feb749bc4e3df7f50f9e59d690cb5217d61c50b2a7e38609a2`. Its complete JSON and handoff decisions are identical to run-05-final. Fresh run-06 logs confirm 24 truth tests and all 119 repository tests pass. Bucket counts remain 5 confirmed-fix claims / 8 needs-verification tasks / 1 optional improvement / 4 scoped keep decisions. All earlier artifacts are preserved. See `run-06-manifest.json` for final hashes.
