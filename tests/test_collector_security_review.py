"""Independent security regression checks. All networking is fake/offline."""
import importlib.util
from pathlib import Path
import socket
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('review_collector', Path(__file__).resolve().parents[1] / 'scripts' / 'collect_public_site.py')
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


def answers(*ips):
    return lambda host, port, **kwargs: [(socket.AF_INET6 if ':' in ip else socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port)) for ip in ips]


class SecurityReview(unittest.TestCase):
    def run_fake(self, routes, url='https://example.com/', resolver=None):
        calls = []
        def transport(url, ips, timeout, max_bytes):
            calls.append(url)
            if url not in routes:
                raise AssertionError('Unexpected request: ' + url)
            return routes[url]
        with tempfile.TemporaryDirectory() as tmp:
            result = collector.Collector(url, Path(tmp) / 'evidence', resolver=resolver or answers('93.184.216.34'), transport=transport, delay=0).run()
        return result, calls

    def test_empty_userinfo_rejected(self):
        for value in ('https://@example.com/', 'https://:@example.com/'):
            with self.subTest(value=value), self.assertRaises((collector.CollectionError, ValueError)):
                collector.normalize(value)

    def test_nondefault_ports_rejected(self):
        for value in ('https://example.com:22/', 'http://example.com:443/', 'https://example.com:80/'):
            with self.subTest(value=value), self.assertRaises(collector.CollectionError):
                collector.normalize(value)

    def test_any_private_dns_answer_rejects_entire_host(self):
        for ip in ('127.0.0.1', '10.0.0.1', '169.254.169.254', '::1', 'fc00::1', 'fe80::1', '::ffff:127.0.0.1', '224.0.0.1'):
            with self.subTest(ip=ip), self.assertRaises(collector.CollectionError):
                collector.public_ips('example.com', 443, answers('93.184.216.34', ip))

    def test_dns_failure_makes_no_network_requests(self):
        result, calls = self.run_fake({}, resolver=answers('93.184.216.34', '127.0.0.1'))
        self.assertEqual(calls, [])
        self.assertFalse(any(page['status'] is not None for page in result['pages']))

    def test_robots_cross_host_redirect_never_followed(self):
        routes = {'https://example.com/robots.txt': (302, {'location': 'https://other.example/robots.txt'}, b'')}
        _, calls = self.run_fake(routes)
        self.assertEqual(calls, list(routes))

    def test_http_to_https_needs_separate_origin_policy(self):
        routes = {'http://example.com/robots.txt': (302, {'location': 'https://example.com/robots.txt'}, b'')}
        _, calls = self.run_fake(routes, url='http://example.com/')
        self.assertEqual(calls, list(routes))

    def test_wildcard_disallow_never_bypassed(self):
        routes = {'https://example.com/robots.txt': (200, {'content-type': 'text/plain'}, b'User-agent: *\nDisallow: /*?secret=\n'),
                  'https://example.com/sitemap.xml': (404, {}, b'')}
        _, calls = self.run_fake(routes, url='https://example.com/page?secret=1')
        self.assertNotIn('https://example.com/page?secret=1', calls)

    def test_robots_server_errors_fail_closed(self):
        for status in (429, 500, 503):
            with self.subTest(status=status):
                routes = {'https://example.com/robots.txt': (status, {}, b'')}
                _, calls = self.run_fake(routes)
                self.assertEqual(calls, list(routes))

    def test_sitemap_rate_limit_stops_all_requests(self):
        routes = {'https://example.com/robots.txt': (404, {}, b''),
                  'https://example.com/sitemap.xml': (429, {'retry-after': '60'}, b'')}
        _, calls = self.run_fake(routes)
        self.assertEqual(calls, list(routes))

    def test_reject_entity_documents_with_multiple_encodings(self):
        xml = '<?xml version="1.0"?><!DOCTYPE urlset [<!ENTITY x "payload">]><urlset><url><loc>&x;</loc></url></urlset>'
        for encoding in ('utf-8', 'utf-16', 'utf-32'):
            with self.subTest(encoding=encoding), self.assertRaises(collector.CollectionError):
                collector.parse_sitemap(xml.encode(encoding))

    def test_repeated_robots_group_cannot_hide_disallow(self):
        routes = {'https://example.com/robots.txt': (200, {}, b'User-agent: *\nDisallow: /other\n\nUser-agent: *\nDisallow: /private\n'),
                  'https://example.com/sitemap.xml': (404, {}, b'')}
        _, calls = self.run_fake(routes, url='https://example.com/private')
        self.assertNotIn('https://example.com/private', calls)

    def test_empty_robots_rule_cannot_hide_disallow(self):
        for directive in ('Allow', 'Disallow'):
            with self.subTest(directive=directive):
                body = ('User-agent: *\n' + directive + ':\nDisallow: /private\n').encode()
                routes = {'https://example.com/robots.txt': (200, {}, body),
                          'https://example.com/sitemap.xml': (404, {}, b'')}
                _, calls = self.run_fake(routes, url='https://example.com/private')
                self.assertNotIn('https://example.com/private', calls)

    def test_malformed_agent_cannot_hide_disallow(self):
        for agent in ('', 'Public%53EOCollector'):
            with self.subTest(agent=agent):
                body = ('User-agent: ' + agent + '\nDisallow: /other\n\nUser-agent: PublicSEOCollector\nDisallow: /private\n').encode()
                routes = {'https://example.com/robots.txt': (200, {}, body),
                          'https://example.com/sitemap.xml': (404, {}, b'')}
                _, calls = self.run_fake(routes, url='https://example.com/private')
                self.assertNotIn('https://example.com/private', calls)

    def test_partial_content_length_not_accepted(self):
        sock = mock.MagicMock()
        response = mock.MagicMock()
        response.status = 200
        response.getheaders.return_value = [('Content-Length', '100')]
        response.length = 90
        response.read1.side_effect = [b'partial', b'']
        conn = mock.MagicMock()
        conn.getresponse.return_value = response
        with mock.patch.object(collector.socket, 'socket', return_value=sock), mock.patch.object(collector.http.client, 'HTTPConnection', return_value=conn):
            with self.assertRaises((collector.CollectionError, collector.http.client.IncompleteRead)):
                collector.PinnedTransport()('http://example.com/', ['93.184.216.34'], 1, 1000)
        sock.connect.assert_called_once_with(('93.184.216.34', 80))

    def test_http_errors_not_successfully_parsed_pages(self):
        routes = {'https://example.com/robots.txt': (404, {}, b''),
                  'https://example.com/sitemap.xml': (404, {}, b''),
                  'https://example.com/': (503, {'content-type': 'text/html'}, b'<title>Not a real page</title>')}
        result, _ = self.run_fake(routes)
        page = result['pages'][0]
        self.assertEqual(page['status'], 503)
        self.assertEqual(page['fetch_state'], 'http_error')
        self.assertEqual(page['title'], '')


if __name__ == '__main__':
    unittest.main()
