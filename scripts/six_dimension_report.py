"""Offline, bounded six-dimension evidence report. No network; no health score.

Input schemas and runnable fictional examples: cases/six-dimension/README.md.
Semantic review is deliberately left pending for a human or agent following SKILL.md.
"""
import argparse
from collections import Counter, deque
from datetime import date, datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from urllib.parse import urldefrag, urlsplit

DIMENSIONS = ('technical', 'onpage_content', 'offpage', 'local', 'ecommerce', 'international')
ESSENTIAL = ('industry', 'audience', 'geography', 'language', 'primary_objective',
             'resources', 'constraints', 'specific_problem')
REVIEW = {
    'technical': 'Confirm intended visibility, canonical choices, rendering and business-critical paths; observed directives do not prove Google index status.',
    'onpage_content': 'Review reader task, accuracy, first-hand evidence, authorship and useful next steps in full content. Do not score E-E-A-T, keyword density or word count.',
    'offpage': 'Review relevance, independence, paid relationships and sample bias. DA/DR are third-party measures, not Google authority scores.',
    'local': 'Confirm real customer contact/service eligibility, branch identity and privacy before suggesting a Business Profile; a city/address alone establishes no eligibility.',
    'ecommerce': 'Confirm current selling purpose, variants, purchase flow, delivery and returns; past ecommerce case studies do not make this site a shop.',
    'international': 'Review actual language/market purpose, translation quality and regional requirements; single-language sites need no standalone missing-hreflang warning.',
}


def normalized(url):
    if not isinstance(url, str):
        return ''
    url = urldefrag(url)[0]
    u = urlsplit(url)
    return url + '/' if u.netloc and not u.path and not u.query else url


def envelope(value, name):
    if not isinstance(value, dict) or not isinstance(value.get('source'), str) or not value['source'].strip():
        raise ValueError(name + ': explicit nonempty source required')
    try:
        date.fromisoformat(value.get('date', ''))
    except (TypeError, ValueError):
        raise ValueError(name + ': date must be YYYY-MM-DD') from None
    if not isinstance(value.get('data'), list) or any(not isinstance(r, dict) for r in value['data']):
        raise ValueError(name + ': data must be a list of objects')
    return value['data']


def context_report(context):
    ctx = context.get('business_context', context)
    if not isinstance(ctx, dict):
        raise ValueError('business_context must be an object')
    answers = ctx.get('answers', {})
    sources = context.get('sources', {})
    if not isinstance(answers, dict) or not isinstance(sources, dict):
        raise ValueError('context answers and sources must be objects')
    try:
        as_of = date.fromisoformat(context.get('as_of', datetime.now(timezone.utc).date().isoformat()))
    except (TypeError, ValueError):
        raise ValueError('context as_of must be YYYY-MM-DD') from None
    invalid_sources = []
    valid_sources = set()
    for sid, source in sources.items():
        try:
            valid = (isinstance(source, dict) and isinstance(source.get('description'), str)
                     and bool(source['description'].strip())
                     and source.get('kind') in ('fictional_fixture', 'supplied_export', 'supplied_manual_check')
                     and date.fromisoformat(source.get('observed_at', '')) <= as_of)
        except (TypeError, ValueError):
            valid = False
        if valid:
            valid_sources.add(sid)
        else:
            invalid_sources.append(sid)
    def known(key):
        a = answers.get(key, {})
        return (isinstance(a, dict) and a.get('status') in ('confirmed', 'self_reported')
                and isinstance(a.get('value'), str) and bool(a['value'].strip())
                and a.get('source_id') in valid_sources
                and isinstance(a.get('evidence_locator'), str) and bool(a['evidence_locator'].strip())
                and (key != 'primary_objective' or a['value'] in ('awareness', 'consideration', 'conversion', 'retention', 'mixed', 'other')))
    needed = list(ESSENTIAL)
    objective_answer = answers.get('primary_objective', {})
    objective = objective_answer.get('value') if isinstance(objective_answer, dict) else None
    if objective in ('conversion', 'retention', 'mixed'):
        needed.append('conversion_definition')
    if objective == 'mixed':
        needed.append('objective_tradeoff')
    missing = [k for k in needed if not known(k)]
    return {'mode': 'tailored' if not missing else 'industry_general' if known('industry') else 'generic_framework',
            'answers': answers, 'sources': sources, 'as_of': as_of.isoformat(),
            'invalid_source_ids': invalid_sources, 'missing_essential': missing,
            'objective': objective if known('primary_objective') else 'unknown',
            'interpretation': 'Context is supplied and attributed, not independently verified. Malformed or future-dated sources cannot establish known answers. Missing context does not block technical observations.'}


# These are investigation plans, not diagnoses or permission to change a site.
BUCKETS = ('confirmed_fix', 'needs_verification', 'optional_improvement', 'keep_or_not_applicable')
ROLES = {'technical': 'Technical SEO reviewer with web engineer',
         'onpage_content': 'Content editor with SEO reviewer',
         'offpage': 'PR or partnerships reviewer', 'local': 'Local operations manager',
         'ecommerce': 'Catalog operations manager with web engineer',
         'international': 'Localization lead with technical SEO reviewer'}


def rule_plan(code):
    """Return concrete checks and conditional fixes without guessing business intent."""
    if code == 'HTTP_ERROR':
        return (['Repeat the request and record URL, timestamp, status and redirect chain; compare the saved response.',
                 'Ask the site owner whether this URL should serve content, redirect or remain retired.',
                 'If unintended, repair the route/service or choose an approved equivalent redirect; if intentionally retired, retain the status and review internal links.'],
                ['URL lifecycle and intended destination confirmed by site owner', 'Access to route configuration and fresh response capture'],
                ['A fresh request matches the documented intended status/destination.', 'Any changed internal links resolve to the approved destination; attach before/after responses.'])
    if code == 'CANONICAL_REVIEW':
        return (['Capture every HTML and HTTP canonical declaration and resolve each target.',
                 'Compare content and ask the owner to document the intended preferred URL; check rendering and redirects.',
                 'Only if declarations contradict that intent, align the template and related signals with the approved preferred URL.'],
                ['Documented canonical intent and content-equivalence review', 'HTML/header access for source and targets'],
                ['Record whether the existing canonical is intentional.', 'If changed, one consistent intended canonical is present across the reviewed declarations; its target is reachable and equivalent.'])
    if code == 'NOINDEX_REVIEW':
        return (['Record the precise HTML meta or HTTP header containing noindex and inspect rendered output.',
                 'Confirm with the owner whether this URL is intended for search visibility or exclusion.',
                 'Retain deliberate exclusions; remove or correct directives only after an unintended exclusion is confirmed.'],
                ['Explicit URL visibility intent', 'Access to rendered HTML, response headers and relevant template'],
                ['The recorded directive matches documented visibility intent in a fresh response and rendered check.', 'If visibility is intended, inspect Search Console separately; do not equate directive removal with indexing.'])
    if code.startswith(('EMPTY_', 'DUPLICATE_')):
        field = 'title' if code.endswith('TITLE') else 'meta description'
        return ([f'Inspect the {field} in full rendered pages and the template for every listed URL.',
                 'Document whether these pages serve distinct reader tasks or intentional duplicate/alternate purposes.',
                 f'For pages needing differentiation, draft a truthful, purpose-specific {field}; retain intentional shared values when justified.'],
                ['Page purpose and target reader confirmed', 'Editorial approval and template access'],
                [f'Each scoped URL has an approved {field} or a documented reason for retaining/omitting it.', 'Fresh HTML/rendered evidence matches the approved copy; no ranking or click-rate gain is assumed.'])
    if code == 'JSONLD_SHAPE':
        return (['Locate the exact JSON-LD block in the saved raw HTML and reproduce the parsing/shape result.',
                 'Confirm the markup describes visible current content, then repair JSON syntax or node/type shape as needed.',
                 'Run a JSON parser and the relevant schema/official rich-result validator; record results and eligibility limits.'],
                ['Raw JSON-LD block and intended schema type', 'Template access and visible-content review'],
                ['Every changed block parses and has the intended object/array and node/type shapes.', 'Attach validator output and content comparison; valid syntax alone does not establish eligibility.'])
    if code.startswith('CWV_'):
        metric = code[4:]
        limit = {'LCP': '2500 ms', 'INP': '200 ms', 'CLS': '0.1'}[metric]
        probe = {'LCP': 'Trace LCP element discovery, server timing and resource loading.',
                 'INP': 'Trace slow interactions and long main-thread tasks.',
                 'CLS': 'Identify layout-shift sources, reserved dimensions and late content insertion.'}[metric]
        return (['Verify the field export scope, device, p75 and observation window; distinguish URL from origin aggregation.',
                 probe, 'Test a targeted change against a reproducible diagnostic case, then collect a comparable post-change field window.'],
                ['Valid field export with scope/device/window', 'Performance trace access and a comparable follow-up field window'],
                [f'Record before/after {metric} for the same scope/device; target p75 <= {limit}.', 'Keep the outcome unresolved until a comparable field window is available; lab improvements alone do not close it.'])
    if code.startswith('FIELD_MISMATCH_'):
        field = code.removeprefix('FIELD_MISMATCH_').lower()
        return ([f'Recheck paired {field} values for the exact entity or product variant and effective timestamp.',
                 'Identify the authoritative current source, including currency or branch context where relevant.',
                 'Correct only the source proven stale or incorrect; record intentional differences rather than forcing agreement.'],
                ['Matching identity, effective time and authoritative value', 'Operations approval and access to the affected source'],
                [f'Fresh paired {field} evidence matches the authoritative value for the same identity/time, or the intentional difference is documented.', 'For price, compare only identical currencies and variants; attach both observations.'])
    if code.startswith('HREFLANG_'):
        return (['Document the intended language/region cluster and collect its HTML, HTTP header and sitemap declarations.',
                 'Check each intended member for self-reference, unique language mappings, reciprocal references and reachable targets.',
                 'If a mismatch remains across the complete strategy, update the approved cluster declarations consistently.'],
                ['Confirmed alternate-market strategy and cluster inventory', 'Access to all declaration methods and target pages'],
                ['Each intended cluster member has a consistent unique mapping, self-reference and reciprocal references across the chosen strategy.', 'Record status and canonical checks for every target; missing sample pages remain unresolved, not failed.'])
    raise ValueError('No actionable plan for rule: ' + code)


