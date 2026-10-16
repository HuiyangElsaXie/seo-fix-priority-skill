# HarborFlow owner handoff

Fictional case • agent-executed offline demonstration • not a live audit. All actions below are proposed and unimplemented. Owners are fictional roles, not assignments to real people. No rankings, revenue, traffic loss or conversion gains have been measured or predicted.

## Decision summary

15 supplied URL rows generated 9 findings: one P1, two P2, one P3 and five review-only. Nine other observations were suppressed by explicit exclusion intent. Four rows have missing signals. Start by validating the supplier-onboarding noindex conflict; prepare title and legacy-link repairs next. Treat the scorecard's two findings as one investigation, despite the helper's standalone P3 depth label. Neither a high heuristic score nor high evidence consistency grants implementation authority.

Machine sources: preserved first output.v1.json and final output.v2.json (same findings, added confidence-definition metadata). Business intent: BRIEF.md and evidence/editorial-intent.json. Technical observations: evidence/crawl-slice.csv using E01–E15; supporting details: evidence/observation-notes.md using N01–N06.

## Proposed work packets

### 1. Validate unintended exclusion on supplier onboarding
- IDs: SEO-001; E02 / N01; /solutions/supplier-onboarding. Owner: SEO lead with engineering support.
- Observation: 200, export non-indexable, and synthetic noindex HTML extract; intended acquisition page. P1 9.0; source age 2 days. “High” means consistency within supplied evidence only.
- Rationale: this is a critical evaluation landing page in the fictional brief. Impact size is unknown.
- Action/gate: verify live response headers, rendered HTML, applicable robots rules and intended canonical; obtain product/SEO agreement that noindex is accidental. Only then propose removing the unintended directive at its source. Check for template-wide scope before scheduling.
- Acceptance: approved page returns intended status, directives and canonical agree with approved intent, and fresh rendered/response checks show the unintended exclusion removed. Record before/after evidence and regression-test deliberately excluded pages. Search inclusion is not guaranteed.

### 2. Repair missing vendor-risk title after template check
- IDs: SEO-002; E03; /solutions/vendor-risk. Owner: Content lead, engineering if template-owned.
- Observation: observed empty title string, not missing measurement. P2 7.2; age 2 days.
- Rationale: critical product-evaluation page should clearly identify its subject.
- Action/gate: inspect rendered output and title-generation template, confirm intended page positioning, then approve a specific descriptive title. No final copy has been approved in this example.
- Acceptance: rendered title is nonempty, reflects approved intent, and relevant template duplicate/missing-title checks pass. No CTR improvement claim.

### 3. Shorten links through legacy platform redirect
- IDs: SEO-003; E07 / N03; /platform. Owner: Engineering lead with SEO target approval.
- Observation: /platform → /product → /solutions/supplier-onboarding, two redirects; seven reported inlinks in the slice. P2 6.4; age 2 days.
- Rationale: simplify a supporting entry path toward the intended product page.
- Action/gate: acquire actual referring URLs and full current hop responses; confirm final destination is appropriate. Update approved internal links directly to the final destination. A server redirect change is a separate scoped proposal, not automatically authorized here.
- Acceptance: each approved changed link reaches the intended 200 destination without intermediate hops; no loop, incorrect destination or regression to old inbound URLs. Preserve redirect coverage for legitimate historic inbound links. Missing HTML signals on a 301 are not evidence of HTML defects.

### 4. Investigate scorecard discovery as one packet
- IDs: SEO-004 + SEO-008; E05; /resources/vendor-scorecard. Owner: SEO lead.
- Observation: depth 5 and zero inlinks in a partial seeded crawl. Helper emits P3 5.2 and review 5.6, respectively; age 2 days. These are two symptoms on one URL, not two independently quantified benefits.
- Human disposition: gate the entire packet for investigation. The seeded sample/partial scope cannot establish orphan status, and its depth and inlink metrics need compatible definitions and crawl scope before acting.
- Action/gate: obtain crawl start, discovery-path definition, full internal link graph and relevant sitemap/landing-page inventory. Reconcile how depth 5 was recorded while supplied inlinks are zero; this can reflect filtered link reporting, but the fixture does not prove the explanation. If useful links are genuinely absent, propose relevant navigation/contextual placement with content owners.
- Acceptance: document metric definitions and reconciled discovery path; only after an approved link change, verify actual link placement and recalculate depth/inlinks with the same scope. Do not promise a numeric depth target before the navigation decision.

