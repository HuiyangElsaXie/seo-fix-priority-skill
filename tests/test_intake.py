import copy
import unittest
from scripts.triage import triage, root_equivalent
from test_triage import fixture, answer

class IntakeTests(unittest.TestCase):
    def test_tailored_and_general_same_observation(self):
        d=fixture(status=503);a=triage(d)
        del d['business_context']['answers']['specific_problem'];b=triage(d)
        self.assertEqual(a['intake']['mode'],'tailored')
        self.assertEqual(b['intake']['mode'],'industry_general')
        self.assertEqual(a['queue'][0]['observation'],b['queue'][0]['observation'])
        self.assertEqual((b['queue'][0]['priority'],b['queue'][0]['score']),('review',None))
    def test_no_industry_generic(self):
        d=fixture(status=503);d['business_context'].pop('answers')
        o=triage(d);self.assertEqual(o['intake']['mode'],'generic_framework');self.assertIsNone(o['queue'][0]['score'])
    def test_unknown_valid_and_no_fabricated_score(self):
        d=fixture(status=503,importance='unknown');d['business_context']['answers']['industry']={'status':'unknown','value':None}
        q=triage(d)['queue'][0];self.assertIsNone(q['score']);self.assertIsNone(q['score_inputs']['business_importance'])
    def test_assumption_cannot_unlock(self):
        d=fixture(status=503);d['business_context']['answers']['specific_problem']={'status':'assumption','value':'Lost revenue'}
        self.assertIsNone(triage(d)['queue'][0]['score'])
    def test_unproven_brand_position_not_impact(self):
        d=fixture(status=503);d['business_context']['answers']['positioning']=answer('Market leader');d['rows'][0].pop('business_impact')
        self.assertIsNone(triage(d)['queue'][0]['score'])
    def test_conversion_branch(self):
        d=fixture(status=503);d['business_context']['answers'].pop('conversion_definition')
        self.assertEqual(triage(d)['intake']['mode'],'industry_general')
        d['business_context']['answers']['primary_objective']=answer('awareness')
        self.assertEqual(triage(d)['intake']['mode'],'tailored')
    def test_mixed_requires_explicit_tradeoff(self):
        d=fixture(status=503);d['business_context']['answers']['primary_objective']=answer('mixed')
        self.assertIsNone(triage(d)['queue'][0]['score'])
        d['business_context']['answers']['objective_tradeoff']=answer('Conversion first this quarter; awareness secondary')
        self.assertEqual(triage(d)['intake']['mode'],'tailored')
    def test_consideration_supported(self):
        d=fixture(status=503);d['business_context']['answers']['primary_objective']=answer('consideration')
        self.assertEqual(triage(d)['intake']['mode'],'tailored')
    def test_reuse_supplied_answers(self):
        o=triage(fixture());self.assertNotIn('industry',[q['field'] for q in o['intake']['questions']])
    def test_unknown_healthy_page_still_has_questions(self):
        d=fixture(intent='unknown');o=triage(d);self.assertEqual(o['queue'],[]);self.assertTrue(o['intake']['page_questions'])
    def test_no_effort_no_score(self):
        d=fixture(status=503);d['rows'][0].pop('effort');q=triage(d)['queue'][0];self.assertIsNone(q['score']);self.assertIsNone(q['score_inputs']['effort'])
    def test_invalid_answers(self):
        for a in ('unknown',{'status':'unknown','value':'known'}, {'status':'confirmed','value':'leader'}, {'status':'guess','value':'leader'}):
            d=fixture();d['business_context']['answers']['industry']=a
            with self.assertRaises(ValueError):triage(d)
    def test_intentional_exclusion_protected(self):
        d=fixture(intent='exclude',indexable=False,canonical='https://harbor.example/other');o=triage(d)
        self.assertFalse(o['queue']);self.assertEqual(len(o['suppressed']),2)
    def test_narrow_root_normalization(self):
        self.assertTrue(root_equivalent('https://a.example','https://a.example/'))
        for a,b in [('https://a.example/page','https://a.example/page/'),('http://a.example','https://a.example/'),('https://a.example?x=1','https://a.example/'),('https://a.example#x','https://a.example/'),('https://a.example','https://b.example/')]:
            self.assertFalse(root_equivalent(a,b))
        d=fixture(url='https://harbor.example/',canonical='https://harbor.example');self.assertFalse(triage(d)['queue'])
    def test_stale_context_gated(self):
        d=fixture(status=503);d['sources']['brief']={'kind':'fictional_fixture','description':'Old brief','observed_at':'2026-01-01'}
        d['rows'][0]['business_impact']['source_id']='brief';self.assertIsNone(triage(d)['queue'][0]['score'])
if __name__=='__main__':unittest.main()
