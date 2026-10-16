# Fictional observation notes (N01–N06)
All observations and dates below are authored simulation inputs. No request was sent to a host.

- N01 / E02: simulated HTML extract has <meta name="robots" content="noindex,follow">. Indexability false is an explicit fixture observation, not inferred from HTTP 200. The brief wants organic acquisition here; verify production directives before changing anything.
- N02 / E06: simulated HTML canonical is /solutions/supplier-onboarding. Product naming overlap makes this possibly intentional. No content comparison, owner sign-off, selected canonical or index inclusion evidence exists.
- N03 / E07: simulated hop log: /platform → 301 /product → 301 /solutions/supplier-onboarding → 200. Seven inlinks to /platform are reported in this slice, but referring URL identities were not exported. Two redirects, three request URLs. /product is a hop-only observation, not a row in the 15-URL slice.
- N04 / E10: HTTP 200 and noindex come from a hypothetical supplied direct fetch; robots blocked comes from a separate hypothetical robots-rule evaluator for the same date. A robots-respecting crawler would not necessarily fetch that page. The synthetic merged export explicitly retains both signals. Internal preview is intentionally excluded; no access-control removal proposed.
- N05 / E11: pricing is from an older snapshot only. No October pricing check was supplied; this is not proof of an ongoing issue.
- N06 / E08 and E15: checklist retirement decision is missing; the campaign is known to be excluded but whether its 404 is the desired retirement response is not documented. Neither automatically warrants restoration or a redirect.
