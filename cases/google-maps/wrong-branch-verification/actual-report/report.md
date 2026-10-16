# SEO review and action plan

Report level: generic_framework
Business objective: unknown
Technical facts and interpretive judgments are separated. Supplied scoped reviews do not clear unreviewed semantic scope.
Final review status: not_supplied
Review input binding: evidence_locator_only; review assertions may be stale if source content changed

## Questions to confirm scope

- What is the website purpose: portfolio, content, lead generation, online sales or other?

## Decisions at a glance

- confirmed_fix: 0
- needs_verification: 7
- optional_improvement: 0
- keep_or_not_applicable: 1

[Go to concrete steps, proposed roles, dependencies and acceptance checks](#actionable-handoff).
Confirmed fixes are scoped supplied-review decisions, not independent verification. Verification tasks are not diagnosed site faults.

## Technical
Applicability: yes. General website review dimension.
Evidence: partial (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 4; findings: 0.
Review: Confirm intended visibility, canonical choices, rendering and business-critical paths; observed directives do not prove Google index status.
- Unknown: Crawl/HTML sample does not prove index inclusion, rendered parity, complete internal graph or robots access for every crawler.
- Unknown: No supplied field CWV export: LCP/INP/CLS unknown, not measured.

## Onpage Content
Applicability: yes. General website review dimension.
Evidence: partial (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 1; findings: 0.
Review: Review reader task, accuracy, first-hand evidence, authorship and useful next steps in full content. Do not score E-E-A-T, keyword density or word count.
- Unknown: Full-content task satisfaction and factual accuracy need semantic review; excerpts/word counts cannot establish thin content.

## Offpage
Applicability: yes. General website review dimension.
Evidence: not_assessed (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 0; findings: 0.
Review: Review relevance, independence, paid relationships and sample bias. DA/DR are third-party measures, not Google authority scores.
- Unknown: No backlink/mention data supplied; this does not mean no backlinks exist.

## Local
Applicability: yes. Explicit local customer service or local acquisition purpose; Business Profile eligibility remains separately reviewable. Supplied basis: Explicit fictional business model; not inferred from URL or page features.
Evidence: partial (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 1; findings: 1.
Review: Confirm real customer contact/service eligibility, branch identity and privacy before suggesting a Business Profile; a city/address alone establishes no eligibility.
- Google Maps static signals: embedded_map; branch comparison: mismatch; rendered functionality: unverified.
- Unknown: https://fictional.example/contact: Google Maps rendering, interaction, consent behavior and actual destination remain unverified.
- Unknown: NAP/hours paired website and reference evidence unavailable
- Unknown: Google aggregate trend unknown; two genuinely comparable dated aggregates required
- Unknown: No comparable peer context supplied; rating/count threshold warnings are not comparative market judgments
- Unknown: Current Google aggregate reputation unknown; no valid supplied aggregate evidence

## Ecommerce
Applicability: no. Online transaction purpose is explicitly no. Supplied basis: Explicit fictional business model; not inferred from URL or page features.
Evidence: not_assessed (bounded checks only); semantic review: not_applicable.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 0; findings: 0.
Review: Confirm current selling purpose, variants, purchase flow, delivery and returns; past ecommerce case studies do not make this site a shop.
- Unknown: Not applicable according to supplied business reason; no penalty assigned.

## International
Applicability: unknown. Business applicability has not been confirmed.
Evidence: not_assessed (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 0; findings: 0.
Review: Review actual language/market purpose, translation quality and regional requirements; single-language sites need no standalone missing-hreflang warning.
- Unknown: Actual language/region variants are unknown; paths or location names do not establish applicability.

## Deduplicated findings

### issue-a9808dfbe738 / local
- Subject: https://fictional.example/contact
- Technical fact: Supplied explicit map place identifier conflicts with the supplied target branch; real destination is unverified.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Verify intended public branch before changing map links or embeds.
- Priority: verify_before_change (provisional). Verify a possible customer navigation mismatch first; urgency depends on confirmed visit impact and source freshness.
- Evidence: e-a7565c56265e

## Actionable handoff

Actionable investigation and conditional repair plans, not execution approval. Evidence gaps are conditional scope checks, not mandatory tool purchases or website changes. Empty confirmed-fix and optional buckets do not mean healthy. Proposed roles are not assigned people. Business priority remains pending; investigation sequencing is evidence-based.

### confirmed_fix

No supported decisions in this bucket.

### needs_verification

#### task-issue-a9808dfbe738
- Scope: local / https://fictional.example/contact
- Basis: Supplied explicit map place identifier conflicts with the supplied target branch; real destination is unverified.
- Proposed role: Local operations manager
- Why this next: Verify a possible customer navigation mismatch first; urgency depends on confirmed visit impact and source freshness.
- Dependencies: Confirmed target branch and publicly shareable address; Owner approval and website access for any future edit; Rendered-browser verification; this report performs no API calls or publishing
- Evidence: e-a7565c56265e
1. Inspect the page in a rendered browser, including consent-delayed and mobile behavior; save sanitized evidence.
2. Confirm the intended public branch, customer visit purpose and address privacy with the owner.
3. If a wrong destination is confirmed, correct only the approved link/embed; otherwise retain intentional behavior.
- Acceptance: Record rendered behavior and actual destination for the intended branch without storing API keys.
- Acceptance: Verify mobile accessibility, consent behavior and destination after any approved change, or document the choice to retain the page.

#### task-404b69bc24c4
- Scope: technical / Evidence investigation
- Basis: Crawl/HTML sample does not prove index inclusion, rendered parity, complete internal graph or robots access for every crawler.; No supplied field CWV export: LCP/INP/CLS unknown, not measured.
- Proposed role: Technical SEO reviewer with web engineer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.technical.unknowns
1. Investigate only these scoped gaps: Crawl/HTML sample does not prove index inclusion, rendered parity, complete internal graph or robots access for every crawler.; No supplied field CWV export: LCP/INP/CLS unknown, not measured.
2. If any scoped HTTP/parse failures are listed, repeat the exact requests and save status, headers and raw HTML before re-running skipped checks.
3. For index/rendering uncertainty, compare rendered HTML and URL Inspection evidence for the scoped URLs; inspect robots rules for the relevant crawler and record sample limits.
4. For CWV gaps, request a field p75 export with URL/origin scope, device, metric, units and window; invalid or absent records remain unknown.
5. Attach source, date, scope and locator for each resolved gap; keep unavailable or irrelevant checks explicitly unresolved/not applicable.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-b47cd1f66509
- Scope: onpage_content / Evidence investigation
- Basis: Full-content task satisfaction and factual accuracy need semantic review; excerpts/word counts cannot establish thin content.
- Proposed role: Content editor with SEO reviewer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.onpage_content.unknowns
1. Investigate only these scoped gaps: Full-content task satisfaction and factual accuracy need semantic review; excerpts/word counts cannot establish thin content.
2. Review full content for the exact affected URLs against the intended reader task; list factual claims and their supporting sources.
3. Check authorship/first-hand evidence and whether internal links or a relevant next action help the reader; compare rendered metadata with raw HTML where parsing failed.
4. Attach source, date, scope and locator for each resolved gap; keep unavailable or irrelevant checks explicitly unresolved/not applicable.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-debf275596d0
- Scope: offpage / Evidence investigation
- Basis: No backlink/mention data supplied; this does not mean no backlinks exist.
- Proposed role: PR or partnerships reviewer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.offpage.unknowns
1. Investigate only these scoped gaps: No backlink/mention data supplied; this does not mean no backlinks exist.
2. If external reputation evidence is needed for this objective, obtain a dated referring-page/target/rel export with its sampling limits.
3. Inspect a documented sample for live links, topical relevance, independence and paid relationships; do not infer reputation from missing data or recommend buying links.
4. Attach source, date, scope and locator for each resolved gap; keep unavailable or irrelevant checks explicitly unresolved/not applicable.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-76a28996d350
- Scope: local / Evidence investigation
- Basis: https://fictional.example/contact: Google Maps rendering, interaction, consent behavior and actual destination remain unverified.; NAP/hours paired website and reference evidence unavailable; Google aggregate trend unknown; two genuinely comparable dated aggregates required; No comparable peer context supplied; rating/count threshold warnings are not comparative market judgments; Current Google aggregate reputation unknown; no valid supplied aggregate evidence
- Proposed role: Local operations manager
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.local.unknowns
1. Investigate only these scoped gaps: https://fictional.example/contact: Google Maps rendering, interaction, consent behavior and actual destination remain unverified.; NAP/hours paired website and reference evidence unavailable; Google aggregate trend unknown; two genuinely comparable dated aggregates required; No comparable peer context supplied; rating/count threshold warnings are not comparative market judgments; Current Google aggregate reputation unknown; no valid supplied aggregate evidence
2. First ask whether this business actually serves customers at an eligible location or service area; document the decision and privacy constraints.
3. Only if applicable, compare current website and approved business-profile records for the same entity/branch and effective time: name, address, phone and hours.
4. For review gaps, obtain a dated platform/branch-scoped sample and its coverage, counts, timestamps and reply evidence; no supplied reviews means review activity is unknown, not absent.
5. For profile or location-page gaps, capture the approved branch profile and matching live location page; confirm categories, service area, displayed-address privacy and current customer contact details before edits.
6. For citation or competitor gaps, identify dated same-market, same-query and same-branch sources; formatting variants and incomplete samples alone do not establish inconsistency or competitive weakness.
7. Attach source, date, scope and locator for each resolved gap; keep unavailable or irrelevant checks explicitly unresolved/not applicable.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-9deb213cb399
- Scope: international / Evidence investigation
- Basis: Actual language/region variants are unknown; paths or location names do not establish applicability.
- Proposed role: Localization lead with technical SEO reviewer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.international.unknowns
1. Investigate only these scoped gaps: Actual language/region variants are unknown; paths or location names do not establish applicability.
2. Confirm the actual language/region variants and intended alternate strategy before requiring hreflang.
3. For each explicitly missing target in the scoped gaps, collect target HTML plus relevant header/sitemap declarations; compare return references, self-reference, mappings and canonical targets.
4. Have a fluent reviewer check the intended reader task and translation on the scoped variants; uncollected targets remain unknown.
5. Attach source, date, scope and locator for each resolved gap; keep unavailable or irrelevant checks explicitly unresolved/not applicable.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-business-context
- Scope: business_context / Missing essential context
- Basis: industry, audience, geography, language, primary_objective, resources, constraints, specific_problem
- Proposed role: Business owner with SEO lead
- Why this next: Context gates business-specific ordering; it does not prevent reporting observed technical signals.
- Dependencies: Business owner input
- Evidence: Evidence gap / supplied applicability decision; see intake.missing_essential
1. Ask the business owner for each missing answer: industry, audience, geography, language, primary_objective, resources, constraints, specific_problem
2. Record each answer with a dated source and evidence locator before tailoring recommendations.
- Acceptance: Every missing essential answer has a valid attributed source or is explicitly left unknown.
- Acceptance: Business prioritization remains provisional for unresolved answers.

### optional_improvement

No supported decisions in this bucket.

### keep_or_not_applicable

#### task-bab237b49009
- Scope: ecommerce / Applicability decision
- Basis: Online transaction purpose is explicitly no. Supplied basis: Explicit fictional business model; not inferred from URL or page features.
- Proposed role: Catalog operations manager with web engineer
- Why this next: Preserve an explicit supplied scope decision.
- Dependencies: Business owner confirmation if applicability changes
- Evidence: Evidence gap / supplied applicability decision; see sections.ecommerce.applicability
1. Retain the documented applicability decision: Online transaction purpose is explicitly no. Supplied basis: Explicit fictional business model; not inferred from URL or page features.
2. Revisit only if the business offering or market scope changes.
- Acceptance: Applicability reason, source and date remain recorded; no missing-data penalty is assigned.

## Boundaries
- No overall health/authority score, traffic loss, ranking penalty or ROI is calculated.
- Unreviewed semantic scope remains pending; supplied external reviews are attributed assertions, not AI review performed by this deterministic script.
- JSON-LD checks are not official rich-result validation. FAQ rich results were removed May 7, 2026; no FAQ rich-result benefit is promised.
- Priority is qualitative and pending business-impact/effort/owner evidence; technical severity is separate.
- Static HTML signals only; rendering, interactivity, availability and consent behavior are not verified.
- JavaScript or consent-delayed maps may be absent from supplied HTML; absence is not proof of a missing map.
- Opaque pb payloads, coordinates and place names do not establish branch identity. Short links are not resolved.
- A map is optional user-experience support, not an automatic SEO defect or ranking requirement.
- Only explicitly allowlisted Google hosts and map paths are recognized; no network requests are made.
- Supplied evidence is not independently verified; missing evidence is unknown, never zero.
- Thresholds are configurable triage heuristics, not Google ranking factors or benchmarks.
- Visible review samples cannot establish total volume, average rating or a trend; sample selection may be biased.
- LocalBusiness checks cover supplied field presence/shape only, not Google eligibility, indexing or full schema validation.
- No live Business Profile, Maps, API, network or paid data calls; no publishing or profile changes.
- Invite genuine customers neutrally and consistently when appropriate; no incentives, review gating, fabricated reviews or automatic replies. Review any response for accuracy and privacy before approval.
- Service-area and home-based businesses require address privacy review; never publish an address merely to fill a schema field.
- Do not add self-serving Google review aggregateRating markup to the business own site as a rich-result recommendation.

Detailed checked observations and source/date/scope evidence are in report.json.
