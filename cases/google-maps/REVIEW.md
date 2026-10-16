# Independent Google Maps and business-applicability review

2026-10-16. All inputs are fictional. No network requests, live Google queries, real credentials, website edits, or external writes were performed.

## Actual results

- 30 independent tests passed: `independent-final-30-test-run.txt`.
- All 228 project tests passed: `full-regression-final-run.txt`.
- Four complete six-dimension report examples were executed through the CLI. Each directory contains its input files, execution record, and actual JSON/Markdown report. `actual-example-summary.json` records the outcomes.

### Executed report examples

1. `personal-portfolio-na/`: attributed noncommercial purpose and no customer service/transaction goals; local and ecommerce are not applicable, and no map finding is generated.
2. `local-clinic-map-optional/`: attributed physical customer visits with no supplied static Maps evidence; exactly one optional navigation-support task, no confirmed map defect. It explicitly allows retaining no map.
3. `contact-map-blog-absence/`: contact page contains a map signal while the blog page does not. No missing-map suggestion is generated. A map is not required on every page.
4. `wrong-branch-verification/`: explicit supplied place ID differs from the target; one branch-verification task, zero confirmed map fixes. Actual destination and browser behavior remain unverified.

## Business-model coverage

The independent tests exercise these supplied, attributed models without inferring purpose from a URL, missing cart, or missing map:

- Personal portfolio and online-only noncommercial content: no forced local or ecommerce work.
- Local shop without online transactions: local yes, ecommerce no.
- Standalone local clinic: local yes, ecommerce no; domain form makes no difference.
- Multibranch ecommerce with local customer service and transactions: both yes.
- Noncommercial organization with an explicit local-service purpose: local yes remains possible.
- Unknown context: remains unknown, no finding or health-score penalty; explicit applicability overrides are preserved.

Future-dated or unattributed business-model claims are rejected or cannot establish applicability.

## Security and evidence review

Tests distinguish iframe embeds, Maps JavaScript signals, directions links, and location links. Lookalike domains, unsupported paths, embedded credentials, unresolved short links, opaque `pb` values, names, coordinates, and origin-only IDs cannot establish the intended branch. Duplicate conflicting explicit IDs remain mixed rather than silently matching one branch.

Forged structured evidence cannot preserve supplied rendering verdicts, arbitrary text, full map URLs, or API-key-shaped IDs. Missing/malformed evidence cannot become an absence recommendation. Consent-deferred maps remain unverified runtime signals. Static absence never establishes that a functional map is missing.

Two issues were found and fixed during review:

1. Encoded query-key names/values and numeric HTML entities bypassed raw-artifact key redaction. Regression tests now verify both are removed before artifact storage.
2. Redacting a credential-bearing URL before extracting safe structured evidence erased its unknown signal. The collector now extracts sanitized Maps evidence from the original in-memory HTML, then saves/redoes general parsing on the redacted artifact. Offline fake-transport tests verify credentials are absent from artifacts and snapshot output while unknown evidence is preserved. Source and artifact hashes record the redaction difference.

The initial failing security log is preserved as history. Final logs pass. Fixture HTML contains visibly fictional test strings only; generated report outputs are sanitized.

## Remaining limits

This is offline parser, collector-hygiene, and report-integration verification. It does not prove browser rendering, mobile interaction, consent behavior, actual destination, Google listing ownership, source authenticity, live API behavior, ranking effects, or revenue impact. Human review and appropriate permission are still required before any website changes.
