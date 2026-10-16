"""Independent adversarial checks. Entirely fictional evidence; no live SEO claims."""
import copy
import importlib.util
import json
import itertools
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / 'cases/local-evidence'
spec = importlib.util.spec_from_file_location('local_truth_subject', ROOT / 'scripts/local_seo_evidence.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(name='substantial-low-rating'):
    return json.loads((CASES / (name + '.json')).read_text())


def codes(report):
    return {x['code'] for x in report['findings']}


class LocalEvidenceTruthTests(unittest.TestCase):
    def setUp(self):
        self.payload = fixture()
        self.site, self.profile = self.payload['observations']

    def report(self):
        return module.analyze_local_evidence(self.payload)

    def test_unknown_is_not_zero(self):
        r = module.analyze_local_evidence(fixture('unknown-reputation'))
        self.assertNotIn('LOCAL_NO_GOOGLE_REVIEWS', codes(r))
        self.assertTrue(any('missing is not zero' in x for x in r['unknowns']))

    def test_explicit_zero_is_distinct(self):
        r = module.analyze_local_evidence(fixture('explicit-zero'))
        self.assertIn('LOCAL_NO_GOOGLE_REVIEWS', codes(r))
        self.assertNotIn('LOCAL_LOW_GOOGLE_RATING', codes(r))

    def test_low_rating_sample_size_changes_confidence(self):
        substantial = next(x for x in self.report()['findings'] if x['code'] == 'LOCAL_LOW_GOOGLE_RATING')
        self.profile['google_reviews'].update(total_count=2, visible_sample_count=2)
        tiny = next(x for x in self.report()['findings'] if x['code'] == 'LOCAL_LOW_GOOGLE_RATING')
        self.assertEqual(tiny['confidence'], 'low')
        self.assertNotEqual(tiny['confidence'], substantial['confidence'])

    def test_invalid_counts_never_become_low_volume(self):
        for value in (True, -1, 1.5, '0'):
            with self.subTest(value=value):
                self.profile['google_reviews']['total_count'] = value
                r = self.report()
                self.assertFalse(codes(r) & {'LOCAL_NO_GOOGLE_REVIEWS', 'LOCAL_LOW_GOOGLE_REVIEW_COUNT'})
                self.assertTrue(any('invalid total_count' in x for x in r['unknowns']))

    def test_invalid_ratings_never_warn_low_rating(self):
        for value in (True, 0, -1, 5.1, '2', float('nan')):
            with self.subTest(value=value):
                self.profile['google_reviews']['rating'] = value
                self.assertNotIn('LOCAL_LOW_GOOGLE_RATING', codes(self.report()))

    def test_zero_with_rating_is_conflict(self):
        self.profile['google_reviews'].update(total_count=0, visible_sample_count=0)
        r = self.report()
        self.assertFalse(codes(r) & {'LOCAL_NO_GOOGLE_REVIEWS', 'LOCAL_LOW_GOOGLE_RATING'})
        self.assertTrue(any('conflicting zero' in x for x in r['unknowns']))

    def test_partial_visible_samples_do_not_establish_population_or_trend(self):
        r = module.analyze_local_evidence(fixture('partial-visible-sample'))
        self.assertFalse(codes(r) & {'LOCAL_LOW_GOOGLE_REVIEW_COUNT', 'LOCAL_LOW_GOOGLE_RATING'})
        self.assertFalse(any(x.get('comparison') == 'dated_aggregate_change' for x in r['checked']))
        self.assertTrue(any('aggregate rating/count unknown' in x for x in r['unknowns']))

    def test_sample_larger_than_population_withholds_aggregate(self):
        self.profile['google_reviews']['visible_sample_count'] = 121
        self.assertNotIn('LOCAL_LOW_GOOGLE_RATING', codes(self.report()))

    def test_stale_current_claims_withheld(self):
        self.profile.update(observed_at='2026-01-01', captured_at='2026-01-01')
        r = self.report()
        self.assertNotIn('LOCAL_LOW_GOOGLE_RATING', codes(r))
        self.assertTrue(any('stale' in x for x in r['unknowns']))

    def test_future_and_invalid_times_rejected(self):
        for value in ('2099-01-01', 'bad-date', '2026-10-16T10:00:00'):
            with self.subTest(value=value):
                self.profile.update(observed_at=value,captured_at=value)
                r = self.report()
                self.assertTrue(r['rejected'])
                self.assertNotIn('LOCAL_LOW_GOOGLE_RATING', codes(r))

    def test_observation_after_capture_rejected(self):
        self.profile.update(observed_at='2026-10-16', captured_at='2026-10-15')
        self.assertTrue(self.report()['rejected'])

    def test_each_wrong_identity_component_rejected(self):
        for key in ('entity_id','branch_id','place_id','market'):
            with self.subTest(key=key):
                p=fixture(); p['observations'][1][key]='other-fictional-value'
                r=module.analyze_local_evidence(p)
                self.assertTrue(r['rejected'])
                self.assertNotIn('LOCAL_LOW_GOOGLE_RATING',codes(r))

    def test_nap_formatting_only_equal(self):
        self.profile['nap'].update(name='  FICTIONAL   FERN studio ', address='10 example road   UNIT 2', phone='+1-202-555-0100')
        self.assertFalse(any(x.startswith('LOCAL_NAP_') for x in codes(self.report())))

    def test_nap_semantic_differences_preserved(self):
        for field, value in [('name','Different Studio'),('address','10 Example Road Unit 3'),('phone','+1 202 555 0199')]:
            with self.subTest(field=field):
                p=fixture();p['observations'][1]['nap'][field]=value
                self.assertIn('LOCAL_NAP_'+field.upper(), codes(module.analyze_local_evidence(p)))

    def test_country_prefix_not_invented(self):
        self.profile['nap']['phone']='2025550100'
        self.assertIn('LOCAL_NAP_PHONE',codes(self.report()))

    def test_noncontemporaneous_nap_withheld(self):
        self.profile['nap']['phone']='+1 202 555 0199'
        self.profile.update(observed_at='2026-10-10', captured_at='2026-10-10')
        self.assertNotIn('LOCAL_NAP_PHONE',codes(self.report()))

    def test_no_peers_has_no_relative_performance(self):
        self.assertFalse(any(x.get('comparison')=='supplied_peer' for x in self.report()['checked']))

    def peer(self):
        peer=copy.deepcopy(self.profile)
        peer.update(id='fictional-peer',entity_id='fictional-other',branch_id='fictional-other-branch',place_id='fictional-other-place',source_kind='peer_profile')
        self.payload['peers']=[peer]
        return peer

    def test_valid_peer_is_bounded_comparison_only(self):
        self.peer()
        values=[x for x in self.report()['checked'] if x.get('comparison')=='supplied_peer']
        self.assertEqual(len(values),1)
        self.assertEqual(values[0]['confidence'],'low')
        self.assertIn('no market benchmark',values[0]['interpretation'])

    def test_bad_peer_comparability_withheld(self):
        for key,value in [('market','elsewhere'),('category','other'),('comparison_group','other'),('maturity_group','other'),('maturity_group',None),('coverage','sample'),('place_id','fictional-place-north'),('observed_at','2026-10-10')]:
            with self.subTest(key=key):
                self.payload=fixture();self.site,self.profile=self.payload['observations'];peer=self.peer();peer[key]=value
                self.assertFalse(any(x.get('comparison')=='supplied_peer' for x in self.report()['checked']))

    def test_localbusiness_missing_fields_bounded_to_supplied_node(self):
        self.site['localbusiness']={'@type':'LocalBusiness','name':'Fictional Fern Studio'}
        r=self.report(); f=next(x for x in r['findings'] if x['code']=='LOCALBUSINESS_FIELDS_REVIEW')
        self.assertIn('not a complete eligibility decision',f['reason'])
        self.assertEqual(f['evidence_ids'],[self.site['id']])

    def test_markup_does_not_establish_google_reputation(self):
        self.payload['observations']=[self.site]
        self.site['localbusiness']['aggregateRating']={'ratingValue':1,'reviewCount':0}
        self.assertFalse(codes(self.report()) & {'LOCAL_LOW_GOOGLE_RATING','LOCAL_NO_GOOGLE_REVIEWS'})

    def test_localbusiness_invalid_shapes_scoped(self):
        self.site['localbusiness'].update(telephone=12,address=[],url='javascript:alert(1)')
        r=self.report()
        entry=next(x for x in r['checked'] if 'localbusiness_invalid_fields' in x)
        self.assertEqual(set(entry['localbusiness_invalid_fields']),{'telephone','address','url'})

    def test_actions_are_neutral_customer_invitations_with_manual_review(self):
        f=next(x for x in self.report()['findings'] if x['code']=='LOCAL_LOW_GOOGLE_RATING')
        text=' '.join(f['actions']).lower()
        for required in ('genuine customers','neutrally','no incentives','review gating','fabricated reviews','automatic replies','before approval'):
            self.assertIn(required,text)
        self.assertEqual(f['priority']['value'],'needs_verification')
        self.assertIn('no ranking gain promised',' '.join(f['acceptance']))

    def test_hours_require_current_matching_timezone_and_window(self):
        hours={'timezone':'Etc/UTC','regular':{'monday':'09:00-17:00'},'exceptions':{},'effective_from':'2026-10-01','effective_to':'2026-10-31'}
        self.site['hours']=copy.deepcopy(hours);self.profile['hours']=copy.deepcopy(hours)
        self.profile['hours']['regular']['monday']='10:00-17:00'
        self.assertIn('LOCAL_HOURS_MISMATCH',codes(self.report()))
        self.profile['hours']['timezone']='America/Toronto'
        self.assertNotIn('LOCAL_HOURS_MISMATCH',codes(self.report()))
        self.profile['hours']=copy.deepcopy(hours);self.profile['hours']['effective_to']='2026-10-15'
        self.assertNotIn('LOCAL_HOURS_MISMATCH',codes(self.report()))

    def test_aggregate_trends_order_independent_and_not_sample_derived(self):
        rows=[]
        for i,day in enumerate(('2026-10-14','2026-10-15','2026-10-16')):
            row=copy.deepcopy(self.profile);row.update(id='dated-'+str(i),observed_at=day,captured_at=day)
            row['google_reviews']['total_count']=100+i;rows.append(row)
        for order in itertools.permutations(rows):
            with self.subTest(order=[x['id'] for x in order]):
                self.payload['observations']=list(order)
                values=[x for x in self.report()['checked'] if x.get('comparison')=='dated_aggregate_change']
                self.assertEqual(len(values),3)
                self.assertEqual({tuple(x['evidence_ids']) for x in values},{('dated-0','dated-1'),('dated-0','dated-2'),('dated-1','dated-2')})
                self.assertTrue(all(x['total_count_delta']>0 for x in values))

    def test_importer_does_not_retain_raw_review_text_or_token(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from import_local_google_export import convert
        metadata={'as_of':self.payload['as_of'],'target':self.payload['target'],'observation':{k:self.profile[k] for k in ('id','source_url','captured_at','observed_at')}}
        raw={'id':self.payload['target']['place_id'],'rating':3,'userRatingCount':100,'reviews':[{'text':'FICTIONAL PRIVATE REVIEW BODY'}],'nextPageToken':'FICTIONAL TOKEN'}
        value=convert(raw,metadata,'places')
        self.assertNotIn('FICTIONAL PRIVATE REVIEW BODY',json.dumps(value))
        self.assertNotIn('FICTIONAL TOKEN',json.dumps(value))

    def test_importer_rejects_or_drops_unrecognized_metadata_data(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from import_local_google_export import convert
        metadata={'as_of':self.payload['as_of'],'target':self.payload['target'],'observation':{k:self.profile[k] for k in ('id','source_url','captured_at','observed_at')}}
        metadata['observation'].update(access_token='FICTIONAL METADATA TOKEN',reviews=[{'text':'FICTIONAL METADATA REVIEW'}])
        try:
            value=convert({'id':self.payload['target']['place_id']},metadata,'places')
        except ValueError:
            return
        self.assertNotIn('FICTIONAL METADATA TOKEN',json.dumps(value))
        self.assertNotIn('FICTIONAL METADATA REVIEW',json.dumps(value))

    def test_cli_executes_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'output'
            args=[sys.executable,str(ROOT/'scripts/local_seo_evidence.py'),str(CASES/'substantial-low-rating.json'),'--out',str(output)]
            first=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            stored=json.loads((output/'local-report.json').read_text())
            self.assertIn('LOCAL_LOW_GOOGLE_RATING',codes(stored))
            second=subprocess.run(args,capture_output=True,text=True)
            self.assertNotEqual(second.returncode,0)
            self.assertEqual(stored,json.loads((output/'local-report.json').read_text()))

if __name__=='__main__':
    unittest.main()