def gap_plan(dim, gaps):
    plans = {
        'technical': ['If any scoped HTTP/parse failures are listed, repeat the exact requests and save status, headers and raw HTML before re-running skipped checks.',
                      'For index/rendering uncertainty, compare rendered HTML and URL Inspection evidence for the scoped URLs; inspect robots rules for the relevant crawler and record sample limits.',
                      'For CWV gaps, request a field p75 export with URL/origin scope, device, metric, units and window; invalid or absent records remain unknown.'],
        'onpage_content': ['Review full content for the exact affected URLs against the intended reader task; list factual claims and their supporting sources.',
                           'Check authorship/first-hand evidence and whether internal links or a relevant next action help the reader; compare rendered metadata with raw HTML where parsing failed.'],
        'offpage': ['If external reputation evidence is needed for this objective, obtain a dated referring-page/target/rel export with its sampling limits.',
                    'Inspect a documented sample for live links, topical relevance, independence and paid relationships; do not infer reputation from missing data or recommend buying links.'],
        'local': ['First ask whether this business actually serves customers at an eligible location or service area; document the decision and privacy constraints.',
                  'Only if applicable, compare current website and approved business-profile records for the same entity/branch and effective time: name, address, phone and hours.',
                  'For review gaps, obtain a dated platform/branch-scoped sample and its coverage, counts, timestamps and reply evidence; no supplied reviews means review activity is unknown, not absent.',
                  'For profile or location-page gaps, capture the approved branch profile and matching live location page; confirm categories, service area, displayed-address privacy and current customer contact details before edits.',
                  'For citation or competitor gaps, identify dated same-market, same-query and same-branch sources; formatting variants and incomplete samples alone do not establish inconsistency or competitive weakness.'],
        'ecommerce': ['First confirm whether the site currently sells products; a case study or Product markup alone is insufficient.',
                      'Only if applicable, compare website, markup and authoritative catalog for the same SKU, variant, currency and effective time; review checkout, delivery and returns separately.'],
        'international': ['Confirm the actual language/region variants and intended alternate strategy before requiring hreflang.',
                          'For each explicitly missing target in the scoped gaps, collect target HTML plus relevant header/sitemap declarations; compare return references, self-reference, mappings and canonical targets.',
                          'Have a fluent reviewer check the intended reader task and translation on the scoped variants; uncollected targets remain unknown.']}
    return ['Investigate only these scoped gaps: ' + '; '.join(gaps)] + plans[dim] + ['Attach source, date, scope and locator for each resolved gap; keep unavailable or irrelevant checks explicitly unresolved/not applicable.']


def handoff_report(findings, sections, intake):
    buckets = {name: [] for name in BUCKETS}
    for finding in findings:
        code = finding['root_cause_key'].split('|', 1)[0]
        plan = finding.get('action_plan')
        steps, dependencies, acceptance = ((plan['steps'], plan['dependencies'], plan['acceptance'])
                                            if plan else rule_plan(code))
        dim = finding['primary_dimension']
        reason = ('Validate this observed HTTP error before dependent content changes; intended lifecycle and business impact remain unknown.'
                  if code == 'HTTP_ERROR' else
                  'Investigate this supplied field threshold exceedance using comparable scope/device data; business urgency is not established.'
                  if code.startswith('CWV_') else
                  'Resolve the observed signal and its intent before approving a change; no measured business urgency or effort estimate is supplied.')
        if plan:
            reason = plan['priority_reason']
        task = {'task_id': 'task-' + finding['issue_id'], 'issue_id': finding['issue_id'],
                'dimension': dim, 'subject': finding['subject'],
                'bucket': 'optional_improvement' if plan and plan.get('optional') else 'needs_verification',
                'evidence_ids': list(finding['evidence_ids']), 'observed_basis': finding['technical_fact'],
                'steps': steps, 'proposed_role': ROLES[dim], 'dependencies': dependencies,
                'acceptance': acceptance, 'priority_reason': reason,
                'source_truth': 'supplied_input_not_independently_verified'}
        buckets[task['bucket']].append(task)
        finding['bucket'] = task['bucket']
        finding['owner'] = ROLES[dim] + ' (proposed role; assignment requires agreement)'
        finding['acceptance'] = ' '.join(acceptance)
        finding['priority']['reason'] = reason
    for dim, section in sections.items():
        na = section['applicability']['value'] == 'no'
        for item in (['; '.join(dict.fromkeys(section['unknowns']))] if section['unknowns'] else []):
            bucket = 'keep_or_not_applicable' if na else 'needs_verification'
            basis = section['applicability']['reason'] if na else item
            task_id = 'task-' + hashlib.sha256((dim + '|' + item).encode()).hexdigest()[:12]
            steps = ([f'Retain the documented applicability decision: {basis}', 'Revisit only if the business offering or market scope changes.'] if na else
                     [f'Resolve this specific evidence gap: {item}', 'Collect a dated, scoped source or manual check with a reproducible locator; record unavailable evidence explicitly.',
                      'Have the proposed reviewer interpret that evidence before proposing any site change.'])
            if not na:
                steps = gap_plan(dim, section['unknowns'])
            task = {'task_id': task_id, 'issue_id': None, 'dimension': dim,
                    'subject': 'Applicability decision' if na else 'Evidence investigation', 'bucket': bucket,
                    'evidence_ids': [], 'observed_basis': basis,
                    'source_locator': f'sections.{dim}.applicability' if na else f'sections.{dim}.unknowns',
                    'steps': steps, 'proposed_role': ROLES[dim],
                    'dependencies': ['Business owner confirmation if applicability changes'] if na else ['Access to the scoped source identified in the evidence gap', 'Reviewer availability'],
                    'acceptance': ['Applicability reason, source and date remain recorded; no missing-data penalty is assigned.'] if na else
                                  ['Attach dated evidence with scope and locator for this exact gap, or record why it remains unavailable.', 'Mark the check resolved only after review; unresolved evidence is never a site defect or a healthy result.'],
                    'priority_reason': 'Preserve an explicit supplied scope decision.' if na else 'Collect missing evidence before diagnosing faults or ordering changes; missing data alone establishes no urgency.',
                    'source_truth': 'supplied_input_not_independently_verified'}
            buckets[bucket].append(task)
    if intake['missing_essential']:
        buckets['needs_verification'].append({
            'task_id': 'task-business-context', 'issue_id': None, 'dimension': 'business_context',
            'subject': 'Missing essential context', 'bucket': 'needs_verification', 'evidence_ids': [],
            'observed_basis': ', '.join(intake['missing_essential']), 'source_locator': 'intake.missing_essential',
            'steps': ['Ask the business owner for each missing answer: ' + ', '.join(intake['missing_essential']),
                      'Record each answer with a dated source and evidence locator before tailoring recommendations.'],
            'proposed_role': 'Business owner with SEO lead', 'dependencies': ['Business owner input'],
            'acceptance': ['Every missing essential answer has a valid attributed source or is explicitly left unknown.', 'Business prioritization remains provisional for unresolved answers.'],
            'priority_reason': 'Context gates business-specific ordering; it does not prevent reporting observed technical signals.',
            'source_truth': 'supplied_input_not_independently_verified'})
    return {'status': 'verification_required', 'buckets': buckets,
            'interpretation': 'Actionable investigation and conditional repair plans, not execution approval. Evidence gaps are conditional scope checks, not mandatory tool purchases or website changes. Empty confirmed-fix and optional buckets do not mean healthy. Proposed roles are not assigned people. Business priority remains pending; investigation sequencing is evidence-based.'}


