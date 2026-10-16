#!/usr/bin/env python3
"""Bounded, public-only, robots-aware static HTML evidence collector (stdlib only)."""
import argparse
import collections
import datetime as dt
import hashlib
import http.client
import ipaddress
import json
import re
import queue
import threading
import socket
import ssl
import time
import urllib.parse as up
import urllib.robotparser
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
try:
    from google_maps_evidence import analyze_google_maps, redact_google_maps_secrets
except ModuleNotFoundError:
    # Support importlib-based offline consumers without changing global sys.path.
    import importlib.util
    _maps_spec = importlib.util.spec_from_file_location('google_maps_evidence', Path(__file__).with_name('google_maps_evidence.py'))
    _maps_module = importlib.util.module_from_spec(_maps_spec)
    _maps_spec.loader.exec_module(_maps_module)
    analyze_google_maps = _maps_module.analyze_google_maps
    redact_google_maps_secrets = _maps_module.redact_google_maps_secrets

AGENT = 'PublicSEOCollector'
REDIRECTS = {301, 302, 303, 307, 308}


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


class CollectionError(Exception):
    pass


def normalize(url):
    p = up.urlsplit(url)
    if p.scheme.lower() not in ('http', 'https') or not p.hostname or p.username is not None or p.password is not None:
        raise CollectionError('Only public HTTP(S) URLs without credentials are allowed')
    try:
        port = p.port
    except ValueError as exc:
        raise CollectionError('Invalid port') from exc
    if port not in (None, 80, 443) or (port == 80 and p.scheme == 'https') or (port == 443 and p.scheme == 'http'):
        raise CollectionError('Only default HTTP/HTTPS ports are allowed')
    host = p.hostname.rstrip('.').encode('idna').decode('ascii').lower()
    if '%' in host or any(ord(c) < 33 for c in url) or '\\' in url:
        raise CollectionError('Ambiguous or unsafe URL')
    authority = '[' + host + ']' if ':' in host else host
    return up.urlunsplit((p.scheme.lower(), authority, p.path or '/', p.query, ''))


def public_ips(host, port, resolver=socket.getaddrinfo):
    if host in ('localhost', 'metadata.google.internal') or host.endswith(('.localhost', '.local', '.internal')):
        raise CollectionError('Private hostname rejected')
    try:
        answers = resolver(host, port, type=socket.SOCK_STREAM)
        ips = list(dict.fromkeys(a[4][0] for a in answers))
        if not ips:
            raise ValueError('No DNS answers')
        for ip in ips:
            address = ipaddress.ip_address(ip)
            if isinstance(address, ipaddress.IPv6Address) and (address.sixtofour is not None or address.teredo is not None or address in ipaddress.ip_network('64:ff9b::/96') or address in ipaddress.ip_network('64:ff9b:1::/48')):
                raise ValueError('IPv6 transition address rejected')
            if not address.is_global or address.is_multicast or address.is_reserved or address.is_unspecified or getattr(address, 'ipv4_mapped', None):
                raise ValueError('Non-public address')
        return ips
    except (OSError, ValueError) as exc:
        raise CollectionError('DNS not verifiably public: ' + str(exc)) from exc


