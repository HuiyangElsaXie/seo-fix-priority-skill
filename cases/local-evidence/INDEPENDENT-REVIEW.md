# Independent Local SEO evidence review

Reviewed on 2026-10-16. All inputs are fictional. No external services, live profiles, credentials, real customers, or business data were used.

## Actual execution results

- 28 independently authored truth tests in `tests/test_local_seo_truth.py` passed.
- Combined local-module, importer, integration, and independent suites: 60 tests passed in `combined-local-test-run-final.txt`.
- Full project regression: 179 tests passed in `full-regression-run.txt`.
- Executed the offline Places importer and then the six-dimension report CLI using its output. See `actual-imported-places.json` and `actual-import-to-six-report/`.
- Integrated report preserves all six dimensions, one low-rating investigation task, zero confirmed fixes, unknown business impact, and the supplied-input/non-independent-verification caveat.
- Additional standalone module outputs are preserved in `actual-low-rating-output/` and `actual-partial-sample-output/`.

These are actual executions, not a claimed live Google test or a future test plan. Test totals describe the source state at execution; subsequent edits require a rerun.

## Truth boundaries checked

Explicit zero and unknown reviews remain distinct. Low ratings use lower confidence for tiny counts. Invalid metrics do not create low-volume or low-rating findings. Stale, future, malformed, wrong-branch/place/market, and observation-after-capture evidence cannot establish current reputation findings. Formatting-only NAP differences normalize conservatively; altered address units and telephone digits remain distinguishable. No country prefix is inferred.

No peers means no relative performance calculation. Peers require explicit comparable market, category, comparison group, maturity, date, and aggregate coverage. Partial visible-review samples cannot establish aggregate total, aggregate rating, or trend. Three-date aggregate comparisons were tested in all six input permutations. Hours require matching explicit timezone, current effective windows, and covered regular/exception hours.

LocalBusiness checks stay scoped to supplied markup fields and cannot prove Google profile reputation, ownership, or complete eligibility. Review-related action plans explicitly require genuine customers, neutral invitations, no incentives, no gating or fabricated reviews, and no automatic replies. Findings remain investigations pending current evidence and human decisions.

## Findings resolved during review

1. Flagged the risk of legacy raw-string NAP comparison running after the new module. Enriched integration now bypasses legacy local processing while preserving the other dimensions.
2. Flagged arbitrary importer metadata passthrough, which could retain unrelated review text or token-shaped fields. Coordinator replaced it with allowlists; independent regressions confirm both raw-response and metadata review text/tokens are omitted.
3. One intermediate combined test run failed because an assertion expected the previous LocalBusiness limitation wording. The newer wording distinguishes documented required/recommended fields while retaining the incomplete-eligibility caveat. The semantic-boundary assertion was updated; final runs pass. Earlier logs are retained as execution history.

## Remaining limits

The importer does not fetch Google APIs or verify authenticity. GBP resource binding is explicitly supplied, not independently established. Operating status is not ownership verification. Tests cover these offline contracts, not live API access, all schema vocabulary, real review policy enforcement, ranking improvements, or business outcomes.
