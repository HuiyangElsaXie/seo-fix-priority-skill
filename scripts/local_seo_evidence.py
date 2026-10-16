"""Offline Local SEO evidence checks; supplied observations, never live verification.

Import analyze_local_evidence(payload, as_of=None), or run INPUT --out NEW_DIRECTORY.
Required payload: schema_version=1.0, target={entity_id,branch_id,place_id,market},
observations=[{id,entity_id,branch_id,place_id,market,source_kind,source_url,
captured_at,observed_at,coverage}]. Times are ISO dates or timezone-aware timestamps.
source_kind: website/google_business_profile/directory; coverage: aggregate/snapshot/sample.
Optional observation fields: nap={name,address,phone}; hours={timezone,regular,
exceptions,effective_from,effective_to}, where regular/exceptions are explicit JSON
objects; google_reviews={rating,total_count,visible_sample_count}; localbusiness is
a supplied JSON-LD LocalBusiness node (explicit @type LocalBusiness only).
Optional config: freshness_days, max_pair_gap_days, low_rating_threshold,
low_count_threshold. Optional peers: observations with source_kind=peer_profile,
peer identity fields, category and comparison_group; target GBP observations must
have the same category, comparison_group and explicit maturity_group (or lifecycle) for peer comparison. All examples
must use fictional data. No network, credentials, writes to external services.
"""
import argparse
from datetime import date, datetime, time, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit

DEFAULTS = {'freshness_days': 30, 'max_pair_gap_days': 1,
            'low_rating_threshold': 4.0, 'low_count_threshold': 10}
IDENTITY = ('entity_id', 'branch_id', 'place_id', 'market')
# Bounded explicit vocabulary, not a full schema.org hierarchy resolver.
LOCAL_TYPES = {'LocalBusiness', 'Restaurant', 'Dentist', 'Store', 'CafeOrCoffeeShop',
               'Bakery', 'Hotel', 'LodgingBusiness', 'MedicalBusiness', 'ProfessionalService',
               'AutomotiveBusiness', 'HomeAndConstructionBusiness', 'HealthAndBeautyBusiness'}
ETHICS = ('Invite genuine customers neutrally and consistently when appropriate; no incentives, review gating, '
          'fabricated reviews or automatic replies. Review any response for accuracy and privacy before approval.')
LIMITATIONS = [
    'Supplied evidence is not independently verified; missing evidence is unknown, never zero.',
    'Thresholds are configurable triage heuristics, not Google ranking factors or benchmarks.',
    'Visible review samples cannot establish total volume, average rating or a trend; sample selection may be biased.',
    'LocalBusiness checks cover supplied field presence/shape only, not Google eligibility, indexing or full schema validation.',
    'No live Business Profile, Maps, API, network or paid data calls; no publishing or profile changes.',
    ETHICS,
    'Service-area and home-based businesses require address privacy review; never publish an address merely to fill a schema field.',
    'Do not add self-serving Google review aggregateRating markup to the business own site as a rich-result recommendation.',
]


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be an ISO date or timezone-aware datetime')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return datetime.combine(date.fromisoformat(value), time.min, timezone.utc)
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('datetime requires timezone')
    return parsed.astimezone(timezone.utc)


def text_normalized(value):
    return ' '.join(value.casefold().split()) if nonempty(value) else None


def normalize_nap(field, value):
    """Formatting only. Never infer a country code or equate street abbreviations."""
    if not nonempty(value):
        return None
    if field == 'phone':
        # Keep leading +, extensions, letters and digits; remove presentation punctuation only.
        return re.sub(r'[\s().-]', '', value.casefold())
    return text_normalized(value)


def number(value, low, high=None, integer=False):
    return (type(value) in ((int,) if integer else (int, float)) and math.isfinite(value)
            and value >= low and (high is None or value <= high))


def valid_url(value):
    if not nonempty(value):
        return False
    try:
        u = urlsplit(value)
        return u.scheme in ('http', 'https') and bool(u.hostname) and not u.username and not u.password
    except ValueError:
        return False


