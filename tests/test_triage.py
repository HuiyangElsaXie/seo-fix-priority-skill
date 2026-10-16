import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from scripts.triage import triage

ROOT=Path(__file__).resolve().parents[1]
def answer(value):
    return dict(value=value,status='self_reported',source_id='crawl',evidence_locator='fictional brief')

def fixture(**kw):
    r=dict(url='https://harbor.example/demo',source_id='crawl',evidence_locator='crawl.csv:2',status=200,intent='index',importance='critical',indexable=True,robots_blocked=False,title='Demo',canonical='https://harbor.example/demo',depth=1,inlinks=4)
    r.update(effort=5, business_impact=answer('Primary qualified-demo acquisition page'), visibility_reason=answer('Owner intends organic acquisition'))
    r.update(kw)
    return dict(schema_version='0.2',as_of='2026-10-16',business_context={'objective':'Demo enquiries','answers':{k:answer(v) for k,v in {'industry':'B2B software','audience':'Operations leaders','geography':'Canada','language':'English','primary_objective':'conversion','conversion_definition':'Qualified demo submission','resources':'One engineer','constraints':'No URL changes','specific_problem':'Demo page inaccessible'}.items()},'owners':{'engineering':'Web team','seo':'Marketing','content':'Editor'}},sources={'crawl':{'kind':'fictional_fixture','description':'Partial fictional crawl','observed_at':'2026-10-15'}},rows=[r])

