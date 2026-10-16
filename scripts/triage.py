"""Offline evidence triage v0.3. Reads supplied JSON only; never fetches URLs."""
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
    if not isinstance(data, dict) or data.get('schema_version') not in ('0.2', '0.3'):
        raise ValueError('schema_version must be 0.2 or 0.3; legacy rows require explicit migration')
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
    validate_intake(data)
    return today

# Structured answers carry provenance; assumptions cannot unlock business urgency.
CONTEXT_FIELDS = ('industry', 'audience', 'geography', 'language', 'positioning',
                  'brand_lifecycle', 'product_lifecycle', 'primary_objective',
                  'conversion_definition', 'objective_tradeoff', 'resources', 'constraints', 'specific_problem',
                  'site_age', 'migration_history')
ESSENTIAL = ('industry', 'audience', 'geography', 'language', 'primary_objective',
             'resources', 'constraints', 'specific_problem')
STATUSES = ('confirmed', 'self_reported', 'assumption', 'unknown')

def root_equivalent(a, b):
    """Only empty root vs slash; no non-root, query, fragment, host or scheme merging."""
    if a == b: return True
    ua, ub = urlsplit(a), urlsplit(b)
    return (ua.scheme == ub.scheme and ua.netloc == ub.netloc
            and ua.path in ('', '/') and ub.path in ('', '/')
            and ua.query == ub.query and ua.fragment == ub.fragment)

def validate_answer(answer, sources, name):
    if not isinstance(answer, dict) or answer.get('status') not in STATUSES:
        raise ValueError(f'{name}: structured answer with valid status required')
    value = answer.get('value')
    if answer['status'] == 'unknown':
        if value not in (None, ''): raise ValueError(f'{name}: unknown must have null/empty value')
        return
    if not isinstance(value, str) or not value.strip(): raise ValueError(f'{name}: nonempty text required')
    if answer['status'] in ('confirmed', 'self_reported'):
        if answer.get('source_id') not in sources or not isinstance(answer.get('evidence_locator'), str) or not answer['evidence_locator'].strip():
            raise ValueError(f'{name}: supplied source and locator required')

def validate_intake(data):
    ctx = data['business_context']
    answers = ctx.get('answers', {})
    if not isinstance(answers, dict): raise ValueError('answers must be an object')
    if set(answers) - set(CONTEXT_FIELDS): raise ValueError('unknown intake field; use documented fields')
    for key, answer in answers.items(): validate_answer(answer, data['sources'], key)
    objective = answers.get('primary_objective', {})
    if objective.get('status') != 'unknown' and objective and objective.get('value') not in ('awareness','consideration','conversion','retention','mixed','other'):
        raise ValueError('primary_objective must be awareness, consideration, conversion, retention, mixed or other')
    for r in data['rows']:
        for key in ('business_impact', 'visibility_reason', 'canonical_intent'):
            if key in r: validate_answer(r[key], data['sources'], key)

def known(answer):
    return isinstance(answer, dict) and answer.get('status') in ('confirmed', 'self_reported')

def intake_report(data):
    answers = data['business_context'].get('answers', {})
    objective = answers.get('primary_objective', {})
    essentials = list(ESSENTIAL)
    if known(objective) and objective.get('value') in ('conversion', 'retention', 'mixed'):
        essentials.append('conversion_definition')
    if known(objective) and objective.get('value') == 'mixed':
        essentials.append('objective_tradeoff')
    missing = [k for k in essentials if not known(answers.get(k))]
    mode = 'tailored' if not missing else 'industry_general' if known(answers.get('industry')) else 'generic_framework'
    # Relevant branch prompts are unfilled only; previously supplied answers are reused.
    questions = [{'field':k, 'reason':'Needed to tailor business urgency; unknown is acceptable'} for k in missing]
    for k in ('positioning', 'brand_lifecycle', 'product_lifecycle', 'site_age', 'migration_history'):
        if not known(answers.get(k)): questions.append({'field':k, 'reason':'Clarifies expectations or change risk; never implies technical impact'})
    page_questions = []
    for r in data['rows']:
        gaps = []
        if r['intent'] == 'unknown': gaps.append('intended_visibility')
        if not known(r.get('visibility_reason')): gaps.append('visibility_reason / intentional noindex')
        if r['importance'] == 'unknown' or not known(r.get('business_impact')): gaps.append('critical_page_and_business_impact')
        if r.get('canonical') and not root_equivalent(r['canonical'],r['url']) and not known(r.get('canonical_intent')): gaps.append('intentional_canonical')
        if gaps: page_questions.append({'url':r['url'], 'questions':gaps})
    return {'mode':mode, 'context':answers, 'missing_essential':missing, 'questions':questions,
            'page_questions':page_questions,
            'interpretation': 'Tailored to supplied context; estimates remain provisional.' if mode == 'tailored' else 'Industry-general orientation retains reference value; business urgency is not established.' if mode == 'industry_general' else 'General diagnostic framework; no industry-specific conclusions are supported.',
            'limitations':'Self-reported context is attributed, not independently verified. Brand position/lifecycle never supplies measured traffic, demand or financial impact.'}

