# Local SEO: evidence collection, review signals and handoff

## What runs automatically

The local evidence module validates/imports supplied observations, rejects incompatible/stale records, compares normalized NAP/hours within a matched branch, checks scoped LocalBusiness fields and produces review-rating/count warnings with actions and acceptance checks. The six-dimension reporter can consume that evidence. Neither module signs into Google, retrieves live GBP reviews, measures Maps rankings, posts replies or edits listings.

## Read-only evidence workflow

1. Reuse authorized business context. Confirm whether real customer contact makes local visibility relevant; do not infer GBP eligibility from a city, personal address or portfolio. Record source/date and yes/no/unknown applicability. For a service-area business, do not publish a private home address to satisfy a schema suggestion.
2. Identify the exact branch: business/entity ID, branch ID, Google place ID when available, market, website and correct Google listing URL. A shared brand name is not enough. Conflicting place/branch identity stops that comparison.
3. Use a genuinely available, authorized public browser/search tool to view the correct listing, or a user-supplied dated export. Preserve source URL, capture timestamp, observation timestamp, scope, selected fields and coverage. If the listing cannot be read, record that limitation; do not fill a zero rating/count.
4. With an already connected and authorized GBP/Places capability, inspect its actual supported fields and permissions first. GBP review access requires OAuth authorization; Places has billing/field-mask and attribution requirements. This repository does not provision credentials, request new access or make paid API calls. When no such capability is available, use the runnable normalized JSON import route below.
5. Capture total aggregate rating/count separately from visible review samples. Record comparison peers only when market, category, maturity and dates are genuinely comparable. Do not infer all-review sentiment, prevalence or recent trends from selected snippets.
6. Collect public website NAP, hours and JSON-LD using the existing bounded collector or supplied source files. A reviewer maps the exact branch into normalized local input; the collector does not automatically bind a JSON-LD entity to a Google listing. Multiple directory observations may be supplied, but the script does not discover every directory.
7. Run the local checks and integrate into the six-dimension report. Review warnings against authoritative business information before recommending an edit. Decide priority from service/customer impact, evidence confidence, business goal and effort; thresholds alone do not create an urgent SEO task.
8. Deliver source-linked warnings, rejected evidence and unknowns alongside recommended verification/actions. Preserve original input. No action is performed on the website or Business Profile.

## Official evidence rules checked 2026-10-16