### 5. Refresh stale pricing evidence
- IDs: SEO-005; E11 / N05; /pricing. Owner: SEO lead.
- Observation: non-indexable in the August 20 snapshot, 57 days old. Review-only despite score 8.6; confidence low.
- Rationale: pricing is critical, but the old state cannot establish a present defect.
- Action/gate: obtain a fresh authorized current observation plus intended pricing visibility. Do not apply an old noindex fix blindly; the exclusion cause is not supplied.
- Acceptance: attach dated current status, directives, canonical and rendered evidence. Close if intended/current state is sound; otherwise open a newly scoped repair with owner approval. This refresh is outstanding, not performed.

### 6. Confirm procurement canonical intent
- IDs: SEO-006; E06 / N02; /solutions/procurement-automation. Owner: SEO lead with product/content owners.
- Observation: canonical points to supplier-onboarding. Review 8.0, age 2 days.
- Rationale: both are marked critical, but product overlap could make consolidation intentional.
- Action/gate: compare content, approved positioning and source/target status/directives; get canonical ownership decision. No automatic self-canonicalization. Canonical selection by a search engine has not been inspected.
- Acceptance: written canonical decision and consistent approved implementation across HTML/headers and sitemap entries where applicable; target is suitable and available. Close as intentional if evidence supports it.

### 7. Resolve historical checklist lifecycle
- IDs: SEO-007; E08 / N06; /resources/vendor-checklist-2023. Owner: Engineering lead, with SEO/content decision first.
- Observation: 404, two supplied inlinks, unknown intent and importance. Review 6.6; age 2 days. Default effort 5 is only a placeholder.
- Action/gate: determine retirement/replacement policy and identify referring links. Depending on documented decision, retain the 404 and remove obsolete links, restore accidentally removed content, or use an approved genuinely relevant replacement. Do not redirect every 404 to the homepage.
- Acceptance: signed-off lifecycle decision; current response and changed internal links match it; any replacement chain is relevant and loop-free. A correct retained 404 can pass.

### 8. Confirm retired campaign response policy
- IDs: SEO-009; E15 / N06; /campaigns/spring-demo. Owner: Engineering lead with marketing/SEO decision.
- Observation: 404; intentional organic exclusion. Review 5.4; age 2 days; effort default 5.
- Action/gate: confirm whether 404 is the intended retirement response and whether campaign links still need updating. Exclusion is not permission to restore or redirect.
- Acceptance: documented retirement state and matching response; update stale links if justified and authorized. Close without code change if current response is intentional.

## Suppressed, unflagged and unknown are distinct

- E09 thank-you: suppress NONINDEXABLE, MISSING_TITLE, ZERO_INLINKS (3).
- E10 internal preview: suppress NONINDEXABLE, ROBOTS_BLOCKED, MISSING_TITLE, DEEP_PAGE, ZERO_INLINKS (5). No recommendation to remove intentional restrictions. A robots rule is not an access-control security guarantee.
- E14 privacy: suppress NONINDEXABLE (1), per explicit brief; do not generalize this policy to other sites.
- E01 homepage, E04 demo, E13 blog: no supported rule triggered in supplied rows. This is not a full audit pass.
- E12 API guide: six unavailable signals, so absence of findings is explicitly inconclusive. Request actual rendered/response/crawl evidence before calling it healthy.
- E07/E08/E15: five HTML/crawl signals each unavailable; non-200 responses limit relevance of some HTML checks. Current status/hops/lifecycle remain the appropriate first checks.

## Evidence needed from a real owner

Current snapshots; response headers and rendered HTML; authoritative intent/lifecycle and canonical decisions; complete crawl configuration and link graph with referring URLs; template scope; current redirect log; and realistic effort/owner availability. No Search Console, analytics, rank tracking, revenue data, JavaScript rendering, Core Web Vitals, schema validation or full sitemap assessment was supplied. No outreach or collection was performed.
