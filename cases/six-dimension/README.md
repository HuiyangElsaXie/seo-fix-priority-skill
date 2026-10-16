# Six-dimension offline examples and input contract

All domains, entities, business statements and measurements in this folder are fictional. These fixtures demonstrate logic, not measured site performance. The reporter reads local JSON only, never makes a network request, never modifies a website and refuses an existing output directory. Optional exports are file adapters, not API integrations.

From the repository root:

```sh
python scripts/six_dimension_report.py cases/six-dimension/snapshot.json \
  --context cases/six-dimension/context.json \
  --supplement cases/six-dimension/supplement.json --out /tmp/new-six-dimension-report
python -m unittest discover -s tests -p 'test_six_dimension_report.py' -v
```

`example-report-current3/` is the current actual executed fictional report; earlier `example-report/`, `example-report-verified/` , `example-report-current/` and `example-report-current2/` runs are preserved as development evidence. Choose a new directory for each subsequent run; no overwrite flag exists. `report.json` holds all bounded checks/evidence and `report.md` is the readable summary.

## Snapshot

Use `scripts/collect_public_site.py`'s snapshot schema version `1.0`. The reporter accepts `collection`, `pages`, `robots`, `sitemaps`, `graph`, `errors` and uses:

- Page `url`, `status`, `fetch_state`, `fetched_at`, `content_type`, `parse_state`, `title`, `meta_description`, `h1`, `canonical`, `robots_meta`, `response_headers`, `internal_links`, `hreflang`, `jsonld`, `raw_artifact_path`.
- `canonical`: URL array; `hreflang`: `{lang,url}` array; `robots_meta`: `{name,content}` array; `internal_links`: URL array; `jsonld`: `{valid_json:true,value:object_or_array}` or `{valid_json:false,raw_excerpt:...}`.
- `collection.requested_url`, `final_url`, `finished_at` define origin and sample provenance. Page timestamps remain on finding evidence. Collection errors are surfaced for every section, not silently converted into successful checks.
- Metadata/content checks require `fetch_state:ok`, `parse_state:parsed` and an explicit HTML media type (`text/html` or `application/xhtml+xml`, optional charset allowed); unparsed empty fields are unknown, not missing-title findings.
- Unknown/unfetched target pages do not trigger missing-reciprocal-hreflang conclusions. Internal depth/inlinks use this HTML link sample only. No orphan or complete coverage claim follows.

## Optional context

`--context CONTEXT.json` accepts existing v0.3-style `business_context.answers` and `sources` for report level selection. An answer is `{value,status,source_id,evidence_locator}`; a known answer requires `status` confirmed/self_reported and a resolvable source. No assumptions unlock specificity. Missing industry gives `generic_framework`; known industry with incomplete essential context gives `industry_general`; full essential answers give `tailored`. This is compatible level selection, not a claim to re-run v0.3's entire validated intake or numeric priority mechanism. `triage.py` remains the separately supported v0.3 workflow.

Essential fields: industry, audience, geography, language, primary_objective, resources, constraints, specific_problem; conversion/retention/mixed additionally require conversion_definition, and mixed requires objective_tradeoff. Unknown problem or objective never blocks technical facts or useful general review.

New optional top-level `applicability` holds `local`, `ecommerce`, `international`, each `{value:"yes"|"no"|"unknown",reason,source,date}`. Yes/no require nonempty source/reason and ISO date. No is a business applicability decision, not a missing-data judgment. Omission yields unknown. See `portfolio-context.json` for an explicit N/A case. A city in a title or ecommerce career case does not establish applicability; observed Product/Offer markup is only a business-confirmation candidate.

## Optional supplemental exports

`--supplement SUPPLEMENT.json` may contain `cwv`, `backlinks`, `local`, `products`. Each is `{source:"description of actual supplied source",date:"YYYY-MM-DD",data:[records]}`. These provenance envelopes are required; rejected envelopes fail before output creation. Records outside the supported shapes are skipped with explicit unknowns, never fabricated. The source/date identify the export, while observed_at/window identify measurement time. Validate authenticity and relevance as part of agent review.

### cwv records

`{kind:"field",percentile:75,scope:"absolute URL or origin",scope_type:"url"|"origin",device:"mobile"|"desktop",window_start:"YYYY-MM-DD",window_end:"YYYY-MM-DD",metric:"LCP"|"INP"|"CLS",value:number,unit:"ms"|"score"}`.

LCP/INP require milliseconds; CLS requires score units. All fields are required, window must parse and be ordered, and lab/Lighthouse scores are rejected. Good thresholds used: LCP ≤2500 ms, INP ≤200 ms, CLS ≤0.1. Absence means unknown; one supplied metric does not establish passing all Core Web Vitals. The tool neither measures CWV nor guarantees ranking benefit.

### backlinks records

`{source_url,target_url,rel}`. Deduplicates supplied source/target/rel tuples and flags missing endpoints. Neither external link liveness nor backlink completeness is measured. Review the source export separately for mention context, reputation, independence and paid relationships. DA/DR, if supplied elsewhere, are never treated as Google authority.

### local records

`{entity_id,observed_at,reference_source,website:{name,address,phone,hours},reference:{name,address,phone,hours}}`.

The record explicitly asserts that website and reference observations belong to the same entity and effective date. `reference_source` identifies the Business Profile or other actual supplied snapshot. The program compares supplied paired values only; missing fields remain gaps, disagreement does not prove which side is wrong. No entity matching from names or addresses, no eligibility inference, no automatic Business Profile creation. Applicability must be yes before comparisons run.

### products records

`{product_id,variant_id,observed_at,reference_source,website:{price,currency,availability},reference:{price,currency,availability}}`.

The record explicitly asserts the same product, variant and effective date on both sides. Reference can be a supplied page Offer extraction or supplied feed export; it must be named. Normalize both sides to the same representation before use (for example price strings `"12.00"`, currency `"CAD"`, availability `"InStock"`); this adapter performs exact comparisons, not semantic coercion. Price comparison is withheld if currencies differ or are absent. No identity/variant/date means no comparison. No feed means feed review has not occurred. These checks never infer price from unrelated products or generic JSON-LD; human/agent review must verify identity and source fidelity.

## Interpretation and remaining work

The six sections separate applicability, bounded evidence status and semantic-review status. `checked` means specified machine checks executed, never that a dimension is SEO-approved. All semantic review remains pending until an agent follows the skill and records its assessment separately. All deterministic priorities currently remain qualitative `pending`: business impact/visibility intent, sourced effort and owner need review. There is no health score, E-E-A-T score, modeled traffic loss, ranking-penalty diagnosis or implied API connection.

Findings share stable root-cause IDs; product mismatch appears once, with on-page cross-reference, rather than counted twice. Metadata duplicates are candidates only. JSON-LD checks cover parsing/root/node shape and presence, not official rich-result validation. FAQPage markup is not a Google FAQ-rich-result opportunity: these results were removed May 7, 2026.

### Confidence and context provenance

Every section and finding separates reproducible input-rule classification from source truth (not independently verified) and business impact (unknown). These are scope labels, not estimated probabilities. `checked` means the specified deterministic checks executed; semantic and eligibility review remain pending even when paired comparison records are complete.

Context sources require nonempty description, kind (`fictional_fixture`, `supplied_export`, or `supplied_manual_check`) and valid `observed_at` YYYY-MM-DD no later than context `as_of` (defaults to execution date). Invalid source IDs are reported and cannot establish known answers or unlock tailored mode. Supplied valid dates establish provenance completeness, not authenticity or freshness.
