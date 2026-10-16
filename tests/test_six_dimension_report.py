"""Offline contract/regression tests. Every URL and metric is fictional."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('six_dimension_report', ROOT / 'scripts/six_dimension_report.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(name):
    return json.loads((ROOT / 'cases/six-dimension' / name).read_text())


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = fixture('snapshot.json')
        self.context = fixture('context.json')
        self.supplement = fixture('supplement.json')

    def test_malformed_sources_never_unlock_tailored(self):
        for source in ({}, {'description':'brief', 'kind':'fictional_fixture', 'observed_at':'bad-date'},
                       {'description':'brief', 'kind':'fictional_fixture', 'observed_at':'2099-01-01'}):
            context = {'as_of':'2026-10-16', 'sources':{'brief':source}, 'business_context':{'answers':{
                k:{'value':'awareness' if k == 'primary_objective' else 'Known answer',
                   'status':'self_reported','source_id':'brief','evidence_locator':'brief'} for k in module.ESSENTIAL}}}
            r = module.build_report(self.snapshot, context)
            self.assertEqual(r['intake']['mode'], 'generic_framework')
            self.assertEqual(r['intake']['invalid_source_ids'], ['brief'])

    def test_valid_dated_sources_allow_tailored_without_claiming_truth(self):
        context = copy.deepcopy(self.context)
        context['as_of'] = '2026-10-16'
        context['business_context']['answers'] = {
            k:{'value':'awareness' if k == 'primary_objective' else 'Known answer',
               'status':'self_reported','source_id':'brief','evidence_locator':'brief'} for k in module.ESSENTIAL}
        r = module.build_report(self.snapshot, context, self.supplement)
        self.assertEqual(r['intake']['mode'], 'tailored')
        for s in r['sections'].values():
            self.assertEqual(s['confidence']['source_truth'], 'not_independently_verified')
            self.assertIn('deterministic', s['evidence_status_meaning'])
            self.assertEqual(s['semantic_review'], 'pending')
        for f in r['findings']:
            self.assertEqual(f['confidence']['business_impact'], 'unknown')
            self.assertEqual(f['confidence']['classification'], 'reproducible_rule_match_in_supplied_input')

    def test_all_six_and_industry_general(self):
        r = module.build_report(self.snapshot, self.context, self.supplement)
        self.assertEqual(set(r['sections']), set(module.DIMENSIONS))
        self.assertEqual(r['intake']['mode'], 'industry_general')
        self.assertTrue(all(s['applicability']['value'] == 'yes' for s in r['sections'].values()))
        self.assertTrue(all(s['semantic_review'] == 'pending' for s in r['sections'].values()))
        self.assertTrue(all(s['evidence_status'] != 'not_assessed' for s in r['sections'].values()))
        self.assertTrue(r['evidence'])

    def test_missing_data_is_not_good_health(self):
        r = module.build_report(self.snapshot)
        self.assertEqual(r['intake']['mode'], 'generic_framework')
        self.assertEqual(r['sections']['offpage']['evidence_status'], 'not_assessed')
        for k in ('local', 'international', 'ecommerce'):
            self.assertEqual(r['sections'][k]['applicability']['value'], 'unknown')
        self.assertNotIn('health_score', r)
        self.assertFalse(any('CWV_' in f['root_cause_key'] for f in r['findings']))

    def test_na_has_reason_not_missing_data_penalty(self):
        r = module.build_report(self.snapshot, fixture('portfolio-context.json'), self.supplement)
        for k in ('local', 'international', 'ecommerce'):
            self.assertEqual(r['sections'][k]['applicability']['value'], 'no')
            self.assertEqual(r['sections'][k]['issue_ids'], [])
        self.assertFalse(any('HREFLANG' in f['root_cause_key'] for f in r['findings']))

    def test_no_inference_from_product_or_city(self):
        r = module.build_report(self.snapshot)
        self.assertEqual(r['sections']['ecommerce']['applicability']['value'], 'unknown')
        self.snapshot['pages'][0]['title'] = 'Vancouver local service ecommerce career case study'
        self.assertEqual(module.build_report(self.snapshot)['sections']['local']['applicability']['value'], 'unknown')

    def test_deduplicated_product_mismatch_and_metadata_candidates(self):
        self.supplement['products']['data'] *= 2
        r = module.build_report(self.snapshot, self.context, self.supplement)
        matches = [f for f in r['findings'] if f['root_cause_key'].startswith('FIELD_MISMATCH_PRICE')]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['primary_dimension'], 'ecommerce')
        self.assertIn(matches[0]['issue_id'], r['sections']['onpage_content']['issue_ids'])
        duplicates = [f for f in r['findings'] if f['root_cause_key'].startswith('DUPLICATE_TITLE')]
        self.assertEqual(len(duplicates), 1)
        self.assertIn('not a ranking-penalty diagnosis', duplicates[0]['recommendation'])

    def test_cwv_rejects_lab_and_missing_scope(self):
        self.supplement['cwv']['data'][0]['kind'] = 'lab'
        r = module.build_report(self.snapshot, self.context, self.supplement)
        self.assertFalse(any('CWV_' in f['root_cause_key'] for f in r['findings']))
        self.assertTrue(any('rejected' in s for s in r['sections']['technical']['unknowns']))
        self.supplement['cwv']['data'][0]['kind'] = 'field'
        del self.supplement['cwv']['data'][0]['device']
        r = module.build_report(self.snapshot, self.context, self.supplement)
        self.assertFalse(any('CWV_' in f['root_cause_key'] for f in r['findings']))

    def test_actual_supplied_field_threshold(self):
        r = module.build_report(self.snapshot, self.context, self.supplement)
        self.assertEqual(len([f for f in r['findings'] if 'CWV_LCP' in f['root_cause_key']]), 1)
        self.assertTrue(all(f['priority']['value'] == 'pending' for f in r['findings']))

    def test_hreflang_return_only_collected_target(self):
        r = module.build_report(self.snapshot, self.context)
        self.assertTrue(any('HREFLANG_RETURN' in f['root_cause_key'] for f in r['findings']))
        self.snapshot['pages'] = self.snapshot['pages'][:1]
        r = module.build_report(self.snapshot, self.context)
        self.assertFalse(any('HREFLANG_RETURN' in f['root_cause_key'] for f in r['findings']))
        self.assertTrue(any('reciprocity unknown' in s for s in r['sections']['international']['unknowns']))

    def test_identity_time_and_currency_gates(self):
        del self.supplement['products']['data'][0]['variant_id']
        r = module.build_report(self.snapshot, self.context, self.supplement)
        self.assertFalse(any(f['primary_dimension'] == 'ecommerce' for f in r['findings']))
        self.supplement = fixture('supplement.json')
        self.supplement['products']['data'][0]['reference']['currency'] = 'USD'
        r = module.build_report(self.snapshot, self.context, self.supplement)
        self.assertFalse(any('FIELD_MISMATCH_PRICE' in f['root_cause_key'] for f in r['findings']))

    def test_collector_jsonld_and_header_schema(self):
        p = self.snapshot['pages'][0]
        p['jsonld'] = [{'valid_json': False, 'raw_excerpt': '{broken'}]
        p['response_headers'] = {'x-robots-tag': 'noindex'}
        r = module.build_report(self.snapshot)
        self.assertTrue(any('JSONLD_SHAPE' in f['root_cause_key'] for f in r['findings']))
        self.assertTrue(any('NOINDEX_REVIEW' in f['root_cause_key'] for f in r['findings']))

    def test_supplement_provenance_required(self):
        del self.supplement['backlinks']['source']
        with self.assertRaises(ValueError):
            module.build_report(self.snapshot, self.context, self.supplement)

    def test_no_network_dependencies_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'new'
            cmd = [sys.executable, str(ROOT / 'scripts/six_dimension_report.py'), str(ROOT / 'cases/six-dimension/snapshot.json'), '--out', str(out)]
            first = subprocess.run(cmd, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue((out / 'report.md').exists())
            previous = (out / 'report.json').read_bytes()
            second = subprocess.run(cmd, capture_output=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(previous, (out / 'report.json').read_bytes())

    def test_graph_is_sample_only_and_no_orphan_finding(self):
        r = module.build_report(self.snapshot)
        graph = next(c for c in r['sections']['technical']['checked'] if 'internal_graph' in c)
        self.assertTrue(graph['sample_only'])
        self.assertEqual(graph['orphan_assessment'], 'unknown')
        self.assertFalse(any('ORPHAN' in f['root_cause_key'] for f in r['findings']))

    def test_non_html_parsed_and_missing_media_type_are_not_metadata_candidates(self):
        for media in ('text/plain', 'application/xml', 'application/json', '', None):
            p = self.snapshot['pages'][0]
            p['content_type'] = media
            p['parse_state'] = 'parsed'
            p['title'] = ''
            p['meta_description'] = ''
            r = module.build_report(self.snapshot)
            self.assertFalse(any(f['subject'] == p['url'] and f['root_cause_key'].startswith(('EMPTY_', 'JSONLD_', 'CANONICAL_')) for f in r['findings']))
        p['content_type'] = 'text/html; charset=utf-8'
        r = module.build_report(self.snapshot)
        self.assertTrue(any(f['subject'] == p['url'] and f['root_cause_key'].startswith('EMPTY_TITLE') for f in r['findings']))

    def test_unparsed_empty_fields_are_unknown_not_missing(self):
        self.snapshot['pages'][0]['parse_state'] = 'not_html'
        self.snapshot['pages'][0]['title'] = ''
        r = module.build_report(self.snapshot)
        url = self.snapshot['pages'][0]['url']
        self.assertFalse(any(f['subject'] == url and f['root_cause_key'].startswith(('EMPTY_', 'JSONLD_', 'CANONICAL_')) for f in r['findings']))
        self.assertTrue(any('parse not confirmed' in x for x in r['sections']['onpage_content']['unknowns']))

    def test_error_status_and_timestamps_per_section(self):
        self.snapshot['errors'] = [{'url':'https://fictional.example/blocked','error':'timeout'}]
        r = module.build_report(self.snapshot)
        for s in r['sections'].values():
            self.assertEqual(s['collection_error_status'], 'errors_present')
            self.assertEqual(s['source_timestamps']['collection_finished_at'], '2026-10-16T00:00:01Z')


if __name__ == '__main__':
    unittest.main()