def apply_review(handoff, review, findings, evidence, sections, as_of):
    """Validate supplied review provenance; never label it independent verification."""
    if review is None:
        return {'status': 'not_supplied', 'source_truth': 'not_independently_verified'}
    def text_field(obj, field):
        if not isinstance(obj.get(field), str) or not obj[field].strip():
            raise ValueError('review: nonempty ' + field + ' required')
    if not isinstance(review, dict):
        raise ValueError('review must be an object')
    for field in ('reviewer', 'source'):
        text_field(review, field)
    try:
        if date.fromisoformat(review['date']) > date.fromisoformat(as_of):
            raise ValueError()
    except (ValueError, TypeError, KeyError):
        raise ValueError('review date must be YYYY-MM-DD and not after as_of') from None
    provenance = {k: review[k] for k in ('reviewer', 'source', 'date')}
    provenance['source_truth'] = 'supplied_reviewer_assertion_not_independently_verified'
    all_ids = {e['evidence_id'] for e in evidence}
    evidence_by_id = {e['evidence_id']: e for e in evidence}
    indexed = {f['issue_id']: f for f in findings}
    seen = set()
    decisions = review.get('decisions', [])
    section_reviews = review.get('section_reviews', [])
    if not isinstance(decisions, list) or not isinstance(section_reviews, list):
        raise ValueError('review decisions and section_reviews must be lists')
    def validate(entry, allowed_ids):
        if not isinstance(entry, dict):
            raise ValueError('review entry must be an object')
        for field in ('rationale', 'intended_behavior', 'business_context_basis'):
            text_field(entry, field)
        ids = entry.get('evidence_ids')
        if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in allowed_ids for i in ids):
            raise ValueError('review evidence_ids must reference existing evidence in the relevant scope')
        for eid in ids:
            observed = evidence_by_id[eid]['date']
            try:
                observed_date = datetime.fromisoformat(observed.replace('Z', '+00:00')).date()
            except (ValueError, TypeError, AttributeError):
                if entry.get('decision') == 'confirmed_fix':
                    raise ValueError('confirmed_fix requires dated evidence') from None
                continue
            if observed_date > date.fromisoformat(review['date']):
                raise ValueError('review date cannot precede cited evidence')
        if entry.get('decision') not in BUCKETS:
            raise ValueError('review decision must be a handoff bucket')
        for field in ('steps', 'acceptance'):
            if field in entry and (not isinstance(entry[field], list) or not entry[field] or
                                  any(not isinstance(t, str) or not t.strip() for t in entry[field])):
                raise ValueError('review ' + field + ' must be a nonempty list of nonempty strings')
    for entry in decisions:
        if not isinstance(entry, dict) or entry.get('issue_id') not in indexed:
            raise ValueError('review issue_id must identify an existing finding')
        iid = entry['issue_id']
        if iid in seen:
            raise ValueError('review has duplicate decisions for ' + iid)
        seen.add(iid)
        finding = indexed[iid]
        validate(entry, set(finding['evidence_ids']))
        decision = entry['decision']
        code = finding['root_cause_key'].split('|', 1)[0]
        conflict = None
        if decision in ('confirmed_fix', 'optional_improvement'):
            if sections[finding['primary_dimension']]['applicability']['value'] != 'yes':
                conflict = 'Applicability is not confirmed; supplied change decision remains verification.'
            if code in ('NOINDEX_REVIEW', 'CANONICAL_REVIEW'):
                if entry.get('visibility_intent') not in ('index', 'exclude', 'canonicalize_elsewhere'):
                    raise ValueError('directive review requires explicit visibility_intent')
                if entry['visibility_intent'] != 'index':
                    conflict = 'Exclusion or alternate canonical intent is compatible with this signal; do not infer a change is needed.'
            if code.startswith(('FIELD_MISMATCH_', 'LOCAL_NAP_', 'LOCAL_HOURS_')) and (not isinstance(entry.get('authoritative_source'), str) or not entry['authoritative_source'].strip()):
                conflict = 'Authoritative current source is missing; verify which paired value is correct before any edit.'
        if decision == 'confirmed_fix':
            if code == 'GOOGLE_MAPS_OPTIONAL_VISIT_SUPPORT':
                conflict = 'Static map absence alone is an optional navigation choice, not a confirmed defect; rendered behavior and a concrete fault require separate evidence.'
            for field in ('steps', 'acceptance'):
                if field not in entry:
                    raise ValueError('confirmed_fix requires explicit ' + field)
            if code.startswith(('FIELD_MISMATCH_', 'LOCAL_NAP_', 'LOCAL_HOURS_')):
                if not isinstance(entry.get('authoritative_source'), str) or not entry['authoritative_source'].strip():
                    conflict = 'Authoritative current source is missing; verify which paired value is correct before any edit.'
            if sections[finding['primary_dimension']]['applicability']['value'] != 'yes':
                conflict = 'Applicability is not confirmed; supplied fix decision remains verification.'
            if code in ('NOINDEX_REVIEW', 'CANONICAL_REVIEW'):
                if entry.get('visibility_intent') not in ('index', 'exclude', 'canonicalize_elsewhere'):
                    raise ValueError('directive review requires explicit visibility_intent')
                if entry['visibility_intent'] != 'index':
                    conflict = 'Exclusion or alternate canonical intent is compatible with this signal; do not infer a defect.'
            if code == 'HTTP_ERROR' and entry.get('url_lifecycle') != 'active':
                conflict = 'An active URL lifecycle has not been established; a collected error alone does not prove a repair is required.'
            if code.startswith('CWV_'):
                conflict = 'An above-threshold aggregate alone does not confirm a repair cause; validate the proposed intervention first.'
        target_bucket = 'needs_verification' if conflict else decision
        old = next(t for tasks in handoff['buckets'].values() for t in tasks if t.get('issue_id') == iid)
        handoff['buckets'][old['bucket']].remove(old)
        old['bucket'] = target_bucket
        old['review'] = {**provenance, **entry, 'applied_decision': target_bucket}
        old['priority_reason'] = 'Supplied reviewer rationale: ' + entry['rationale'] + ' Business basis (supplied): ' + entry['business_context_basis']
        if conflict:
            old['review']['conflict'] = conflict
            old['priority_reason'] += ' ' + conflict
        else:
            for field in ('steps', 'acceptance'):
                if field in entry:
                    old[field] = entry[field]
            if target_bucket == 'keep_or_not_applicable' and 'steps' not in entry:
                old['steps'] = ['Retain the reviewed behavior: ' + entry['intended_behavior'], 'Revisit if the documented intent or scoped evidence changes.']
                old['acceptance'] = ['Record the supplied rationale and evidence; no site change is required within this reviewed scope.']
        handoff['buckets'][target_bucket].append(old)
        finding['bucket'] = target_bucket
        finding['review'] = old['review']
        finding['confirmation_status'] = 'reviewer_supported_fix_claim' if target_bucket == 'confirmed_fix' else 'supplied_review_' + target_bucket
        finding['acceptance'] = ' '.join(old['acceptance'])
        finding['priority']['reason'] = old['priority_reason']
        finding['priority']['value'] = {'confirmed_fix': 'reviewed_fix_sequence', 'needs_verification': 'verify_before_change', 'optional_improvement': 'optional', 'keep_or_not_applicable': 'retain'}[target_bucket]
        finding['priority']['gates'] = ['Confirm source freshness and accountable assignment before execution', 'Business urgency and effort require separate sourced assessment']
    for index, entry in enumerate(section_reviews):
        if not isinstance(entry, dict) or entry.get('dimension') not in sections:
            raise ValueError('section review requires an existing dimension')
        dim = entry['dimension']
        # Snapshot evidence may support technical/content/alternate review; other
        # dimensions require an evidence record already linked to their findings.
        relevant = {eid for f in findings if f['primary_dimension'] == dim or dim in f['related_dimensions'] for eid in f['evidence_ids']}
        if dim == 'local':
            relevant |= {e['evidence_id'] for e in evidence if e['locator'].startswith('local_evidence.observations:')}
        if dim == 'offpage':
            relevant |= {e['evidence_id'] for e in evidence if e['locator'] == 'backlinks:data'}
        if dim in ('technical', 'onpage_content', 'international'):
            relevant |= {e['evidence_id'] for e in evidence if e['source'] == 'snapshot'}
        validate(entry, all_ids & relevant)
        if entry['decision'] not in ('keep_or_not_applicable', 'needs_verification'):
            raise ValueError('section reviews support only keep_or_not_applicable or needs_verification; fixes require a finding')
        task = {'task_id': 'task-section-review-' + str(index), 'issue_id': None, 'dimension': dim,
                'subject': 'Scoped supplied review', 'bucket': entry['decision'], 'evidence_ids': entry['evidence_ids'],
                'observed_basis': entry['rationale'], 'steps': entry.get('steps', ['Retain or investigate the scoped behavior: ' + entry['intended_behavior'], 'Revisit if the scoped evidence or intent changes.']),
                'proposed_role': ROLES[dim], 'dependencies': ['Only the linked evidence and stated review scope are covered'],
                'acceptance': entry.get('acceptance', ['Preserve linked evidence and rationale; do not treat unreviewed pages or unresolved gaps as cleared.']),
                'priority_reason': 'Supplied business context: ' + entry['business_context_basis'], 'review': {**provenance, **entry},
                'source_truth': provenance['source_truth']}
        handoff['buckets'][entry['decision']].append(task)
        sections[dim].setdefault('supplied_reviews', []).append(task['review'])
    return {**provenance, 'status': 'supplied_scoped_review', 'decision_count': len(decisions),
            'section_review_count': len(section_reviews), 'interpretation': 'Evidence links and structure validated; reviewer conclusions and business rationale are supplied assertions. Unreviewed scope remains pending.'}


