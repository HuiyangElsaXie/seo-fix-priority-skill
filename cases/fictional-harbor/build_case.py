"""Create explicitly fictional raw fixture and normalize it; never create a queue."""
import csv,json
from pathlib import Path
P=Path(__file__).resolve().parent
base='https://harborflow.example'
# E IDs are stable evidence row keys, not live observations.
rows=[
['E01','/',200,'yes','no','/','HarborFlow supplier onboarding',0,12,0,'2026-10-14'],
['E02','/solutions/supplier-onboarding',200,'no','no','/solutions/supplier-onboarding','Supplier onboarding platform',1,8,0,'2026-10-14'],
['E03','/solutions/vendor-risk',200,'yes','no','/solutions/vendor-risk','',2,6,0,'2026-10-14'],
['E04','/demo',200,'yes','no','/demo','Book a HarborFlow demo',1,10,0,'2026-10-14'],
['E05','/resources/vendor-scorecard',200,'yes','no','/resources/vendor-scorecard','Vendor scorecard template',5,0,0,'2026-10-14'],
['E06','/solutions/procurement-automation',200,'yes','no','/solutions/supplier-onboarding','Procurement automation',2,4,0,'2026-10-14'],
['E07','/platform',301,'NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED',7,2,'2026-10-14'],
['E08','/resources/vendor-checklist-2023',404,'NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED',2,0,'2026-10-14'],
['E09','/thank-you/demo',200,'no','no','/thank-you/demo','',2,0,0,'2026-10-14'],
['E10','/internal-preview',200,'no','yes','/internal-preview','',4,0,0,'2026-10-14'],
['E11','/pricing',200,'no','no','/pricing','Pricing',1,9,0,'2026-08-20'],
['E12','/resources/api-integration',200,'NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED',0,'2026-10-14'],
['E13','/blog/vendor-risk-basics',200,'yes','no','/blog/vendor-risk-basics','Vendor risk basics',2,5,0,'2026-10-14'],
['E14','/legal/privacy',200,'no','no','/legal/privacy','Privacy policy',1,20,0,'2026-10-14'],
['E15','/campaigns/spring-demo',404,'NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED','NOT_COLLECTED',0,0,'2026-10-14'],
]
headers=['Evidence ID','Address','Status Code','Export Indexable','Robots Blocked','Canonical Link','Title 1','Crawl Depth','Unique Inlinks','Redirect Count','Snapshot Date']
with (P/'evidence/crawl-slice.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(headers)
 for r in rows:
  r=r.copy();r[1]=base+r[1]
  if r[5]!='NOT_COLLECTED':r[5]=base+r[5]
  w.writerow(r)
plans={
'E01':('index','critical',None),'E02':('index','critical',3),'E03':('index','critical',2),'E04':('index','critical',None),
'E05':('index','supporting',4),'E06':('index','critical',4),'E07':('index','supporting',2),'E08':('unknown','unknown',None),
'E09':('exclude','low',None),'E10':('exclude','low',None),'E11':('index','critical',None),'E12':('index','supporting',None),
'E13':('index','supporting',None),'E14':('exclude','low',None),'E15':('exclude','low',None)}
(P/'evidence/editorial-intent.json').write_text(json.dumps({k:{'intent':v[0],'importance':v[1], 'effort':v[2]} for k,v in plans.items()},indent=2)+'\n')
(P/'evidence/observation-notes.md').write_text('''# Fictional observation notes (N01–N06)
All observations and dates below are authored simulation inputs. No request was sent to a host.

- N01 / E02: simulated HTML extract has <meta name="robots" content="noindex,follow">. Indexability false is an explicit fixture observation, not inferred from HTTP 200. The brief wants organic acquisition here; verify production directives before changing anything.
- N02 / E06: simulated HTML canonical is /solutions/supplier-onboarding. Product naming overlap makes this possibly intentional. No content comparison, owner sign-off, selected canonical or index inclusion evidence exists.
- N03 / E07: simulated hop log: /platform → 301 /product → 301 /solutions/supplier-onboarding → 200. Seven inlinks to /platform are reported in this slice, but referring URL identities were not exported. Two redirects, three request URLs. /product is a hop-only observation, not a row in the 15-URL slice.
- N04 / E10: HTTP 200 and noindex come from a hypothetical supplied direct fetch; robots blocked comes from a separate hypothetical robots-rule evaluator for the same date. A robots-respecting crawler would not necessarily fetch that page. The synthetic merged export explicitly retains both signals. Internal preview is intentionally excluded; no access-control removal proposed.
- N05 / E11: pricing is from an older snapshot only. No October pricing check was supplied; this is not proof of an ongoing issue.
- N06 / E08 and E15: checklist retirement decision is missing; the campaign is known to be excluded but whether its 404 is the desired retirement response is not documented. Neither automatically warrants restoration or a redirect.
''')
# Normalize only raw saved evidence. No priority/rule/queue is authored here.
normalized=[]
with (P/'evidence/crawl-slice.csv').open(newline='') as f:
 for r in csv.DictReader(f):
  eid=r['Evidence ID'];p=plans[eid]
  out={'url':r['Address'],'source_id':'S-AUG' if r['Snapshot Date']=='2026-08-20' else 'S-OCT','evidence_locator':f'evidence/crawl-slice.csv#{eid}; evidence/editorial-intent.json#{eid}', 'status':int(r['Status Code']),'intent':p[0],'importance':p[1]}
  for src,dst in [('Export Indexable','indexable'),('Robots Blocked','robots_blocked')]:
   out[dst]={'yes':True,'no':False,'NOT_COLLECTED':None}[r[src]]
  for src,dst in [('Crawl Depth','depth'),('Unique Inlinks','inlinks'),('Redirect Count','redirect_hops')]:
   out[dst]=None if r[src]=='NOT_COLLECTED' else int(r[src])
  for src,dst in [('Canonical Link','canonical'),('Title 1','title')]:out[dst]=None if r[src]=='NOT_COLLECTED' else r[src]
  if p[2] is not None:out['effort']=p[2]
  normalized.append(out)
data={'schema_version':'0.2','as_of':'2026-10-16','business_context':{'objective':'Help procurement teams evaluate HarborFlow supplier onboarding and reach the demo request page. Protect intended organic landing pages while preserving deliberate exclusions.','owners':{'engineering':'Engineering lead (fictional role)','seo':'SEO lead (fictional role)','content':'Content lead (fictional role)'},'coverage':'Fictional 15-URL partial sample; not whole-site coverage'},'sources':{sid:{'kind':'fictional_fixture','description':description,'observed_at':date} for sid,date,description in [('S-OCT','2026-10-14','Agent-authored fictional desktop-crawler-style partial CSV export plus explicit intent map. Homepage-start sample plus seeded URLs, no external crawl performed; see PROVENANCE.md and observation notes.'),('S-AUG','2026-08-20','Agent-authored fictional historical pricing snapshot in same CSV; no current replacement available; same simulated extraction vocabulary.')]},'rows':normalized}
(P/'input.v1.json').write_text(json.dumps(data,indent=2)+'\n')
print('Authored fictional raw evidence: 15 URL rows. Normalized input.v1.json; no queue prefilled.')