def priority_gates(data, row, role):
    gates = []
    intake = intake_report(data)
    if intake['mode'] != 'tailored': gates.append('Business intake incomplete; '+intake['mode']+' report only')
    if not known(row.get('business_impact')): gates.append('Supply page-level business impact rationale; brand position alone is insufficient')
    if not known(row.get('visibility_reason')): gates.append('Confirm visibility intent and intentional exclusions')
    if 'effort' not in row: gates.append('Supply effort estimate before business ranking')
    if not data['business_context'].get('owners',{}).get(role): gates.append('Assign accountable owner before scheduling')
    for answer in list(data['business_context'].get('answers', {}).values()) + [row.get('business_impact'), row.get('visibility_reason')]:
        if known(answer) and (date.fromisoformat(data['as_of']) - date.fromisoformat(data['sources'][answer['source_id']]['observed_at'])).days > 30:
            gates.append('Context evidence older than local 30-day window; reconfirm before prioritizing')
            break
    return gates


def triage(data):
    today = validate(data)
    queue, suppressed, gaps = [], [], []
    for r in data['rows']:
        rules = []
        if r['status'] >= 400: rules.append(('HTTP_ERROR', f"Supplied HTTP status {r['status']}"))
        if r['status'] == 200:
            if r.get('indexable') is False: rules.append(('NONINDEXABLE', 'Export marks page non-indexable; cause not independently verified'))
            if r.get('robots_blocked') is True: rules.append(('ROBOTS_BLOCKED', 'Supplied robots flag is true'))
            if r.get('canonical') and not root_equivalent(r['canonical'], r['url']): rules.append(('CANONICAL_REVIEW', f"Canonical points to {r['canonical']}"))
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
            business = {'critical':10,'supporting':6,'low':2,'unknown':None}[r['importance']]
            context_gates = priority_gates(data, r, role)
            gates.extend(context_gates)
            effort = r.get('effort', 5)
            score = round(impact*.4 + business*.4 + (10-effort)*.2, 1) if not gates else None
            priority = 'review' if gates else ('P1' if score >= 8 else 'P2' if score >= 6 else 'P3')
            queue.append({'url':r['url'],'rule':rule,'priority':priority,'score':score,
                'score_inputs':{'seo_impact':impact,'business_importance':business,'effort':r.get('effort'),'effort_basis':'supplied estimate' if 'effort' in r else 'missing; score withheld'},
                'confidence':confidence,'observation':observation,'technical_severity':impact,'business_urgency':'not established' if gates else 'supported provisional estimate','business_reason':{'supplied_importance':r['importance'],'objective':data['business_context']['objective'],'rationale':r.get('business_impact',{'status':'unknown','value':None}),'caution':'No traffic or revenue loss measured; technical severity does not establish business urgency'},
                'owner':data['business_context'].get('owners',{}).get(role,f'unassigned ({role})'),
                'source_id':r['source_id'],'evidence_locator':r['evidence_locator'],'evidence_age_days':age,
                'gates':gates,'proposed_fix':fix,'verification':verification,'status':'proposed; not implemented'})
    order = {'P1':0,'P2':1,'P3':2,'review':3}
    queue.sort(key=lambda x:(order[x['priority']],-(x['score'] or 0),x['url'],x['rule']))
    for i,item in enumerate(queue,1): item['id']=f'SEO-{i:03d}'
    return {'schema_version':'0.3','intake':intake_report(data),'as_of':data['as_of'],'scope':'Supplied evidence only; no live crawl, complete audit, ranking prediction, or implemented fixes',
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
