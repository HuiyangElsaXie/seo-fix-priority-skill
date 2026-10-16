"""Offline converter for already-authorized Places/GBP JSON exports. No network."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
try:
    from .local_seo_evidence import analyze_local_evidence
except ImportError:
    from local_seo_evidence import analyze_local_evidence


def convert(raw, metadata, format_name):
    if not isinstance(raw, dict) or not isinstance(metadata, dict):
        raise ValueError('export and metadata must be JSON objects')
    target = metadata.get('target')
    base = metadata.get('observation')
    if not isinstance(target, dict) or not isinstance(base, dict):
        raise ValueError('metadata requires target and observation objects')
    # Keep only provenance/context fields; never propagate tokens, review text or claimed verification.
    allowed = {'id', 'entity_id', 'branch_id', 'place_id', 'market', 'source_url',
               'captured_at', 'observed_at', 'category', 'comparison_group', 'maturity_group', 'lifecycle'}
    row = {k: copy.deepcopy(v) for k, v in base.items() if k in allowed}
    for key in ('entity_id', 'branch_id', 'place_id', 'market'):
        if not isinstance(target.get(key), str) or not target[key].strip():
            raise ValueError('explicit target identity required: ' + key)
        if key in row and row[key] != target[key]:
            raise ValueError('observation conflicts with target: ' + key)
        row[key] = target[key]
    if format_name == 'places':
        if raw.get('id') != target['place_id']:
            raise ValueError('raw Places id must match target place_id; never infer by business name')
        reviews = raw.get('reviews')
        if reviews is not None and not isinstance(reviews, list):
            raise ValueError('Places reviews must be list when supplied')
        row['google_reviews'] = {'rating': raw.get('rating'), 'total_count': raw.get('userRatingCount'),
                                 'visible_sample_count': len(reviews) if reviews is not None else None}
        row['nap'] = {'name': raw.get('displayName', {}).get('text') if isinstance(raw.get('displayName'), dict) else None,
                      'address': raw.get('formattedAddress'),
                      'phone': raw.get('internationalPhoneNumber') or raw.get('nationalPhoneNumber')}
        if raw.get('businessStatus') is not None:
            row['operating_status'] = raw['businessStatus']
        row['source_method'] = 'supplied_places_api_response; no live API request or ownership verification'
    elif format_name == 'gbp':
        resource = metadata.get('resource_name')
        if not isinstance(resource, str) or not resource.startswith('accounts/') or '/locations/' not in resource or target.get('gbp_resource_name') != resource:
            raise ValueError('GBP requires matching supplied resource_name and target.gbp_resource_name; response alone cannot prove branch')
        reviews = raw.get('reviews')
        if reviews is not None and not isinstance(reviews, list):
            raise ValueError('GBP reviews must be list when supplied')
        row['google_reviews'] = {'rating': raw.get('averageRating'), 'total_count': raw.get('totalReviewCount'),
                                 'visible_sample_count': len(reviews) if reviews is not None else None}
        row['source_method'] = 'supplied_gbp_reviews_list_response; location binding supplied, not independently verified'
        row['pagination'] = 'more_pages_available' if raw.get('nextPageToken') else 'no_next_token_in_supplied_response; completeness_not_independently_verified'
        row['resource_name'] = resource
    else:
        raise ValueError('format must be places or gbp')
    row['source_kind'] = 'google_business_profile'
    row['coverage'] = 'aggregate'
    row['export_sha256'] = hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()
    # Aggregate fields originate only in raw export; never computed from visible reviews.
    result = {'schema_version': '1.0', 'as_of': metadata.get('as_of'), 'target': {k: target[k] for k in ('entity_id', 'branch_id', 'place_id', 'market', 'gbp_resource_name') if k in target}, 'observations': [row]}
    if 'config' in metadata:
        result['config'] = copy.deepcopy(metadata['config'])
    checked = analyze_local_evidence(result)
    if checked.get('rejected'):
        raise ValueError('supplied export metadata rejected: ' + json.dumps(checked['rejected']))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--format', choices=['places', 'gbp'], required=True)
    p.add_argument('--raw', required=True)
    p.add_argument('--metadata', required=True)
    p.add_argument('--out', required=True, help='New JSON file, never overwritten')
    a = p.parse_args()
    try:
        result = convert(json.loads(Path(a.raw).read_text()), json.loads(Path(a.metadata).read_text()), a.format)
        with Path(a.out).open('x', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            f.write('\n')
    except (ValueError, OSError, TypeError, KeyError) as e:
        p.exit(2, str(e) + '\n')
    print(a.out)


if __name__ == '__main__':
    main()
