# Six-dimension SEO evidence review

Report level: industry_general
Business objective: unknown
Technical facts and interpretive judgments are separated. All semantic review remains pending.

## Technical
Applicability: yes. General website review dimension.
Evidence: partial (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 12; findings: 5.
Review: Confirm intended visibility, canonical choices, rendering and business-critical paths; observed directives do not prove Google index status.
- Unknown: Crawl/HTML sample does not prove index inclusion, rendered parity, complete internal graph or robots access for every crawler.
- Unknown: CWV checks apply only to supplied valid metric/scope/device/window records; no overall CWV pass is inferred.

## Onpage Content
Applicability: yes. General website review dimension.
Evidence: partial (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 3; findings: 5.
Review: Review reader task, accuracy, first-hand evidence, authorship and useful next steps in full content. Do not score E-E-A-T, keyword density or word count.
- Unknown: https://fictional.example/deleted: HTML parse not confirmed or HTML media type unavailable; metadata and content checks not assessed.
- Unknown: Full-content task satisfaction and factual accuracy need semantic review; excerpts/word counts cannot establish thin content.

## Offpage
Applicability: yes. General website review dimension.
Evidence: partial (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 1; findings: 0.
Review: Review relevance, independence, paid relationships and sample bias. DA/DR are third-party measures, not Google authority scores.
- Unknown: Supplied sample is not a complete backlink index or reputation assessment.

## Local
Applicability: yes. Fictional in-person shop confirmed by supplied brief.
Evidence: checked (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 1; findings: 1.
Review: Confirm real customer contact/service eligibility, branch identity and privacy before suggesting a Business Profile; a city/address alone establishes no eligibility.

## Ecommerce
Applicability: yes. Fictional site currently sells mugs.
Evidence: checked (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 2; findings: 1.
Review: Confirm current selling purpose, variants, purchase flow, delivery and returns; past ecommerce case studies do not make this site a shop.

## International
Applicability: yes. Fictional English and French variants are intentional.
Evidence: partial (bounded checks only); semantic review: pending.
Confidence: rule-based input classification; source truth unverified and business impact unknown.
Bounded checks: 3; findings: 1.
Review: Review actual language/market purpose, translation quality and regional requirements; single-language sites need no standalone missing-hreflang warning.
- Unknown: https://fictional.example/private: no HTML hreflang collected; check actual alternate strategy and other delivery methods.

## Deduplicated findings

### issue-4f63b549389e / onpage_content
- Subject: https://fictional.example/
- Technical fact: title is empty in collected HTML.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Review a descriptive field for the page purpose; absence is not proof of a ranking penalty.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-17e7e31e0b58

### issue-bb3319679a5e / onpage_content
- Subject: https://fictional.example/
- Technical fact: meta_description is empty in collected HTML.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Review a descriptive field for the page purpose; absence is not proof of a ranking penalty.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-17e7e31e0b58

### issue-25c023a35282 / technical
- Subject: https://fictional.example/
- Technical fact: JSON-LD block 1 has a parse error or non-object/non-array root.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Inspect raw JSON and relevant schema; use official validation separately where applicable.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-17e7e31e0b58

### issue-cbdc88d4e6c1 / onpage_content
- Subject: https://fictional.example/fr/
- Technical fact: meta_description is empty in collected HTML.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Review a descriptive field for the page purpose; absence is not proof of a ranking penalty.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-3c2e659c7faa

### issue-a1a8f98965ed / technical
- Subject: https://fictional.example/deleted
- Technical fact: Collected HTTP status 404.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Confirm URL lifecycle and intended audience; investigate service or approved replacement.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-5e04a41bed8b

### issue-301503fd0bb1 / technical
- Subject: https://fictional.example/private
- Technical fact: Observed canonical target(s): https://fictional.example/
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Confirm intended canonical and content equivalence; cross-page canonical can be intentional.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-59c793e20b11

### issue-e05bc57614ca / technical
- Subject: https://fictional.example/private
- Technical fact: Collected HTML or HTTP robots directive includes noindex.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Confirm intended exclusion before considering any directive change.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-59c793e20b11

### issue-10815e17eca9 / onpage_content
- Subject: https://fictional.example/private
- Technical fact: meta_description is empty in collected HTML.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Review a descriptive field for the page purpose; absence is not proof of a ranking penalty.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-59c793e20b11

### issue-3efd990c9dbe / technical
- Subject: https://fictional.example/|mobile|2026-10-15
- Technical fact: Supplied field p75 LCP = 3000 ms; above good threshold 2500.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Investigate experience using the same scope/device/window; do not promise ranking gains.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-3c077eaeea41

### issue-fa846f76ab6f / local
- Subject: fictional-store-1|2026-10-16
- Technical fact: Supplied phone differs: website='000-0000'; reference='000-0001'.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Confirm entity/variant, effective time and authoritative value before updating either source.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-35d5950d49f0

### issue-e1f671956c40 / ecommerce
- Subject: fictional-mug|blue|2026-10-16
- Technical fact: Supplied price differs: website='12.00'; reference='10.00'.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Confirm entity/variant, effective time and authoritative value before updating either source.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-b7125bc669ca

### issue-975c4796c099 / international
- Subject: https://fictional.example/|https://fictional.example/fr/
- Technical fact: Collected target HTML lacks a return reference to the source.
- Interpretation: Candidate requiring contextual review; no ranking or revenue effect established.
- Recommendation: Check intended cluster and all declaration methods before changing alternates.
- Priority: pending (provisional); impact/intent, effort and owner require confirmation.
- Evidence: e-de4d873a90fa

## Actionable handoff

Actionable investigation and conditional repair plans, not execution approval. Empty confirmed-fix and optional buckets do not mean healthy. Proposed roles are not assigned people. Business priority remains pending; investigation sequencing is evidence-based.

### confirmed_fix

No supported decisions in this bucket.

### needs_verification

#### task-issue-4f63b549389e
- Scope: onpage_content / https://fictional.example/
- Basis: title is empty in collected HTML.
- Proposed role: Content editor with SEO reviewer
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Page purpose and target reader confirmed; Editorial approval and template access
- Evidence: e-17e7e31e0b58
1. Inspect the title in full rendered pages and the template for every listed URL.
2. Document whether these pages serve distinct reader tasks or intentional duplicate/alternate purposes.
3. For pages needing differentiation, draft a truthful, purpose-specific title; retain intentional shared values when justified.
- Acceptance: Each scoped URL has an approved title or a documented reason for retaining/omitting it.
- Acceptance: Fresh HTML/rendered evidence matches the approved copy; no ranking or click-rate gain is assumed.

#### task-issue-bb3319679a5e
- Scope: onpage_content / https://fictional.example/
- Basis: meta_description is empty in collected HTML.
- Proposed role: Content editor with SEO reviewer
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Page purpose and target reader confirmed; Editorial approval and template access
- Evidence: e-17e7e31e0b58
1. Inspect the meta description in full rendered pages and the template for every listed URL.
2. Document whether these pages serve distinct reader tasks or intentional duplicate/alternate purposes.
3. For pages needing differentiation, draft a truthful, purpose-specific meta description; retain intentional shared values when justified.
- Acceptance: Each scoped URL has an approved meta description or a documented reason for retaining/omitting it.
- Acceptance: Fresh HTML/rendered evidence matches the approved copy; no ranking or click-rate gain is assumed.

#### task-issue-25c023a35282
- Scope: technical / https://fictional.example/
- Basis: JSON-LD block 1 has a parse error or non-object/non-array root.
- Proposed role: Technical SEO reviewer with web engineer
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Raw JSON-LD block and intended schema type; Template access and visible-content review
- Evidence: e-17e7e31e0b58
1. Locate the exact JSON-LD block in the saved raw HTML and reproduce the parsing/shape result.
2. Confirm the markup describes visible current content, then repair JSON syntax or node/type shape as needed.
3. Run a JSON parser and the relevant schema/official rich-result validator; record results and eligibility limits.
- Acceptance: Every changed block parses and has the intended object/array and node/type shapes.
- Acceptance: Attach validator output and content comparison; valid syntax alone does not establish eligibility.

#### task-issue-cbdc88d4e6c1
- Scope: onpage_content / https://fictional.example/fr/
- Basis: meta_description is empty in collected HTML.
- Proposed role: Content editor with SEO reviewer
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Page purpose and target reader confirmed; Editorial approval and template access
- Evidence: e-3c2e659c7faa
1. Inspect the meta description in full rendered pages and the template for every listed URL.
2. Document whether these pages serve distinct reader tasks or intentional duplicate/alternate purposes.
3. For pages needing differentiation, draft a truthful, purpose-specific meta description; retain intentional shared values when justified.
- Acceptance: Each scoped URL has an approved meta description or a documented reason for retaining/omitting it.
- Acceptance: Fresh HTML/rendered evidence matches the approved copy; no ranking or click-rate gain is assumed.

#### task-issue-a1a8f98965ed
- Scope: technical / https://fictional.example/deleted
- Basis: Collected HTTP status 404.
- Proposed role: Technical SEO reviewer with web engineer
- Why this next: Validate this observed HTTP error before dependent content changes; intended lifecycle and business impact remain unknown.
- Dependencies: URL lifecycle and intended destination confirmed by site owner; Access to route configuration and fresh response capture
- Evidence: e-5e04a41bed8b
1. Repeat the request and record URL, timestamp, status and redirect chain; compare the saved response.
2. Ask the site owner whether this URL should serve content, redirect or remain retired.
3. If unintended, repair the route/service or choose an approved equivalent redirect; if intentionally retired, retain the status and review internal links.
- Acceptance: A fresh request matches the documented intended status/destination.
- Acceptance: Any changed internal links resolve to the approved destination; attach before/after responses.

#### task-issue-301503fd0bb1
- Scope: technical / https://fictional.example/private
- Basis: Observed canonical target(s): https://fictional.example/
- Proposed role: Technical SEO reviewer with web engineer
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Documented canonical intent and content-equivalence review; HTML/header access for source and targets
- Evidence: e-59c793e20b11
1. Capture every HTML and HTTP canonical declaration and resolve each target.
2. Compare content and ask the owner to document the intended preferred URL; check rendering and redirects.
3. Only if declarations contradict that intent, align the template and related signals with the approved preferred URL.
- Acceptance: Record whether the existing canonical is intentional.
- Acceptance: If changed, one consistent intended canonical is present across the reviewed declarations; its target is reachable and equivalent.

#### task-issue-e05bc57614ca
- Scope: technical / https://fictional.example/private
- Basis: Collected HTML or HTTP robots directive includes noindex.
- Proposed role: Technical SEO reviewer with web engineer
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Explicit URL visibility intent; Access to rendered HTML, response headers and relevant template
- Evidence: e-59c793e20b11
1. Record the precise HTML meta or HTTP header containing noindex and inspect rendered output.
2. Confirm with the owner whether this URL is intended for search visibility or exclusion.
3. Retain deliberate exclusions; remove or correct directives only after an unintended exclusion is confirmed.
- Acceptance: The recorded directive matches documented visibility intent in a fresh response and rendered check.
- Acceptance: If visibility is intended, inspect Search Console separately; do not equate directive removal with indexing.

#### task-issue-10815e17eca9
- Scope: onpage_content / https://fictional.example/private
- Basis: meta_description is empty in collected HTML.
- Proposed role: Content editor with SEO reviewer
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Page purpose and target reader confirmed; Editorial approval and template access
- Evidence: e-59c793e20b11
1. Inspect the meta description in full rendered pages and the template for every listed URL.
2. Document whether these pages serve distinct reader tasks or intentional duplicate/alternate purposes.
3. For pages needing differentiation, draft a truthful, purpose-specific meta description; retain intentional shared values when justified.
- Acceptance: Each scoped URL has an approved meta description or a documented reason for retaining/omitting it.
- Acceptance: Fresh HTML/rendered evidence matches the approved copy; no ranking or click-rate gain is assumed.

#### task-issue-3efd990c9dbe
- Scope: technical / https://fictional.example/|mobile|2026-10-15
- Basis: Supplied field p75 LCP = 3000 ms; above good threshold 2500.
- Proposed role: Technical SEO reviewer with web engineer
- Why this next: Investigate this supplied field threshold exceedance using comparable scope/device data; business urgency is not established.
- Dependencies: Valid field export with scope/device/window; Performance trace access and a comparable follow-up field window
- Evidence: e-3c077eaeea41
1. Verify the field export scope, device, p75 and observation window; distinguish URL from origin aggregation.
2. Trace LCP element discovery, server timing and resource loading.
3. Test a targeted change against a reproducible diagnostic case, then collect a comparable post-change field window.
- Acceptance: Record before/after LCP for the same scope/device; target p75 <= 2500 ms.
- Acceptance: Keep the outcome unresolved until a comparable field window is available; lab improvements alone do not close it.

#### task-issue-fa846f76ab6f
- Scope: local / fictional-store-1|2026-10-16
- Basis: Supplied phone differs: website='000-0000'; reference='000-0001'.
- Proposed role: Local operations manager
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Matching identity, effective time and authoritative value; Operations approval and access to the affected source
- Evidence: e-35d5950d49f0
1. Recheck paired phone values for the exact entity or product variant and effective timestamp.
2. Identify the authoritative current source, including currency or branch context where relevant.
3. Correct only the source proven stale or incorrect; record intentional differences rather than forcing agreement.
- Acceptance: Fresh paired phone evidence matches the authoritative value for the same identity/time, or the intentional difference is documented.
- Acceptance: For price, compare only identical currencies and variants; attach both observations.

#### task-issue-e1f671956c40
- Scope: ecommerce / fictional-mug|blue|2026-10-16
- Basis: Supplied price differs: website='12.00'; reference='10.00'.
- Proposed role: Catalog operations manager with web engineer
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Matching identity, effective time and authoritative value; Operations approval and access to the affected source
- Evidence: e-b7125bc669ca
1. Recheck paired price values for the exact entity or product variant and effective timestamp.
2. Identify the authoritative current source, including currency or branch context where relevant.
3. Correct only the source proven stale or incorrect; record intentional differences rather than forcing agreement.
- Acceptance: Fresh paired price evidence matches the authoritative value for the same identity/time, or the intentional difference is documented.
- Acceptance: For price, compare only identical currencies and variants; attach both observations.

#### task-issue-975c4796c099
- Scope: international / https://fictional.example/|https://fictional.example/fr/
- Basis: Collected target HTML lacks a return reference to the source.
- Proposed role: Localization lead with technical SEO reviewer
- Why this next: Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.
- Dependencies: Confirmed alternate-market strategy and cluster inventory; Access to all declaration methods and target pages
- Evidence: e-de4d873a90fa
1. Document the intended language/region cluster and collect its HTML, HTTP header and sitemap declarations.
2. Check each intended member for self-reference, unique language mappings, reciprocal references and reachable targets.
3. If a mismatch remains across the complete strategy, update the approved cluster declarations consistently.
- Acceptance: Each intended cluster member has a consistent unique mapping, self-reference and reciprocal references across the chosen strategy.
- Acceptance: Record status and canonical checks for every target; missing sample pages remain unresolved, not failed.

#### task-281f15df68d3
- Scope: technical / Evidence investigation
- Basis: Crawl/HTML sample does not prove index inclusion, rendered parity, complete internal graph or robots access for every crawler.
- Proposed role: Technical SEO reviewer with web engineer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.technical.unknowns
1. Resolve this specific evidence gap: Crawl/HTML sample does not prove index inclusion, rendered parity, complete internal graph or robots access for every crawler.
2. Collect a dated, scoped source or manual check with a reproducible locator; record unavailable evidence explicitly.
3. Have the proposed reviewer interpret that evidence before proposing any site change.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-4b33fe9dc400
- Scope: technical / Evidence investigation
- Basis: CWV checks apply only to supplied valid metric/scope/device/window records; no overall CWV pass is inferred.
- Proposed role: Technical SEO reviewer with web engineer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.technical.unknowns
1. Resolve this specific evidence gap: CWV checks apply only to supplied valid metric/scope/device/window records; no overall CWV pass is inferred.
2. Collect a dated, scoped source or manual check with a reproducible locator; record unavailable evidence explicitly.
3. Have the proposed reviewer interpret that evidence before proposing any site change.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-b2f7fdc5e993
- Scope: onpage_content / Evidence investigation
- Basis: https://fictional.example/deleted: HTML parse not confirmed or HTML media type unavailable; metadata and content checks not assessed.
- Proposed role: Content editor with SEO reviewer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.onpage_content.unknowns
1. Resolve this specific evidence gap: https://fictional.example/deleted: HTML parse not confirmed or HTML media type unavailable; metadata and content checks not assessed.
2. Collect a dated, scoped source or manual check with a reproducible locator; record unavailable evidence explicitly.
3. Have the proposed reviewer interpret that evidence before proposing any site change.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-b47cd1f66509
- Scope: onpage_content / Evidence investigation
- Basis: Full-content task satisfaction and factual accuracy need semantic review; excerpts/word counts cannot establish thin content.
- Proposed role: Content editor with SEO reviewer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.onpage_content.unknowns
1. Resolve this specific evidence gap: Full-content task satisfaction and factual accuracy need semantic review; excerpts/word counts cannot establish thin content.
2. Collect a dated, scoped source or manual check with a reproducible locator; record unavailable evidence explicitly.
3. Have the proposed reviewer interpret that evidence before proposing any site change.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-6b5195eb6eff
- Scope: offpage / Evidence investigation
- Basis: Supplied sample is not a complete backlink index or reputation assessment.
- Proposed role: PR or partnerships reviewer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.offpage.unknowns
1. Resolve this specific evidence gap: Supplied sample is not a complete backlink index or reputation assessment.
2. Collect a dated, scoped source or manual check with a reproducible locator; record unavailable evidence explicitly.
3. Have the proposed reviewer interpret that evidence before proposing any site change.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-82e66296a1d1
- Scope: international / Evidence investigation
- Basis: https://fictional.example/private: no HTML hreflang collected; check actual alternate strategy and other delivery methods.
- Proposed role: Localization lead with technical SEO reviewer
- Why this next: Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.
- Dependencies: Access to the scoped source identified in the evidence gap; Reviewer availability
- Evidence: Evidence gap / supplied applicability decision; see sections.international.unknowns
1. Resolve this specific evidence gap: https://fictional.example/private: no HTML hreflang collected; check actual alternate strategy and other delivery methods.
2. Collect a dated, scoped source or manual check with a reproducible locator; record unavailable evidence explicitly.
3. Have the proposed reviewer interpret that evidence before proposing any site change.
- Acceptance: Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.
- Acceptance: Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.

#### task-business-context
- Scope: business_context / Missing essential context
- Basis: audience, geography, language, primary_objective, resources, constraints, specific_problem
- Proposed role: Business owner with SEO lead
- Why this next: Context gates business-specific ordering; it does not prevent reporting observed technical signals.
- Dependencies: Business owner input
- Evidence: Evidence gap / supplied applicability decision; see intake.missing_essential
1. Ask the business owner for each missing answer: audience, geography, language, primary_objective, resources, constraints, specific_problem
2. Record each answer with a dated source and evidence locator before tailoring recommendations.
- Acceptance: Every missing essential answer has a valid attributed source or is explicitly left unknown.
- Acceptance: Business prioritization remains provisional for unresolved answers.

### optional_improvement

No supported decisions in this bucket.

### keep_or_not_applicable

No supported decisions in this bucket.

## Boundaries
- No overall health/authority score, traffic loss, ranking penalty or ROI is calculated.
- Semantic review is pending; this deterministic script does not perform AI review.
- JSON-LD checks are not official rich-result validation. FAQ rich results were removed May 7, 2026; no FAQ rich-result benefit is promised.
- Priority is qualitative and pending business-impact/effort/owner evidence; technical severity is separate.

Detailed checked observations and source/date/scope evidence are in report.json.
