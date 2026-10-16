import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from google_maps_evidence import analyze_google_maps

FIXTURES = {
    'iframe': '<iframe src="https://www.google.com/maps/embed/v1/place?key=AIzaSECRET&amp;q=place_id:ChIJfictionalNorth"></iframe>',
    'navigation': '<a href="https://www.google.com/maps/dir/?api=1&amp;destination_place_id=ChIJfictionalNorth">Directions</a><a href="https://maps.google.com/?q=Fictional">Location</a>',
    'js': '<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSECRET"></script><div id="google-map"></div>',
    'wrong_branch': '<iframe src="https://google.com/maps/embed/v1/place?q=place_id:ChIJfictionalSouth"></iframe>',
    'evil': '<iframe src="https://google.com.evil.example/maps/embed?key=secret"></iframe>',
    'credentials': '<iframe src="https://user:password@google.com/maps/embed?q=place_id:ChIJfictionalNorth"></iframe>',
    'empty': '<h1>Fictional personal portfolio</h1>',
}

class GoogleMapsTests(unittest.TestCase):
    def test_embed_and_branch(self):
        r = analyze_google_maps(FIXTURES['iframe'], 'ChIJfictionalNorth')
        self.assertEqual(r['classifications'], ['embedded_map'])
        self.assertEqual(r['branch_status'], 'match')
        self.assertFalse(r['rendered_verified'])
        self.assertNotIn('AIzaSECRET', json.dumps(r))
    def test_navigation_not_embed(self):
        r = analyze_google_maps(FIXTURES['navigation'])
        self.assertEqual(r['classifications'], ['directions_link', 'location_link'])
    def test_js_not_rendering(self):
        r = analyze_google_maps(FIXTURES['js'])
        self.assertEqual(r['classifications'], ['maps_js_signal'])
        self.assertFalse(r['rendered_verified'])
        self.assertNotIn('AIzaSECRET', json.dumps(r))
    def test_wrong_branch(self):
        self.assertEqual(analyze_google_maps(FIXTURES['wrong_branch'], 'ChIJfictionalNorth')['branch_status'], 'mismatch')
    def test_opaque_unknown(self):
        r = analyze_google_maps('<iframe src="https://google.com/maps/embed?pb=!1m!ChIJfictionalNorth"></iframe>', 'ChIJfictionalNorth')
        self.assertEqual(r['branch_status'], 'unknown')
        self.assertTrue(r['evidence'][0]['opaque_pb_present'])
    def test_untrusted_and_credentials(self):
        for key in ('evil', 'credentials'):
            r = analyze_google_maps(FIXTURES[key], 'ChIJfictionalNorth')
            self.assertEqual(r['classifications'], ['untrusted/unknown'])
            self.assertEqual(r['branch_status'], 'unknown')
            self.assertNotIn('password', json.dumps(r))
            self.assertNotIn('secret', json.dumps(r))
    def test_host_path_allowlist(self):
        for url in ('https://google.com/mapsnot/embed', 'https://google.evil/maps/embed', 'https://www.google.zz/maps/embed', 'https://google.com:8443/maps/embed'):
            self.assertEqual(analyze_google_maps('<iframe src="'+url+'"></iframe>')['classifications'], ['untrusted/unknown'])
        self.assertEqual(analyze_google_maps('<iframe src="https://www.google.co.uk/maps/embed"></iframe>')['classifications'], ['embedded_map'])
    def test_short_links_unresolved(self):
        for url in ('https://maps.app.goo.gl/fake', 'https://goo.gl/maps/fake'):
            r = analyze_google_maps('<a href="'+url+'">Map</a>')
            self.assertEqual(r['classifications'], ['untrusted/unknown'])
    def test_optional_only_confirmed_visit(self):
        self.assertIsNone(analyze_google_maps(FIXTURES['empty'])['optional_recommendation'])
        self.assertIsNotNone(analyze_google_maps(FIXTURES['empty'], customer_visit_confirmed=True)['optional_recommendation'])
        for kind in ('personal_portfolio', 'service_area', 'private_address'):
            self.assertIsNone(analyze_google_maps(FIXTURES['empty'], customer_visit_confirmed=True, site_kind=kind)['optional_recommendation'])
        self.assertIsNone(analyze_google_maps('', customer_visit_confirmed='true')['optional_recommendation'])
    def test_deferred_and_inline(self):
        for html in ('<iframe data-src="https://google.com/maps/embed"></iframe>', '<script>new google.maps.Map(el, options);</script>'):
            self.assertEqual(analyze_google_maps(html)['classifications'], ['maps_js_signal'])
    def test_mixed_and_api_key_as_id(self):
        r = analyze_google_maps(FIXTURES['iframe']+FIXTURES['wrong_branch'], 'ChIJfictionalNorth')
        self.assertEqual(r['branch_status'], 'mixed')
        r = analyze_google_maps('<a href="https://google.com/maps?place_id=AIzaSECRET">Map</a>')
        self.assertNotIn('AIza', json.dumps(r))

class GoogleMapsCollectorTests(unittest.TestCase):
    def test_collector_redacts_before_saving_and_parsing(self):
        import tempfile
        import socket
        import hashlib
        from collect_public_site import Collector
        body = (FIXTURES['iframe'] + FIXTURES['credentials'] +
                '<script>google.maps.importLibrary({key: \"AIzaINLINESECRET\"});</script>' +
                '<a href="https://google.com/maps?key=link-secret">Map</a>' +
                '<script type="application/ld+json">{"url":"https://google.com/maps?key=json-secret"}</script>').encode()
        def transport(url, ips, timeout, max_bytes):
            if url == 'https://example.com/':
                return 200, {'content-type': 'text/html'}, body
            return 404, {'content-type': 'text/plain'}, b''
        def resolver(host, port, **kwargs):
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', port))]
        with tempfile.TemporaryDirectory() as tmp:
            c = Collector('https://example.com/', Path(tmp)/'output', max_pages=1,
                          resolver=resolver, transport=transport, sleep=lambda n: None, delay=0)
            snap = c.run()
            page = snap['pages'][0]
            raw = (c.out / page['raw_artifact_path']).read_bytes()
            for secret in ('AIzaSECRET', 'AIzaINLINESECRET', 'password', 'link-secret', 'json-secret'):
                self.assertNotIn(secret, raw.decode())
                self.assertNotIn(secret, json.dumps(snap))
            self.assertTrue(page['artifact_redacted'])
            self.assertEqual(page['raw_source_sha256'], hashlib.sha256(body).hexdigest())
            self.assertEqual(page['artifact_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertNotEqual(page['raw_source_sha256'], page['artifact_sha256'])
            self.assertIn('embedded_map', page['google_maps']['classifications'])
            self.assertEqual(page['internal_links'], [])

if __name__ == '__main__':
    unittest.main()
