"""Offline Google Maps HTML signals. No network, rendering or branch inference.

Only supplied HTML is inspected. URLs/HTML/API keys are never returned. A map
signal is not a verified working map; opaque pb payloads are never decoded.
"""
from html.parser import HTMLParser
from html import unescape
import re
from urllib.parse import parse_qs, parse_qsl, urlencode, urlsplit, urlunsplit

# Deliberately bounded: unlisted country domains remain unknown, not trusted.
GOOGLE_DOMAINS = frozenset(('google.com', 'google.co.uk', 'google.ca', 'google.com.au',
                            'google.de', 'google.fr', 'google.co.nz', 'google.co.jp',
                            'google.co.in', 'google.com.sg', 'google.com.hk'))
GOOGLE_HOSTS = GOOGLE_DOMAINS | frozenset('www.' + d for d in GOOGLE_DOMAINS)
SHORT_HOSTS = frozenset(('maps.app.goo.gl', 'goo.gl'))
LIMITATIONS = [
    'Static HTML signals only; rendering, interactivity, availability and consent behavior are not verified.',
    'JavaScript or consent-delayed maps may be absent from supplied HTML; absence is not proof of a missing map.',
    'Opaque pb payloads, coordinates and place names do not establish branch identity. Short links are not resolved.',
    'A map is optional user-experience support, not an automatic SEO defect or ranking requirement.',
    'Only explicitly allowlisted Google hosts and map paths are recognized; no network requests are made.',
]


def _place_id(value):
    # API-key-shaped strings are never retained, even in a misleading parameter.
    if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,256}', value) and 'AIza' not in value:
        return value
    return None


def _url_signal(raw, tag, attribute):
    if not raw:
        return None
    candidate = any(s in raw.lower() for s in ('google', 'goo.gl', 'maps/api'))
    try:
        p = urlsplit('https:' + raw if raw.startswith('//') else raw)
        if p.username is not None or p.password is not None:
            return {'classification': 'untrusted/unknown', 'reason': 'credential-bearing URL skipped'} if candidate else None
        if (p.scheme not in ('https', 'http') or not p.hostname or '\\' in raw
                or any(ord(c) < 33 for c in raw) or p.port not in (None, 80, 443)):
            return {'classification': 'untrusted/unknown', 'reason': 'unsupported or ambiguous URL'} if candidate else None
        host = p.hostname.lower()
        path = p.path
        if host in SHORT_HOSTS and (host != 'goo.gl' or path.startswith('/maps/')):
            return {'classification': 'untrusted/unknown', 'reason': 'short map URL unresolved'}
        web = (host in GOOGLE_HOSTS and (path == '/maps' or path.startswith('/maps/')))
        old = host == 'maps.google.com' and (path in ('', '/', '/maps') or path.startswith('/maps/'))
        js = host in ('maps.googleapis.com', 'maps.google.com') and path == '/maps/api/js'
        if not (web or old or js):
            return {'classification': 'untrusted/unknown', 'reason': 'unrecognized Google Maps host or path'} if candidate and ('map' in raw.lower()) else None
        q = parse_qs(p.query, keep_blank_values=True)
        embed = path == '/maps/embed' or path.startswith('/maps/embed/') or ((web or old) and path in ('', '/', '/maps') and q.get('output') == ['embed'])
        if js and tag == 'script':
            category = 'maps_js_signal'
        elif embed and tag == 'iframe' and attribute == 'src':
            category = 'embedded_map'
        elif embed and tag == 'iframe':
            category = 'maps_js_signal'
        elif tag == 'a' and (path == '/maps/dir' or path.startswith('/maps/dir/') or 'daddr' in q or q.get('map_action') == ['directions']):
            category = 'directions_link'
        elif tag == 'a' and not js:
            category = 'location_link'
        else:
            return {'classification': 'untrusted/unknown', 'reason': 'map URL in unsupported HTML context'}
        evidence = {'classification': category, 'source_tag': tag, 'source_attribute': attribute}
        ids = []
        # Only explicit destination/search IDs or place_id: values are comparable.
        for key in ('place_id', 'query_place_id', 'destination_place_id'):
            ids.extend(q.get(key, []))
        for key in ('q', 'query'):
            ids.extend(v[len('place_id:'):] for v in q.get(key, []) if v.startswith('place_id:'))
        ids = sorted(set(i for i in map(_place_id, ids) if i))
        if ids:
            evidence['explicit_place_ids'] = ids
        if 'pb' in q:
            evidence['opaque_pb_present'] = True
        if attribute != 'src' and tag == 'iframe':
            evidence['reason'] = 'deferred iframe placeholder; runtime loading unverified'
        return evidence
    except (ValueError, UnicodeError):
        return {'classification': 'untrusted/unknown', 'reason': 'malformed URL skipped'} if candidate else None


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.evidence = []
        self.script_parts = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            self.script_parts = []
        keys = {'iframe': ('src', 'data-src', 'data-lazy-src'), 'a': ('href',), 'script': ('src',)}.get(tag, ())
        for key in keys:
            item = _url_signal(attrs.get(key), tag, key)
            if item:
                self.evidence.append(item)
        if any('google-map' in (attrs.get(k) or '').lower() for k in ('id', 'class', 'data-provider')) or attrs.get('data-provider') == 'google':
            self.evidence.append({'classification': 'maps_js_signal', 'reason': 'Google map placeholder; runtime loading unverified'})

    def handle_data(self, data):
        if self.script_parts is not None:
            self.script_parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.script_parts is not None:
            script = ''.join(self.script_parts)
            if re.search(r'\bgoogle\s*\.\s*maps\s*\.|\bgoogle\s*\.\s*maps\s*\[', script) or ('maps/api/js' in script and 'google' in script):
                self.evidence.append({'classification': 'maps_js_signal', 'reason': 'inline Maps JavaScript reference; execution unverified'})
            self.script_parts = None


