# Independent Local SEO evidence checks

All businesses, place identifiers, addresses, URLs, review text, and metrics in this folder are fictional. The fixtures test deterministic evidence handling; they do not establish live Google Business Profile status, customer sentiment, rankings, eligibility, or business impact.

## Review scope

- Explicit zero review count must remain different from missing/unknown count.
- Low ratings with tiny samples must not carry the same confidence as substantial review counts.
- Stale, malformed, and future-dated observations cannot establish current profile facts.
- Brand-level matches do not establish branch/place identity.
- Formatting-only NAP differences should not be treated as substantive conflicts; differing units, street numbers, and phone digits must not be silently erased.
- Missing peers and incomparable peer samples cannot justify relative performance conclusions.
- A partial visible-review sample cannot establish total reviews, population response rate, or sentiment trend.
- LocalBusiness markup checks remain bounded to supplied markup; website schema does not establish profile state or ownership.
- Review invitations must be neutral and intended for actual customers. No review gating, purchased/fake reviews, incentives, or automatic posting of replies.

`test_local_seo_truth.py` is independently authored. Execution logs record actual test runs; a fixture alone is not evidence that a check passed.

## Executed review

See `INDEPENDENT-REVIEW.md` for actual results, resolved findings, retained intermediate logs, and scope limits. `actual-import-to-six-report/` demonstrates the full offline import-to-report path with fictional data.

## Final integrated examples

- [Low rating, substantial count](final-substantial-low-rating/report.md): fictional 3.0/5, total 120, visible sample 3. Investigate service/reputation context, no ranking-loss assertion.
- [Explicit zero reviews](final-explicit-zero/report.md): neutral genuine-customer invitation suggestion, no incentives/gating.
- [Unknown aggregate](final-unknown-reputation/report.md): no low/zero-review diagnosis; collect appropriate evidence first.
- [Offline export import](final-imported-report/report.md): actual runnable Places-shaped fictional JSON → converter → reporter route.

These six-section examples deliberately have an empty fictional website snapshot to isolate local behavior. Other sections remain unassessed/N/A according to the fictional context; this is not a six-dimension healthy-site demonstration. Sources under example.invalid are synthetic locators, not live Google access. Final coordinator regression includes the later detailed-warning assertion: 180 tests passed, including 28 independent truth tests. Earlier 179-test log is preserved as its actual historical result.