class DecisionTests(unittest.TestCase):
    def test_nonindexable_critical_page(self):
        q=triage(fixture(indexable=False))['queue'][0]
        self.assertEqual((q['rule'],q['priority']),('NONINDEXABLE','P1'))
    def test_robots_blocked_intended_page(self):
        q=triage(fixture(robots_blocked=True))['queue'][0]
        self.assertEqual((q['rule'],q['priority']),('ROBOTS_BLOCKED','P1'))
    def test_depth_boundary(self):
        self.assertEqual(triage(fixture(depth=3))['queue'],[])
        self.assertEqual(triage(fixture(depth=4))['queue'][0]['rule'],'DEEP_PAGE')
    def test_cli_invalid_input_exit_code(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w',suffix='.json') as f:
            f.write('{"rows": []}'); f.flush()
            r=subprocess.run([sys.executable,str(ROOT/'scripts/triage.py'),f.name],capture_output=True,text=True)
        self.assertEqual(r.returncode,2); self.assertEqual(r.stdout,''); self.assertIn('Invalid input',r.stderr)
    def test_healthy_row_no_findings(self): self.assertEqual(triage(fixture())['queue'],[])
    def test_http_error_critical(self):
        q=triage(fixture(status=503))['queue'][0]
        self.assertEqual((q['rule'],q['priority'],q['score'],q['owner']),('HTTP_ERROR','P1',8.6,'Web team'))
    def test_unknown_lifecycle_not_auto_restore(self):
        q=triage(fixture(status=404,intent='unknown'))['queue'][0]
        self.assertEqual(q['priority'],'review'); self.assertTrue(q['gates'])
    def test_excluded_visibility_suppressed(self):
        r=triage(fixture(intent='exclude',indexable=False,robots_blocked=True,title='',depth=5,inlinks=0))
        self.assertEqual(r['queue'],[]);self.assertEqual(len(r['suppressed']),5)
    def test_excluded_http_error_still_review(self): self.assertEqual(triage(fixture(intent='exclude',status=404))['queue'][0]['priority'],'review')
    def test_canonical_difference_always_review(self): self.assertEqual(triage(fixture(canonical='https://harbor.example/other'))['queue'][0]['priority'],'review')
    def test_zero_inlinks_not_confirmed_orphan(self):
        q=triage(fixture(inlinks=0))['queue'][0]
        self.assertEqual(q['priority'],'review');self.assertIn('does not prove',q['proposed_fix'])
    def test_stale_high_score_gated(self):
        d=fixture(status=503);d['sources']['crawl']['observed_at']='2026-08-01'
        q=triage(d)['queue'][0];self.assertEqual((q['priority'],q['confidence']),('review','low'))
    def test_missing_signals_not_pass(self):
        d=fixture();del d['rows'][0]['title'];d['rows'][0]['indexable']=None
        r=triage(d);self.assertEqual(r['queue'],[]);self.assertIn('indexable',r['coverage_gaps'][0]['not_assessed'])
    def test_priority_then_score_sort(self):
        d=fixture(status=503);d['rows'] += [dict(d['rows'][0],url='https://harbor.example/low',importance='low'),dict(d['rows'][0],url='https://harbor.example/review',intent='unknown')]
        self.assertEqual([x['priority'] for x in triage(d)['queue']],['P1','P3','review'])
    def test_lower_business_importance_changes_score(self): self.assertGreater(triage(fixture(status=503))['queue'][0]['score'],triage(fixture(status=503,importance='low'))['queue'][0]['score'])
    def test_redirect_detected_on_3xx(self): self.assertEqual(triage(fixture(status=301,redirect_hops=3))['queue'][0]['rule'],'REDIRECT_CHAIN')
    def test_empty_and_whitespace_titles(self):
        for title in ('','   '): self.assertEqual(triage(fixture(title=title))['queue'][0]['rule'],'MISSING_TITLE')
    def test_no_title_rule_on_error_page(self): self.assertEqual(len(triage(fixture(status=404,title=''))['queue']),1)
    def test_unknown_importance_gated(self): self.assertEqual(triage(fixture(status=503,importance='unknown'))['queue'][0]['priority'],'review')
    def test_owner_missing_explicit(self):
        d=fixture(status=503);d['business_context']['owners']={}
        self.assertEqual(triage(d)['queue'][0]['owner'],'unassigned (engineering)')
    def test_no_input_mutation(self):
        d=fixture(status=503); original=copy.deepcopy(d);triage(d);self.assertEqual(d,original)
    def test_repeatable(self): self.assertEqual(triage(fixture(status=503)),triage(fixture(status=503)))
    def test_empty_rows_valid(self):
        d=fixture();d['rows']=[];self.assertEqual(triage(d)['summary']['supplied_urls'],0)
    def test_invalid_field_types(self):
        for kw in ({'status':True},{'status':700},{'indexable':'false'},{'robots_blocked':0},{'depth':-1},{'inlinks':False},{'title':0},{'effort':11},{'intent':'yes'},{'importance':'huge'},{'url':'file:///tmp/a'},{'url':'https://a:b@harbor.example'},{'canonical':'relative'},{'evidence_locator':''},{'source_id':'missing'}):
            with self.subTest(kw=kw), self.assertRaises(ValueError): triage(fixture(**kw))
    def test_future_evidence_rejected(self):
        d=fixture();d['sources']['crawl']['observed_at']='2026-11-01'
        with self.assertRaises(ValueError):triage(d)
    def test_duplicates_rejected(self):
        d=fixture();d['rows']*=2
        with self.assertRaises(ValueError):triage(d)
    def test_legacy_rejected(self):
        with self.assertRaises(ValueError):triage({'rows':[]})
    def test_output_contract(self):
        q=triage(fixture(status=503))['queue'][0]
        self.assertTrue({'id','rule','priority','score_inputs','confidence','observation','business_reason','owner','source_id','evidence_locator','gates','proposed_fix','verification','status'}<=q.keys())
    def test_source_snapshot_integrity(self):
        import hashlib
        manifest=json.loads((ROOT/'upstream/source-lock.json').read_text())
        for f in manifest['files']:
            b=(ROOT/f['local_path']).read_bytes()
            self.assertEqual(hashlib.sha256(b).hexdigest(),f['sha256'])
            self.assertEqual(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),f['git_blob_sha'])
if __name__=='__main__':unittest.main()