class PinnedTransport:
    """Connect directly to validated IP; preserve Host and TLS SNI/cert verification."""
    def __call__(self, url, ips, timeout, max_bytes):
        deadline = time.monotonic() + timeout
        p = up.urlsplit(url)
        port = 443 if p.scheme == 'https' else 80
        conn = http.client.HTTPConnection(p.hostname, port, timeout=timeout)
        sock = None
        expired = threading.Event()
        def expire():
            expired.set()
            if sock:
                try: sock.shutdown(socket.SHUT_RDWR)
                except OSError: pass
                sock.close()
        timer = threading.Timer(timeout, expire)
        timer.daemon = True
        timer.start()
        try:
            ip = ips[0]
            sock = socket.socket(socket.AF_INET6 if ':' in ip else socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            if p.scheme == 'https':
                sock = ssl.create_default_context().wrap_socket(sock, server_hostname=p.hostname, do_handshake_on_connect=False)
                sock.do_handshake()
            conn.sock = sock
            conn.request('GET', up.urlunsplit(('', '', p.path or '/', p.query, '')), headers={
                'User-Agent': AGENT + '/1.0', 'Accept': 'text/html,application/xml,text/plain;q=0.8',
                'Accept-Encoding': 'identity', 'Connection': 'close'})
            response = conn.getresponse()
            headers = {k.lower(): v for k, v in response.getheaders()}
            chunks, size = [], 0
            while size <= max_bytes:
                remaining = deadline - time.monotonic()
                if remaining <= 0: raise CollectionError('Response deadline exceeded')
                sock.settimeout(remaining)
                chunk = response.read1(min(65536, max_bytes + 1 - size))
                if not chunk: break
                chunks.append(chunk); size += len(chunk)
            if expired.is_set(): raise CollectionError('Response deadline exceeded')
            if response.length is not None and response.length > 0:
                raise CollectionError('Truncated response body')
            body = b''.join(chunks)
            if len(body) > max_bytes:
                raise CollectionError('Response exceeds byte limit')
            if headers.get('content-encoding', 'identity').lower() not in ('', 'identity'):
                raise CollectionError('Encoded response not supported safely')
            return response.status, headers, body
        finally:
            timer.cancel()
            conn.close()
            if sock:
                sock.close()


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts, self.h1, self.links, self.canonical = [], [], [], []
        self.meta_description, self.robots_meta, self.hreflang, self.jsonld = '', [], [], []
        self.html_lang = ''
        self.text = []
        self.in_title = False
        self.h1_parts = None
        self.script = None
        self.script_type = ''
        self.hidden = 0
        self.base = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.html_lang = a.get('lang') or ''
        if tag == 'base' and self.base is None: self.base = a.get('href')
        if tag == 'title': self.in_title = True
        if tag == 'h1':
            if self.h1_parts is not None: self.h1.append(' '.join(self.h1_parts).strip())
            self.h1_parts = []
        if tag in ('style', 'script'): self.hidden += 1
        if tag == 'script':
            self.script, self.script_type = [], (a.get('type') or '').lower()
        if tag == 'meta':
            name = (a.get('name') or '').lower()
            if name == 'description': self.meta_description = a.get('content') or ''
            if name in ('robots', 'googlebot', 'bingbot'):
                self.robots_meta.append({'name': name, 'content': a.get('content') or ''})
        if tag == 'link':
            rel = (a.get('rel') or '').lower().split()
            if 'canonical' in rel and a.get('href'): self.canonical.append(a['href'])
            if 'alternate' in rel and a.get('hreflang') and a.get('href'):
                self.hreflang.append({'lang': a['hreflang'], 'url': a['href']})
        if tag == 'a' and a.get('href'): self.links.append(a['href'])

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'h1' and self.h1_parts is not None:
            self.h1.append(' '.join(self.h1_parts).strip()); self.h1_parts = None
        if tag == 'script' and self.script is not None:
            if self.script_type == 'application/ld+json':
                raw = ''.join(self.script)
                try: self.jsonld.append({'valid_json': True, 'value': json.loads(raw)})
                except (ValueError, RecursionError): self.jsonld.append({'valid_json': False, 'raw_excerpt': raw[:1000]})
            self.script = None
        if tag in ('script', 'style'): self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if self.script is not None: self.script.append(data)
        if self.hidden: return
        value = ' '.join(data.split())
        if not value: return
        self.text.append(value)
        if self.in_title: self.title_parts.append(value)
        if self.h1_parts is not None: self.h1_parts.append(value)

    def finish(self):
        self.close()
        if self.h1_parts is not None:
            self.h1.append(' '.join(self.h1_parts).strip()); self.h1_parts = None


def parse_sitemap(body):
    # ElementTree never retrieves external entities; reject declarations, including UTF-16 forms.
    if re.search(br'<!\s*(DOCTYPE|ENTITY)', body.replace(b'\x00', b''), re.I):
        raise CollectionError('DTD/entity sitemap rejected')
    try:
        root = ET.fromstring(body)
    except (ET.ParseError, ValueError) as exc:
        raise CollectionError('Malformed sitemap XML') from exc
    kind = root.tag.rsplit('}', 1)[-1]
    if kind not in ('urlset', 'sitemapindex'):
        raise CollectionError('Not a sitemap document')
    locs = [(node.text or '').strip() for node in root.iter() if node.tag.rsplit('}', 1)[-1] == 'loc']
    return kind, locs[:5000]


class Collector:
    def __init__(self, url, out, max_pages=20, max_requests=60, max_depth=3,
                 max_bytes=2_000_000, timeout=10, delay=1, max_seconds=300,
                 resolver=socket.getaddrinfo, transport=None, sleep=time.sleep):
        if not (1 <= max_pages <= 100 and 1 <= max_requests <= 200 and 0 <= max_depth <= 10 and 1 <= max_bytes <= 10_000_000 and 0 < timeout <= 30 and 0 <= delay <= 30 and 0 < max_seconds <= 900):
            raise CollectionError('Collection limits outside supported safe bounds')
        self.requested = normalize(url)
        self.host = up.urlsplit(self.requested).hostname
        self.out = Path(out)
        self.limits = dict(max_pages=max_pages, max_requests=max_requests, max_depth=max_depth,
                           max_bytes=max_bytes, timeout=timeout, delay=delay, max_seconds=max_seconds)
        self.resolver, self.transport, self.sleep = resolver, transport or PinnedTransport(), sleep
        self.calls = 0
        self.begin = time.monotonic()
        self.last_request = None
        self.robot = None
        self.halted = False
        self.robot_policy = 'unknown'
        self.effective_delay = delay
        self.snap = {'schema_version': '1.0', 'collection': {'started_at': utc(), 'requested_url': self.requested,
            'final_url': None, 'limits': self.limits, 'limitations': [
                'Static HTML sample only; no JavaScript rendering, Core Web Vitals, backlinks, or Google index verification.',
                'Robots policy is fail-closed when unavailable or using unsupported wildcard/Allow directives; cross-origin redirects and sitemaps are not followed.',
                'Sitemap coverage and graph measurements describe only this bounded sample.']},
            'pages': [], 'robots': {}, 'sitemaps': {'documents': [], 'urls': [], 'errors': []}, 'errors': []}

    def allowed(self, url):
        url = normalize(url)
        p = up.urlsplit(url)
        if p.hostname != self.host or p.scheme != up.urlsplit(self.requested).scheme:
            raise CollectionError('Off-origin hostname or HTTPS downgrade rejected')
        return url

    def can_fetch(self, url):
        return self.robot_policy == 'allow_all' or (self.robot_policy == 'parsed' and self.robot.can_fetch(AGENT, url))

    def fetch(self, url, check_robots=True):
        seen = set()
        if self.halted: raise CollectionError('Collection halted after HTTP 429')
        for _ in range(6):
            url = self.allowed(url)
            if url in seen: raise CollectionError('Redirect loop')
            seen.add(url)
            if check_robots and not self.can_fetch(url): raise CollectionError('Blocked by robots policy')
            if self.calls >= self.limits['max_requests']: raise CollectionError('Request budget exhausted')
            elapsed = time.monotonic() - self.begin
            if elapsed >= self.limits['max_seconds']: raise CollectionError('Time budget exhausted')
            if self.last_request is not None:
                wait = max(0, self.effective_delay - (time.monotonic() - self.last_request))
                if elapsed + wait >= self.limits['max_seconds']: raise CollectionError('Time budget exhausted')
                self.sleep(wait)
            p = up.urlsplit(url)
            result = queue.Queue(maxsize=1)
            def resolve():
                try: result.put((True, public_ips(p.hostname, 443 if p.scheme == 'https' else 80, self.resolver)))
                except Exception as exc: result.put((False, exc))
            threading.Thread(target=resolve, daemon=True).start()
            try: ok, ips = result.get(timeout=min(self.limits['timeout'], max(.01, self.limits['max_seconds'] - (time.monotonic() - self.begin))))
            except queue.Empty:
                self.halted = True
                raise CollectionError('DNS deadline exceeded')
            if not ok: raise ips
            self.calls += 1
            self.last_request = time.monotonic()
            status, headers, body = self.transport(url, ips, min(self.limits['timeout'], max(.1, self.limits['max_seconds'] - (time.monotonic() - self.begin))), self.limits['max_bytes'])
            if len(body) > self.limits['max_bytes']: raise CollectionError('Response exceeds byte limit')
            if status == 429: self.halted = True
            if status in REDIRECTS:
                location = headers.get('location')
                if not location: raise CollectionError('Redirect without Location')
                next_url = up.urljoin(url, location)
                if p.scheme == 'https' and up.urlsplit(next_url).scheme != 'https': raise CollectionError('HTTPS downgrade rejected')
                url = next_url
                continue
            return url, status, headers, body
        raise CollectionError('Redirect limit exceeded')

    def save_raw(self, url, body, suffix):
        name = 'raw/' + hashlib.sha256(url.encode()).hexdigest()[:20] + suffix
        (self.out / name).write_bytes(body)
        return name

    def collect_robots(self):
        url = up.urljoin(self.requested, '/robots.txt')
        record = self.snap['robots'] = {'url': url, 'status': None, 'assessment': 'unknown', 'fetched_at': utc()}
        sitemap_urls = []
        try:
            final, status, headers, body = self.fetch(url, check_robots=False)
            record.update(final_url=final, status=status, raw_artifact_path=self.save_raw(final, body, '.robots.txt'))
            if status in (404, 410): self.robot_policy = 'allow_all'
            elif status in (401, 403): self.robot_policy = 'deny_all'
            elif status == 200:
                content = body.decode('utf-8-sig', 'replace')
                if '<html' in content.lower() or '\x00' in content or '\ufffd' in content:
                    raise CollectionError('Robots response not assessable as text')
                # Conservative support: reject policies whose wildcard/end-anchor or Allow
                # precedence cannot be evaluated by stdlib RobotFileParser.
                for line in content.splitlines():
                    clean = line.split('#', 1)[0].strip()
                    if not clean: continue
                    if ':' not in clean: raise CollectionError('Malformed robots directive')
                    key, value = clean.split(':', 1)
                    if key.strip().lower() == 'user-agent' and not re.fullmatch(r'(?:\*|[A-Za-z_-]+)', value.strip()):
                        raise CollectionError('Unsupported robots user-agent token; fail closed')
                    if key.strip().lower() in ('allow', 'disallow') and ('*' in value or '$' in value):
                        raise CollectionError('Wildcard robots policy requires unsupported matching; fail closed')
                    if key.strip().lower() == 'allow' and value.strip():
                        raise CollectionError('Allow precedence requires unsupported matching; fail closed')
                agents = re.findall(r'^\s*user-agent\s*:\s*([^#\r\n]+)', content, re.I | re.M)
                specific = [a.strip().lower() for a in agents if a.strip() != '*' and a.strip().lower() in AGENT.lower()]
                stars = [a for a in agents if a.strip() == '*']
                if len(specific) > 1 or (not specific and len(stars) > 1):
                    raise CollectionError('Multiple matching robots groups require unsupported merging; fail closed')
                self.robot = urllib.robotparser.RobotFileParser()
                policy_lines = [line for line in content.splitlines() if not re.match(r'^\s*(?:allow|disallow)\s*:\s*(?:#.*)?$', line, re.I)]
                self.robot.parse(policy_lines)
                # Invalid/nonstandard delays are fail-closed, rather than silently ignored.
                raw_delays = re.findall(r'^\s*crawl-delay\s*:\s*([^#\r\n]+)', content, re.I | re.M)
                delays = []
                for raw in raw_delays:
                    try: value = float(raw.strip())
                    except ValueError: raise CollectionError('Unassessable crawl-delay')
                    if not 0 <= value <= 30: raise CollectionError('Crawl-delay exceeds safe collection budget')
                    delays.append(value)
                self.effective_delay = max([self.effective_delay] + delays)
                self.robot_policy = 'parsed'
                sitemap_urls = self.robot.site_maps() or []
            else: record['error'] = 'Robots HTTP response prevents safe assessment'
            record['assessment'] = self.robot_policy
            record['effective_delay_seconds'] = self.effective_delay
        except (CollectionError, OSError, http.client.HTTPException, ValueError) as exc:
            record['error'] = str(exc)
        return sitemap_urls

    def collect_sitemaps(self, urls):
        queue = collections.deque(urls or [up.urljoin(self.requested, '/sitemap.xml')])
        seen, discovered = set(), set()
        while queue and len(seen) < 5:
            url = queue.popleft()
            if url in seen: continue
            seen.add(url)
            try:
                final, status, headers, body = self.fetch(url)
                record = {'url': url, 'final_url': final, 'status': status, 'fetched_at': utc(),
                          'raw_artifact_path': self.save_raw(final, body, '.sitemap.xml')}
                self.snap['sitemaps']['documents'].append(record)
                if status != 200:
                    self.snap['sitemaps']['errors'].append({'url': url, 'error': 'HTTP ' + str(status)})
                    if status == 429: break
                    continue
                kind, locs = parse_sitemap(body)
                record.update(kind=kind, loc_count=len(locs))
                for loc in locs:
                    try: loc = self.allowed(loc)
                    except (CollectionError, ValueError): continue
                    if kind == 'sitemapindex': queue.append(loc)
                    elif len(discovered) < 5000: discovered.add(loc)
            except (CollectionError, OSError, http.client.HTTPException, ValueError) as exc:
                self.snap['sitemaps']['errors'].append({'url': url, 'error': str(exc)})
        self.snap['sitemaps']['urls'] = sorted(discovered)
        self.snap['sitemaps']['complete'] = False
        return sorted(discovered)

    def page(self, url, depth):
        record = {'requested_url': url, 'url': url, 'final_url': None, 'status': None, 'fetch_state': 'unknown',
                  'fetched_at': utc(), 'depth': depth, 'title': '', 'meta_description': '', 'h1': [], 'canonical': [],
                  'robots_meta': [], 'hreflang': [], 'html_lang': '', 'links': [], 'internal_links': [], 'jsonld': [],
                  'text_excerpt': '', 'word_count': None, 'raw_artifact_path': None, 'sources': []}
        try:
            final, status, headers, body = self.fetch(url)
            source_hash = hashlib.sha256(body).hexdigest()
            html = None
            redacted = False
            artifact_body = body
            if 'html' in headers.get('content-type', '').lower():
                charset = re.search(r'charset\s*=\s*["\x27]?([\w-]+)', headers.get('content-type', ''), re.I)
                try: html = body.decode(charset.group(1) if charset else 'utf-8', 'replace')
                except LookupError: html = body.decode('utf-8', 'replace')
                map_evidence = analyze_google_maps(html)
                html, redacted = redact_google_maps_secrets(html)
                if redacted: artifact_body = html.encode('utf-8')
            raw = self.save_raw(final, artifact_body, '.html')
            record.update(artifact_redacted=redacted, raw_source_sha256=source_hash,
                          artifact_sha256=hashlib.sha256(artifact_body).hexdigest())
            record.update(url=final, final_url=final, status=status, fetch_state='ok' if 200 <= status < 300 else 'http_error',
                          content_type=headers.get('content-type', ''), response_headers={k: headers[k] for k in ('content-type', 'x-robots-tag', 'last-modified', 'retry-after') if k in headers},
                          raw_artifact_path=raw, sources=[{'url': final, 'fetched_at': record['fetched_at'], 'raw_artifact_path': raw}])
            if not 200 <= status < 300: return record
            if 'html' not in headers.get('content-type', '').lower():
                record['parse_state'] = 'not_html'; return record
            record['google_maps'] = map_evidence
            parser = PageParser(); parser.feed(html); parser.finish()
            record.update(title=' '.join(parser.title_parts), meta_description=parser.meta_description, h1=parser.h1,
                          robots_meta=parser.robots_meta, html_lang=parser.html_lang, jsonld=parser.jsonld,
                          text_excerpt=' '.join(parser.text)[:4000], word_count=len(' '.join(parser.text).split()), parse_state='parsed')
            base = up.urljoin(final, parser.base) if parser.base else final
            record['canonical'] = [up.urljoin(base, c) for c in parser.canonical]
            record['hreflang'] = [{'lang': x['lang'], 'url': up.urljoin(base, x['url'])} for x in parser.hreflang]
            seen_links, seen_internal = set(), set()
            record['links_truncated'] = len(parser.links) > 5000
            for link in parser.links[:5000]:
                try: target = normalize(up.urljoin(base, link))
                except (CollectionError, ValueError, UnicodeError): continue
                if target not in seen_links:
                    record['links'].append(target); seen_links.add(target)
                try: self.allowed(target)
                except CollectionError: continue
                if target not in seen_internal:
                    record['internal_links'].append(target); seen_internal.add(target)
        except (CollectionError, OSError, http.client.HTTPException, ValueError, RecursionError) as exc:
            record['error'] = str(exc)
            if 'robots' in str(exc).lower() or 'halted' in str(exc).lower(): record['fetch_state'] = 'blocked'
        return record

    def run(self):
        if self.out.exists() and (not self.out.is_dir() or any(self.out.iterdir())):
            raise CollectionError('Output directory must be new or empty; existing evidence is preserved')
        self.out.mkdir(parents=True, exist_ok=True); (self.out / 'raw').mkdir()
        sitemap_urls = self.collect_robots()
        seeds = self.collect_sitemaps(sitemap_urls) if self.robot_policy in ('parsed', 'allow_all') else []
        queue = collections.deque([(self.requested, 0)] + [(url, 0) for url in seeds[:self.limits['max_pages']]])
        visited = set()
        while queue and len(self.snap['pages']) < self.limits['max_pages']:
            url, depth = queue.popleft()
            if url in visited: continue
            visited.add(url)
            page = self.page(url, depth); self.snap['pages'].append(page)
            if page['final_url']: visited.add(page['final_url'])
            if url == self.requested: self.snap['collection']['final_url'] = page['final_url']
            if page['status'] == 429:
                self.snap['errors'].append('Collection stopped on HTTP 429; no automatic retries'); break
            if depth < self.limits['max_depth']:
                queue.extend((link, depth + 1) for link in page['internal_links'][:max(0, 5000 - len(queue))] if link not in visited)
            if self.halted or self.calls >= self.limits['max_requests'] or time.monotonic() - self.begin >= self.limits['max_seconds']: break
        pages = self.snap['pages']
        edges = [{'from': p['url'], 'to': link} for p in pages for link in p['internal_links']]
        self.snap['graph'] = {'sample_only': True, 'pages_fetched': sum(p['status'] is not None for p in pages),
            'internal_edges': edges, 'orphan_assessment': 'unknown', 'max_observed_depth': max((p['depth'] for p in pages), default=0)}
        self.snap['sitemaps']['sampled_url_count'] = sum(p['url'] in seeds for p in pages)
        self.snap['collection'].update(finished_at=utc(), requests_made=self.calls, pages_recorded=len(pages))
        (self.out / 'snapshot.json').write_text(json.dumps(self.snap, ensure_ascii=False, indent=2), encoding='utf-8')
        return self.snap


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('url'); ap.add_argument('--out', required=True)
    ap.add_argument('--max-pages', type=int, default=20)
    args = ap.parse_args()
    if not 1 <= args.max_pages <= 100: ap.error('--max-pages must be 1..100')
    try:
        snapshot = Collector(args.url, args.out, max_pages=args.max_pages).run()
    except (CollectionError, ValueError, OSError) as exc:
        ap.exit(2, 'Collection failed: ' + str(exc) + '\n')
    print(json.dumps({'snapshot': str(Path(args.out) / 'snapshot.json'), 'pages': len(snapshot['pages']), 'robots': snapshot['robots']['assessment']}))


if __name__ == '__main__': main()
