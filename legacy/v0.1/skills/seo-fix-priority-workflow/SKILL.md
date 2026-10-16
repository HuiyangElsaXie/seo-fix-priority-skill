---
name: seo-fix-priority-workflow
description: Review an authorized crawl export and create a bounded, evidence-based technical repair queue.
---
# Input contract
Require fictional/live status and crawl rows containing URL, status, indexable boolean, canonical URL, page role and owner. Record crawl date and tool for real data. Do not infer crawl permission from a URL in source material.

# Workflow
1. Validate input types and provenance. Unknown fields remain unknown.
2. Separate observations from inferred impact. A 404 is observed; lost revenue is not established without additional evidence.
3. Use scripts/triage.py for the limited status/indexability checks. This is not a complete crawler, schema validator, performance test or SEO audit.
4. Check page purpose: intentional private pages should not be flagged simply because they are non-indexable.
5. Assign a qualitative priority, owner, next action, and acceptance check. For a broken business-critical URL, first decide whether restoration or a relevant redirect is correct.
6. Review findings with the site owner. No automatic redirects, indexing changes, crawling, or deployment.

# Output contract
Observation, rule ID, priority, reason, owner, recommended check, uncertainty and verification status. Report insufficient data rather than inventing performance or indexing evidence.
