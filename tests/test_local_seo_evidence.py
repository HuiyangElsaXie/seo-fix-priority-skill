"""All values in this module describe fictional businesses only."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from local_seo_evidence import analyze_local_evidence, normalize_nap


def fixture():
    target = dict(entity_id='fictional-brand', branch_id='fictional-north', place_id='fictional-place', market='fictional-market')
    def row(key, kind):
        return dict(target, id=key, source_kind=kind, source_url='https://example.invalid/'+key,
                    captured_at='2026-10-15T12:00:00Z', observed_at='2026-10-15T11:00:00Z', coverage='aggregate',
                    nap=dict(name='Fictional Workshop', address='12 Example Lane, Unit 1', phone='+1 (202) 555-0100'))
    site, profile = row('site', 'website'), row('profile', 'google_business_profile')
    profile['google_reviews'] = dict(rating=3.2, total_count=2, visible_sample_count=2)
    return dict(schema_version='1.0', as_of='2026-10-16', target=target, observations=[site, profile])


class LocalEvidenceTests(unittest.TestCase):
    def test_low_rating_and_count_have_actionable_evidence(self):
        result = analyze_local_evidence(fixture())
        codes = {f['code'] for f in result['findings']}
        self.assertIn('LOCAL_LOW_GOOGLE_RATING', codes)
        self.assertIn('LOCAL_LOW_GOOGLE_REVIEW_COUNT', codes)
        for f in result['findings']:
            self.assertTrue(f['actions'] and f['acceptance'] and f['evidence'])
            self.assertEqual('needs_verification', f['priority']['value'])

    def test_low_rating_report_exposes_count_sample_date_and_confidence(self):
        p = fixture()
        p['observations'][1]['google_reviews'].update(total_count=120, visible_sample_count=3)
        result = analyze_local_evidence(p)
        finding = next(f for f in result['findings'] if f['code'] == 'LOCAL_LOW_GOOGLE_RATING')
        self.assertIn('total_count=120', finding['technical_fact'])
        self.assertIn('visible_sample_count=3', finding['technical_fact'])
        self.assertIn('2026-10-15T11:00:00Z', finding['technical_fact'])
        self.assertIn('bounded supplied evidence', finding['reason'])
        self.assertTrue(any('No comparable peer context supplied' in u for u in result['unknowns']))
        p['observations'][1]['google_reviews']['total_count'] = 3
        finding = next(f for f in analyze_local_evidence(p)['findings'] if f['code'] == 'LOCAL_LOW_GOOGLE_RATING')
        self.assertIn('Confidence is low', finding['reason'])

    def test_unknown_never_zero(self):
        p = fixture()
        p['observations'][1]['google_reviews'] = {'visible_sample_count': 0}
        r = analyze_local_evidence(p)
        self.assertFalse(r['findings'])
        self.assertTrue(any('missing is not zero' in u for u in r['unknowns']))

    def test_explicit_zero(self):
        p = fixture()
        p['observations'][1]['google_reviews'] = {'total_count': 0}
        self.assertIn('LOCAL_NO_GOOGLE_REVIEWS', [f['code'] for f in analyze_local_evidence(p)['findings']])

    def test_invalid_aggregate_values_never_become_warnings(self):
        for value in (-1, True, 1.1, '0'):
            p = fixture()
            p['observations'][1]['google_reviews'] = {'total_count': value}
            self.assertFalse(analyze_local_evidence(p)['findings'])
        for value in (0, 6, True, float('nan'), '3'):
            p = fixture()
            p['observations'][1]['google_reviews'] = {'rating': value}
            self.assertFalse(analyze_local_evidence(p)['findings'])

    def test_sample_never_substitutes_aggregate(self):
        p = fixture()
        p['observations'][1]['coverage'] = 'sample'
        self.assertFalse(analyze_local_evidence(p)['findings'])

    def test_wrong_branch_and_place_rejected(self):
        for key in ('branch_id', 'place_id', 'entity_id', 'market'):
            p = fixture()
            p['observations'][1][key] = 'fictional-other'
            r = analyze_local_evidence(p)
            self.assertEqual(1, len(r['rejected']))
            self.assertFalse(r['findings'])

    def test_future_bad_date_and_stale(self):
        for observed, captured in [('2027-01-01', '2027-01-01'), ('bad', '2026-10-15')]:
            p = fixture()
            p['observations'][1].update(observed_at=observed, captured_at=captured)
            self.assertTrue(analyze_local_evidence(p)['rejected'])
        p = fixture()
        p['observations'][1].update(observed_at='2026-08-01', captured_at='2026-08-01')
        self.assertFalse(analyze_local_evidence(p)['findings'])
        p['config'] = {'freshness_days': 90}
        self.assertTrue(analyze_local_evidence(p)['findings'])

    def test_conservative_nap(self):
        self.assertEqual(normalize_nap('phone', '+1 (202) 555-0100'), '+12025550100')
        self.assertNotEqual(normalize_nap('phone', '2025550100'), '+12025550100')
        p = fixture()
        p['observations'][0]['nap'].update(name=' FICTIONAL   WORKSHOP ', phone='+12025550100', address='12 example lane, unit 1')
        self.assertFalse(any(f['code'].startswith('LOCAL_NAP') for f in analyze_local_evidence(p)['findings']))
        p['observations'][0]['nap']['address'] = '12 Example Lane, Unit 2'
        self.assertTrue(any(f['code'] == 'LOCAL_NAP_ADDRESS' for f in analyze_local_evidence(p)['findings']))

    def test_hours_require_scope(self):
        p = fixture()
        hours = dict(timezone='Etc/UTC', regular={'Monday':'09:00-17:00'}, exceptions={}, effective_from='2026-10-01', effective_to='2026-10-31')
        for row in p['observations']:
            row['hours'] = copy.deepcopy(hours)
        p['observations'][0]['hours']['regular']['Monday'] = '10:00-17:00'
        self.assertTrue(any(f['code'] == 'LOCAL_HOURS_MISMATCH' for f in analyze_local_evidence(p)['findings']))
        p['observations'][1]['hours']['timezone'] = 'Europe/London'
        self.assertFalse(any(f['code'] == 'LOCAL_HOURS_MISMATCH' for f in analyze_local_evidence(p)['findings']))

    def test_aggregate_changes_sorted_and_sample_excluded(self):
        p = fixture()
        first = p['observations'][1]
        for i, day in enumerate(('2026-10-14', '2026-10-13')):
            row = copy.deepcopy(first)
            row.update(id='history'+str(i), observed_at=day, captured_at=day)
            row['google_reviews'].update(rating=3.1-i/10, total_count=2)
            p['observations'].append(row)
        changes = [x for x in analyze_local_evidence(p)['checked'] if x.get('comparison') == 'dated_aggregate_change']
        self.assertEqual(3, len(changes))
        self.assertTrue(all(x['rating_delta'] > 0 for x in changes))
        p['observations'][2]['coverage'] = 'sample'
        self.assertEqual(1, len([x for x in analyze_local_evidence(p)['checked'] if x.get('comparison') == 'dated_aggregate_change']))

    def test_markup_does_not_supply_google_rating(self):
        p = fixture()
        p['observations'] = p['observations'][:1]
        p['observations'][0]['localbusiness'] = {'@type':'LocalBusiness', 'name':'Fictional', 'aggregateRating':{'ratingValue':2,'reviewCount':1}}
        r = analyze_local_evidence(p)
        self.assertFalse(any('GOOGLE' in f['code'] for f in r['findings']))
        self.assertTrue(any(f['code'] == 'LOCALBUSINESS_FIELDS_REVIEW' for f in r['findings']))

    def test_local_subclass_and_provenance_preserved(self):
        p = fixture()
        row = p['observations'][1]
        row.update(source_method='fictional manual check', export_sha256='fictional-digest')
        row['localbusiness'] = {'@type': 'Restaurant', 'name': 'Fictional Kitchen'}
        result = analyze_local_evidence(p)
        self.assertTrue(any(f['code'] == 'LOCALBUSINESS_FIELDS_REVIEW' for f in result['findings']))
        self.assertTrue(any(x.get('field_roles', {}).get('telephone') == 'recommended field' for x in result['checked']))
        self.assertEqual('fictional manual check', result['findings'][0]['evidence'][0]['source_method'])

    def test_peer_requires_maturity_and_no_unsupported_benchmark(self):
        p = fixture()
        row = p['observations'][1]
        row.update(category='fictional-workshop', comparison_group='fictional-local')
        peer = copy.deepcopy(row)
        peer.update(id='peer', place_id='fictional-peer', branch_id='fictional-other', source_kind='peer_profile')
        p['peers'] = [peer]
        self.assertFalse(any(c.get('comparison') == 'supplied_peer' for c in analyze_local_evidence(p)['checked']))
        row['maturity_group'] = peer['maturity_group'] = 'established'
        self.assertTrue(any(c.get('comparison') == 'supplied_peer' for c in analyze_local_evidence(p)['checked']))

    def test_cli_preserves_existing_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)/'fixture.json'
            source.write_text(json.dumps(fixture()))
            out = Path(temp)/'output'
            command = [sys.executable, str(Path(__file__).resolve().parents[1]/'scripts/local_seo_evidence.py'), str(source), '--out', str(out)]
            self.assertEqual(0, subprocess.run(command, capture_output=True).returncode)
            self.assertTrue((out/'local-report.json').exists())
            self.assertNotEqual(0, subprocess.run(command, capture_output=True).returncode)


if __name__ == '__main__':
    unittest.main()
