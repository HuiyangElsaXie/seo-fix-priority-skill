"""Regenerate only synthetic review assertions against the current fixture evidence IDs."""
import importlib.util
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('reporter', ROOT / 'scripts/six_dimension_report.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
args = [json.loads((HERE / (name + '.json')).read_text()) for name in ('snapshot', 'context', 'supplement')]
r = m.build_report(*args)
review = {'input_fingerprint': r['input_fingerprint'], 'reviewer':'Synthetic QA reviewer', 'date':'2026-10-16',
          'source':'Synthetic acceptance ledger; generated fixture, not independent site review', 'decisions':[], 'section_reviews':[]}
plans = {
 'JSONLD_SHAPE': ('confirmed_fix', 'The deliberately malformed second JSON-LD block must parse as a JSON object.',
                  ['Replace the malformed synthetic second JSON-LD block with the approved visible-content object.'],
                  ['Parse the second block successfully and compare its properties with visible synthetic content; preserve validator output.']),
 'EMPTY_TITLE': ('confirmed_fix', 'The synthetic public shop homepage must display its approved descriptive title.',
                 ['Add the approved synthetic homepage title to the page template and capture rendered and raw HTML.'],
                 ['The homepage has exactly the approved nonempty descriptive title in rendered and raw captures.']),
 'FIELD_MISMATCH_PHONE': ('confirmed_fix', 'Synthetic branch ledger confirms 000-0001 as the intended current phone.',
                         ['Update only the synthetic website phone to the value in the dated synthetic branch ledger.'],
                         ['Same-branch fresh website and authoritative synthetic ledger both show 000-0001.']),
 'FIELD_MISMATCH_PRICE': ('confirmed_fix', 'Synthetic catalog ledger confirms CAD 10.00 for the blue mug variant.',
                         ['Update only the synthetic blue mug website price to CAD 10.00 from the authoritative dated catalog fixture.'],
                         ['Fresh paired blue-variant captures show CAD 10.00; no other currency or variant was changed.']),
 'HREFLANG_RETURN': ('confirmed_fix', 'The synthetic English/French cluster is intended reciprocal; fixture review excludes header/sitemap alternatives.',
                     ['Add the English return alternate to the synthetic French page and retain its French self-reference.'],
                     ['Both collected cluster members reciprocate with intended language mappings; record reachable status and canonical checks.']),
 'EMPTY_META_DESCRIPTION': ('optional_improvement', 'A truthful summary is optional editorial work, not a diagnosed ranking penalty.',
                             ['Draft a useful summary only if the synthetic editor judges it helpful to the reader.'],
                             ['If adopted, fresh HTML matches the approved truthful summary; no gain is promised.']),
 'NOINDEX_REVIEW': ('keep_or_not_applicable', 'Private synthetic page is deliberately excluded from search.', None, None),
 'CANONICAL_REVIEW': ('keep_or_not_applicable', 'Synthetic private alternate intentionally canonicalizes to the public homepage.', None, None),
 'HTTP_ERROR': ('keep_or_not_applicable', 'Synthetic deleted URL is deliberately retired with HTTP 404.', None, None),
}
for code,(decision,intent,steps,acceptance) in plans.items():
 f=next(x for x in r['findings'] if x['root_cause_key'].startswith(code+'|'))
 d={'issue_id':f['issue_id'],'evidence_ids':f['evidence_ids'],'decision':decision,
    'rationale':'Synthetic reviewer compares this exact observation to the deliberately constructed acceptance ledger.',
    'intended_behavior':intent,'business_context_basis':'Synthetic retail discovery brief; no quantified urgency or impact and no assigned owner.'}
 if steps: d.update(steps=steps,acceptance=acceptance)
 if code.startswith('FIELD_MISMATCH_'):d['authoritative_source']='Synthetic branch/catalog ledger dated 2026-10-16; fixture assertion only'
 if code=='NOINDEX_REVIEW':d['visibility_intent']='exclude'
 if code=='CANONICAL_REVIEW':d['visibility_intent']='canonicalize_elsewhere'
 if code=='HTTP_ERROR':d['url_lifecycle']='retired'
 review['decisions'].append(d)
ids=[e['evidence_id'] for e in r['evidence'] if e['locator']=='backlinks:data']
review['section_reviews'].append({'dimension':'offpage','evidence_ids':ids,'decision':'keep_or_not_applicable',
 'rationale':'This single synthetic backlink sample establishes no action; no automated offpage defect detection is implemented.',
 'intended_behavior':'Retain this bounded sample only; liveness, completeness, reputation and paid status remain unknown.',
 'business_context_basis':'Synthetic retail discovery brief; do not manufacture a link-removal or acquisition recommendation.'})
(HERE/'review.json').write_text(json.dumps(review,indent=2)+'\n')
print(HERE/'review.json')