- [Google review guidance](https://support.google.com/business/answer/3474122?hl=en): seek genuine customer feedback, use a review link/QR code where appropriate, respond helpfully and protect privacy. Do not offer incentives, condition benefits on reviews, filter requests to only happy customers, fake reviews or pressure removal of negative feedback. Prioritize service improvement and neutral invitations; draft replies need human approval.
- [GBP reviews.list](https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list): a verified location's authorized endpoint supplies averageRating, totalReviewCount and paginated review records. A single page of reviews is not the entire dataset.
- [Places fields](https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places): rating and userRatingCount are aggregate fields; reviews contains at most five relevance-ranked entries. Their dates cannot establish a recent overall trend. businessStatus describes operating state, not proof of GBP ownership or verification.
- [Place Details requirements](https://developers.google.com/maps/documentation/places/web-service/place-details): fields are explicitly selected, with billing and attribution obligations. API availability in documentation is not an active integration.
- [Business representation](https://support.google.com/business/answer/3038177?hl=en): review the applicable eligibility/location/service-area rules before recommending a profile. Do not declare a portfolio eligible by default.
- [LocalBusiness structured data](https://developers.google.com/search/docs/appearance/structured-data/local-business): Google documents name/address as required for the described rich-result feature and recommends other fields. A scoped field check is not full schema/Google validation or a display guarantee. Do not add self-serving aggregateRating from Google reviews to the business's own schema as a promised rich-result tactic.

## Interpretation limits

Low-rating, low-count, freshness and timing thresholds are configurable project heuristics, not Google ranking requirements. Zero explicitly observed total reviews can support a neutral review-collection suggestion; missing count means unknown. Low rating with very few reviews is a fragile reputation signal; more observations strengthen the supplied aggregate but do not independently prove service failure. No peers means no competitive deficit claim. Comparable historical aggregates can describe a change in aggregate rating/count, not the sentiment of all recent reviews or causal impact.

NAP normalization is deliberately conservative: formatting differences should not become defects, while distinct street numbers, suites, country codes, extensions and branch identities must survive. Hours require comparable schedule/timezone/effective scope; holiday/regular schedules cannot be forced to match. Every proposed correction needs the authoritative current source.

## 中文使用边界

这套流程会分析已取得的商家证据并出具示警，不会自动登录 GBP、回复评论或修改资料。总评分、总评价数与可见样本分开；缺数据不填零。同品牌不同门店不能混比；电话/地址格式差异要先规范化。少评、低分阈值属于可调业务启发式，不是 Google 规则；没有可比同行或足够时间证据就不声称落后或趋势恶化。建议先改进真实服务、适当回复，再中性邀请真实顾客自愿评价，不能奖励换评价或只邀请满意顾客。

## Runnable commands (Python standard library only)

From repository root, select a new output directory/file. The examples below are entirely fictional and reserved-domain evidence, not real Google observations.

```sh
# Analyze a normalized supplied dataset.
python scripts/local_seo_evidence.py cases/local-evidence/substantial-low-rating.json --out /tmp/local-review-new

# Convert an already obtained Places JSON file, with explicit provenance/branch metadata.
python scripts/import_local_google_export.py --format places --raw cases/local-evidence/places-export.fictional.json --metadata cases/local-evidence/export-metadata.fictional.json --out /tmp/local-import-new.json

# Produce the actual six-section Markdown/JSON report with local action handoff.
python scripts/six_dimension_report.py cases/local-evidence/report-snapshot.fictional.json --context cases/local-evidence/report-context.fictional.json --local-evidence /tmp/local-import-new.json --out /tmp/six-section-local-new
```

The importer also accepts `--format gbp` for a supplied reviews.list response. It requires metadata.resource_name to match target.gbp_resource_name (the supplied accounts/.../locations/... binding). A reviews.list response by itself cannot establish which branch it came from. The Places importer requires raw `id` equal target.place_id. Neither association is independent verification of export authenticity.

Only aggregate raw fields are mapped: Places rating/userRatingCount or GBP averageRating/totalReviewCount. Review array length becomes visible_sample_count, never total_count. Raw review text and pagination tokens are not retained; GBP pagination presence is summarized. Unknown fields remain null. Metadata has an allowlist, excluding pasted credentials and review text from the converted output. Do not provide secrets in any input. Only submit export data you have rights/authorization to use and retain; apply provider terms, attribution and privacy requirements.

### Normalized schema

- Top level: schema_version `1.0`, as_of date, target, observations, optional config and peers.
- target: entity_id, branch_id, place_id, market. These are exact supplied identity keys, not inferred from names. If place identity is unknown, stop the Google comparison and report missing evidence; do not invent a place ID.
- Each observation: id plus matching entity/branch/place/market, source_kind (`website`, `google_business_profile`, `directory`; peers use `peer_profile`), source_url, captured_at, observed_at, coverage (`aggregate`, `snapshot`, `sample`). Dates or timezone-aware ISO timestamps are accepted.
- Optional nap: name/address/phone. Optional hours: timezone, regular, exceptions, effective_from/effective_to; regular/exceptions are structured objects. Only matching time and schedule scopes compare.
- google_reviews: rating (1–5 or null), total_count (nonnegative integer or null), visible_sample_count (integer or null). A zero count with a rating is contradictory and withheld.
- localbusiness: supplied JSON-LD node. Explicit LocalBusiness and a documented bounded common-subtype set are recognized; unsupported types are unassessed, not invalid by default. Required/recommended distinction is scoped to documented fields, not exhaustive schema validation.
- Optional peer context: category, comparison_group and a matching maturity_group or lifecycle. Same market and close observation dates are also required. Selection remains supplied, not a representative market benchmark.
- config defaults: freshness_days=30, max_pair_gap_days=1, low_rating_threshold=4.0, low_count_threshold=10. These are configurable review cues, not universal standards. Document why different thresholds fit the engagement.

The enriched route supersedes the old supplement.local comparison within the same report, avoiding duplicate raw-string mismatches. Existing legacy input still runs unchanged when enriched evidence is absent. Local applicability must be an attributed `yes` before interpretation; `unknown`/`no` does not become a review warning. A separate normalized local CLI assumes the caller already chose the local scope; use the six-dimension route for applicability gating.

## Google Maps on the website

The bounded collector inspects fetched HTML for Google Maps iframe embeds, Maps JavaScript loader/placeholder signals, directions links and location links. These are different features: a directions link is useful navigation but not an embedded interactive map; a JavaScript loader does not prove a rendered map works. No map URL is fetched, no script is executed and no short link is expanded by this check.

Maps evidence retains classifications, bounded source tags and explicit valid place IDs; original hosts/paths/queries are not returned. Credentials, API-key query values and arbitrary original URLs are not copied into Maps evidence. Similar-looking domains are not Google. Opaque embed `pb` data and unresolved short links do not establish the correct branch. An explicit mismatching destination place ID is a verification task, not automatic authorization to change a link.

A static HTML absence means only no supported static signal was observed: a map might appear after consent or JavaScript. Verify the actual intended visitor journey before proposing a change. For a confirmed customer-visit location, an accurate map or directions link can be an optional usability improvement. It is not a required SEO component or a claimed ranking factor. Personal portfolios, private-address service-area businesses and sites without a local visitor task should not receive a missing-map defect.

Official references checked 2026-10-16: [Maps embeds](https://developers.google.com/maps/documentation/embed/embedding-map), [Maps URLs](https://developers.google.com/maps/documentation/urls/get-started), [Maps JavaScript loading](https://developers.google.com/maps/documentation/javascript/load-maps-js-api). These explain supported formats, not evidence that an inspected site rendered or loaded them successfully. We do not create API keys or request Maps access to perform static inspection.

## Business applicability, not missing-feature penalties

A standalone/independent domain is not a business model. An independent local clinic can need local review, while a purely online publication may not. No online transactions means ecommerce checks can be N/A; a local shop does not acquire an ecommerce defect merely because it has no cart. Noncommercial portfolios/content sites do not automatically need local or commerce features; an explicitly stated local public-service purpose can still justify relevant local checks.

Reuse attributed business facts and record the decision. Missing or conflicting facts stay unknown, not N/A and not an error. Existing explicit applicability choices remain auditable; domain names, missing markup, missing map or missing checkout are not grounds to infer intended business functions. This tool has no additive SEO score and introduces no penalty for N/A dimensions.

### Applicability context contract

The optional `business_model` in the six-dimension context file carries `source`, `date`, `reason` and four `yes`/`no`/`unknown` answers: `commercial`, `local_customer_service`, `local_acquisition_goal`, `online_transactions`. Descriptive `website_purpose` can be portfolio/content/lead_generation/online_sales/other; `service_delivery`, `business_profile_status`, `address_privacy`, `branches` preserve context but do not independently unlock checks. Record uncertainty instead of guessing. Explicit `applicability` values take precedence, including explicit unknown.

Optional `map_visit_context` has `value` yes/no/unknown, `source`, `date`, `reason`, `site_kind`. A yes means an attributed actual public customer-visit task, not merely local SEO applicability. `personal_portfolio`, `service_area` and `private_address` suppress missing-map suggestions. Default remains unknown. The [fillable six-dimension template](../skills/seo-fix-priority-workflow/SIX-DIMENSION-CONTEXT.template.json) executes without complete answers; update as_of and source dates to the actual review date.

The reporter includes remaining scope questions; it does not conduct an interactive interview. The AI first reuses authorized current context, maps already-known facts and asks only missing/conflicting essentials. A source/date is provenance, not independently verified truth.
