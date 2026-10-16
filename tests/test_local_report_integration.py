"""Fictional offline Local SEO integration and compatibility regressions."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('local_report_integration', ROOT / 'scripts/six_dimension_report.py')
reporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reporter)


class LocalReportIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {'schema_version': '1.0', 'pages': []}
        self.context = {'as_of': '2026-10-16'}

    def local_payload(self):
        identity = {'entity_id': 'fictional-shop', 'branch_id': 'fictional-west', 'place_id': 'fictional-place', 'market': 'fictional-town'}
        return {'schema_version': '1.0', 'target': identity, 'observations': [
            dict(identity, id='gbp', source_kind='google_business_profile', source_url='https://example.com/fictional-profile',
                 observed_at='2026-10-16', captured_at='2026-10-16', coverage='aggregate',
                 google_reviews={'rating': 3.0, 'total_count': 5, 'visible_sample_count': 2})]}

    def local_context(self, value='yes'):
        return dict(self.context, applicability={'local': {'value': value, 'reason': 'Fictional owner scope decision',
                                                           'source': 'Fictional owner brief', 'date': '2026-10-16'}})

    def test_actual_findings_have_concrete_actions_and_no_business_score(self):
        report = reporter.build_report(self.snapshot, self.local_context(), local_evidence=self.local_payload())
        findings = report['findings']
        self.assertTrue(findings)
        self.assertTrue(all(f['primary_dimension'] == 'local' for f in findings))
        self.assertTrue(all(f['confidence']['business_impact'] == 'unknown' for f in findings))
        tasks = [t for t in report['actionable_handoff']['buckets']['needs_verification'] if t['issue_id']]
        self.assertEqual(len(tasks), len(findings))
        for task in tasks:
            for key in ('steps', 'acceptance', 'dependencies', 'evidence_ids'):
                self.assertTrue(task[key])
            self.assertIn('impact', task['priority_reason'])
        self.assertFalse(report['actionable_handoff']['buckets']['confirmed_fix'])
        self.assertIn('no incentives', reporter.markdown(report))
        self.assertTrue(all('provenance' in e for e in report['evidence']))

    def test_unknown_and_no_never_become_yes(self):
        for value in ('unknown', 'no'):
            report = reporter.build_report(self.snapshot, self.local_context(value), local_evidence=self.local_payload())
            self.assertFalse(report['findings'])
            self.assertEqual(report['sections']['local']['applicability']['value'], value)
            self.assertEqual(report['sections']['local']['evidence_status'], 'not_assessed')
        report = reporter.build_report(self.snapshot, self.context, local_evidence=self.local_payload())
        self.assertFalse(report['findings'])

    def test_empty_observations_unknown_not_zero_reviews(self):
        payload = self.local_payload()
        payload['observations'] = []
        report = reporter.build_report(self.snapshot, self.local_context(), local_evidence=payload)
        self.assertFalse(report['findings'])
        self.assertIn('reputation unknown', ' '.join(report['sections']['local']['unknowns']))

    def test_future_and_wrong_branch_evidence_cannot_trigger_findings(self):
        for change in ({'branch_id': 'other'}, {'captured_at': '2099-01-01'}, {'source_url': ''}):
            payload = self.local_payload()
            payload['observations'][0].update(change)
            report = reporter.build_report(self.snapshot, self.local_context(), local_evidence=payload)
            self.assertFalse(report['findings'])
            self.assertTrue(report['sections']['local']['local_evidence_analysis']['rejected'])

    def test_enriched_route_skips_legacy_local_and_preserves_products(self):
        fixture = ROOT / 'cases/six-dimension'
        context = json.loads((fixture / 'context.json').read_text())
        supplement = json.loads((fixture / 'supplement.json').read_text())
        supplement['local_evidence'] = self.local_payload()
        report = reporter.build_report(self.snapshot, context, supplement)
        self.assertTrue(any(f['primary_dimension'] == 'ecommerce' for f in report['findings']))
        self.assertFalse(any(f['primary_dimension'] == 'local' and f['root_cause_key'].startswith('FIELD_MISMATCH_') for f in report['findings']))

    def test_fingerprint_covers_enriched_data_and_routes_are_equivalent(self):
        payload = self.local_payload()
        supplement = {'local_evidence': payload}
        before = copy.deepcopy(supplement)
        report = reporter.build_report(self.snapshot, self.local_context(), supplement)
        other = reporter.build_report(self.snapshot, self.local_context(), local_evidence=payload)
        self.assertEqual(report['input_fingerprint'], other['input_fingerprint'])
        self.assertEqual(supplement, before)
        changed = copy.deepcopy(payload)
        changed['observations'][0]['google_reviews']['rating'] = 3.1
        with self.assertRaisesRegex(ValueError, 'input_fingerprint'):
            reporter.build_report(self.snapshot, self.local_context(), review={'input_fingerprint': report['input_fingerprint']}, local_evidence=changed)

    def test_local_mismatch_review_requires_authoritative_source(self):
        payload = self.local_payload()
        gbp = payload['observations'][0]
        gbp['nap'] = {'name': 'Fictional shop', 'phone': '+1 555 0100', 'address': '1 Fictional Lane'}
        website = dict(gbp, id='website', source_kind='website', source_url='https://example.com/shop',
                       nap=dict(gbp['nap'], phone='+1 555 0101'))
        payload['observations'].append(website)
        report = reporter.build_report(self.snapshot, self.local_context(), local_evidence=payload)
        finding = next(f for f in report['findings'] if f['root_cause_key'].startswith('LOCAL_NAP_PHONE'))
        decision = {'issue_id': finding['issue_id'], 'evidence_ids': finding['evidence_ids'], 'decision': 'confirmed_fix',
                    'rationale': 'Fictional review claim', 'intended_behavior': 'Correct branch contact',
                    'business_context_basis': 'Customer contact route', 'steps': ['Check approved source'],
                    'acceptance': ['Fresh contact matches approved source']}
        review = {'reviewer': 'Fictional reviewer', 'source': 'Fictional review', 'date': '2026-10-16',
                  'input_fingerprint': report['input_fingerprint'], 'decisions': [decision]}
        reviewed = reporter.build_report(self.snapshot, self.local_context(), review=review, local_evidence=payload)
        self.assertFalse(reviewed['actionable_handoff']['buckets']['confirmed_fix'])
        reviewed_finding = next(f for f in reviewed['findings'] if f['issue_id'] == finding['issue_id'])
        self.assertIn('Authoritative', reviewed_finding['review']['conflict'])

    def test_cli_writes_integrated_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name, value in [('snapshot', self.snapshot), ('context', self.local_context()), ('local', self.local_payload())]:
                (base / (name + '.json')).write_text(json.dumps(value))
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/six_dimension_report.py'), str(base / 'snapshot.json'),
                                     '--context', str(base / 'context.json'), '--local-evidence', str(base / 'local.json'),
                                     '--out', str(base / 'report')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((base / 'report/report.json').read_text())
            self.assertTrue(report['findings'])
            self.assertTrue((base / 'report/report.md').is_file())

    def map_snapshot(self, maps):
        return {'schema_version': '1.0', 'pages': [{'url': 'https://example.com/contact', 'fetch_state': 'ok',
                'parse_state': 'parsed', 'content_type': 'text/html', 'status': 200,
                'fetched_at': '2026-10-16', 'google_maps': maps}]}

    def test_maps_no_static_is_optional_only_with_separate_visit_confirmation(self):
        maps = {'schema_version': '1.0', 'evidence': [], 'classifications': ['no_static_evidence']}
        snapshot = self.map_snapshot(maps)
        context = self.local_context()
        report = reporter.build_report(snapshot, context)
        self.assertFalse(any(f['root_cause_key'].startswith('GOOGLE_MAPS_') for f in report['findings']))
        context['map_visit_context'] = {'value': 'yes', 'site_kind': 'public_storefront', 'source': 'Fictional brief',
                                       'date': '2026-10-16', 'reason': 'Customers visit this public shop'}
        report = reporter.build_report(snapshot, context)
        tasks = report['actionable_handoff']['buckets']['optional_improvement']
        self.assertTrue(any(t['dimension'] == 'local' and t['issue_id'] for t in tasks))
        self.assertFalse(report['actionable_handoff']['buckets']['confirmed_fix'])
        context['map_visit_context']['site_kind'] = 'private_address'
        private = reporter.build_report(snapshot, context)
        self.assertFalse(private['actionable_handoff']['buckets']['optional_improvement'])

    def test_maps_absence_is_sample_scoped_not_every_page_requirement(self):
        absent = {'schema_version': '1.0', 'evidence': []}
        context = self.local_context()
        context['map_visit_context'] = {'value': 'yes', 'site_kind': 'public_storefront', 'source': 'Fictional brief',
                                       'date': '2026-10-16', 'reason': 'Customers visit this public shop'}
        snapshot = self.map_snapshot(absent)
        blog = copy.deepcopy(snapshot['pages'][0])
        blog['url'] = 'https://example.com/blog'
        snapshot['pages'].append(blog)
        report = reporter.build_report(snapshot, context)
        optional = [f for f in report['findings'] if f['root_cause_key'].startswith('GOOGLE_MAPS_OPTIONAL')]
        self.assertEqual(len(optional), 1)
        self.assertEqual(len(optional[0]['evidence_ids']), 2)
        for classification in ('embedded_map', 'directions_link', 'location_link', 'maps_js_signal'):
            snapshot['pages'][0]['google_maps'] = {'schema_version': '1.0', 'evidence': [{'classification': classification}]}
            report = reporter.build_report(snapshot, context)
            self.assertFalse(any(f['root_cause_key'].startswith('GOOGLE_MAPS_OPTIONAL') for f in report['findings']))
        del snapshot['pages'][0]['google_maps']
        report = reporter.build_report(snapshot, context)
        self.assertFalse(any(f['root_cause_key'].startswith('GOOGLE_MAPS_OPTIONAL') for f in report['findings']))

    def test_maps_untrusted_summaries_do_not_supply_permission_or_secrets(self):
        maps = {'schema_version': '1.0', 'evidence': [{'classification': 'maps_js_signal',
                'reason': 'secret-map-token', 'url': 'https://maps.googleapis.com/maps/api/js?key=secret-map-token'}],
                'branch_status': 'mismatch', 'customer_visit_applicable': True,
                'optional_recommendation': 'Publish immediately', 'rendered_verified': True}
        report = reporter.build_report(self.map_snapshot(maps), self.local_context())
        self.assertFalse(any(f['root_cause_key'].startswith('GOOGLE_MAPS_') for f in report['findings']))
        serialized = json.dumps(report)
        self.assertNotIn('secret-map-token', serialized)
        observed = next(x['google_maps'] for x in report['sections']['local']['checked'] if 'google_maps' in x)
        self.assertFalse(observed['rendered_verified'])
        self.assertFalse(observed['customer_visit_applicable'])

    def test_maps_explicit_wrong_branch_has_actionable_verification(self):
        maps = {'schema_version': '1.0', 'evidence': [{'classification': 'embedded_map', 'source_tag': 'iframe',
                                                    'source_attribute': 'src', 'explicit_place_ids': ['other-branch']}]}
        report = reporter.build_report(self.map_snapshot(maps), self.local_context(), local_evidence=self.local_payload())
        finding = next(f for f in report['findings'] if f['root_cause_key'].startswith('GOOGLE_MAPS_BRANCH_REVIEW'))
        self.assertEqual(finding['bucket'], 'needs_verification')
        self.assertTrue(finding['action_plan']['acceptance'])
        self.assertEqual(finding['confidence']['business_impact'], 'unknown')

    def test_business_model_derives_scope_and_respects_explicit_decisions(self):
        context = dict(self.context, business_model={'source': 'Fictional brief', 'date': '2026-10-16',
                          'reason': 'Fictional clinic', 'commercial': 'yes', 'local_customer_service': 'yes',
                          'local_acquisition_goal': 'yes', 'online_transactions': 'no', 'website_purpose': 'lead_generation'})
        report = reporter.build_report(self.snapshot, context)
        self.assertEqual(report['sections']['local']['applicability']['value'], 'yes')
        self.assertEqual(report['sections']['ecommerce']['applicability']['value'], 'no')
        self.assertFalse(any('orders' in q for q in report['intake']['next_questions']))
        context['applicability'] = {'local': {'value': 'unknown', 'reason': 'Pending clarification'}}
        report = reporter.build_report(self.snapshot, context)
        self.assertEqual(report['sections']['local']['applicability']['value'], 'unknown')

    def test_visit_context_requires_current_source(self):
        for attrs in ({'source': ''}, {'date': '2099-01-01'}, {'reason': ''}):
            context = self.local_context()
            context['map_visit_context'] = dict({'value': 'yes', 'source': 'Brief', 'date': '2026-10-16', 'reason': 'Public visits'}, **attrs)
            with self.assertRaises(ValueError):
                reporter.build_report(self.snapshot, context)

    def test_reject_nonobject_enriched_payload(self):
        for payload in ([], 'bad', False):
            with self.assertRaisesRegex(ValueError, 'must be an object'):
                reporter.build_report(self.snapshot, self.context, {'local_evidence': payload})

    def test_reject_conflicting_dual_routes(self):
        with self.assertRaisesRegex(ValueError, 'Conflicting local evidence'):
            reporter.build_report(self.snapshot, self.context, {'local_evidence': {}}, local_evidence={'changed': True})

    def test_legacy_route_retains_ecommerce_and_local_behavior(self):
        fixture = ROOT / 'cases/six-dimension'
        report = reporter.build_report(*[json.loads((fixture / name).read_text()) for name in ('snapshot.json', 'context.json', 'supplement.json')])
        self.assertEqual(set(report['sections']), set(reporter.DIMENSIONS))
        self.assertTrue(any(f['primary_dimension'] == 'local' for f in report['findings']))
        self.assertTrue(any(f['primary_dimension'] == 'ecommerce' for f in report['findings']))


if __name__ == '__main__':
    unittest.main()