def analyze_local_input(payload, as_of):
    """Load the sibling module without requiring callers to edit sys.path."""
    spec = importlib.util.spec_from_file_location('local_seo_evidence', Path(__file__).with_name('local_seo_evidence.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.analyze_local_evidence(payload, as_of=as_of)


def business_model_applicability(context, as_of):
    """Derive optional scope from attributed business purpose, never domain/features."""
    model = context.get('business_model')
    if model is None:
        return {}
    if not isinstance(model, dict):
        raise ValueError('business_model must be an object')
    keys = ('commercial', 'local_customer_service', 'local_acquisition_goal', 'online_transactions')
    if any(model.get(k, 'unknown') not in ('yes', 'no', 'unknown') for k in keys):
        raise ValueError('business_model answers must be yes/no/unknown')
    if all(model.get(k, 'unknown') == 'unknown' for k in keys):
        return {}
    envelope({**model, 'data': []}, 'business_model')
    if date.fromisoformat(model['date']) > date.fromisoformat(as_of):
        raise ValueError('business_model: date cannot be after as_of')
    if not isinstance(model.get('reason'), str) or not model['reason'].strip():
        raise ValueError('business_model: reason required')
    derived = {}
    def decision(dim, value, reason):
        derived[dim] = {'value': value, 'reason': reason + ' Supplied basis: ' + model['reason'],
                        'source': model['source'], 'date': model['date'], 'derived_from': 'business_model'}
    local_service, local_goal = model.get('local_customer_service'), model.get('local_acquisition_goal')
    if 'yes' in (local_service, local_goal):
        decision('local', 'yes', 'Explicit local customer service or local acquisition purpose; Business Profile eligibility remains separately reviewable.')
    elif (local_service == 'no' and local_goal == 'no') or model.get('commercial') == 'no':
        decision('local', 'no', 'No confirmed local acquisition/service purpose, or noncommercial scope without a stated local-service exception; no Local SEO requirement imposed.')
    selling = model.get('online_transactions')
    if selling in ('yes', 'no'):
        decision('ecommerce', selling, 'Online transaction purpose is explicitly ' + selling + '.')
    elif model.get('commercial') == 'no':
        decision('ecommerce', 'no', 'Noncommercial purpose without a stated online-transaction exception; no ecommerce requirement imposed.')
    return derived


def maps_visit_context(context, as_of):
    """Visit intent is separately attributed; local eligibility alone is insufficient."""
    visit = context.get('map_visit_context', {'value': 'unknown', 'reason': 'Customer visits and address privacy not confirmed.'})
    if not isinstance(visit, dict) or visit.get('value') not in ('yes', 'no', 'unknown'):
        raise ValueError('map_visit_context: value must be yes/no/unknown')
    if visit['value'] != 'unknown':
        envelope({**visit, 'data': []}, 'map_visit_context')
        if date.fromisoformat(visit['date']) > date.fromisoformat(as_of):
            raise ValueError('map_visit_context: date cannot be after as_of')
        if not isinstance(visit.get('reason'), str) or not visit['reason'].strip():
            raise ValueError('map_visit_context: reason required')
    return visit


def review_maps_input(payload, expected_place_id, customer_visit_confirmed, site_kind):
    spec = importlib.util.spec_from_file_location('google_maps_evidence', Path(__file__).with_name('google_maps_evidence.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.review_google_maps(payload, expected_place_id=expected_place_id,
                                     customer_visit_confirmed=customer_visit_confirmed, site_kind=site_kind)


def build_report(snapshot, context=None, supplement=None, review=None, local_evidence=None):
    context, supplement = context or {}, dict(supplement or {})
    if local_evidence is not None:
        if 'local_evidence' in supplement and supplement['local_evidence'] != local_evidence:
            raise ValueError('Conflicting local evidence supplied via two input routes')
        supplement['local_evidence'] = local_evidence
    enriched_local = 'local_evidence' in supplement
    if enriched_local and not isinstance(supplement['local_evidence'], dict):
        raise ValueError('local_evidence must be an object')
    if not isinstance(snapshot, dict) or snapshot.get('schema_version') != '1.0' or not isinstance(snapshot.get('pages'), list):
        raise ValueError('snapshot schema_version 1.0 and pages list required')
    pages = snapshot['pages']
    if any(not isinstance(p, dict) or not isinstance(p.get('url'), str) for p in pages):
        raise ValueError('each page requires a URL string')
    records = {k: envelope(v, k) for k, v in supplement.items() if k in ('cwv', 'backlinks', 'local', 'products') and not (enriched_local and k == 'local')}
    intake = context_report(context)
    visit_context = maps_visit_context(context, intake['as_of'])
    derived_applicability = business_model_applicability(context, intake['as_of'])
    rejected_dates = []
    for key in records:
        if date.fromisoformat(supplement[key]['date']) > date.fromisoformat(intake['as_of']):
            records[key] = []
            rejected_dates.append(key)
    sections = {}
    for dim in DIMENSIONS:
        applicability = {'value': 'yes', 'reason': 'General website review dimension.'}
        if dim in ('local', 'ecommerce', 'international'):
            applicability = context.get('applicability', {}).get(dim, derived_applicability.get(dim, {'value': 'unknown', 'reason': 'Business applicability has not been confirmed.'}))
            if not isinstance(applicability, dict) or applicability.get('value') not in ('yes', 'no', 'unknown'):
                raise ValueError('applicability.' + dim + ': value must be yes/no/unknown')
            if applicability['value'] != 'unknown':
                envelope({**applicability, 'data': []}, 'applicability.' + dim)
                if date.fromisoformat(applicability['date']) > date.fromisoformat(intake['as_of']):
                    raise ValueError('applicability.' + dim + ': date cannot be after as_of')
                if not applicability.get('reason'):
                    raise ValueError('applicability.' + dim + ': reason required')
        sections[dim] = {'applicability': applicability, 'evidence_status': 'not_assessed',
                         'semantic_review': 'pending' if applicability['value'] != 'no' else 'not_applicable',
                         'evidence_status_meaning': 'Status covers specified deterministic checks only; not complete SEO verification or semantic/eligibility approval.',
                         'confidence': {'classification': 'bounded_input_rules', 'source_truth': 'not_independently_verified', 'business_impact': 'unknown', 'coverage': 'limited_to_supplied_sample'},
                         'checked': [], 'unknowns': [], 'issue_ids': [], 'review_task': REVIEW[dim],
                         'source_timestamps': {'collection_finished_at': snapshot.get('collection', {}).get('finished_at', 'unknown'),
                                               'supplement_source': supplement.get({'technical': 'cwv', 'offpage': 'backlinks', 'local': 'local', 'ecommerce': 'products'}.get(dim, ''), {}).get('source', 'not_supplied'),
                                               'supplement_date': supplement.get({'technical': 'cwv', 'offpage': 'backlinks', 'local': 'local', 'ecommerce': 'products'}.get(dim, ''), {}).get('date', 'not_supplied')},
                         'collection_errors': snapshot.get('errors', []),
                         'collection_error_status': 'errors_present' if snapshot.get('errors') else 'none_reported'}
    model = context.get('business_model') or {}
    next_questions = []
    if not model.get('website_purpose'):
        next_questions.append('What is the website purpose: portfolio, content, lead generation, online sales or other?')
    if sections['local']['applicability']['value'] == 'unknown':
        next_questions.append('Do you serve customers locally, at premises or in a service area, or want local customer acquisition? An independent domain alone does not determine applicability.')
    elif sections['local']['applicability']['value'] == 'yes' and visit_context['value'] == 'unknown':
        next_questions.append('Should customers visit a public business location, or is this a service-area/private-address business? Confirm this before considering a map.')
    if sections['ecommerce']['applicability']['value'] == 'unknown':
        next_questions.append('Can customers place online orders or make purchase payments, rather than only request an appointment or contact you?')
    intake['next_questions'] = next_questions
    findings = {}
    evidence = []
    def ev(source, observed, scope, locator):
        eid = 'e-' + hashlib.sha256(json.dumps([source, observed, scope, locator], sort_keys=True).encode()).hexdigest()[:12]
        if not any(e['evidence_id'] == eid for e in evidence):
            evidence.append({'evidence_id': eid, 'source': source, 'date': observed or 'unknown', 'scope': scope, 'locator': locator})
        return eid
    def add(code, subject, dim, observation, recommendation, eid, severity='review', tags=()):
        key = code + '|' + subject
        iid = 'issue-' + hashlib.sha256(key.encode()).hexdigest()[:12]
        if iid not in findings:
            findings[iid] = {'issue_id': iid, 'root_cause_key': key, 'subject': subject, 'primary_dimension': dim,
                'related_dimensions': list(tags), 'technical_fact': observation,
                'interpretive_judgment': 'Candidate requiring contextual review; no ranking or revenue effect established.',
                'confirmation_status': 'observed_signal', 'technical_severity': severity,
                'confidence': {'classification': 'reproducible_rule_match_in_supplied_input', 'source_truth': 'not_independently_verified', 'business_impact': 'unknown', 'meaning': 'Rule matching is distinct from factual authenticity, SEO harm and business priority; no probability is estimated.'},
                'evidence_ids': [eid], 'recommendation': recommendation,
                'priority': {'value': 'pending', 'provisional': True, 'gates': ['Confirm business impact and visibility intent', 'Supply sourced effort estimate and accountable owner']},
                'acceptance': 'Recheck the same scoped evidence after an approved change and resolve the contextual review.',
                'owner': 'unassigned', 'effort': 'unknown'}
        elif eid not in findings[iid]['evidence_ids']:
            findings[iid]['evidence_ids'].append(eid)
        for d in (dim, *tags):
            if iid not in sections[d]['issue_ids']:
                sections[d]['issue_ids'].append(iid)
    def checked(dim, item):
        sections[dim]['checked'].append(item)
    def gap(dim, item):
        sections[dim]['unknowns'].append(item)
    for key in rejected_dates:
        gap({'cwv': 'technical', 'backlinks': 'offpage', 'local': 'local', 'products': 'ecommerce'}[key],
            key + ': supplement date is after as_of; evidence rejected pending a valid dated source.')
    by_url = {normalized(p['url']): p for p in pages}
    html_pages = [p for p in pages if p.get('fetch_state') == 'ok' and p.get('parse_state') == 'parsed'
                  and isinstance(p.get('content_type'), str)
                  and p['content_type'].split(';', 1)[0].strip().lower() in ('text/html', 'application/xhtml+xml')]
    for p in pages:
        url = p['url']
        eid = ev('snapshot', p.get('fetched_at'), url, p.get('raw_artifact_path') or 'pages:' + url)
        status = p.get('status')
        if isinstance(status, int):
            checked('technical', {'url': url, 'http_status': status})
            if status >= 400:
                add('HTTP_ERROR', url, 'technical', f'Collected HTTP status {status}.', 'Confirm URL lifecycle and intended audience; investigate service or approved replacement.', eid, 'error')
        else:
            gap('technical', f'{url}: HTTP result unavailable; fetch state {p.get("fetch_state", "unknown")}.')
        if p not in html_pages:
            gap('onpage_content', url + ': HTML parse not confirmed or HTML media type unavailable; metadata and content checks not assessed.')
            continue
        checked('technical', {'url': url, 'canonical': p.get('canonical', []), 'robots_meta': p.get('robots_meta', []), 'index_status': 'unknown'})
        canon = p.get('canonical', [])
        if isinstance(canon, str):
            canon = [canon]
        if len(set(canon)) > 1 or (canon and normalized(canon[0]) != normalized(url)):
            add('CANONICAL_REVIEW', url, 'technical', 'Observed canonical target(s): ' + ', '.join(canon), 'Confirm intended canonical and content equivalence; cross-page canonical can be intentional.', eid)
        robots = json.dumps([p.get('robots_meta', []), p.get('response_headers', {}).get('x-robots-tag', '')]).lower()
        if 'noindex' in robots:
            add('NOINDEX_REVIEW', url, 'technical', 'Collected HTML or HTTP robots directive includes noindex.', 'Confirm intended exclusion before considering any directive change.', eid)
        checked('onpage_content', {'url': url, 'title': p.get('title'), 'meta_description': p.get('meta_description'), 'h1': p.get('h1', [])})
        for field in ('title', 'meta_description'):
            if field in p and not (p[field] or '').strip():
                add('EMPTY_' + field.upper(), url, 'onpage_content', field + ' is empty in collected HTML.', 'Review a descriptive field for the page purpose; absence is not proof of a ranking penalty.', eid)
        jd = p.get('jsonld', [])
        checked('technical', {'url': url, 'jsonld_blocks': len(jd), 'validation': 'presence and supplied JSON shape only; not official rich-result validation'})
        for i, block in enumerate(jd):
            payload = block.get('value', block.get('data', block)) if isinstance(block, dict) else block
            if (isinstance(block, dict) and (block.get('parse_error') or block.get('valid_json') is False)) or not isinstance(payload, (dict, list)):
                add('JSONLD_SHAPE', url, 'technical', f'JSON-LD block {i} has a parse error or non-object/non-array root.', 'Inspect raw JSON and relevant schema; use official validation separately where applicable.', eid)
            else:
                nodes = payload if isinstance(payload, list) else payload.get('@graph', [payload])
                if not isinstance(nodes, list):
                    nodes = [nodes]
                malformed = any(not isinstance(n, dict) or ('@type' in n and not isinstance(n['@type'], (str, list))) for n in nodes)
                if malformed:
                    add('JSONLD_SHAPE', url, 'technical', f'JSON-LD block {i} contains a non-object node or invalid @type shape.', 'Inspect graph nodes and schema types; presence is not eligibility or official validation.', eid)
                types = [t for n in nodes if isinstance(n, dict) for t in (n.get('@type', []) if isinstance(n.get('@type'), list) else [n.get('@type')])]
                if 'Product' in types or 'Offer' in types:
                    checked('ecommerce', {'url': url, 'applicability_candidate': 'Product/Offer markup observed; current selling purpose still requires business confirmation.'})
                if 'FAQPage' in types:
                    checked('technical', {'url': url, 'FAQPage': 'Ordinary supplied content markup; no Google FAQ rich-result opportunity (removed May 7, 2026).'} )
    for field in ('title', 'meta_description'):
        grouped = {}
        for p in html_pages:
            value = (p.get(field) or '').strip()
            if value:
                grouped.setdefault(value, set()).add(p['url'])
        for value, urls in grouped.items():
            if len(urls) > 1:
                subject = '|'.join(sorted(urls))
                eid = ev('snapshot', snapshot.get('collection', {}).get('finished_at'), sorted(urls), 'duplicate:' + field)
                add('DUPLICATE_' + field.upper(), subject, 'onpage_content', f'Exact {field} duplicate in collected sample ({len(urls)} URLs).', 'Check page intent and template. Duplicate metadata is a review candidate, not a ranking-penalty diagnosis.', eid)
    # The graph only measures the collected sample; omitted pages cannot be classified as orphans.
    edges = {(normalized(p['url']), normalized(link.get('url', link.get('href', '')) if isinstance(link, dict) else link)) for p in html_pages for link in p.get('internal_links', [])}
    incoming = Counter(dst for src, dst in edges if src != dst)
    start = normalized(snapshot.get('collection', {}).get('final_url') or snapshot.get('collection', {}).get('requested_url', ''))
    depths, queue = {start: 0}, deque([start])
    while queue:
        src = queue.popleft()
        for a, b in edges:
            if a == src and b not in depths:
                depths[b] = depths[src] + 1
                queue.append(b)
    if html_pages:
        checked('technical', {'internal_graph': [{'url': p['url'], 'sample_inlinks': incoming[normalized(p['url'])], 'sample_depth': depths.get(normalized(p['url']))} for p in html_pages], 'sample_only': True, 'orphan_assessment': 'unknown'})
    if snapshot.get('robots'):
        checked('technical', {'robots_txt_signal': snapshot['robots'], 'interpretation': 'Collector user-agent access signal only; not Googlebot access or index status.'})
    gap('technical', 'Crawl/HTML sample does not prove index inclusion, rendered parity, complete internal graph or robots access for every crawler.')
    gap('onpage_content', 'Full-content task satisfaction and factual accuracy need semantic review; excerpts/word counts cannot establish thin content.')
    # Field Core Web Vitals only: no Lighthouse score or lab result is substituted.
    for r in records.get('cwv', []):
        required = ('scope', 'scope_type', 'device', 'window_start', 'window_end', 'metric', 'value', 'unit')
        valid = (all(r.get(k) is not None for k in required) and r.get('kind') == 'field' and r.get('percentile') == 75
                 and r.get('scope_type') in ('url', 'origin') and isinstance(r.get('scope'), str)
                 and urlsplit(r['scope']).scheme in ('https', 'http') and bool(urlsplit(r['scope']).hostname)
                 and r.get('device') in ('mobile', 'desktop', 'tablet') and r.get('metric') in ('LCP', 'INP', 'CLS')
                 and type(r.get('value')) in (float, int) and math.isfinite(r['value']) and r['value'] >= 0
                 and r.get('unit') == ('score' if r.get('metric') == 'CLS' else 'ms'))
        try:
            valid = valid and date.fromisoformat(r['window_start']) <= date.fromisoformat(r['window_end']) <= date.fromisoformat(intake['as_of'])
        except (ValueError, TypeError, KeyError):
            valid = False
        if not valid:
            gap('technical', 'CWV record rejected for field/p75/scope/window/device/metric/unit completeness: ' + str(r.get('metric', 'unknown')))
            continue
        threshold = {'LCP': 2500, 'INP': 200, 'CLS': 0.1}[r['metric']]
        checked('technical', {'cwv': r, 'good_threshold': threshold, 'assessment': 'within_good_threshold' if r['value'] <= threshold else 'above_good_threshold'})
        if r['value'] > threshold:
            s = supplement['cwv']
            eid = ev(s['source'], s['date'], r['scope'], 'cwv:' + r['metric'])
            add('CWV_' + r['metric'], r['scope'] + '|' + r['device'] + '|' + r['window_end'], 'technical', f'Supplied field p75 {r["metric"]} = {r["value"]} {r["unit"]}; above good threshold {threshold}.', 'Investigate experience using the same scope/device/window; do not promise ranking gains.', eid)
    if records.get('cwv'):
        gap('technical', 'CWV checks apply only to supplied valid metric/scope/device/window records; no overall CWV pass is inferred.')
    if not records.get('cwv'):
        gap('technical', 'No supplied field CWV export: LCP/INP/CLS unknown, not measured.')
    # External links are never inferred from an internal crawl.
    if records.get('backlinks'):
        unique = set()
        ev(supplement['backlinks']['source'], supplement['backlinks']['date'], 'offpage', 'backlinks:data')
        for r in records['backlinks']:
            if not r.get('source_url') or not r.get('target_url'):
                gap('offpage', 'Backlink record lacks source_url or target_url.')
                continue
            unique.add((r['source_url'], r['target_url'], r.get('rel', 'unknown')))
        checked('offpage', {'supplied_records': len(records['backlinks']), 'unique_link_records': len(unique), 'link_liveness': 'not_verified'})
        gap('offpage', 'Supplied sample is not a complete backlink index or reputation assessment.')
    else:
        gap('offpage', 'No backlink/mention data supplied; this does not mean no backlinks exist.')
    map_pages = [p for p in html_pages if 'google_maps' in p]
    if not map_pages:
        gap('local', 'Google Maps static evidence was not collected; feature presence and rendered functionality remain unknown.')
    target = supplement.get('local_evidence', {}).get('target', {}) if enriched_local else {}
    expected_place = target.get('place_id') if isinstance(target, dict) else None
    local_yes = sections['local']['applicability']['value'] == 'yes'
    visit_yes = local_yes and visit_context['value'] == 'yes'
    reviewed_maps = [(p, review_maps_input(p['google_maps'], expected_place, visit_yes, visit_context.get('site_kind'))) for p in map_pages]
    sample_absent = (bool(reviewed_maps) and len(map_pages) == len(html_pages) and
                     all(m['classifications'] == ['no_static_evidence'] for _, m in reviewed_maps))
    optional_emitted = False
    for page, maps in reviewed_maps:
        checked('local', {'url': page['url'], 'google_maps': maps,
                         'source_truth': 'supplied_static_evidence_not_independently_verified'})
        sections['local'].setdefault('limitations', []).extend(x for x in maps['limitations'] if x not in sections['local'].get('limitations', []))
        gap('local', page['url'] + ': Google Maps rendering, interaction, consent behavior and actual destination remain unverified.')
        mismatch = local_yes and maps['branch_status'] in ('mismatch', 'mixed')
        optional = visit_yes and sample_absent and not optional_emitted and bool(maps['optional_recommendation'])
        if not (mismatch or optional):
            continue
        code = 'GOOGLE_MAPS_BRANCH_REVIEW' if mismatch else 'GOOGLE_MAPS_OPTIONAL_VISIT_SUPPORT'
        fact = ('Supplied explicit map place identifier conflicts with the supplied target branch; real destination is unverified.' if mismatch else
                'No recognized static Google Maps feature was supplied in the bounded collected HTML sample; uncollected pages and JavaScript/consent-delayed maps remain unknown.')
        reason = ('Verify intended public branch before changing map links or embeds.' if mismatch else maps['optional_recommendation'])
        subject = page['url'] if mismatch else 'Collected HTML sample: optional customer navigation support'
        scoped_pages = [page] if mismatch else map_pages
        for scoped_page in scoped_pages:
            eid = ev('snapshot', scoped_page.get('fetched_at'), scoped_page['url'], 'pages.google_maps:' + scoped_page['url'])
            add(code, subject, 'local', fact, reason, eid)
        optional_emitted = optional_emitted or optional
        iid = 'issue-' + hashlib.sha256((code + '|' + subject).encode()).hexdigest()[:12]
        findings[iid]['action_plan'] = {
            'optional': not mismatch,
            'steps': ['Inspect the page in a rendered browser, including consent-delayed and mobile behavior; save sanitized evidence.',
                      'Confirm the intended public branch, customer visit purpose and address privacy with the owner.',
                      'If a wrong destination is confirmed, correct only the approved link/embed; otherwise retain intentional behavior.' if mismatch else
                      'Only if useful and approved, offer a directions link or lightweight map; retaining no map is an acceptable choice.'],
            'dependencies': ['Confirmed target branch and publicly shareable address', 'Owner approval and website access for any future edit',
                             'Rendered-browser verification; this report performs no API calls or publishing'],
            'acceptance': ['Record rendered behavior and actual destination for the intended branch without storing API keys.',
                           'Verify mobile accessibility, consent behavior and destination after any approved change, or document the choice to retain the page.'],
            'priority_reason': 'Optional customer navigation support; no ranking requirement or measured business urgency is established.' if not mismatch else
                               'Verify a possible customer navigation mismatch first; urgency depends on confirmed visit impact and source freshness.'}
        findings[iid]['priority']['value'] = 'optional' if not mismatch else 'verify_before_change'
    if enriched_local:
        local_section = sections['local']
        local_section['evidence_route'] = 'enriched_local_evidence; legacy local comparison bypassed'
        if local_section['applicability']['value'] != 'yes':
            gap('local', 'Enriched local evidence not interpreted: confirm local applicability with a dated source and business reason first.')
            local_section['local_evidence_analysis'] = {'status': 'not_assessed', 'reason': 'applicability_' + local_section['applicability']['value']}
        else:
            local_result = analyze_local_input(supplement['local_evidence'], intake['as_of'])
            local_section['local_evidence_analysis'] = local_result
            local_section['checked'].extend(local_result['checked'])
            local_section['unknowns'].extend(local_result['unknowns'])
            local_section.setdefault('limitations', []).extend(local_result['limitations'])
            for rejected in local_result['rejected']:
                gap('local', 'Rejected local observation ' + str(rejected.get('id', rejected.get('index'))) + ': ' + '; '.join(rejected['reasons']))
            local_evidence_ids = {}
            for item in local_result['checked']:
                if 'evidence' not in item:
                    continue
                provenance = item['evidence']
                eid = ev(provenance['source_url'], provenance['observed_at'],
                         {k: provenance[k] for k in ('entity_id', 'branch_id', 'place_id', 'market')},
                         'local_evidence.observations:' + provenance['id'])
                next(e for e in evidence if e['evidence_id'] == eid)['provenance'] = provenance
                local_evidence_ids[provenance['id']] = eid
            for item in local_result['findings']:
                subject = item['subject'] + ' / ' + item['issue_id']
                code = item['code']
                for observation_id in item['evidence_ids']:
                    add(code, subject, 'local', item['technical_fact'], item['reason'], local_evidence_ids[observation_id])
                iid = 'issue-' + hashlib.sha256((code + '|' + subject).encode()).hexdigest()[:12]
                finding = findings[iid]
                finding['action_plan'] = {
                    'steps': item['actions'], 'acceptance': item['acceptance'],
                    'dependencies': ['Owner confirmation of current branch source and intended values',
                                     'Approved access, branch identity and address/reviewer privacy review',
                                     'Sourced business impact, effort and accountable owner before prioritization'],
                    'priority_reason': item['priority']['conditional']}
                finding['confidence']['local_evidence'] = item['confidence']
                finding['interpretive_judgment'] = item['reason']
                finding['priority']['value'] = 'verify_before_change'
                finding['local_unknowns'] = item['unknowns']
    # Stable entity/variant identity and contemporaneous supplied observations are required.
    for dim, key, identity, fields in (
            ('local', 'local', ('entity_id', 'observed_at'), ('name', 'address', 'phone', 'hours')),
            ('ecommerce', 'products', ('product_id', 'variant_id', 'observed_at'), ('price', 'currency', 'availability'))):
        if dim == 'local' and enriched_local:
            continue
        if sections[dim]['applicability']['value'] != 'yes':
            if sections[dim]['applicability']['value'] == 'unknown':
                gap(dim, 'Confirm applicability before interpreting supplied entity/product data.')
            continue
        if not records.get(key):
            gap(dim, 'No supplied matching-identity comparison records; comparison not assessed.')
        for r in records.get(key, []):
            if not all(r.get(k) for k in identity) or not isinstance(r.get('website'), dict) or not isinstance(r.get('reference'), dict) or not r.get('reference_source'):
                gap(dim, 'Comparison skipped: matching identity, time, website/reference objects and reference_source required.')
                continue
            try:
                observed = datetime.fromisoformat(r['observed_at'].replace('Z', '+00:00')).date()
                valid_time = observed <= date.fromisoformat(intake['as_of']) and observed <= date.fromisoformat(supplement[key]['date'])
            except (TypeError, ValueError, AttributeError):
                valid_time = False
            if not valid_time:
                gap(dim, 'Comparison skipped: observed_at must be a valid date/time not after as_of or the supplement date.')
                continue
            checked(dim, {'identity': {k: r[k] for k in identity}, 'reference_source': r['reference_source'], 'comparison': 'supplied observations only'})
            s = supplement[key]
            eid = ev(s['source'], s['date'], {k: r[k] for k in identity}, key + ':' + r['reference_source'])
            for field in fields:
                a, b = r['website'].get(field), r['reference'].get(field)
                if a is None or b is None:
                    gap(dim, str(r[identity[0]]) + ': missing paired ' + field)
                    continue
                if field == 'price' and (not r['website'].get('currency') or r['website'].get('currency') != r['reference'].get('currency')):
                    gap(dim, str(r[identity[0]]) + ': price comparison withheld because currencies are missing/different.')
                    continue
                if a != b:
                    add('FIELD_MISMATCH_' + field.upper(), '|'.join(str(r[k]) for k in identity), dim,
                        f'Supplied {field} differs: website={a!r}; reference={b!r}.',
                        'Confirm entity/variant, effective time and authoritative value before updating either source.', eid, tags=('onpage_content',) if dim == 'ecommerce' else ())
    if sections['international']['applicability']['value'] == 'yes':
        for p in html_pages:
            links = p.get('hreflang', [])
            eid = ev('snapshot', p.get('fetched_at'), p['url'], 'hreflang')
            checked('international', {'url': p['url'], 'html_hreflang': links, 'scope': 'collected HTML only'})
            targets = [(h.get('lang', h.get('hreflang')), normalized(h.get('href', h.get('url', '')))) for h in links if isinstance(h, dict)]
            if not targets:
                gap('international', p['url'] + ': no HTML hreflang collected; check actual alternate strategy and other delivery methods.')
                continue
            if normalized(p['url']) not in [t for _, t in targets]:
                add('HREFLANG_SELF', p['url'], 'international', 'Collected HTML alternate set lacks self-reference.', 'Confirm intended alternate cluster and inspect complete HTML/header/sitemap declarations.', eid)
            for lang in set(lang for lang, _ in targets):
                if len({t for l, t in targets if l == lang}) > 1:
                    add('HREFLANG_CONFLICT', p['url'] + '|' + str(lang), 'international', 'Same hreflang code points to multiple targets in collected HTML.', 'Resolve intended language/region mapping after reviewing the cluster.', eid)
            for lang, target in targets:
                other = by_url.get(target)
                if not other or other not in html_pages:
                    gap('international', target + ': target HTML not collected successfully; reciprocity unknown.')
                    continue
                back = [normalized(h.get('href', h.get('url', ''))) for h in other.get('hreflang', []) if isinstance(h, dict)]
                if normalized(p['url']) not in back:
                    add('HREFLANG_RETURN', p['url'] + '|' + target, 'international', 'Collected target HTML lacks a return reference to the source.', 'Check intended cluster and all declaration methods before changing alternates.', eid)
    elif sections['international']['applicability']['value'] == 'unknown':
        gap('international', 'Actual language/region variants are unknown; paths or location names do not establish applicability.')
    for dim, section in sections.items():
        if section['applicability']['value'] == 'no':
            section['evidence_status'] = 'not_assessed'
            section['unknowns'] = ['Not applicable according to supplied business reason; no penalty assigned.']
        elif section['checked'] and section['applicability']['value'] == 'yes':
            section['evidence_status'] = 'partial' if section['unknowns'] else 'checked'
    handoff = handoff_report(list(findings.values()), sections, intake)
    fingerprint = hashlib.sha256(json.dumps([snapshot, context, supplement], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if review is not None and 'input_fingerprint' in review and review['input_fingerprint'] != fingerprint:
        raise ValueError('review input_fingerprint does not match the supplied inputs')
    final_review = apply_review(handoff, review, list(findings.values()), evidence, sections, intake['as_of'])
    final_review['input_binding'] = 'exact_input_fingerprint' if review and review.get('input_fingerprint') else 'evidence_locator_only; review assertions may be stale if source content changed'
    return {'schema_version': '1.0', 'input_fingerprint': fingerprint, 'final_review_status': final_review, 'actionable_handoff': handoff, 'report_type': 'bounded_six_dimension_evidence_review',
            'intake': intake, 'collection': snapshot.get('collection', {}),
            'sections': sections, 'findings': list(findings.values()), 'evidence': evidence,
            'limitations': ['No overall health/authority score, traffic loss, ranking penalty or ROI is calculated.',
                            'Unreviewed semantic scope remains pending; supplied external reviews are attributed assertions, not AI review performed by this deterministic script.',
                            'JSON-LD checks are not official rich-result validation. FAQ rich results were removed May 7, 2026; no FAQ rich-result benefit is promised.',
                            'Priority is qualitative and pending business-impact/effort/owner evidence; technical severity is separate.'] + sections['local'].get('limitations', [])}


def markdown(report):
    lines = ['# SEO review and action plan', '', 'Report level: ' + report['intake']['mode'],
             'Business objective: ' + str(report['intake']['objective']),
             'Technical facts and interpretive judgments are separated. Supplied scoped reviews do not clear unreviewed semantic scope.',
             'Final review status: ' + report['final_review_status']['status'],
             'Review input binding: ' + report['final_review_status']['input_binding'], '']
    if report['intake'].get('next_questions'):
        lines += ['## Questions to confirm scope', ''] + ['- ' + q for q in report['intake']['next_questions']] + ['']
    lines += ['## Decisions at a glance', '']
    for bucket, tasks in report['actionable_handoff']['buckets'].items():
        lines += ['- ' + bucket + ': ' + str(len(tasks))]
    lines += ['', '[Go to concrete steps, proposed roles, dependencies and acceptance checks](#actionable-handoff).',
              'Confirmed fixes are scoped supplied-review decisions, not independent verification. Verification tasks are not diagnosed site faults.', '']
    for dim, s in report['sections'].items():
        lines += ['## ' + dim.replace('_', ' ').title(),
                  f'Applicability: {s["applicability"]["value"]}. {s["applicability"]["reason"]}',
                  f'Evidence: {s["evidence_status"]} (bounded checks only); semantic review: {s["semantic_review"]}.',
                  'Confidence: rule-based input classification; source truth unverified and business impact unknown.',
                  f'Bounded checks: {len(s["checked"])}; findings: {len(s["issue_ids"])}.',
                  'Review: ' + s['review_task']]
        for observation in s['checked']:
            if 'google_maps' in observation:
                maps = observation['google_maps']
                lines += ['- Google Maps static signals: ' + ', '.join(maps['classifications']) +
                          '; branch comparison: ' + maps['branch_status'] + '; rendered functionality: unverified.']
        lines += ['- Unknown: ' + str(x) for x in s['unknowns']]
        lines += ['']
    lines += ['## Deduplicated findings', '']
    if not report['findings']:
        lines += ['No rules triggered in supplied scope. This is not a clean bill of health.']
    for f in report['findings']:
        lines += ['### ' + f['issue_id'] + ' / ' + f['primary_dimension'],
                  '- Subject: ' + f['subject'], '- Technical fact: ' + f['technical_fact'],
                  '- Interpretation: ' + f['interpretive_judgment'], '- Recommendation: ' + f['recommendation'],
                  '- Priority: ' + f['priority']['value'] + ' (provisional). ' + f['priority'].get('reason', 'Business impact requires confirmation.'),
                  '- Evidence: ' + ', '.join(f['evidence_ids']), '']
    lines += ['## Actionable handoff', '', report['actionable_handoff']['interpretation'], '']
    for bucket, tasks in report['actionable_handoff']['buckets'].items():
        lines += ['### ' + bucket, '']
        if not tasks:
            lines += ['No supported decisions in this bucket.', '']
        for task in tasks:
            lines += ['#### ' + task['task_id'], '- Scope: ' + task['dimension'] + ' / ' + task['subject'],
                      '- Basis: ' + task['observed_basis'], '- Proposed role: ' + task['proposed_role'],
                      '- Why this next: ' + task['priority_reason'],
                      '- Dependencies: ' + '; '.join(task['dependencies']),
                      '- Evidence: ' + (', '.join(task['evidence_ids']) or 'Evidence gap / supplied applicability decision; see ' + task.get('source_locator', 'intake'))]
            if task.get('review'):
                lines += ['- Review provenance: ' + task['review']['reviewer'] + ' / ' + task['review']['date'] + ' / ' + task['review']['source'] + '; supplied assertion, not independently verified.']
            lines += [str(i) + '. ' + step for i, step in enumerate(task['steps'], 1)]
            lines += ['- Acceptance: ' + check for check in task['acceptance']]
            lines += ['']
    lines += ['## Boundaries'] + ['- ' + x for x in report['limitations']]
    lines += ['', 'Detailed checked observations and source/date/scope evidence are in report.json.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot')
    parser.add_argument('--out', required=True)
    parser.add_argument('--context')
    parser.add_argument('--supplement')
    parser.add_argument('--local-evidence', help='Optional offline enriched Local SEO evidence JSON')
    parser.add_argument('--review', help='Optional attributed, evidence-linked review JSON; conclusions remain supplied assertions')
    args = parser.parse_args()
    def read(path):
        return json.loads(Path(path).read_text(encoding='utf-8')) if path else {}
    try:
        report = build_report(read(args.snapshot), read(args.context), read(args.supplement), read(args.review) if args.review else None,
                              local_evidence=read(args.local_evidence) if args.local_evidence else None)
        output = Path(args.out)
        output.mkdir(parents=True, exist_ok=False)
        (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (output / 'report.md').write_text(markdown(report), encoding='utf-8')
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, 'Error: ' + str(error) + '\n')
    print(str(output))


if __name__ == '__main__':
    main()
