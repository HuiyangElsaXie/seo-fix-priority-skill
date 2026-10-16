# Public collector contract

Run from the repository root:

```sh
python scripts/collect_public_site.py https://example.com/ --out /tmp/new-seo-evidence --max-pages 20
```

Python standard library only. No login, browser, JavaScript execution, paid API, remote writes, or package installation. Output must be a new or empty directory; a nonempty directory is rejected. The CLI permits 1–100 page records (default 20). Public reachability is checked at collection time; do not supply authenticated or signed URLs.

## Safety and scope

- Exact starting scheme and hostname only, default HTTP/HTTPS ports, no userinfo. Cross-origin redirects, including HTTP-to-HTTPS, are refused. Start with the site's final HTTPS URL.
- Resolve every hop; reject the whole DNS answer set if any address is not globally routable. Connect directly to a validated IP. HTTPS uses the original hostname for SNI and certificate verification; no second hostname lookup or proxy is used.
- Fetch robots.txt first. 404/410 permit crawling; 401/403 deny. Other errors or unavailable policy fail closed. Because stdlib robots matching cannot safely evaluate every RFC 9309 pattern, wildcard/end-anchor rules, nonempty Allow rules, and multiple matching groups fail closed. This is a deliberate coverage limitation, not evidence that the site is broken.
- Crawl-delay is honored conservatively across groups. Invalid delays or delays above 30 seconds stop collection. HTTP 429 halts all further requests without retries. No concurrency; request spacing is at least one second by default.
- Defaults: 60 total HTTP requests including robots/sitemaps/redirects, 20 page records, link depth 3, 2 MB per response, 10-second per-request deadline, 300-second collection budget. DNS wait is bounded; timed-out resolution stops future requests. Transport has a socket shutdown timer and remaining-time read limits.
- At most five sitemap documents and 5,000 sitemap URLs are collected. Sitemap XML never loads external entities; DTD/entity declarations are rejected. Sitemap coverage is always explicitly incomplete.
- At most 5,000 links per page and 5,000 queued links are retained. JSON-LD is parsed as JSON only. Raw source artifacts are never executed. HTML extraction is static and best-effort, including unclosed/nested headings.

## Output schema (version 1.0)

`snapshot.json` contains:

- `collection`: UTC timestamps, requested/final starting URL, limits, actual request/page counts, limitations.
- `pages`: URL, requested/final URL, depth, HTTP `status` or null, `fetch_state`, timestamp, content type, selected response headers, title, meta description, `h1` array, canonical URL array, robots-meta objects, hreflang objects (`lang`, `url`), HTML language, link/internal-link URL arrays, `links_truncated`, JSON-LD records (`valid_json`, `value` or invalid excerpt), text excerpt, whitespace-token word count, relative raw artifact path, source attribution, parse state/error when applicable.
- `robots`: requested/final URL, HTTP status when observed, assessment (`parsed`, `allow_all`, `deny_all`, `unknown`), raw source path, UTC timestamp, effective crawl delay/error.
- `sitemaps`: documents with timestamps/status/raw source paths, discovered in-scope URL sample, errors, `complete: false`, sampled URL count.
- `graph`: `sample_only: true`, fetched page count, observed internal edges, maximum observed depth, `orphan_assessment: unknown`.
- `errors`: collection-level limitations or stop reasons.

`fetch_state: http_error` means an actual non-2xx response was received. Network, DNS, size, unsupported redirect, and other transport failures have `status: null` and `fetch_state: unknown`; robots/rate-limit suppression is `blocked`. Non-HTML responses retain HTTP evidence without invented HTML fields. A parse error after receipt may retain its observed status. Empty extracted fields must not be interpreted as confirmed SEO defects unless an HTML parse succeeded.

Relative paths refer to the evidence output directory, which contains `raw/` and `snapshot.json`. The output directory may contain copyrighted text or unexpected personal information from public pages; review before sharing or committing evidence.

## Interpretation limits

This evidence does not verify JavaScript-rendered content, Core Web Vitals, actual Google indexing, rankings, backlinks, analytics, or conversions. It cannot determine sitewide orphan pages, full sitemap coverage, or all broken links. Word count is a whitespace-token heuristic, not language-aware content-quality scoring. Recorded fetch time and runtime are not performance scores. Unavailable evidence should become `unknown` or an explicit follow-up requirement in downstream reports.
