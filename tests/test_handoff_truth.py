"""Independent recommendation-truth checks using entirely synthetic supplied data.

These assertions test bounded evidence and actionable handoff, not actual-site SEO
truth, Google index status, business impact, ranking gains, or offpage defect recall.
"""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'cases/actionable-handoff'
spec = importlib.util.spec_from_file_location('truth_reporter', ROOT / 'scripts/six_dimension_report.py')
reporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reporter)
BUCKETS = {'confirmed_fix', 'needs_verification', 'optional_improvement', 'keep_or_not_applicable'}


def inputs():
    return [json.loads((CASE / (n + '.json')).read_text()) for n in ('snapshot', 'context', 'supplement')]


def tasks(report):
    return [t for values in report['actionable_handoff']['buckets'].values() for t in values]


class HandoffTruthTests(unittest.TestCase):
    def setUp(self):
        self.snapshot, self.context, self.supplement = inputs()

    def report(self):
        return reporter.build_report(self.snapshot, self.context, self.supplement)

    def test_four_buckets_and_unique_tasks_cover_observed_signals(self):
        r = self.report()
        self.assertEqual(set(r['actionable_handoff']['buckets']), BUCKETS)
        ts = tasks(r)
        self.assertEqual(len(ts), len({t['task_id'] for t in ts}))
        for finding in r['findings']:
            matches = [t for t in ts if t.get('issue_id') == finding['issue_id']]
            self.assertEqual(len(matches), 1, finding['root_cause_key'])
        for bucket, values in r['actionable_handoff']['buckets'].items():
            self.assertTrue(all(t['bucket'] == bucket for t in values))

    def test_positive_signals_exist_across_five_detectable_dimensions(self):
        r = self.report()
        expected = {'technical': 'JSONLD_SHAPE', 'onpage_content': 'EMPTY_TITLE',
                    'local': 'FIELD_MISMATCH_PHONE', 'ecommerce': 'FIELD_MISMATCH_PRICE',
                    'international': 'HREFLANG_RETURN'}
        for dimension, code in expected.items():
            found = [f for f in r['findings'] if f['primary_dimension'] == dimension
                     and f['root_cause_key'].startswith(code + '|')]
            self.assertEqual(len(found), 1, (dimension, code))
        self.assertFalse(any(f['primary_dimension'] == 'offpage' for f in r['findings']))
        self.assertTrue(r['sections']['offpage']['checked'])

    def test_task_has_operational_steps_role_acceptance_and_traceable_evidence(self):
        r = self.report()
        evidence = {e['evidence_id']: e for e in r['evidence']}
        for t in tasks(r):
            for field in ('steps', 'acceptance'):
                self.assertIsInstance(t[field], list)
                self.assertTrue(t[field], (t['task_id'], field))
                self.assertTrue(all(isinstance(x, str) and len(x.strip()) >= 12 for x in t[field]))
            self.assertTrue(t['proposed_role'].strip())
            self.assertNotIn(t['proposed_role'].lower(), ('unassigned', 'unknown', 'tbd'))
            self.assertIsInstance(t['dependencies'], list)
            self.assertTrue(t['priority_reason'].strip())
            self.assertTrue(t['observed_basis'])
            for eid in t['evidence_ids']:
                self.assertIn(eid, evidence)
                e = evidence[eid]
                self.assertTrue(e['source'])
                self.assertNotEqual(e['date'], 'unknown')
                self.assertTrue(e['locator'])
            if t.get('issue_id'):
                self.assertTrue(t['evidence_ids'])

    def test_intent_sensitive_signals_never_become_automatic_fixes(self):
        r = self.report()
        intentional_codes = ('NOINDEX_REVIEW|', 'CANONICAL_REVIEW|', 'HTTP_ERROR|')
        ids = {f['issue_id'] for f in r['findings'] if f['root_cause_key'].startswith(intentional_codes)}
        self.assertEqual(len(ids), 3)
        for t in tasks(r):
            if t.get('issue_id') in ids:
                self.assertEqual(t['bucket'], 'needs_verification')
                self.assertTrue(t['dependencies'], t)

    def test_conflicting_reference_does_not_choose_authoritative_value(self):
        r = self.report()
        ids = {f['issue_id'] for f in r['findings'] if f['root_cause_key'].startswith('FIELD_MISMATCH_')}
        self.assertEqual(len(ids), 2)
        for t in tasks(r):
            if t.get('issue_id') in ids:
                self.assertEqual(t['bucket'], 'needs_verification')
                text = json.dumps(t).lower()
                self.assertTrue(any(x in text for x in ('authoritative', 'source of truth', 'approved value')), text)

    def test_offpage_missing_data_is_investigation_not_zero_backlinks_or_defect(self):
        self.supplement.pop('backlinks')
        r = self.report()
        self.assertFalse(any(f['primary_dimension'] == 'offpage' for f in r['findings']))
        offpage = [t for t in tasks(r) if t['dimension'] == 'offpage']
        self.assertTrue(offpage)
        self.assertFalse(any(t['bucket'] == 'confirmed_fix' for t in offpage))
        self.assertTrue(any('backlink' in json.dumps(t).lower() for t in offpage))
        self.assertIn('does not mean no backlinks', ' '.join(r['sections']['offpage']['unknowns']))

    def test_explicit_not_applicable_is_keep_not_missing_defect(self):
        for d in ('local', 'ecommerce', 'international'):
            self.context['applicability'][d].update(value='no', reason='Synthetic portfolio: this business feature is intentionally absent.')
        r = self.report()
        for d in ('local', 'ecommerce', 'international'):
            relevant = [t for t in tasks(r) if t['dimension'] == d]
            self.assertTrue(relevant)
            self.assertTrue(all(t['bucket'] == 'keep_or_not_applicable' for t in relevant))
            self.assertEqual(r['sections'][d]['issue_ids'], [])

    def test_missing_identity_prevents_product_fault_classification(self):
        self.supplement['products']['data'][0].pop('variant_id')
        r = self.report()
        self.assertFalse(any(f['primary_dimension'] == 'ecommerce' for f in r['findings']))
        self.assertTrue(any(t['dimension'] == 'ecommerce' and t['bucket'] == 'needs_verification' for t in tasks(r)))

    def test_different_currency_never_generates_price_mismatch_fix(self):
        self.supplement['products']['data'][0]['reference']['currency'] = 'USD'
        r = self.report()
        self.assertFalse(any(f['root_cause_key'].startswith('FIELD_MISMATCH_PRICE|') for f in r['findings']))
        for t in tasks(r):
            if t['dimension'] == 'ecommerce':
                self.assertNotEqual(t['bucket'], 'confirmed_fix')

    def test_invalid_or_future_comparison_dates_are_not_supported_mismatches(self):
        for value in ('not-a-date', '2099-01-01'):
            with self.subTest(observed_at=value):
                for key in ('local', 'products'):
                    self.supplement[key]['data'][0]['observed_at'] = value
                try:
                    r = self.report()
                except ValueError:
                    continue  # Explicit input rejection is also safe.
                self.assertFalse(any(f['primary_dimension'] in ('local', 'ecommerce') for f in r['findings']))

    def test_lab_cwv_and_unfetched_hreflang_target_are_unknown(self):
        self.supplement['cwv']['data'][0]['kind'] = 'lab'
        self.snapshot['pages'] = self.snapshot['pages'][:1]
        r = self.report()
        self.assertFalse(any(f['root_cause_key'].startswith(('CWV_', 'HREFLANG_RETURN|')) for f in r['findings']))
        self.assertTrue(any('reciprocity unknown' in x for x in r['sections']['international']['unknowns']))
        self.assertTrue(any(t['dimension'] == 'international' and t['bucket'] == 'needs_verification' for t in tasks(r)))

    def test_priority_remains_provisional_without_business_owner_effort_evidence(self):
        r = self.report()
        for f in r['findings']:
            self.assertEqual(f['priority']['value'], 'pending')
            self.assertTrue(f['priority']['provisional'])
        self.assertNotIn('health_score', r)
        self.assertNotIn('revenue_gain', r)


    def review_decision(self, code, decision='confirmed_fix', **extra):
        r = self.report()
        f = next(f for f in r['findings'] if f['root_cause_key'].startswith(code + '|'))
        d = {'issue_id': f['issue_id'], 'evidence_ids': f['evidence_ids'], 'decision': decision,
             'rationale': 'Synthetic reviewer checked this exact scoped observation against the fixture brief.',
             'intended_behavior': 'Synthetic visible page has a valid descriptive title and valid JSON-LD.',
             'business_context_basis': 'Entirely fictional owner brief: this public page supports product discovery.',
             'steps': ['Repair the exact reviewed field in the synthetic template and capture the new HTML.'],
             'acceptance': ['The fresh saved HTML contains the approved value and the scoped check no longer fails.']}
        d.update(extra)
        return {'reviewer': 'Synthetic QA reviewer', 'source': 'Synthetic review ledger, not an actual audit',
                'date': '2026-10-16', 'decisions': [d]}

    def test_supported_review_can_confirm_bounded_fix(self):
        review = self.review_decision('JSONLD_SHAPE')
        r = reporter.build_report(self.snapshot, self.context, self.supplement, review=review)
        matched = [t for t in tasks(r) if t.get('issue_id') == review['decisions'][0]['issue_id']]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]['bucket'], 'confirmed_fix')
        self.assertIn('Synthetic QA reviewer', json.dumps(matched[0]))
        self.assertIn('2026-10-16', json.dumps(matched[0]))
        reviewed = next(f for f in r['findings'] if f['issue_id'] == review['decisions'][0]['issue_id'])
        self.assertEqual(reviewed['priority']['value'], 'reviewed_fix_sequence')
        self.assertTrue(reviewed['priority']['provisional'])
        self.assertIn(review['decisions'][0]['rationale'], reviewed['priority']['reason'])
        self.assertTrue(all(f['priority']['value'] == 'pending' for f in r['findings'] if f['issue_id'] != reviewed['issue_id']))

    def test_intentional_exclusion_review_can_preserve_noindex(self):
        review = self.review_decision('NOINDEX_REVIEW', decision='keep_or_not_applicable',
                                     visibility_intent='exclude', intended_behavior='Private synthetic page must remain excluded.')
        r = reporter.build_report(self.snapshot, self.context, self.supplement, review=review)
        t = next(t for t in tasks(r) if t.get('issue_id') == review['decisions'][0]['issue_id'])
        self.assertEqual(t['bucket'], 'keep_or_not_applicable')

    def test_conflicting_visibility_review_cannot_confirm_removing_noindex(self):
        review = self.review_decision('NOINDEX_REVIEW', visibility_intent='exclude',
                                     intended_behavior='Private synthetic page must remain excluded.',
                                     steps=['Remove noindex from the private synthetic page.'])
        r = reporter.build_report(self.snapshot, self.context, self.supplement, review=review)
        t = next(t for t in tasks(r) if t.get('issue_id') == review['decisions'][0]['issue_id'])
        self.assertEqual(t['bucket'], 'needs_verification')

    def test_mismatched_or_missing_review_evidence_cannot_confirm_fix(self):
        for ids in ([], ['e-not-present']):
            review = self.review_decision('JSONLD_SHAPE', evidence_ids=ids)
            try:
                r = reporter.build_report(self.snapshot, self.context, self.supplement, review=review)
            except ValueError:
                continue
            self.assertFalse(r['actionable_handoff']['buckets']['confirmed_fix'])

    def test_reference_conflict_review_requires_authoritative_source(self):
        review = self.review_decision('FIELD_MISMATCH_PRICE')
        r = reporter.build_report(self.snapshot, self.context, self.supplement, review=review)
        t = next(t for t in tasks(r) if t.get('issue_id') == review['decisions'][0]['issue_id'])
        self.assertEqual(t['bucket'], 'needs_verification')


    def test_future_supplement_cannot_establish_current_mismatch(self):
        for key in ('local', 'products', 'cwv'):
            self.supplement[key]['date'] = '2099-01-01'
        r = self.report()
        self.assertFalse(any(f['root_cause_key'].startswith(('FIELD_MISMATCH_', 'CWV_')) for f in r['findings']))

    def test_review_cannot_predate_cited_observation(self):
        review = self.review_decision('JSONLD_SHAPE')
        review['date'] = '2026-01-01'
        try:
            r = reporter.build_report(self.snapshot, self.context, self.supplement, review=review)
        except ValueError:
            return
        self.assertFalse(r['actionable_handoff']['buckets']['confirmed_fix'])

    def test_offpage_section_review_is_scoped_keep_not_defect_detection(self):
        r = self.report()
        ids = [e['evidence_id'] for e in r['evidence'] if e['locator'] == 'backlinks:data']
        self.assertTrue(ids)
        review = {'reviewer': 'Synthetic QA reviewer', 'date': '2026-10-16',
                  'source': 'Synthetic backlink sample inspection', 'section_reviews': [{
                      'dimension': 'offpage', 'evidence_ids': ids, 'decision': 'keep_or_not_applicable',
                      'rationale': 'No action established by this one supplied synthetic backlink record.',
                      'intended_behavior': 'Retain this sample without inferring liveness or whole-profile quality.',
                      'business_context_basis': 'Fictional awareness brief; complete reputation evidence is missing.'}]}
        r = reporter.build_report(self.snapshot, self.context, self.supplement, review=review)
        self.assertTrue(any(t['dimension'] == 'offpage' for t in r['actionable_handoff']['buckets']['keep_or_not_applicable']))
        self.assertTrue(r['sections']['offpage']['unknowns'])
        self.assertFalse(any(f['primary_dimension'] == 'offpage' for f in r['findings']))


    def test_section_keep_never_clears_unreviewed_findings(self):
        r = self.report()
        f = next(f for f in r['findings'] if f['primary_dimension'] == 'technical')
        review = {'reviewer': 'Synthetic QA reviewer', 'date': '2026-10-16', 'source': 'Synthetic scoped note',
                  'section_reviews': [{'dimension': 'technical', 'evidence_ids': f['evidence_ids'],
                    'decision': 'keep_or_not_applicable', 'rationale': 'Only one bounded observation reviewed.',
                    'intended_behavior': 'Preserve only the explicitly scoped behavior.',
                    'business_context_basis': 'Synthetic brief does not establish whole-site health.'}]}
        r = reporter.build_report(self.snapshot, self.context, self.supplement, review=review)
        self.assertEqual(next(t for t in tasks(r) if t.get('issue_id') == f['issue_id'])['bucket'], 'needs_verification')
        self.assertEqual(r['sections']['technical']['semantic_review'], 'pending')
        self.assertTrue(r['sections']['technical']['unknowns'])

    def test_future_or_malformed_review_date_rejected(self):
        for date in ('2099-01-01', 'not-a-date'):
            review = self.review_decision('JSONLD_SHAPE')
            review['date'] = date
            with self.assertRaises(ValueError):
                reporter.build_report(self.snapshot, self.context, self.supplement, review=review)

    def test_other_findings_evidence_cannot_confirm_cross_entity_fix(self):
        review = self.review_decision('FIELD_MISMATCH_PRICE', authoritative_source='Synthetic current catalog')
        local = next(f for f in self.report()['findings'] if f['primary_dimension'] == 'local')
        review['decisions'][0]['evidence_ids'] = local['evidence_ids']
        with self.assertRaises(ValueError):
            reporter.build_report(self.snapshot, self.context, self.supplement, review=review)


    def test_fingerprint_bound_review_rejects_changed_same_locator_content(self):
        review = self.review_decision('FIELD_MISMATCH_PRICE', authoritative_source='Synthetic current catalog')
        review['input_fingerprint'] = self.report()['input_fingerprint']
        self.supplement['products']['data'][0]['reference']['price'] = '14.00'
        with self.assertRaises(ValueError):
            reporter.build_report(self.snapshot, self.context, self.supplement, review=review)


if __name__ == '__main__':
    unittest.main()
