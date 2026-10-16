"""Offline collector acceptance tests. No network access is used."""
import importlib.util
import json
import pathlib
import socket
import tempfile
import unittest
from unittest import mock

MODULE = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'collect_public_site.py'
spec = importlib.util.spec_from_file_location('public_collector', MODULE)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def dns(ip='93.184.216.34'):
    return lambda host, port, **kw: [(socket.AF_INET6 if ':' in ip else socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port))]


class Fake:
    def __init__(self, responses): self.responses, self.calls = responses, []
    def __call__(self, url, ips, timeout, max_bytes):
        self.calls.append((url, ips))
        response = self.responses.get(url, (404, {'content-type': 'text/plain'}, b'Not found'))
        if isinstance(response, Exception): raise response
        return response


def html(body): return 200, {'content-type': 'text/html; charset=utf-8'}, body.encode()


class PublicCollectorTests(unittest.TestCase):
    def run_site(self, responses, **kwargs):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        fake = Fake(responses)
        collector = m.Collector('https://example.com/', pathlib.Path(temporary.name) / 'output',
            resolver=dns(), transport=fake, sleep=lambda seconds: None, delay=0, **kwargs)
        return collector.run(), fake, collector

    def test_reject_private_ipv4_ipv6_and_mixed_dns(self):
        for ip in ['127.0.0.1', '10.0.0.1', '169.254.169.254', '192.168.1.1', '0.0.0.0', '::1', 'fc00::1', 'fe80::1', '::ffff:8.8.8.8', '64:ff9b::7f00:1', '2002:7f00:1::', '224.0.0.1']:
            with self.subTest(ip=ip), self.assertRaises(m.CollectionError): m.public_ips('example.com', 443, dns(ip))
        def mixed(*args, **kw): return dns()(*args, **kw) + dns('127.0.0.1')(*args, **kw)
        with self.assertRaises(m.CollectionError): m.public_ips('example.com', 443, mixed)
        for host in ['localhost', 'metadata.google.internal', 'secret.local']:
            with self.assertRaises(m.CollectionError): m.public_ips(host, 443, dns())

    def test_bad_schemes_credentials_ports(self):
        for url in ['file:///etc/passwd', 'http://u:p@example.com', 'http://example.com:8080', 'https://example.com:80', 'http://example.com:443', 'http://example.com/\\private']:
            with self.subTest(url=url), self.assertRaises(m.CollectionError): m.normalize(url)

    def test_parse_nested_h1_jsonld_and_evidence(self):
        snap, fake, c = self.run_site({'https://example.com/': html('''<html lang="en"><title>Hello</title><meta name="description" content="A description"><meta name="robots" content="noindex"><link rel="canonical" href="/"><link rel="alternate" hreflang="fr" href="/fr"><h1>One <span>nested</span> heading</h1><a href="/two#anchor">Two</a><script type="application/ld+json">{"@type":"WebPage"}</script>'''), 'https://example.com/two': html('<h1>Two')}, max_pages=2)
        page = snap['pages'][0]
        self.assertEqual(page['h1'], ['One nested heading'])
        self.assertEqual(page['canonical'], ['https://example.com/'])
        self.assertEqual(page['jsonld'][0]['value']['@type'], 'WebPage')
        self.assertEqual(page['internal_links'], ['https://example.com/two'])
        self.assertEqual(snap['pages'][1]['h1'], ['Two'])
        self.assertTrue((c.out / page['raw_artifact_path']).exists())
        self.assertTrue((c.out / 'snapshot.json').exists())
        self.assertTrue(snap['graph']['sample_only'])
        self.assertEqual(snap['graph']['orphan_assessment'], 'unknown')

    def test_robots_deny_and_unavailable_fail_closed(self):
        for response in [(200, {}, b'User-agent: *\nDisallow: /'), (403, {}, b''), (500, {}, b'error'), (429, {}, b'rate limit'), OSError('DNS failed')]:
            snap, fake, c = self.run_site({'https://example.com/robots.txt': response})
            self.assertEqual(len(fake.calls), 1)
            self.assertEqual(snap['pages'][0]['fetch_state'], 'blocked')
            self.assertIsNone(snap['pages'][0]['status'])

    def test_http_error_is_distinct_from_unknown(self):
        for response, expected, status in [(OSError('timeout'), 'unknown', None), ((500, {}, b'error'), 'http_error', 500), ((429, {}, b'wait'), 'http_error', 429)]:
            snap, _, _ = self.run_site({'https://example.com/': response})
            self.assertEqual(snap['pages'][0]['fetch_state'], expected)
            self.assertEqual(snap['pages'][0]['status'], status)

    def test_oversized_response(self):
        snap, _, _ = self.run_site({'https://example.com/': html('x' * 200)}, max_bytes=100)
        self.assertEqual(snap['pages'][0]['fetch_state'], 'unknown')
        self.assertIn('byte limit', snap['pages'][0]['error'])

    def test_redirect_scope_and_loops(self):
        for target in ['https://elsewhere.example/', 'http://example.com/', 'https://127.0.0.1/', 'https://example.com/']:
            snap, fake, _ = self.run_site({'https://example.com/': (302, {'location': target}, b'')})
            self.assertEqual(snap['pages'][0]['fetch_state'], 'unknown')
            self.assertEqual(len([u for u, _ in fake.calls if u == 'https://example.com/']), 1)
            self.assertFalse(any(u == target for u, _ in fake.calls if target != 'https://example.com/'))

    def test_dns_revalidated_after_redirect(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Fake({'https://example.com/': (302, {'location': '/next'}, b'')})
            answers = iter([dns(), dns('127.0.0.1')])
            c = m.Collector('https://example.com/', tmp, resolver=lambda *a, **k: next(answers)(*a, **k), transport=fake, delay=0)
            c.robot_policy = 'allow_all'
            with self.assertRaises(m.CollectionError): c.fetch(c.requested)
            self.assertEqual(len(fake.calls), 1)

    def test_sitemap_malformed_entities_and_valid(self):
        for xml in [b'<broken', b'<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><urlset>&x;</urlset>', b'<html/>']:
            with self.assertRaises(m.CollectionError): m.parse_sitemap(xml)
        kind, urls = m.parse_sitemap(b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/a</loc></url></urlset>')
        self.assertEqual((kind, urls), ('urlset', ['https://example.com/a']))
        snap, _, _ = self.run_site({'https://example.com/sitemap.xml': (200, {}, b'<broken')})
        self.assertIn('Malformed sitemap', snap['sitemaps']['errors'][0]['error'])

    def test_limits_and_output_preservation(self):
        snap, fake, c = self.run_site({'https://example.com/': html('<a href="/a">A</a><a href="/b">B</a>')}, max_pages=1)
        before = (c.out / 'snapshot.json').read_bytes()
        with self.assertRaises(m.CollectionError): c.run()
        self.assertEqual(before, (c.out / 'snapshot.json').read_bytes())
        self.assertEqual(len(snap['pages']), 1)
        snap, fake, _ = self.run_site({}, max_requests=1)
        self.assertEqual(len(fake.calls), 1)

    def test_crawl_delay_cap_fail_closed(self):
        for delay in ['31', 'NaN', '-1', 'nonsense']:
            snap, fake, _ = self.run_site({'https://example.com/robots.txt': (200, {}, ('User-agent: *\nCrawl-delay: '+delay).encode())})
            self.assertEqual(snap['robots']['assessment'], 'unknown')
            self.assertEqual(len(fake.calls), 1)

    def test_transport_connects_pinned_ip_and_verifies_hostname(self):
        sock = mock.MagicMock()
        response = mock.MagicMock()
        response.length = 0; response.status = 200; response.getheaders.return_value = [('Content-Type', 'text/html')]
        response.read1.side_effect = [b'hello', b'']
        conn = mock.MagicMock(); conn.getresponse.return_value = response
        context = mock.MagicMock(); context.wrap_socket.return_value = sock
        with mock.patch.object(m.socket, 'socket', return_value=sock), mock.patch.object(m.http.client, 'HTTPConnection', return_value=conn), mock.patch.object(m.ssl, 'create_default_context', return_value=context):
            m.PinnedTransport()('https://example.com/', ['93.184.216.34'], 5, 100)
        sock.connect.assert_called_once_with(('93.184.216.34', 443))
        context.wrap_socket.assert_called_once_with(sock, server_hostname='example.com', do_handshake_on_connect=False)
        sock.do_handshake.assert_called_once()
        self.assertIs(conn.sock, sock)


if __name__ == '__main__': unittest.main()
