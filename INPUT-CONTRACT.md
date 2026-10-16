# Input contract v0.3

Python 3.10+, standard library only. `python scripts/triage.py INPUT.json` reads UTF-8 supplied JSON and prints JSON; invalid input exits 2. No URL is fetched. Preserve outputs using new filenames.

Top-level: `schema_version: "0.3"`, ISO `as_of`, `business_context`, `sources`, `rows`. Legacy `0.2` inputs are accepted for diagnostic migration only: absent new context gates business priority. Frozen original v0.2 script/tests are in legacy/v0.2; existing executed cases and reports remain untouched.

## Structured business answers
`business_context.objective`: nonempty human summary; use `unknown` when unavailable. `owners`: optional role→nonempty name/team map for engineering/seo/content. `answers`: optional object, keyed by these fields:

industry, audience, geography, language, positioning, brand_lifecycle, product_lifecycle, primary_objective, conversion_definition, objective_tradeoff, resources, constraints, specific_problem, site_age, migration_history.

Each answer is `{ "value": "text", "status": "self_reported", "source_id": "brief", "evidence_locator": "brief.md:section" }`.
- status: confirmed / self_reported / assumption / unknown. Confirmed means asserted supported by supplied evidence, never independently verified by this helper.
- confirmed and self_reported require a known source and nonempty locator. Assumptions require text but cannot unlock priority. Unknown requires null/empty value. Missing fields mean unknown.
- primary_objective values: awareness / consideration / conversion / retention / mixed / other. Conversion, retention and mixed require conversion_definition for tailored mode.
- Tailored essentials: industry, audience, geography, language, primary_objective, resources, constraints, specific_problem. The source-backed brand/competitive positioning, brand lifecycle, product lifecycle, site age and migrations remain contextual follow-up questions, not automatic impact multipliers. Do not force an enormous interview to provide initial reference value.
- industry_general: industry supplied, one or more essentials missing/assumed. generic_framework: industry missing/assumed. A specific problem is optional for receiving a report, mandatory for claiming the report is tailored.

## Evidence and rows
`sources`: nonempty ID→object map. Each source needs kind (fictional_fixture / supplied_export / supplied_manual_check), nonempty description including scope/provenance, ISO observed_at no later than as_of. User answers may be a supplied_manual_check with a brief locator; fictional answers use fictional_fixture.

`rows`: array with unique exact absolute HTTP(S) url without credentials; source_id; evidence_locator; integer status 100–599; intent index/exclude/unknown; importance critical/supporting/low/unknown.

Optional signals: indexable / robots_blocked boolean or null; canonical absolute URL or empty/null; title string or null; depth / inlinks / redirect_hops nonnegative integer or null; effort integer 1–10. Missing measurements are not zero. No string-number coercion. Indexability must be supplied, not inferred from HTTP status.

New per-row structured answers: business_impact (why this page matters to the stated goal), visibility_reason (including deliberate noindex), canonical_intent (when a canonical differs). Use the same answer object. A business score requires source-backed business_impact and visibility_reason, known importance/index intent, supplied effort, assigned role owner, tailored essentials and fresh evidence; other rule gates can still block it. Canonical differences always require manual corroboration even when intended.

URL deduplication is exact and requires explicit reconciliation. Canonical comparison ONLY treats the same scheme/authority/query/fragment with empty root path versus `/` as equivalent. Non-root trailing slashes, query parameters, fragments, ports, host spelling and schemes are not silently normalized.

## Output and limits
Output v0.3 includes intake mode, supplied context, missing essentials, adaptive unanswered context/page questions, counts, queue, suppressed observations and coverage_gaps. Queue includes technical_severity separately from business_urgency, numeric score only when every gate passes (otherwise null), transparent score_inputs, source/locator/age, attributed page rationale, owner, proposed fix, verification and proposed-not-implemented status.

A source-backed context answer is still a supplied claim. Scores are local heuristics, not measured loss. Freshness uses the local 30-day window. Missing owners/effort block business ranking, not diagnosis. No direct CSV import or collector; explicitly map headers and preserve originals. For the adaptive conversational flow and Chinese explanation see INTAKE.md.

For mixed goals, supply source-backed objective_tradeoff naming the primary goal and tradeoff; unresolved mixed priorities keep the report general and scores withheld. Consideration/evaluation uses primary_objective=consideration; name the evaluation behavior or success signal in the objective summary.
混合目标须说明主次与取舍（objective_tradeoff）；未解决的目标冲突不能解锁业务排序。考虑/评估目标使用 consideration，并说明评估行为或成功指标。
