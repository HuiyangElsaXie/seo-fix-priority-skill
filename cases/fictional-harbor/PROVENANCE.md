# Source manifest and mapping

All source data, organization, people/roles, dates and URLs are fictional and agent-authored for this example. Only local normalization, CLI execution and review actually occurred. There is no customer export, crawler run, independent human reviewer or live verification. build_case.py is the reproducible fixture author and converter, not a crawler.

- S-OCT: simulated October 14 partial crawl and explicit intent map, E01–E10 and E12–E15. Homepage-start crawl-style sample plus seeded URLs; HTML extraction without JavaScript rendering, simulated desktop crawler user agent. No complete link graph, authenticated content, response-header dump, sitemap or analytics. Depth and inlinks describe this slice; seeded scorecard zero inlinks is not an orphan verdict.
- S-AUG: simulated August 20 historical pricing snapshot, E11. 57 days old at review, and deliberately not represented as current.
- editorial-intent.json: simulated marketer's brief classification, separate from technical observations. Unknowns remain unknown; effort estimates are hypothetical integers, not measured delivery estimates.
- observation-notes.md N01–N06: synthetic supporting details and limitations. E10 combines direct-fetch and rule-evaluator signals explicitly; E07 includes a hop-only intermediate URL outside the 15-row slice.

## Explicit CSV → JSON mapping
Address → url (exact, no URL rewriting or deduplication); Status Code → status (explicit int); Export Indexable and Robots Blocked → indexable/robots_blocked via the exact yes/ no/ NOT_COLLECTED vocabulary; Canonical Link → canonical; Title 1 → title; Crawl Depth/Unique Inlinks/Redirect Count → depth/inlinks/redirect_hops (int). NOT_COLLECTED → null everywhere. An empty title cell remains an observed empty string. Blank canonical cells are not used. Missing is never zero. Snapshot Date selects S-OCT or S-AUG; Evidence ID plus intent-map key becomes evidence_locator. All 15 exact URLs are unique; no conflicts were silently resolved.

Intent, importance and optional effort come from the saved editorial map; omitted effort uses the helper's disclosed default 5. No indexability is inferred from status. Normalization reads the saved CSV; the map written in the same reproducible script is the identical classification source. Source row keys E01–E15 are stable even if file line numbers move.

Raw files are preserved with input.v1.json and output.v1.json. commands.log records actual local execution. sha256.txt records artifacts after review. No network or remote writes were used.
