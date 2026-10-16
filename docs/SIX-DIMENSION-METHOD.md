# Six-dimension method, tool coverage and review

This is a project-specific, overlapping report framework, not Google's universal taxonomy or a ranking-weight model. A URL-first run consists of public collector → dated snapshot/raw evidence → offline report → separately recorded agent/human semantic review. Existing supplied-data triage is a separate compatible route. All real audit artifacts stay outside the repository.

## Scope and inputs

| Dimension | Public URL input checks actually implemented | Optional supplied evidence / interpretation | Missing and applicability handling |
|---|---|---|---|
| Technical | Observed HTTP status; robots access signal for collector; canonical/noindex review; JSON-LD JSON shape; sampled internal graph | Real field p75 LCP/INP/CLS records with scope/device/window/unit; verify intended visibility, rendering and service lifecycle | Actual Google indexing, selected canonical, full graph and field CWV unknown without evidence. Zero sampled inlinks does not prove orphan. |
| On-page/content | Collected title/description/H1; exact duplicate title/description in sample | AI/human reads captured text and checks reader task, factual support, first-hand proof, clarity and next step | No automatic quality/E-E-A-T score, thin-content finding from word count, or description ranking penalty. Semantic review remains pending until performed. |
| Off-page | No automatic backlink discovery from an internal crawl | Count/deduplicate supplied source-target records; human reviews relevance, independence, paid relationships and sample bias | No export means unknown, not zero links. Link liveness and total coverage are not verified. No DA/DR guarantee. |
| Local | Public HTML contributes review material, not eligibility certification | Explicit applicability; compare supplied same-entity/date website vs reference name/address/phone/hours | Only if relevant customer-contact business; city/address alone insufficient. No GBP login, eligibility checker, map-ranking or review audit. |
| Ecommerce | Product/Offer presence is only an applicability candidate | Explicit current selling purpose; compare supplied same-product/variant/date price/currency/availability across website and reference | No cart/checkout crawling, feed connection or product-rich-result certification. Career project about ecommerce does not imply a current store. |
| International | Collected HTML hreflang; self-reference/conflicting mapping; reciprocity only where target HTML is collected | Explicit language/region applicability; human checks translation, actual equivalent content and target markets | Other origins, uncollected targets and header/sitemap alternate methods remain unknown. Single-language site need not have hreflang. |

Exact machine input: [collector schema](COLLECTOR-CONTRACT.md), [optional context/supplement contract and fictional examples](../cases/six-dimension/README.md). All optional measurements need source/date. A supplied record is not independently verified merely because it parses.

## Tool inventory

- Built in: Python standard-library public HTTP collector (static HTML; strict same scheme/host; robots and budgets), offline six-dimension JSON/Markdown reporter, existing normalized-export triage helper.
- Provided-data adapters: explicit JSON envelopes for field CWV, backlink records, local entity comparisons and product/variant comparisons. These are data contracts, not API integrations or automatic CSV imports.
- Optional outside evidence, not bundled/invoked: authorized Search Console exports for queries/indexing; field performance exports; a suitably licensed backlink export; permitted Business Profile data; Merchant Center/feed observations. Do not imply these accounts or tools were used without actual records.
- Manual/agent layer: business-intent and semantic content review, applicability, correction log and final handoff. No built-in LLM API call; an agent can execute the skill, while Python alone leaves review pending.

Start with final HTTPS URL: cross-scheme/host redirects are refused. Some valid complex robots policies are conservatively unsupported and stop collection. A robots or transport stop is a limitation, not an SEO failure. See collector contract for exact limits; never bypass it to make a report look complete.

## Report and prioritization contract

Every dimension carries applicability (`yes`, `no`, `unknown`) separately from evidence status (`checked`, `partial`, `not_assessed`). `checked` means the listed bounded checks ran, not that the dimension is healthy or complete. Explicit no requires supplied business rationale/source/date; absent data cannot turn into N/A.

