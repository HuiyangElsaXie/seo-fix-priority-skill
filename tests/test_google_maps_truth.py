"""Independent, offline Google Maps truth/safety checks; fictional place identities."""
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
import socket

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('independent_maps_subject',ROOT/'scripts/google_maps_evidence.py')
maps=importlib.util.module_from_spec(spec);spec.loader.exec_module(maps)


class GoogleMapsTruthTests(unittest.TestCase):
    def analyze(self,html,**kwargs):
        return maps.analyze_google_maps(html,**kwargs)

    def test_classification_separates_iframe_javascript_and_links(self):
        cases=[('<iframe src="https://www.google.com/maps/embed?pb=opaque"></iframe>','embedded_map'),
               ('<script src="https://maps.googleapis.com/maps/api/js?key=FICTIONAL_KEY"></script>','maps_js_signal'),
               ('<a href="https://www.google.com/maps/dir/?api=1&destination=Fictional">Directions</a>','directions_link'),
               ('<a href="https://www.google.com/maps/search/?api=1&query=Fictional">Find us</a>','location_link')]
        for html,category in cases:
            with self.subTest(category=category):
                r=self.analyze(html)
                self.assertIn(category,r['classifications'])
                self.assertFalse(r['rendered_verified'])

    def test_lookalike_and_wrong_paths_never_trusted(self):
        urls=['https://www.google.com.evil.invalid/maps/embed','https://google-map.invalid/maps/embed',
              'https://evilgoogle.com/maps/embed','https://www.google.com/notmaps/embed',
              'https://maps.googleapis.com/other/api/js','https://maps.google.com.evil.invalid/maps',
              'https://google.com:444/maps/embed','javascript:https://google.com/maps/embed',
              'https://google.com\\@evil.invalid/maps/embed']
        for url in urls:
            with self.subTest(url=url):
                r=self.analyze('<iframe src="'+url+'"></iframe>')
                self.assertNotIn('embedded_map',r['classifications'])
                self.assertNotIn('maps_js_signal',r['classifications'])

    def test_embedded_credentials_never_retained_or_trusted(self):
        r=self.analyze('<iframe src="https://fictional-user:FICTIONAL_PASSWORD@www.google.com/maps/embed?q=place_id:fictional-place"></iframe>')
        self.assertNotIn('embedded_map',r['classifications'])
        self.assertNotIn('FICTIONAL_PASSWORD',json.dumps(r))
        self.assertNotIn('fictional-user',json.dumps(r))
        self.assertEqual(r['branch_status'],'unknown')

    def test_keys_full_urls_and_opaque_payload_not_retained(self):
        url='https://www.google.com/maps/embed/v1/place?key=AIzaFICTIONAL_SECRET_123&q=place_id:fictional-branch&pb=FICTIONAL_OPAQUE_PAYLOAD'
        r=self.analyze('<iframe src="'+url+'"></iframe>',expected_place_id='fictional-branch')
        text=json.dumps(r)
        for secret in (url,'AIzaFICTIONAL_SECRET_123','FICTIONAL_OPAQUE_PAYLOAD'):
            self.assertNotIn(secret,text)
        self.assertEqual(r['branch_status'],'match')

    def test_key_disguised_as_place_id_not_retained(self):
        r=self.analyze('<iframe src="https://google.com/maps/embed?place_id=AIzaFICTIONAL_SECRET"></iframe>',expected_place_id='AIzaFICTIONAL_SECRET')
        self.assertNotIn('AIzaFICTIONAL_SECRET',json.dumps(r))
        self.assertEqual(r['branch_status'],'unknown')

    def test_shortlinks_not_resolved_or_assumed_branch(self):
        for host,path in [('maps.app.goo.gl','/fictional'),('goo.gl','/maps/fictional')]:
            r=self.analyze('<a href="https://'+host+path+'">Find us</a>',expected_place_id='fictional-branch')
            self.assertEqual(r['branch_status'],'unknown')
            self.assertIn('untrusted/unknown',r['classifications'])
            self.assertNotIn('location_link',r['classifications'])

    def test_opaque_pb_names_coordinates_do_not_establish_identity(self):
        r=self.analyze('<iframe src="https://google.com/maps/embed?pb=!1sfictional-branch&q=Fictional%20Branch&center=1,2"></iframe>',expected_place_id='fictional-branch')
        self.assertEqual(r['branch_status'],'unknown')
        self.assertTrue(r['evidence'][0]['opaque_pb_present'])

    def test_explicit_identity_mismatch_and_mixed(self):
        one='<iframe src="https://google.com/maps/embed?q=place_id:fictional-other"></iframe>'
        two='<a href="https://google.com/maps/search/?query_place_id=fictional-branch">Location</a>'
        self.assertEqual(self.analyze(one,expected_place_id='fictional-branch')['branch_status'],'mismatch')
        self.assertEqual(self.analyze(one+two,expected_place_id='fictional-branch')['branch_status'],'mixed')

    def test_origin_place_does_not_become_destination_match(self):
        r=self.analyze('<a href="https://google.com/maps/dir/?origin_place_id=fictional-branch&destination=Fictional">Directions</a>',expected_place_id='fictional-branch')
        self.assertEqual(r['branch_status'],'unknown')

    def test_no_static_signal_is_not_nonfunctional_map(self):
        r=self.analyze('<html><div id="app"></div></html>')
        self.assertEqual(r['classifications'],['no_static_evidence'])
        self.assertFalse(r['rendered_verified'])
        self.assertIsNone(r['optional_recommendation'])
        self.assertIn('absence is not proof',' '.join(r['limitations']))

    def test_consent_deferred_iframe_is_unverified_runtime_signal(self):
        r=self.analyze('<iframe data-src="https://google.com/maps/embed?pb=fictional"></iframe>')
        self.assertIn('maps_js_signal',r['classifications'])
        self.assertNotIn('embedded_map',r['classifications'])
        self.assertFalse(r['rendered_verified'])

    def test_only_explicit_customer_visit_need_permits_optional_suggestion(self):
        for flag in (False,None,'yes',1):
            self.assertIsNone(self.analyze('',customer_visit_confirmed=flag)['optional_recommendation'])
        r=self.analyze('',customer_visit_confirmed=True,site_kind='physical_customer_location')
        self.assertIn('Optionally',r['optional_recommendation'])
        self.assertIn('address privacy',r['optional_recommendation'])
        self.assertIn('not an automatic SEO defect or ranking requirement',' '.join(r['limitations']))

    def test_portfolio_and_private_service_area_do_not_get_missing_map_advice(self):
        for kind in ('personal_portfolio','service_area','private_address'):
            with self.subTest(kind=kind):
                r=self.analyze('',customer_visit_confirmed=True,site_kind=kind)
                self.assertFalse(r['customer_visit_applicable'])
                self.assertIsNone(r['optional_recommendation'])

    def test_directions_link_alone_prevents_forced_embed_recommendation(self):
        r=self.analyze('<a href="https://google.com/maps/dir/?destination=Fictional">Directions</a>',customer_visit_confirmed=True)
        self.assertIsNone(r['optional_recommendation'])

    def test_duplicate_conflicting_place_ids_never_resolve_to_single_match(self):
        r=self.analyze('<iframe src="https://google.com/maps/embed?place_id=fictional-branch&place_id=fictional-other"></iframe>',expected_place_id='fictional-branch')
        self.assertEqual(r['branch_status'],'mixed')

    def test_forged_structured_output_cannot_echo_keys_urls_or_verdicts(self):
        forged={'schema_version':'1.0','rendered_verified':True,'branch_status':'match','optional_recommendation':'Publish FICTIONAL_SECRET',
                'evidence':[{'classification':'embedded_map','source_tag':'iframe','source_attribute':'src',
                             'source_url':'https://user:FICTIONAL_PASSWORD@google.com/maps/embed?key=AIzaFICTIONAL_SECRET',
                             'reason':'FICTIONAL_PRIVATE_TEXT','explicit_place_ids':['AIzaFICTIONAL_SECRET','https://evil.invalid/?secret=1','fictional-other']}],
                'limitations':['FICTIONAL_PRIVATE_TEXT']}
        r=maps.review_google_maps(forged,expected_place_id='fictional-branch')
        text=json.dumps(r)
        for forbidden in ('FICTIONAL_SECRET','FICTIONAL_PASSWORD','FICTIONAL_PRIVATE_TEXT','https://evil.invalid','https://user:'):
            self.assertNotIn(forbidden,text)
        self.assertFalse(r['rendered_verified'])
        self.assertEqual(r['branch_status'],'mismatch')
        self.assertIsNone(r['optional_recommendation'])

    def test_missing_or_malformed_structured_evidence_cannot_create_absence_advice(self):
        for value in (None,{},[],{'schema_version':'1.0','evidence':'bad'},{'schema_version':'1.0','evidence':[{'classification':'made-up'}]}):
            with self.subTest(value=value):
                r=maps.review_google_maps(value,customer_visit_confirmed=True)
                self.assertIsNone(r['optional_recommendation'])
                self.assertEqual(r['branch_status'],'unknown')
                self.assertIn('untrusted/unknown',r['classifications'])

    def test_encoded_map_query_keys_redacted_before_artifact_save(self):
        for url in ('https://maps.googleapis.com/maps/api/js?k%65y=%41%49%7A%61FICTIONALSECRET',
                    'https://maps.googleapis.com/maps/api/js?key&#61;FICTIONALSECRET',
                    'https://maps.googleapis.com/maps/api/js?foo=bar&amp;key=FICTIONALSECRET'):
            with self.subTest(url=url):
                text,changed=maps.redact_google_maps_secrets('<script src="'+url+'"></script>')
                self.assertTrue(changed)
                self.assertNotIn('FICTIONALSECRET',text)

    def test_offline_collector_redacts_artifact_without_losing_unknown_signal(self):
        spec=importlib.util.spec_from_file_location('independent_maps_collector',ROOT/'scripts/collect_public_site.py')
        collector_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector_module)
        for html,expected in [('<iframe src="https://fictional-user:FICTIONAL_PASSWORD@google.com/maps/embed"></iframe>','untrusted/unknown'),
                              ('<script src="https://maps.googleapis.com/maps/api/js?k%65y=%41%49%7A%61FICTIONALSECRET"></script>','maps_js_signal')]:
            with self.subTest(expected=expected),tempfile.TemporaryDirectory() as directory:
                calls=[]
                def transport(url,*args):
                    calls.append(url)
                    if url=='https://example.com/':return (200,{'content-type':'text/html; charset=utf-8'},html.encode())
                    return (404,{'content-type':'text/plain'},b'Not found')
                resolver=lambda host,port,**kw:[(socket.AF_INET,socket.SOCK_STREAM,6,'',('93.184.216.34',port))]
                collector=collector_module.Collector('https://example.com/',Path(directory)/'output',resolver=resolver,transport=transport,sleep=lambda x:None,delay=0,max_pages=1)
                result=collector.run();page=result['pages'][0]
                self.assertIn(expected,page['google_maps']['classifications'])
                self.assertTrue(page['artifact_redacted'])
                artifact=(collector.out/page['raw_artifact_path']).read_text()
                for secret in ('FICTIONAL_PASSWORD','FICTIONALSECRET'):
                    self.assertNotIn(secret,artifact)
                    self.assertNotIn(secret,json.dumps(result))
                self.assertTrue(all(url.startswith('https://example.com/') for url in calls))
                self.assertNotEqual(page['raw_source_sha256'],page['artifact_sha256'])


class BusinessModelTruthTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('independent_maps_reporter',ROOT/'scripts/six_dimension_report.py')
        self.reporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.reporter)
        self.snapshot={'schema_version':'1.0','pages':[]}

    def report(self,answers,extra=None):
        context={'as_of':'2026-10-16','business_model':{'source':'Fictional owner brief','date':'2026-10-16','reason':'Fictional attributed business model statement.',**answers}}
        context.update(extra or {})
        return self.reporter.build_report(self.snapshot,context)

    def check_dimensions(self,report,local,ecommerce):
        self.assertEqual(report['sections']['local']['applicability']['value'],local)
        self.assertEqual(report['sections']['ecommerce']['applicability']['value'],ecommerce)
        self.assertNotIn('health_score',report)
        self.assertFalse(report['findings'])

    def test_noncommercial_portfolio_and_online_content_not_forced(self):
        for site_kind in ('personal_portfolio','online_content'):
            with self.subTest(site_kind=site_kind):
                r=self.report({'commercial':'no','local_customer_service':'no','local_acquisition_goal':'no','online_transactions':'no'}, {'site_kind':site_kind})
                self.check_dimensions(r,'no','no')

    def test_local_shop_without_transactions_only_local(self):
        self.check_dimensions(self.report({'commercial':'yes','local_customer_service':'yes','online_transactions':'no'}),'yes','no')

    def test_standalone_clinic_domain_form_irrelevant(self):
        self.snapshot['source']='https://fictional-clinic.example/'
        self.check_dimensions(self.report({'commercial':'yes','local_customer_service':'yes','online_transactions':'no'}),'yes','no')

    def test_multibranch_ecommerce_both_when_explicit(self):
        self.check_dimensions(self.report({'commercial':'yes','local_customer_service':'yes','online_transactions':'yes'}),'yes','yes')

    def test_noncommercial_local_service_still_local(self):
        self.check_dimensions(self.report({'commercial':'no','local_customer_service':'yes','online_transactions':'no'}),'yes','no')

    def test_unknown_context_stays_unknown_without_penalty(self):
        self.check_dimensions(self.report({}),'unknown','unknown')
        r=self.reporter.build_report(self.snapshot,{'as_of':'2026-10-16'})
        self.check_dimensions(r,'unknown','unknown')

    def test_explicit_dimension_override_preserves_unknown(self):
        r=self.report({'commercial':'yes','local_customer_service':'yes','online_transactions':'yes'},
                      {'applicability':{'local':{'value':'unknown','reason':'Fictional unresolved eligibility.'}}})
        self.check_dimensions(r,'unknown','yes')

    def test_unattributed_or_future_business_claims_not_used(self):
        for change in ({'source':''},{'date':'2099-01-01'},{'reason':''}):
            context={'as_of':'2026-10-16','business_model':{'source':'Fictional owner','date':'2026-10-16','reason':'Fictional statement','local_customer_service':'yes','online_transactions':'yes',**change}}
            try:r=self.reporter.build_report(self.snapshot,context)
            except ValueError:continue
            self.assertNotEqual(r['sections']['local']['applicability']['value'],'yes')
            self.assertNotEqual(r['sections']['ecommerce']['applicability']['value'],'yes')

    def map_report(self,evidence,visit='unknown',kind=None,local='yes'):
        self.snapshot['pages']=[{'url':'https://fictional.example/','fetched_at':'2026-10-16','fetch_state':'ok','status':200,'parse_state':'parsed','content_type':'text/html','title':'Fictional location','h1':['Fictional location'],'google_maps':evidence}]
        context={'as_of':'2026-10-16','applicability':{'local':{'value':local,'source':'Fictional owner','date':'2026-10-16','reason':'Fictional eligibility'}},
                 'map_visit_context':{'value':visit,'site_kind':kind,'source':'Fictional owner','date':'2026-10-16','reason':'Fictional visit intent'}}
        return self.reporter.build_report(self.snapshot,context)

    def test_report_no_signal_optional_only_for_attributed_physical_visits(self):
        evidence=maps.analyze_google_maps('')
        for visit,kind,local in [('unknown',None,'yes'),('no',None,'yes'),('yes','personal_portfolio','yes'),('yes','service_area','yes'),('yes',None,'unknown')]:
            r=self.map_report(evidence,visit,kind,local)
            self.assertFalse(any(x['root_cause_key'].startswith('GOOGLE_MAPS_') for x in r['findings']))
        r=self.map_report(evidence,'yes','physical_customer_location')
        findings=[x for x in r['findings'] if x['root_cause_key'].startswith('GOOGLE_MAPS_OPTIONAL_VISIT_SUPPORT')]
        self.assertEqual(len(findings),1)
        self.assertFalse(any(x.get('issue_id')==findings[0]['issue_id'] for x in r['actionable_handoff']['buckets']['confirmed_fix']))
        self.assertTrue(any(x.get('issue_id')==findings[0]['issue_id'] for x in r['actionable_handoff']['buckets']['optional_improvement']))

    def test_report_untrusted_or_missing_maps_never_missing_feature_task(self):
        for evidence in (None,{},maps.analyze_google_maps('<a href="https://maps.app.goo.gl/fictional">Map</a>')):
            r=self.map_report(evidence,'yes','physical_customer_location')
            self.assertFalse(any(x['root_cause_key'].startswith('GOOGLE_MAPS_OPTIONAL') for x in r['findings']))

    def test_contact_map_prevents_blog_page_missing_map_suggestion(self):
        existing=maps.analyze_google_maps('<iframe src="https://google.com/maps/embed?pb=fictional"></iframe>')
        self.map_report(existing,'yes','physical_customer_location')
        contact=self.snapshot['pages'][0];contact['url']='https://fictional.example/contact'
        blog=dict(contact,url='https://fictional.example/blog',google_maps=maps.analyze_google_maps(''))
        self.snapshot['pages'].append(blog)
        context={'as_of':'2026-10-16','business_model':{'source':'Fictional owner','date':'2026-10-16','reason':'Fictional clinic','commercial':'yes','local_customer_service':'yes','online_transactions':'no'},
                 'map_visit_context':{'value':'yes','site_kind':'physical_customer_location','source':'Fictional owner','date':'2026-10-16','reason':'Customers attend the public branch'}}
        r=self.reporter.build_report(self.snapshot,context)
        self.assertFalse(any(x['root_cause_key'].startswith('GOOGLE_MAPS_OPTIONAL') for x in r['findings']))

if __name__=='__main__':unittest.main()
