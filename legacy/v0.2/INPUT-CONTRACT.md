# Input contract v0.2

Python 3.10+; standard library only. The CLI reads one UTF-8 JSON file and prints JSON to stdout. Exit 2 means invalid input. It never fetches any listed URL. Write output using shell redirection into a new filename.

Required top-level fields: `schema_version: "0.2"`, ISO date `as_of`, `business_context`, `sources`, `rows`.

- business_context: nonempty `objective`; optional `owners` map for engineering/seo/content. Missing owner becomes visibly unassigned. Additional context fields are allowed for human review.
- sources: object keyed by source ID. Each value requires `kind` (`fictional_fixture`, `supplied_export`, `supplied_manual_check`), nonempty `description`, ISO `observed_at` (not later than as_of). Description should disclose tool, scope and provenance.
- rows: array with unique exact `url` (absolute HTTP(S), no embedded credentials), `source_id`, nonempty `evidence_locator`, integer `status` 100–599, `intent` (`index`, `exclude`, `unknown`), and `importance` (`critical`, `supporting`, `low`, `unknown`). URL equality is exact; resolve variants deliberately before ingest.
- Optional signals: `indexable` / `robots_blocked` strict boolean or null; `canonical` absolute URL or empty/null; `title` string or null; `depth`, `inlinks`, `redirect_hops` nonnegative integer or null; `effort` integer 1–10. Omitted effort defaults to 5 and is disclosed. String booleans/numbers are rejected. Missing measurements are never replaced with zero.

There is intentionally no direct CSV import: explicitly map your export headers and document conversion. Indexability must come from supplied evidence rather than being inferred from status alone. Reconcile duplicate/conflicting observations before running; preserve originals. Export filters and URL samples are coverage limits, not the complete website.

Output: metadata/scope, counts, ordered `queue`, `suppressed` observations, and `coverage_gaps`. Every queue entry has rule, priority, score inputs, confidence, evidence locator/age, business rationale, owner, gates, proposed fix, verification and implementation status. Canonical and zero-inlink findings always need corroboration. Priority labels are proposals and do not grant permission to change a site.
