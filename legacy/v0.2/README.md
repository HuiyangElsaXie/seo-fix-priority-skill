# SEO Fix Priority Workflow

**Purpose: analyze data you provide and produce a reviewable SEO triage report.** Supply normalized crawl observations and business context; the helper analyzes those inputs, and the agent/editor prepares the handoff. There is no built-in website crawler, Search Console connection or independent verification of the supplied observations.

Report usefulness depends on the quality, completeness and scope of the supplied data. Missing evidence must remain explicit; outputs are proposals for human review, not proof that a page needs changing or that a live defect exists. This repository is a portfolio demonstration of analytical reasoning and reporting, not a representation of Huiyang's primary production workflow.

**Everyday/client use:** If a client supplies a permitted crawl export and page/business context, this workflow can help prepare a prioritized review report and developer handoff. Map inputs to the documented schema, check provenance and missing fields, and review conclusions before client delivery. Portfolio demonstration is not the only possible use; it does not turn the draft into a fully validated production service or settle the pending license for new contributions.

[中文说明](README.zh-CN.md)

**A transparent adaptation of [Snippet Digital's technical-seo-audit skill](https://github.com/Snippet-Digital-Agency/tech-seo-audit-skill/tree/8b5b5d5c776ec71a0d427bd6760dfeca058b404c), under the MIT license.** Upstream copyright: © 2026 Snippet Digital. The [exact skill snapshot](upstream/snippet-digital/SKILL.md), [original license](upstream/snippet-digital/LICENCE), [source lock](upstream/source-lock.json), and [adaptation map](ADAPTATION.md) are included. This is a narrower, materially modified workflow, not the original full audit skill, and is not endorsed by its authors.

Local original additions are **license-owner-pending**; see [license status](LICENSE-PROPOSAL.md). This project is intended as a noncommercial learning and professional portfolio demonstration. That intention does not add a noncommercial restriction to upstream MIT-licensed material.

## What it does

Turn supplied crawl evidence plus business context into an owner-ready repair/investigation queue. Useful for a marketer preparing an engineering sprint after a migration, reviewing acquisition pages, or sorting noisy export warnings before asking developers to act.

Input: an explicitly normalized JSON export slice, source dates/row locators, intended page visibility, business importance, objective and optional owner/effort estimates. Output: JSON queue with eight bounded checks, transparent score components, confidence, review gates, owners, proposed fixes, acceptance checks, suppressed findings and missing-signal coverage. The accompanying agent workflow produces a human handoff and review log.

The script does not import arbitrary CSV headers: use [INPUT-CONTRACT.md](INPUT-CONTRACT.md), preserve original evidence, and map fields explicitly. Python 3.10+; no dependencies or paid services.

## Run

```sh
python scripts/triage.py cases/fictional-harbor/input.v1.json > /tmp/seo-first-output.json
python -m unittest discover -s tests -v
```

For agent use, read [SKILL.md](skills/seo-fix-priority-workflow/SKILL.md) and the input contract first. Preserve outputs under new names when reviewing. A queue is a proposal, not permission to modify a site.

## What changed from upstream

- Preserved the supplied-crawl → business-context → impact/effort → actionable handoff sequence and the upstream 40/40/20 scoring formula.
- Narrowed ten audit categories to eight evidence-supported rules: HTTP errors, non-indexable pages, robots blocking flags, canonical differences, redirect chains, missing titles, depth and zero inlinks.
- Added explicit page intent, provenance, freshness, confidence, missing-data reporting, assigned owner, acceptance checks and investigation gates overriding high scores.
- Removed API/live crawl paths, automated platform guesses, full-health scoring, XLSX promises and unsupported outcome claims. Exact source is preserved separately, not executed.

See [ADAPTATION.md](ADAPTATION.md) for section-by-section lineage and rationale.

## Executed case and evidence

[Harbor fictional case](cases/fictional-harbor/) contains a business brief, raw supplied-style evidence, normalization, an actual agent-run first output, review and owner-ready handoff. It is a fictional offline case, not client work, a real website audit, an independent human review, or proof of SEO results. The raw observations and code are enough to reproduce the queue; the review documents the judgment beyond it.

[Evaluation rubric](evals/rubric.md) and tests check decision logic, input/output contracts, uncertainty gates, evidence links and upstream snapshot integrity. They do not establish ranking gains, traffic gains, or effectiveness on unseen websites. Earlier 2-rule/3-row v0.1 material is preserved in [legacy/v0.1](legacy/v0.1/) and original example paths; it is historical, not v0.2 validation.

## Limits

No live URLs fetched, paid calls, customer data, Search Console access, rendered HTML verification, Core Web Vitals, sitemap completeness, duplicate-content analysis or deployment. A canonical difference may be intentional; zero inlinks in a partial crawl does not prove an orphan. Even high confidence means only confidence in classification of supplied signals. It does not verify source truth, a live defect or ranking benefit. A 404 can be an intentional retirement. The 30-day freshness threshold, depth threshold and priority cutoffs are local heuristics. Missing fields are unassessed, not passed. The queue is URL-level and may contain related symptoms that a reviewer should consolidate before scheduling.

Before external release: resolve licensing for new contributions and complete [REVIEW_BEFORE_PUBLIC.md](REVIEW_BEFORE_PUBLIC.md).