def analyze_local_evidence(payload, as_of=None):
    if not isinstance(payload, dict) or payload.get('schema_version') != '1.0':
        raise ValueError('local evidence schema_version must be 1.0')
    target = payload.get('target')
    if not isinstance(target, dict) or not all(nonempty(target.get(k)) for k in IDENTITY):
        raise ValueError('target requires stable entity_id, branch_id, place_id and market')
    observations = payload.get('observations')
    if not isinstance(observations, list):
        raise ValueError('observations must be a list')
    cfg = dict(DEFAULTS)
    supplied_config = payload.get('config', {})
    if not isinstance(supplied_config, dict) or set(supplied_config) - set(DEFAULTS):
        raise ValueError('unrecognized config keys or invalid config')
    cfg.update(supplied_config)
    for key in ('freshness_days', 'max_pair_gap_days', 'low_count_threshold'):
        if not number(cfg[key], 0, integer=True):
            raise ValueError(key + ' must be a nonnegative integer')
    if not number(cfg['low_rating_threshold'], 1, 5):
        raise ValueError('low_rating_threshold must be between 1 and 5')
    day = date.fromisoformat(as_of or payload.get('as_of', datetime.now(timezone.utc).date().isoformat()))
    checked, findings, unknowns, rejected = [], [], [], []
    result = {'schema_version': '1.0', 'as_of': day.isoformat(), 'target': target,
              'config': cfg, 'checked': checked, 'findings': findings,
              'unknowns': unknowns, 'rejected': rejected, 'limitations': LIMITATIONS[:],
              'source_truth': 'supplied_input_not_independently_verified'}

    def gap(message):
        if message not in unknowns:
            unknowns.append(message)

    def evidence(row):
        return {k: row[k] for k in ('id', *IDENTITY, 'source_kind', 'source_url', 'captured_at', 'observed_at', 'coverage',
                                   'source_method', 'export_sha256', 'operating_status', 'ownership_verification_status',
                                   'status_source', 'status_observed_at', 'maturity_group', 'lifecycle') if k in row}

    def finding(code, rows, fact, reason, actions, acceptance, confidence='bounded_supplied_evidence'):
        ids = [r['id'] for r in rows]
        findings.append({'code': code, 'issue_id': 'local-' + hashlib.sha256((code + '|'+ '|'.join(ids)).encode()).hexdigest()[:12],
                         'subject': target['branch_id'], 'evidence_ids': ids, 'evidence': [evidence(r) for r in rows],
                         'technical_fact': fact, 'reason': reason, 'confidence': confidence,
                         'priority': {'value': 'needs_verification', 'conditional': 'Escalate only after current evidence and customer/business impact are confirmed; urgency and effort unknown.'},
                         'actions': actions, 'acceptance': acceptance,
                         'unknowns': ['Authoritative source, business impact and outcome require human confirmation.']})

    seen, good, peers = set(), [], []
    all_rows = observations + payload.get('peers', []) if isinstance(payload.get('peers', []), list) else None
    if all_rows is None:
        raise ValueError('peers must be a list')
    for index, row in enumerate(all_rows):
        errors = []
        if not isinstance(row, dict):
            rejected.append({'index': index, 'reasons': ['observation must be an object']})
            continue
        required = ('id', *IDENTITY, 'source_kind', 'source_url', 'captured_at', 'observed_at', 'coverage')
        if not all(nonempty(row.get(k)) for k in required):
            errors.append('required provenance or stable identity missing')
        if nonempty(row.get('id')) and row['id'] in seen:
            errors.append('duplicate observation id')
        if nonempty(row.get('id')):
            seen.add(row['id'])
        if not valid_url(row.get('source_url')):
            errors.append('source_url must be an http(s) evidence locator without embedded credentials')
        if row.get('source_kind') not in ('website', 'google_business_profile', 'directory', 'peer_profile'):
            errors.append('unsupported source_kind')
        if row.get('coverage') not in ('aggregate', 'snapshot', 'sample'):
            errors.append('coverage must be aggregate, snapshot or sample')
        peer = row.get('source_kind') == 'peer_profile'
        if not peer and any(row.get(k) != target[k] for k in IDENTITY):
            errors.append('target identity/branch/place/market mismatch; no comparison allowed')
        if peer and (row.get('market') != target['market'] or row.get('place_id') == target['place_id']):
            errors.append('peer requires same explicit market and a distinct place')
        try:
            observed, captured = timestamp(row.get('observed_at')), timestamp(row.get('captured_at'))
            if observed > captured or captured.date() > day:
                errors.append('observation after capture or capture after as_of')
        except (TypeError, ValueError):
            errors.append('invalid observed_at/captured_at')
        if errors:
            rejected.append({'index': index, 'id': row.get('id'), 'reasons': errors})
            continue
        fresh = (day - observed.date()).days <= cfg['freshness_days']
        checked.append({'id': row['id'], 'evidence': evidence(row), 'fresh': fresh,
                        'confidence': 'bounded_supplied_evidence' if fresh and row['coverage'] != 'sample' else 'low'})
        if not fresh:
            gap(row['id'] + ': stale evidence; refresh before current warnings/comparisons')
            continue
        (peers if peer else good).append(row)

    profiles = []
    for row in good:
        checked.append({'id': row['id'], 'operating_status': row.get('operating_status', 'unknown'),
                        'ownership_verification_status': row.get('ownership_verification_status', 'unknown'),
                        'status_scope': 'Supplied assertions only; public operational status never proves ownership or GBP verification.'})
        if row['source_kind'] == 'google_business_profile':
            reviews = row.get('google_reviews', {})
            if not isinstance(reviews, dict):
                gap(row['id'] + ': google_reviews must be an object')
                continue
            rating, count = reviews.get('rating'), reviews.get('total_count')
            sample = reviews.get('visible_sample_count')
            if sample is not None and not number(sample, 0, integer=True):
                gap(row['id'] + ': invalid visible sample count')
            checked.append({'id': row['id'], 'visible_sample_count': sample,
                            'sample_caveat': 'Visible samples are not the total and cannot establish aggregate rating or trends.'})
            if row['coverage'] != 'aggregate':
                gap(row['id'] + ': Google aggregate rating/count unknown from snapshot/sample coverage')
                continue
            rating_valid, count_valid = number(rating, 1, 5), number(count, 0, integer=True)
            if rating is not None and not rating_valid:
                gap(row['id'] + ': invalid rating; requires finite numeric 1–5')
            if count is not None and not count_valid:
                gap(row['id'] + ': invalid total_count; requires nonnegative integer')
            if rating is None:
                gap(row['id'] + ': aggregate rating unknown')
            if count is None:
                gap(row['id'] + ': aggregate total_count unknown; missing is not zero')
            if count_valid and count == 0 and rating is not None:
                gap(row['id'] + ': conflicting zero total_count and supplied rating; aggregate withheld')
                continue
            if count_valid and number(sample, 0, integer=True) and sample > count:
                gap(row['id'] + ': visible sample exceeds total_count; aggregate withheld')
                continue
            profiles.append((row, rating if rating_valid else None, count if count_valid else None))
            actions = ['Confirm the current Google aggregate for this exact branch and save dated evidence.',
                       'Review customer feedback and operational issues before proposing remedies.', ETHICS]
            acceptance = ['Attach a fresh same-branch aggregate and document any approved service improvements.',
                          'Keep rating/review-growth outcomes unresolved until a comparable later observation; no ranking gain promised.']
            if rating_valid and rating < cfg['low_rating_threshold']:
                finding('LOCAL_LOW_GOOGLE_RATING', [row], f'Supplied Google rating {rating} is below configured threshold {cfg["low_rating_threshold"]}; aggregate total_count={count if count_valid else "unknown"}, visible_sample_count={sample if number(sample, 0, integer=True) else "unknown"}, observed_at={row["observed_at"]}.',
                        'Configurable investigation cue; business context can change interpretation. ' +
                        ('Confidence is low: aggregate count is unknown or below the configured low-volume threshold, so a small number of reviews may substantially affect the average.' if not count_valid or count < cfg['low_count_threshold'] else
                         'Confidence is bounded supplied evidence: aggregate count meets the configured volume threshold, providing more context than a small review count, but this is not a statistical reliability or authenticity assessment.') +
                        ' Visible samples are incomplete and cannot establish aggregates or trends.', actions, acceptance,
                        'low' if not count_valid or count < cfg['low_count_threshold'] else 'bounded_supplied_evidence')
            if count_valid and count < cfg['low_count_threshold']:
                finding('LOCAL_NO_GOOGLE_REVIEWS' if count == 0 else 'LOCAL_LOW_GOOGLE_REVIEW_COUNT', [row],
                        f'Supplied Google aggregate total_count = {count}; configured low-volume threshold = {cfg["low_count_threshold"]}.',
                        'Zero is supported only by an explicit aggregate zero. Volume heuristic is not a ranking diagnosis. Lifecycle/maturity: ' + str(row.get('maturity_group') or row.get('lifecycle') or 'unknown') + '; comparable peer context is not established by this threshold warning.', actions, acceptance, 'low')
        node = row.get('localbusiness')
        if node is not None:
            types = node.get('@type', []) if isinstance(node, dict) else []
            types = types if isinstance(types, list) else [types]
            if not isinstance(node, dict) or not any(isinstance(t, str) and t in LOCAL_TYPES for t in types):
                gap(row['id'] + ': LocalBusiness field check not assessed; explicit recognized local type required; unrecognized subtype remains unknown' )
            else:
                missing = [key for key in ('name', 'address', 'telephone', 'url') if not node.get(key)]
                invalid = [key for key in ('name', 'telephone') if node.get(key) is not None and not nonempty(node[key])]
                if node.get('url') is not None and not valid_url(node['url']):
                    invalid.append('url')
                if node.get('address') is not None and not (nonempty(node['address']) or isinstance(node['address'], dict) and bool(node['address'])):
                    invalid.append('address')
                checked.append({'id': row['id'], 'localbusiness_missing_fields': missing, 'localbusiness_invalid_fields': invalid,
                                'field_roles': {'name': 'Google documented required field', 'address': 'Google documented required field; address privacy must be reviewed', 'telephone': 'recommended field', 'url': 'recommended field'},
                                'scope': 'selected descriptive fields only; no full schema/Google eligibility assessment'})
                if missing or invalid:
                    finding('LOCALBUSINESS_FIELDS_REVIEW', [row], f'Scoped descriptive fields missing={missing}, invalid_shape={invalid}.',
                            'Scoped field review: name/address are documented required fields; telephone/url are recommended. This is not a complete eligibility decision.',
                            ['Confirm the node describes this branch and visible current content; review address privacy for service-area/home-based businesses before any publication.', 'Review only the listed fields and validate approved changes using appropriate schema tools.'],
                            ['Record truthful field values or documented reasons for omission; attach a visible-content comparison and scoped validation.'])

    websites = [r for r in good if r['source_kind'] == 'website']
    references = [r for r in good if r['source_kind'] in ('google_business_profile', 'directory')]
    if not websites or not references:
        gap('NAP/hours paired website and reference evidence unavailable')
    for a in websites:
        for b in references:
            if abs((timestamp(a['observed_at']) - timestamp(b['observed_at'])).total_seconds()) > cfg['max_pair_gap_days'] * 86400:
                gap(a['id'] + '/' + b['id'] + ': observation dates not comparable for NAP/hours')
                continue
            for field in ('name', 'address', 'phone'):
                av = a.get('nap', {}).get(field) if isinstance(a.get('nap'), dict) else None
                bv = b.get('nap', {}).get(field) if isinstance(b.get('nap'), dict) else None
                na, nb = normalize_nap(field, av), normalize_nap(field, bv)
                if na is None or nb is None:
                    gap(a['id'] + '/' + b['id'] + ': paired ' + field + ' unknown')
                elif na != nb:
                    finding('LOCAL_NAP_' + field.upper(), [a, b], f'Supplied {field} differs after conservative formatting normalization: {av!r} / {bv!r}.',
                            'Difference may be intentional; address abbreviations/country prefixes are not inferred.',
                            ['Confirm same branch and authoritative current value.', 'Correct only a source confirmed wrong after owner review.'],
                            ['Fresh paired evidence agrees with approved branch details or documents the intentional difference.'])
            ah, bh = a.get('hours'), b.get('hours')
            keys = ('timezone', 'regular', 'exceptions', 'effective_from', 'effective_to')
            def valid_hours(h):
                try:
                    return (isinstance(h, dict) and all(k in h for k in keys) and nonempty(h['timezone'])
                            and isinstance(h['regular'], dict) and isinstance(h['exceptions'], dict)
                            and date.fromisoformat(h['effective_from']) <= day <= date.fromisoformat(h['effective_to']))
                except (ValueError, TypeError):
                    return False
            if not valid_hours(ah) or not valid_hours(bh) or any(ah[k] != bh[k] for k in ('timezone', 'effective_from', 'effective_to')):
                gap(a['id'] + '/' + b['id'] + ': hours comparison requires same explicit timezone/current effective window and regular/exception coverage')
            elif ah['regular'] != bh['regular'] or ah['exceptions'] != bh['exceptions']:
                finding('LOCAL_HOURS_MISMATCH', [a, b], 'Supplied regular/exception hours differ for the same timezone and effective window.',
                        'Holiday/service-specific differences require operations review.',
                        ['Confirm current regular and exceptional opening hours with branch operations.', 'Correct only verified stale hours on approved sources.'],
                        ['Fresh paired evidence matches approved regular and exception hours for the same effective window.'])

    # Trend comparison requires two explicit aggregate snapshots from the same Google source URL.
    ordered_profiles = sorted(profiles, key=lambda p: timestamp(p[0]['observed_at']))
    for i, (new, nr, nc) in enumerate(ordered_profiles):
        for old, oldr, oldc in ordered_profiles[:i]:
            if new['source_url'] != old['source_url'] or timestamp(new['observed_at']) == timestamp(old['observed_at']):
                gap(new['id'] + '/' + old['id'] + ': aggregate trend not comparable (source URL or distinct dates)')
                continue
            checked.append({'comparison': 'dated_aggregate_change', 'evidence_ids': [old['id'], new['id']],
                            'rating_delta': round(nr - oldr, 6) if nr is not None and oldr is not None else None,
                            'total_count_delta': nc - oldc if nc is not None and oldc is not None else None,
                            'interpretation': 'Difference between supplied rounded aggregates only; no causal claim, sample-derived trend or forecast.'})
    if len(profiles) < 2:
        gap('Google aggregate trend unknown; two genuinely comparable dated aggregates required')
    for peer in peers:
        for target_row, rating, count in profiles:
            if (not nonempty(peer.get('comparison_group')) or not nonempty(peer.get('category'))
                    or any(peer.get(k) != target_row.get(k) for k in ('comparison_group', 'category'))
                    or not any(nonempty(peer.get(k)) and peer.get(k) == target_row.get(k) for k in ('maturity_group', 'lifecycle'))
                    or peer['coverage'] != 'aggregate'
                    or abs((timestamp(peer['observed_at']) - timestamp(target_row['observed_at'])).total_seconds()) > cfg['max_pair_gap_days'] * 86400):
                gap(peer['id'] + ': peer comparison withheld; matching category/group/market/date/aggregate coverage and explicit maturity/lifecycle required')
                continue
            pr = peer.get('google_reviews', {})
            if not isinstance(pr, dict) or not number(pr.get('rating'), 1, 5) or not number(pr.get('total_count'), 1, integer=True):
                gap(peer['id'] + ': comparable peer aggregate incomplete')
                continue
            checked.append({'comparison': 'supplied_peer', 'evidence_ids': [target_row['id'], peer['id']],
                            'rating_difference': round(rating - pr['rating'], 6) if rating is not None else None,
                            'total_count_difference': count - pr['total_count'] if count is not None else None,
                            'confidence': 'low', 'interpretation': 'Supplied selection only; no market benchmark, rank or causality inferred.'})
    if not any(c.get('comparison') == 'supplied_peer' for c in checked):
        gap('No comparable peer context supplied; rating/count threshold warnings are not comparative market judgments')
    if not profiles:
        gap('Current Google aggregate reputation unknown; no valid supplied aggregate evidence')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('--out', required=True)
    parser.add_argument('--as-of')
    args = parser.parse_args()
    try:
        result = analyze_local_evidence(json.loads(Path(args.input).read_text(encoding='utf-8')), args.as_of)
        output = Path(args.out)
        output.mkdir(parents=True, exist_ok=False)
        (output / 'local-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except (ValueError, TypeError, OSError) as error:
        parser.exit(2, 'Error: ' + str(error) + '\n')
    print(str(output))


if __name__ == '__main__':
    main()