Findings retain observation, interpretive caveat, source/date/scope evidence, root-cause ID, related dimensions and acceptance proposal. Repeated symptoms do not create duplicate business benefits. Version 0.5 adds concrete verification/repair plans and evidence-based sequencing reasons. Reviewed decisions can carry supplied business rationale; unknown impact or effort remains unknown. No overall SEO score or pseudo-precise ROI. See ACTIONABLE-HANDOFF.md for explicit review and four-bucket output. Technical severity and business urgency are different.

The intake reuses authorized current context before asking missing questions. Known answers are not re-asked. Industry-general reports remain useful orientation when the user cannot specify a concrete problem; unknown industry gives a generic framework plus any valid technical observations. These levels do not invent company-specific conclusions.

## Required review record

Preserve the machine report. Create a separate record with:
1. Run command, scope, UTC observation times, exact source files and report level.
2. Per-dimension applicability/coverage and what remains unknown.
3. Actual pages/content reviewed; supported observations and user-task fit, separated from hypotheses.
4. Accepted findings, corrections, deliberate exclusions and duplicate root causes.
5. Business-prioritized proposed actions or explicitly conditional investigations, owner/effort questions and verification criteria.
6. Reviewer identity/type (agent-authored or independent human); never fabricate approval, ranking changes or conversion effects.

## Official reference checks

Guidance checked on 2026-10-16. Recheck before changing rules or promising a feature.

- [Core Web Vitals](https://developers.google.com/search/docs/appearance/core-web-vitals): LCP, INP and CLS; actual field evidence and lab observations must remain separate. Good metrics do not guarantee top ranking.
- [Helpful content and E-E-A-T](https://developers.google.com/search/docs/fundamentals/creating-helpful-content): E-E-A-T is not a specific standalone ranking factor or numeric checklist score.
- [Snippets](https://developers.google.com/search/docs/appearance/snippet): snippets are generated from content and sometimes descriptions, may vary by query, and have no fixed character-limit rule. Do not promise ranking gain from description changes.
- [Search documentation updates](https://developers.google.com/search/updates): May 8, 2026 entry says FAQ rich results stopped appearing May 7; June 15 removed the documentation. Do not repeat obsolete health/government-only availability or promise FAQ rich-result benefits.
- [Business Profile eligibility](https://support.google.com/business/answer/13763036?hl=en): generally requires in-person customer contact, with defined exceptions. Do not mandate GBP for an online portfolio.
- [Localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions): hreflang addresses language/region alternatives, with self and return references; it is not mandatory for every site or a translation mechanism.
- [Product snippets](https://developers.google.com/search/docs/appearance/structured-data/product-snippet) and [Merchant price consistency](https://support.google.com/merchants/answer/6324371?hl=en-GB): product data must reflect the relevant real product/offer; markup is not a guarantee of a rich result.
- [Third-party SEO tools](https://developers.google.com/search/docs/fundamentals/third-party-seo), [ranking systems](https://developers.google.com/search/docs/appearance/ranking-systems-guide), [link spam](https://developers.google.com/search/docs/essentials/spam-policies#link-spam): tools lack internal ranking data; links require contextual assessment, not an external authority-score guarantee.
- [GA4 engagement/bounce](https://support.google.com/analytics/answer/12195621?hl=en-419), [GA vs Search Console](https://developers.google.com/search/docs/monitor-debug/google-analytics-search-console), [SEO starter guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide): engagement and social promotion may inform marketing review; no direct ranking score is calculated from bounce, likes or shares here.

## 与中文使用者相关的解释

六维度是报告结构，实际覆盖程度逐项说明。URL 自动采集仅包括可公开访问的有限样本；站外全量外链、GBP 后台、GSC、真实用户性能与成交数据不会凭空出现。未提供就是未知，不按失败扣分。技术观察可以在业务目标未知时保留，业务优先级则需要具体背景。

AI 对话先复用真正可访问且获准使用的上下文，概述已有判断再追问缺口；Python 只读取已填写 JSON，不自动读取记忆或提问。行业通用报告仍可提供方向，不能冒充企业诊断。人工/AI 语义复核要留下实际读过的页面、证据和修正记录；机器规则运行不等于已经完成语义复核。