def analyze_google_maps(html, expected_place_id=None, customer_visit_confirmed=False, site_kind=None):
    """Return sanitized static evidence; applicability requires literal True.

    site_kind personal_portfolio/service_area/private_address suppresses missing-map
    suggestions even if inconsistent customer-visit flags are supplied.
    """
    if not isinstance(html, str):
        raise ValueError('html must be a string')
    parser = _Parser()
    parser.feed(html)
    parser.close()
    return review_google_maps({'schema_version': '1.0', 'evidence': parser.evidence},
                              expected_place_id, customer_visit_confirmed, site_kind)


def review_google_maps(result, expected_place_id=None, customer_visit_confirmed=False, site_kind=None):
    """Re-sanitize supplied structured evidence and evaluate explicit context.

    Supplied records are observations, never independent verification. Unknown or
    malformed input cannot create an absence recommendation. Arbitrary text,
    keys, URLs and claimed summary verdicts are discarded.
    """
    valid = isinstance(result, dict) and result.get('schema_version') == '1.0' and isinstance(result.get('evidence'), list)
    evidence = []
    categories = {'embedded_map', 'maps_js_signal', 'directions_link', 'location_link', 'untrusted/unknown'}
    for raw in result['evidence'] if valid else []:
        if not isinstance(raw, dict) or not isinstance(raw.get('classification'), str) or raw.get('classification') not in categories:
            valid = False
            continue
        category = raw['classification']
        item = {'classification': category}
        if raw.get('source_tag') in ('iframe', 'a', 'script'):
            item['source_tag'] = raw['source_tag']
        if raw.get('source_attribute') in ('src', 'href', 'data-src', 'data-lazy-src'):
            item['source_attribute'] = raw['source_attribute']
        ids = raw.get('explicit_place_ids', [])
        if category in ('embedded_map', 'directions_link', 'location_link') and isinstance(ids, list):
            ids = sorted(set(i for i in map(_place_id, ids) if i))
            if ids:
                item['explicit_place_ids'] = ids
        if raw.get('opaque_pb_present') is True:
            item['opaque_pb_present'] = True
        # Generic reasons reconstructed, never copied from untrusted input.
        if category == 'maps_js_signal':
            item['reason'] = 'JavaScript or deferred placeholder signal; execution and rendering unverified'
        elif category == 'untrusted/unknown':
            item['reason'] = 'Untrusted, malformed, credential-bearing, unsupported or unresolved map URL; no verification'
        evidence.append(item)
    if not valid:
        evidence.append({'classification': 'untrusted/unknown', 'reason': 'Missing or malformed supplied map evidence'})
    classes = sorted(set(x['classification'] for x in evidence)) or ['no_static_evidence']
    expected = _place_id(expected_place_id)
    ids = {i for x in evidence for i in x.get('explicit_place_ids', [])}
    comparisons = {i == expected for i in ids} if expected else set()
    branch = ('mixed' if len(comparisons) > 1 else 'match' if comparisons == {True}
              else 'mismatch' if comparisons == {False} else 'unknown')
    applicable = customer_visit_confirmed is True and site_kind not in ('personal_portfolio', 'service_area', 'private_address')
    recommendation = None
    if valid and applicable and classes == ['no_static_evidence']:
        recommendation = 'Optionally offer a map or directions link for confirmed customer visits, after verifying the public branch and address privacy.'
    return {'schema_version': '1.0', 'classifications': classes, 'evidence': evidence,
            'branch_status': branch, 'rendered_verified': False,
            'customer_visit_applicable': applicable, 'optional_recommendation': recommendation,
            'limitations': list(LIMITATIONS)}


def redact_google_maps_secrets(html):
    """Redact secrets only in map-related URL literals, including HTML entities.

    This is artifact hygiene, not an authentication-token scanner. Returns text
    and a changed flag so callers can accurately label redacted source artifacts.
    """
    def clean(match):
        value = match.group(0)
        lowered = value.lower()
        if not ('map' in lowered and ('google' in lowered or 'goo.gl' in lowered)):
            return value
        try:
            decoded = unescape(value)
            p = urlsplit('https:' + decoded if decoded.startswith('//') else decoded)
            if p.username is not None or p.password is not None:
                return 'about:blank#redacted-google-map-credential-url'
            pairs = parse_qsl(p.query, keep_blank_values=True)
            cleaned = []
            changed = False
            for key, val in pairs:
                if key.lower() in ('key', 'api_key', 'apikey', 'access_token', 'token', 'signature'):
                    cleaned.append((key, 'REDACTED'))
                    changed = True
                else:
                    safe = re.sub(r'AIza[A-Za-z0-9_-]+', 'REDACTED', val)
                    cleaned.append((key, safe))
                    changed = changed or safe != val
            if changed:
                return urlunsplit((p.scheme, p.netloc, p.path, urlencode(cleaned), p.fragment))
        except ValueError:
            return 'about:blank#redacted-google-map-malformed-url'
        return re.sub(r'AIza[A-Za-z0-9_-]+', 'REDACTED', value)
    sanitized = re.sub(r'(?:https?:)?//[^\s<>\"\x27]+', clean, html, flags=re.I)
    def clean_inline(match):
        script = match.group(0)
        if 'google' in script.lower() and ('maps' in script.lower()):
            return re.sub(r'AIza[A-Za-z0-9_-]+', 'REDACTED', script)
        return script
    sanitized = re.sub(r'<script\b[^>]*>.*?</script\s*>', clean_inline, sanitized, flags=re.I | re.S)
    return sanitized, sanitized != html
