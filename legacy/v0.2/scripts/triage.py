"""Offline evidence triage v0.2. Reads supplied JSON only; never fetches URLs."""
import argparse
import json
from datetime import date
from urllib.parse import urlsplit

RULES = {
    'HTTP_ERROR': (9, 'engineering', 'Confirm intended URL lifecycle; restore service or approve a relevant replacement.', 'Recheck HTTP status, internal links and intended destination after deployment.'),
    'NONINDEXABLE': (9, 'seo', 'Confirm the exclusion cause and intended visibility before changing directives.', 'Recrawl rendered HTML and response headers; inspect intended canonical. Index inclusion is not guaranteed.'),
    'ROBOTS_BLOCKED': (9, 'seo', 'Review supplied robots rule with engineering; do not remove intentional access controls.', 'Validate applicable user-agent rules and recheck crawl access after approval.'),
    'CANONICAL_REVIEW': (7, 'seo', 'Compare source and target content and intended canonical; do not automatically self-canonicalise.', 'Check canonical target status, visibility and consistency across HTML, headers and sitemap.'),
    'REDIRECT_CHAIN': (6, 'engineering', 'Inspect every hop and propose direct internal links to the approved final destination.', 'Recrawl complete hop sequence and confirm no loop or inappropriate destination.'),
    'MISSING_TITLE': (4, 'content', 'Write a unique, descriptive title matching page intent after template review.', 'Inspect rendered title and rerun missing/duplicate checks on the relevant template.'),
    'DEEP_PAGE': (4, 'seo', 'Review navigation and relevant contextual links to this intended landing page.', 'Recompute depth with the same crawl start and scope; verify useful link placement.'),
    'ZERO_INLINKS': (5, 'seo', 'Investigate possible isolation using a complete link graph; zero inlinks alone does not prove an orphan.', 'Compare a complete internal crawl with sitemap and permitted landing-page sources.'),
}

def valid_url(value):
    if not isinstance(value, str): return False
    u = urlsplit(value)
    return u.scheme in ('https', 'http') and bool(u.hostname) and not u.username and not u.password

def validate(data):
    if not isinstance(data, dict) or data.get('schema_version') != '0.2':
        raise ValueError('schema_version must be 0.2; legacy rows require explicit migration')
    for key in ('as_of', 'business_context', 'sources', 'rows'):
        if key not in data: raise ValueError(f'missing {key}')
    today = date.fromisoformat(data['as_of'])
    ctx = data['business_context']
    if not isinstance(ctx, dict) or not isinstance(ctx.get('objective'), str) or not ctx['objective'].strip():
        raise ValueError('business_context.objective is required')
    owners = ctx.get('owners', {})
    if not isinstance(owners, dict) or any(not isinstance(v, str) or not v.strip() for v in owners.values()):
        raise ValueError('owners must map role names to nonempty strings')
    sources = data['sources']
    if not isinstance(sources, dict) or not sources: raise ValueError('sources are required')
    for sid, s in sources.items():
        if not isinstance(s, dict) or not isinstance(s.get('description'), str) or not s['description'].strip(): raise ValueError(f'{sid}: description required')
        if s.get('kind') not in ('fictional_fixture', 'supplied_export', 'supplied_manual_check'): raise ValueError(f'{sid}: invalid source kind')
        if date.fromisoformat(s['observed_at']) > today: raise ValueError(f'{sid}: future observation')
    if not isinstance(data['rows'], list): raise ValueError('rows must be a list')
    seen = set()
    for r in data['rows']:
        if not isinstance(r, dict): raise ValueError('each row must be an object')
        if not valid_url(r.get('url')): raise ValueError('url must be absolute HTTP(S) without credentials')
        if r['url'] in seen: raise ValueError('duplicate URL: reconcile sources explicitly before triage')
        seen.add(r['url'])
        if r.get('source_id') not in sources: raise ValueError('unknown source_id')
        if not isinstance(r.get('evidence_locator'), str) or not r['evidence_locator'].strip(): raise ValueError('evidence_locator required')
        if type(r.get('status')) is not int or not 100 <= r['status'] <= 599: raise ValueError('status must be integer 100..599')
        if r.get('intent') not in ('index', 'exclude', 'unknown'): raise ValueError('intent must be index, exclude, or unknown')
        if r.get('importance') not in ('critical', 'supporting', 'low', 'unknown'): raise ValueError('invalid importance')
        for k in ('indexable', 'robots_blocked'):
            if k in r and r[k] is not None and type(r[k]) is not bool: raise ValueError(f'{k} must be bool or null')
        for k in ('depth', 'inlinks', 'redirect_hops'):
            if k in r and r[k] is not None and (type(r[k]) is not int or r[k] < 0): raise ValueError(f'{k} must be nonnegative int or null')
        if 'title' in r and r['title'] is not None and not isinstance(r['title'], str): raise ValueError('title must be string or null')
        if r.get('canonical') and not valid_url(r['canonical']): raise ValueError('canonical must be an absolute URL')
        if 'effort' in r and (type(r['effort']) is not int or not 1 <= r['effort'] <= 10): raise ValueError('effort must be integer 1..10')
    return today

