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

## Boundaries
- No overall health/authority score, traffic loss, ranking penalty or ROI is calculated.
- Semantic review is pending; this deterministic script does not perform AI review.
- JSON-LD checks are not official rich-result validation. FAQ rich results were removed May 7, 2026; no FAQ rich-result benefit is promised.
- Priority is qualitative and pending business-impact/effort/owner evidence; technical severity is separate.

Detailed checked observations and source/date/scope evidence are in report.json.
