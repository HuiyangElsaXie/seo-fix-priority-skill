# Repair queue — fictional demonstration

Scope: three synthetic crawl rows; two simple checks. Not a full technical SEO audit.

## High: /templates returns HTTP 404
Evidence: fixture row 1, rule HTTP_ERROR. The brief labels this a lead page, so it deserves an early review. Actual traffic and revenue loss are unknown.
Owner: Web developer, with content-owner confirmation of intended destination.
Action: confirm whether the URL should exist. Restore it if appropriate, or select a genuinely relevant redirect. Do not redirect every missing page to the homepage.
Acceptance: recrawl the exact URL; verify intended status and destination; check links pointing to it. Status: not implemented or verified.

## No finding from these checks
/blog/notes: HTTP 200, indexable. This does not prove the page is indexed, fast, useful, or technically healthy.
/private-preview: intentionally private, HTTP 200, non-indexable. No indexing recommendation is made.

## Limits
No robots parsing, redirect-chain inspection, rendered HTML, schema, accessibility, Core Web Vitals, Search Console or server logs were inspected. Priority is a simple editorial rule based on supplied page purpose, not a Google severity score or measured business impact.
