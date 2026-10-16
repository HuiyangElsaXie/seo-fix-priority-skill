"""Local artifact acceptance checks; not a live SEO validation."""
import csv,json
from pathlib import Path
p=Path(__file__).resolve().parent
raw=list(csv.DictReader((p/'evidence/crawl-slice.csv').open()))
i=json.loads((p/'input.v1.json').read_text());o=json.loads((p/'output.v1.json').read_text());intent=json.loads((p/'evidence/editorial-intent.json').read_text())
assert len(raw)==len(i['rows'])==15
assert len({r['url'] for r in i['rows']})==15
for a,b in zip(raw,i['rows']):
 assert a['Address']==b['url'] and int(a['Status Code'])==b['status']
 assert b['url'].split('/')[2]=='harborflow.example'
 for k in ['intent','importance']:assert b[k]==intent[a['Evidence ID']][k]
 for src,dst in [('Export Indexable','indexable'),('Robots Blocked','robots_blocked')]:assert b[dst]=={'yes':True,'no':False,'NOT_COLLECTED':None}[a[src]]
 for src,dst in [('Title 1','title'),('Canonical Link','canonical')]:assert b[dst]==(None if a[src]=='NOT_COLLECTED' else a[src])
assert o['summary']=={'supplied_urls':15,'candidate_findings':9,'suppressed_findings':9,'rows_with_missing_signals':4}
assert all(x['status']=='proposed; not implemented' for x in o['queue'])
assert next(x for x in o['queue'] if x['url'].endswith('/pricing'))['evidence_age_days']==57
assert all(x['priority']=='review' for x in o['queue'] if x['rule'] in ['CANONICAL_REVIEW','ZERO_INLINKS','HTTP_ERROR'])
assert not any(x['url'].endswith('/resources/api-integration') for x in o['queue'])
assert len(next(x for x in o['coverage_gaps'] if x['url'].endswith('/resources/api-integration'))['not_assessed'])==6
handoff=(p/'HANDOFF.md').read_text()
assert all(x['id'] in handoff for x in o['queue'])
print('PASS: 15 fictional rows; normalized identity/status/intent/boolean/text mapping; 9 proposed findings; 9 suppressions; 4 gap rows; stale/canonical/inlink/lifecycle gates; all queue IDs covered in handoff.')
