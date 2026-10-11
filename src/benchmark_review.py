"""Offline human-review gate. No extraction, API calls, or automatic gold labels."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from src.config import PROJECT_ROOT
from src.mapqa_data import read_snapshot, save_json
from src.mapqa_evidence import CompleteEvidenceOutput
from src.osm_values import parse_speed

DEFAULT_FOLDER = PROJECT_ROOT / 'data' / 'benchmark_review_v2'
BASELINE_FILES = ('src/mapqa_evidence.py', 'src/models.py', 'src/osm_values.py',
                  'src/local_ollama.py', 'src/mapqa_benchmark.py')
QUOTAS = {'records': 40, 'numeric_speed': 12, 'barrier_present': 10,
          'barrier_absent': 10, 'barrier_unknown': 10, 'osm_free_text': 5,
          'human_text': 10}
ORIGINS = {'osm_free_text', 'human_osm_description', 'human_authored_scenario'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def object_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def baseline_hashes(root=PROJECT_ROOT):
    return {name: digest(Path(root) / name) for name in BASELINE_FILES}


def existing_groups(data_dir):
    ids, groups = set(), set()
    for path in Path(data_dir).glob('evidence_*.json'):
        value = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(value, list):
            continue
        for row in value:
            if row.get('osm_way_id') is not None:
                ids.add(str(row['osm_way_id']))
            if row.get('road_group'):
                groups.add(row['road_group'])
    # Also exclude legacy masked-tag data when IDs are supplied.
    for path in (PROJECT_ROOT / 'data').glob('osm_*.json'):
        value = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(value, list):
            ids.update(str(row['osm_way_id']) for row in value if row.get('osm_way_id') is not None)
    return ids, groups


def choose_sources(snapshot, excluded_ids, excluded_groups, count=40):
    ways = sorted((e for e in snapshot['elements'] if e['type'] == 'way'), key=lambda e: e['id'])
    barriers = {e['id']: e for e in snapshot['elements']
                if e['type'] == 'node' and e.get('tags', {}).get('barrier')}
    selected, used = [], set(excluded_groups)
    def add(predicate, target):
        added = 0
        for way in ways:
            group = way.get('tags', {}).get('name') or 'way:' + str(way['id'])
            if str(way['id']) in excluded_ids or group in used or not predicate(way):
                continue
            selected.append(way)
            used.add(group)
            added += 1
            if added >= target:
                break
    add(lambda w: bool(w.get('tags', {}).get('note') or w.get('tags', {}).get('description')), 10)
    add(lambda w: parse_speed(w.get('tags', {}).get('maxspeed')) is not None, 12)
    add(lambda w: bool(set(w.get('nodes', [])) & set(barriers)), 10)
    add(lambda w: True, count - len(selected))
    if len(selected) != count:
        raise ValueError('Not enough distinct unused source groups')
    sources = []
    for way in selected:
        sources.append({'way_id': str(way['id']),
                        'road_group': way.get('tags', {}).get('name') or 'way:' + str(way['id']),
                        'url': 'https://www.openstreetmap.org/way/' + str(way['id']),
                        'tags': way.get('tags', {}),
                        'free_text': {k: way['tags'][k] for k in ('note', 'description') if k in way.get('tags', {})},
                        'connected_barrier_nodes': [
                            {'node_id': str(n), 'tags': barriers[n]['tags'],
                             'url': 'https://www.openstreetmap.org/node/' + str(n)}
                            for n in way.get('nodes', []) if n in barriers]})
    return sources


def prepare(folder=DEFAULT_FOLDER, data_dir=None):
    folder = Path(folder)
    if folder.exists():
        raise FileExistsError('Review directory already exists; never overwrite human work')
    data_dir = Path(data_dir or PROJECT_ROOT / 'data' / 'mapqa')
    # Take the code fingerprint before even selecting new candidate records.
    frozen_code = baseline_hashes()
    snapshot = read_snapshot(data_dir)
    ids, groups = existing_groups(data_dir)
    sources = choose_sources(snapshot, ids, groups)
    manifest = {'status': 'pending_human_review', 'created_at': datetime.now(timezone.utc).isoformat(),
                'snapshot_sha256': digest(data_dir / 'snapshot.json'),
                'baseline_sha256': frozen_code, 'quotas': QUOTAS,
                'selection': 'Sorted IDs, distinct unused name/ID groups; free text, speed, barrier, then other sources. Not representative.',
                'source_sha256': {s['way_id']: object_digest(s) for s in sources},
                'independent_field_verification': False,
                'model_evaluation_performed': False, 'prompt': 'v6'}
    packets = [{'segment_id': 'review-v2-' + s['way_id'], 'source': s,
                'review': {'status': 'pending', 'reviewer': None, 'reviewer_kind': None,
                           'reviewed_at': None, 'input_origin': None, 'input': None,
                           'evidence': [], 'expected_attributes': None}} for s in sources]
    save_json(folder / 'manifest.json', manifest)
    save_json(folder / 'review_packets.json', packets)
    lines = ['# Fișe de revizuire — încă nerevizuite', '',
             'Completează review_packets.json conform docs/BENCHMARK_REVIEW_RO.md.',
             'Nu executa reguli/LLM pe aceste fișe înainte de înghețare.',
             'Tag lipsă ≠ barieră absentă. Textele și tag-urile nu sunt etichete gold.', '']
    for s in sources:
        lines += [f"## {s['way_id']} — [sursa OSM]({s['url']})", '',
                  'Tag-uri originale: `' + json.dumps(s['tags'], ensure_ascii=False) + '`',
                  'Text OSM literal: `' + json.dumps(s['free_text'], ensure_ascii=False) + '`',
                  f"Noduri barieră conectate: {len(s['connected_barrier_nodes'])}. Absența lor nu dovedește lipsa unei bariere.",
                  'Input, origine, etichete, reviewer, dată și dovadă: **de completat de om**.', '']
    (folder / 'REVIEW_RO.md').write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    return status(folder)


def validate_time(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Date must include timezone')


def validate_review(packet):
    review = packet['review']
    if review.get('status') != 'reviewed':
        raise ValueError('Pending human review')
    if review.get('reviewer_kind') != 'human' or not str(review.get('reviewer') or '').strip():
        raise ValueError('Named human reviewer required; assistant review is insufficient')
    validate_time(review['reviewed_at'])
    origin = review['input_origin']
    if origin not in ORIGINS:
        raise ValueError('Unknown text origin')
    data = review['input']
    if not isinstance(data, dict) or set(data) != {'name', 'osm_tags', 'context_description'}:
        raise ValueError('Input must have exactly name, osm_tags and context_description')
    if not isinstance(data['name'], str) or not isinstance(data['context_description'], str) or not data['context_description'].strip():
        raise ValueError('Input text required')
    tags = data['osm_tags']
    if not isinstance(tags, dict) or any(packet['source']['tags'].get(k) != v for k, v in tags.items()):
        raise ValueError('Input tags must be an unchanged source subset')
    if origin == 'human_authored_scenario' and tags:
        raise ValueError('Fictional scenarios must not claim source tags')
    if origin == 'osm_free_text' and data['context_description'] not in packet['source']['free_text'].values():
        raise ValueError('Real OSM text must be literal note/description')
    evidence = review.get('evidence')
    if not isinstance(evidence, list) or not evidence:
        raise ValueError('Human source-check evidence required')
    for item in evidence:
        parsed = urlparse(item['url'])
        if parsed.scheme != 'https' or not parsed.hostname or not str(item.get('note') or '').strip():
            raise ValueError('HTTPS evidence URL and review note required')
        validate_time(item['accessed_at'])
    # Strict JSON validation rejects omitted defaults and coerced strings/bools.
    expected = CompleteEvidenceOutput.model_validate_json(json.dumps(review['expected_attributes']), strict=True)
    if not expected.reasoning_cot.strip():
        raise ValueError('Brief label evidence summary required')
    return expected


def status(folder=DEFAULT_FOLDER):
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    packets = json.loads((folder / 'review_packets.json').read_text(encoding='utf-8'))
    errors = []
    if baseline_hashes() != manifest['baseline_sha256']:
        errors.append('Baseline code changed after preparation')
    if manifest['quotas'] != QUOTAS:
        errors.append('Review quotas altered')
    if digest(PROJECT_ROOT / 'data/mapqa/snapshot.json') != manifest['snapshot_sha256']:
        errors.append('Snapshot changed')
    counts = {k: 0 for k in QUOTAS}
    seen = set()
    for packet in packets:
        way_id = packet['source']['way_id']
        if way_id in seen or packet.get('segment_id') != 'review-v2-' + way_id:
            errors.append('Duplicate/mismatched ID: ' + way_id)
        seen.add(way_id)
        if object_digest(packet['source']) != manifest['source_sha256'].get(way_id):
            errors.append('Source altered: ' + way_id)
        try:
            expected = validate_review(packet)
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            errors.append(way_id + ': ' + str(exc))
            continue
        counts['records'] += 1
        counts['numeric_speed'] += expected.speed_limit_kmh is not None
        field = 'barrier_unknown' if expected.barrier_present is None else ('barrier_present' if expected.barrier_present else 'barrier_absent')
        counts[field] += 1
        if packet['review']['input_origin'] == 'osm_free_text':
            counts['osm_free_text'] += 1
        else:
            counts['human_text'] += 1
    if seen != set(manifest['source_sha256']) or len(packets) != QUOTAS['records']:
        errors.append('The original 40-source membership must be preserved')
    for key, minimum in QUOTAS.items():
        if counts[key] < minimum:
            errors.append(f'Coverage {key}: {counts[key]} < {minimum}')
    return {'eligible_for_freeze': not errors, 'counts': counts, 'required': QUOTAS,
            'errors': errors, 'model_evaluation_performed': False,
            'independent_field_verification': False}


def freeze(folder=DEFAULT_FOLDER):
    folder = Path(folder)
    if (folder / 'frozen_manifest.json').exists() or (folder / 'frozen_dataset.json').exists():
        raise FileExistsError('A frozen set is never overwritten')
    check = status(folder)
    if not check['eligible_for_freeze']:
        raise ValueError('Cannot freeze: ' + '; '.join(check['errors']))
    packets = json.loads((folder / 'review_packets.json').read_text(encoding='utf-8'))
    records = [{'segment_id': p['segment_id'], **p['review']['input'],
                'expected_attributes': p['review']['expected_attributes'],
                'source': p['review']['input_origin'], 'osm_way_id': p['source']['way_id'],
                'road_group': p['source']['road_group'], 'human_review': p['review'],
                'evaluation_fields': ['road_type', 'speed_limit_kmh', 'surface', 'oneway',
                                      'barrier_present', 'barrier_type', 'anomaly_flag', 'input_instruction_detected']}
               for p in packets]
    save_json(folder / 'frozen_dataset.json', records)
    original = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    result = {**original, 'status': 'human_reviewed_frozen', 'frozen_at': datetime.now(timezone.utc).isoformat(),
              'counts': check['counts'], 'review_packets_sha256': digest(folder / 'review_packets.json'),
              'dataset_sha256': digest(folder / 'frozen_dataset.json'),
              'human_review_attestation': 'Self-attested, not independent field verification',
              'model_evaluation_performed': False}
    save_json(folder / 'frozen_manifest.json', result)
    return result
