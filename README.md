# SEO Review and Fix Priority Workflow

**Give it a website URL to collect a bounded public sample and produce an evidence-linked six-dimension SEO review, or supply your own crawl data for repair triage.** The report separates observed facts, missing evidence, applicability and review tasks. It does not promise complete verification from a URL.

## Start in one minute

[Example action report](cases/actionable-handoff/run-06-freeze/report.md) · [Synthetic inputs and retained run history](cases/actionable-handoff/README.md) · [Four map/applicability cases](cases/google-maps/REVIEW.md)

These are existing fictional outputs, not a live audit of your URL. The report separates fixes asserted by a supplied scoped review, verification tasks, optional improvements and keep decisions.

| What you have / route | Smallest useful next step | Expected result and limit |
|---|---|---|
| Only a website URL; Codex/AI conversation | Read [the skill](skills/seo-fix-priority-workflow/SKILL.md), supply the URL, site purpose, audience and important pages. Ask for a bounded six-dimension review and evidence gaps. | With actual authorized shell/network tools, use the public collector. Without them, supply page text or exports; do not claim collection was run. |
| Existing crawl/snapshot or supplemental data; Codex/AI | Supply permitted dated files and intended page behavior. Use [the fixture/schema guide](cases/six-dimension/README.md) for mapping. | AI/reviewer interprets findings and applicability; arbitrary CSV columns are not imported automatically. |
| Python with only a URL | Follow [the URL collection commands](#use-python-directly), then analyze the saved snapshot. | Collection makes bounded public HTTP requests; this is the network step, not an offline or JavaScript-rendered audit. |
| Python offline with saved evidence | Run the six-dimension reporter on the documented snapshot schema, or use normalized data with [legacy triage](INPUT-CONTRACT.md). Use new output paths. | Produces a report/queue from supplied evidence. Missing evidence and semantic judgments remain explicit; no automatic account or search-data access. |

Example request: “Review this URL for the supplied business purpose. Separate observed facts, verification tasks and scoped fixes; show sources and what remains uninspected. Do not modify the site.”

AI execution depends on host tools and permissions; no untested cross-host compatibility is promised. Historical test logs below remain evidence of their recorded runs, not a new regression run for this documentation update.

[中文说明](README.zh-CN.md) · [Agent skill](skills/seo-fix-priority-workflow/SKILL.md) · [Fillable bilingual questionnaire](skills/seo-fix-priority-workflow/QUESTIONNAIRE.md) · [Six-dimension method and tools](docs/SIX-DIMENSION-METHOD.md)

**Adapted from [Snippet Digital's MIT technical-seo-audit skill](https://github.com/Snippet-Digital-Agency/tech-seo-audit-skill/tree/8b5b5d5c776ec71a0d427bd6760dfeca058b404c).** Copyright © 2026 Snippet Digital. The [exact upstream skill](upstream/snippet-digital/SKILL.md), [full original MIT license](upstream/snippet-digital/LICENCE), [source lock](upstream/source-lock.json) and [specific changes](ADAPTATION.md) remain included. New public collection/report code is locally authored; it is not an upstream crawler or an endorsement by its authors. [New-contribution licensing remains owner-pending](LICENSE-PROPOSAL.md).

Maintained for personal use and continuously updated. This purpose does not restrict upstream MIT rights. With permitted inputs and human review, the workflow can support an SEO report or developer handoff; it is not a validated full-service SEO platform.

For purpose/applicability questions and runnable JSON, see [the intake](skills/seo-fix-priority-workflow/QUESTIONNAIRE.md) and [six-dimension context template](skills/seo-fix-priority-workflow/SIX-DIMENSION-CONTEXT.template.json). AI reuses available context first; CLI users edit JSON and pass --context. Noncommercial/online-only/local-store scenarios are gated by actual services and transactions, not missing features.

## Local SEO evidence and review warnings

Local checks now use supplied branch-matched evidence for NAP/hours, scoped LocalBusiness fields and Google aggregate rating/review-count signals. Missing counts remain unknown; an observed zero can trigger a neutral invitation suggestion. Low ratings and limited review counts are assessed with configurable, explicitly non-Google thresholds, evidence freshness, sample size and available comparable context. Findings include evidence, uncertainty, actions and acceptance checks.

Read the [collection/import workflow and official sources](docs/LOCAL-SEO-EVIDENCE.md). No live GBP/Places account connection, paid request, review reply or listing change is included. Public browser evidence or authorized exports must be acquired separately, then imported; visible review samples never replace total counts or establish population trends.

## What the final report gives you (v0.5)

The actionable handoff separates **confirmed fixes, specific verification tasks, optional improvements and keep/not-applicable decisions**. Every action includes evidence, a reason for its sequence, concrete steps, a proposed role, dependencies and acceptance checks. Technical signals do not automatically become confirmed defects. The final generated report and the analyst's test commentary are separate deliverables.

Default rule findings remain investigation candidates until evidence and a documented review establish intended behavior. Unknown business impact never becomes invented urgency. Even when no rule fires, the report explains scoped keep decisions and concrete checks for missing evidence instead of claiming a healthy site. See [actionable-report policy](docs/ACTIONABLE-HANDOFF.md) and [synthetic truthfulness tests](cases/actionable-handoff/).

## Concrete uses

- **New portfolio or small business site:** supply its URL, audience and business goal. Receive sampled technical/content observations and a six-section report showing which specialist dimensions apply. A local address or ecommerce case study does not automatically make a site a local business or store.
- **Client already has data:** supply normalized crawl observations, intended visibility and business context. Receive a proposed repair/investigation queue with evidence, owner and acceptance checks. The offline helper does not import arbitrary CSV columns automatically.
- **An actual store or multilingual service:** supply the URL plus explicit applicability and dated product/feed, language-market or backlink evidence where available. The report checks supported comparisons and explains what still needs account access or manual verification.

## What runs, and what still needs review

1. `collect_public_site.py` makes bounded read-only public HTTP requests: robots policy, HTML metadata/text, canonical/hreflang, JSON-LD, sitemap samples and observed internal links. It does not render JavaScript or log in.
2. `six_dimension_report.py` analyzes that snapshot offline and emits `report.json` and `report.md` with Technical, On-page/Content, Off-page, Local, Ecommerce and International sections. Six sections are a coverage framework, not six automatically passed audits. Supplied optional evidence can expand checks; absent evidence remains explicit.
3. The agent/reviewer assesses intent, content usefulness, eligibility, deliberate exclusions and proposed actions. Machine output leaves semantic review pending. The reviewer records corrections without replacing the original output; the report can incorporate validated, explicit review decisions while identifying them as supplied assertions.
4. Existing `triage.py` remains the supplied-data, eight-rule repair-queue mode. Its conditional 40/40/20 scoring is not a score for the six-dimension report or a Google ranking score.

Python 3.10+, standard library only. No paid API, installed SEO suite, account connection, posting or deployment.

## Use through an AI conversation

Load [SKILL.md](skills/seo-fix-priority-workflow/SKILL.md), provide the URL or evidence and your brief. The agent first reuses only actually accessible, authorized memory/current chat/supplied documents, briefly states the business, audience, objective and sources being used, and asks only missing, conflicting or time-sensitive essentials. It does not assume global ChatGPT history access. Adequate context permits the requested read-only analysis without mandatory reconfirmation. Memory cannot replace crawl/GSC/field-performance measurements or grant permissions.

The [questionnaire](skills/seo-fix-priority-workflow/QUESTIONNAIRE.md) and [canonical intake](INTAKE.md) cover industry, market/language, positioning, lifecycle, objective/conversion, resources and important pages. Additional applicability questions determine whether local customer contact, live product sales or language/region variants exist. Unknown is a valid answer. Never store personal/client memory in this repository or its templates.

If a concrete problem/objective is unavailable, an **industry-general report still provides orientation**, conditional checks and useful next questions. Without industry, it becomes a generic framework with any observed technical facts. Neither mode invents demand, industry benchmarks, business urgency or ROI. The three report levels are `tailored`, `industry_general`, and `generic_framework`.

## Use Python directly

Edit input JSON, not script code. The CLIs are noninteractive: they do not ask questions in a terminal or automatically import a completed Markdown questionnaire. An agent/person maps answers to the documented fields. Choose a new output directory; preserve earlier runs.

```sh
# URL-first public sample. Use an output folder outside the repository.
python scripts/collect_public_site.py https://example.com --out /tmp/seo-public-new-run --max-pages 20
python scripts/six_dimension_report.py /tmp/seo-public-new-run/snapshot.json --out /tmp/seo-report-new-run

# Optional context and supplied supplemental evidence: exact schemas and fixtures below.
python scripts/six_dimension_report.py cases/six-dimension/snapshot.json --out /tmp/seo-fictional-new-run

# Existing supplied-data repair triage; JSON template contains no invented observations.
python scripts/triage.py skills/seo-fix-priority-workflow/INPUT.template.json > /tmp/seo-empty-template-output.json
# Optional explicit review: see docs/ACTIONABLE-HANDOFF.md for schema and two-pass usage.
python -m unittest discover -s tests -v
```

See [six-dimension fixture/schema guide](cases/six-dimension/README.md) for actual filenames and optional `--context`/`--supplement` inputs. See [INPUT-CONTRACT.md](INPUT-CONTRACT.md) for legacy normalized crawl inputs. Empty or missing evidence does not demonstrate site health. The provided-data template automatically yields generic mode, next intake questions and an empty queue.

## Evidence and limitations

The collector is bounded by origin, robots policy, request/page/size/time budgets. A sample cannot establish complete sitemap coverage, index status, all backlinks, actual Google-selected canonical, rendered content, conversions or field Core Web Vitals. Errors/blocks are recorded as collection gaps, not automatic site defects. No guessed values fill missing data. Robots compliance does not imply permission to access private data.

No automatic Business Profile eligibility claim, DA-based authority guarantee, numeric E-E-A-T score, ranking benefit from meta descriptions, or ranking penalty from bounce/social metrics. CWV means LCP/INP/CLS, with actual field evidence kept distinct from lab observations. FAQ rich results are no longer shown in Google Search as of May 7, 2026; adding FAQ markup is not offered as a rich-result opportunity. [Official references](docs/SIX-DIMENSION-METHOD.md#official-reference-checks).

[Original executed Harbor case](cases/fictional-harbor/), [business-context cases](cases/fictional-context-intake/HANDOFF.md) and [six-dimension fixtures](cases/six-dimension/) are disclosed fictional tests, not client results or independent human approval. Historic v0.1/v0.2 evidence remains preserved. Tests establish bounded behavior, not ranking, traffic or revenue improvement.

The owner has authorized this clean public snapshot; see [publication provenance](PUBLICATION.md) and the retained [review checklist](REVIEW_BEFORE_PUBLIC.md). New-contribution licensing remains pending and public visibility grants no new license. Real audit inputs, raw pages and client context belong in separately authorized private working storage.

Maps and purpose intake: [four executed fictional report cases and independent review](cases/google-maps/REVIEW.md). The full regression suite passes 228 tests; these checks do not verify live Google listing access or browser rendering.