def triage(data):
    today = validate(data)
    queue, suppressed, gaps = [], [], []
    for r in data['rows']:
        rules = []
        if r['status'] >= 400: rules.append(('HTTP_ERROR', f"Supplied HTTP status {r['status']}"))
        if r['status'] == 200:
            if r.get('indexable') is False: rules.append(('NONINDEXABLE', 'Export marks page non-indexable; cause not independently verified'))
            if r.get('robots_blocked') is True: rules.append(('ROBOTS_BLOCKED', 'Supplied robots flag is true'))
            if r.get('canonical') and r['canonical'] != r['url']: rules.append(('CANONICAL_REVIEW', f"Canonical points to {r['canonical']}"))
            if 'title' in r and r['title'] is not None and not r['title'].strip(): rules.append(('MISSING_TITLE', 'Supplied title is empty'))
            if r.get('depth') is not None and r['depth'] > 3: rules.append(('DEEP_PAGE', f"Supplied depth {r['depth']} exceeds local review threshold 3"))
            if r.get('inlinks') == 0: rules.append(('ZERO_INLINKS', 'Supplied inlink count is zero within supplied scope'))
        if r.get('redirect_hops', 0) is not None and r.get('redirect_hops', 0) > 1:
            rules.append(('REDIRECT_CHAIN', f"Supplied redirect path has {r['redirect_hops']} hops"))
        missing = [k for k in ('indexable','robots_blocked','canonical','title','depth','inlinks') if r.get(k) is None]
        if missing: gaps.append({'url': r['url'], 'not_assessed': missing})
        for rule, observation in rules:
            if r['intent'] == 'exclude' and rule != 'HTTP_ERROR':
                suppressed.append({'url':r['url'], 'rule':rule, 'reason':'Explicitly excluded from organic acquisition; no visibility repair proposed.'})
                continue
            impact, role, fix, verification = RULES[rule]
            age = (today-date.fromisoformat(data['sources'][r['source_id']]['observed_at'])).days
            gates = []
            if age > 30: gates.append('Evidence older than local 30-day review window; refresh first')
            if r['intent'] != 'index': gates.append('Confirm URL lifecycle / intended visibility')
            if r['importance'] == 'unknown': gates.append('Confirm business importance')
            if rule in ('CANONICAL_REVIEW','ZERO_INLINKS'): gates.append('Manual corroboration required; supplied signal is not a confirmed defect')
            confidence = 'low' if age > 30 else ('medium' if gates else 'high')
            business = {'critical':10,'supporting':6,'low':2,'unknown':5}[r['importance']]
            effort = r.get('effort', 5)
            score = round(impact*.4 + business*.4 + (10-effort)*.2, 1)
            priority = 'review' if gates else ('P1' if score >= 8 else 'P2' if score >= 6 else 'P3')
            queue.append({'url':r['url'],'rule':rule,'priority':priority,'score':score,
                'score_inputs':{'seo_impact':impact,'business_importance':business,'effort':effort,'effort_basis':'supplied estimate' if 'effort' in r else 'default 5; estimate before scheduling'},
                'confidence':confidence,'observation':observation,'business_reason':f"{r['importance']} importance in supplied context: {data['business_context']['objective']}; no traffic or revenue loss measured",
                'owner':data['business_context'].get('owners',{}).get(role,f'unassigned ({role})'),
                'source_id':r['source_id'],'evidence_locator':r['evidence_locator'],'evidence_age_days':age,
                'gates':gates,'proposed_fix':fix,'verification':verification,'status':'proposed; not implemented'})
    order = {'P1':0,'P2':1,'P3':2,'review':3}
    queue.sort(key=lambda x:(order[x['priority']],-x['score'],x['url'],x['rule']))
    for i,item in enumerate(queue,1): item['id']=f'SEO-{i:03d}'
    return {'schema_version':'0.2','as_of':data['as_of'],'scope':'Supplied evidence only; no live crawl, complete audit, ranking prediction, or implemented fixes',
        'confidence_definition':'Confidence in classification of supplied signals only; source truth, live defects and ranking benefit are not independently verified',
        'summary':{'supplied_urls':len(data['rows']),'candidate_findings':len(queue),'suppressed_findings':len(suppressed),'rows_with_missing_signals':len(gaps)},
        'queue':queue,'suppressed':suppressed,'coverage_gaps':gaps}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('input'); args=p.parse_args()
    try:
        with open(args.input,encoding='utf-8') as f: result=triage(json.load(f))
    except (ValueError,KeyError,TypeError,OSError) as e: p.exit(2,f'Invalid input: {e}\n')
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
if __name__ == '__main__': main()
