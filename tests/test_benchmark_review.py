"""Review gate tests use fictional fixtures, never approve the real packets."""
import json
import pytest
from src.benchmark_review import (QUOTAS, baseline_hashes, digest, object_digest,
                                 status, freeze, prepare, choose_sources, validate_review)
from src.config import PROJECT_ROOT
from src.mapqa_data import save_json
from src.mapqa_evidence import CompleteEvidenceOutput


def packet(index):
    present = True if index < 10 else False if index < 20 else None
    source = {'way_id': str(index), 'road_group': 'fixture:' + str(index),
              'url': 'https://www.openstreetmap.org/way/' + str(index),
              'tags': {'highway': 'residential'}, 'free_text': {'note': 'Fixture text'},
              'connected_barrier_nodes': []}
    attributes = {'road_type': 'residential', 'speed_limit_kmh': 30 if index < 12 else None,
                  'barrier_present': present, 'barrier_type': 'gate' if present else 'none' if present is False else 'unknown',
                  'surface': 'unknown', 'oneway': None, 'anomaly_flag': False,
                  'input_instruction_detected': False, 'confidence_score': 1,
                  'reasoning_cot': 'Fictional fixture for validating the gate, not real source truth.'}
    review = {'status': 'reviewed', 'reviewer': 'Test fixture, not actual human review',
              'reviewer_kind': 'human', 'reviewed_at': '2026-10-11T20:00:00+00:00',
              'input_origin': 'osm_free_text' if index < 20 else 'human_authored_scenario',
              'input': {'name': 'Fixture', 'osm_tags': {}, 'context_description': 'Fixture text'},
              'evidence': [{'url': source['url'], 'accessed_at': '2026-10-11T20:00:00+00:00',
                            'note': 'Test fixture only; not an approval of real data.'}],
              'expected_attributes': attributes}
    return {'segment_id': 'review-v2-' + str(index), 'source': source, 'review': review}


@pytest.fixture
def review_folder(tmp_path):
    packets = [packet(i) for i in range(40)]
    save_json(tmp_path / 'review_packets.json', packets)
    save_json(tmp_path / 'manifest.json', {'baseline_sha256': baseline_hashes(), 'quotas': QUOTAS,
        'snapshot_sha256': digest(PROJECT_ROOT / 'data/mapqa/snapshot.json'),
        'source_sha256': {p['source']['way_id']: object_digest(p['source']) for p in packets},
        'independent_field_verification': False})
    return tmp_path


def alter(folder, mutate):
    path = folder / 'review_packets.json'
    values = json.loads(path.read_text(encoding='utf-8'))
    mutate(values)
    save_json(path, values)


def test_pending_review_cannot_freeze(review_folder):
    alter(review_folder, lambda p: p[0]['review'].update(status='pending'))
    with pytest.raises(ValueError, match='Pending human review'):
        freeze(review_folder)
    assert not (review_folder / 'frozen_dataset.json').exists()


def test_complete_fixture_freezes_once(review_folder):
    assert status(review_folder)['eligible_for_freeze']
    result = freeze(review_folder)
    assert result['counts']['barrier_absent'] == 10
    assert not result['model_evaluation_performed']
    assert not result['independent_field_verification']
    assert result['dataset_sha256'] == digest(review_folder / 'frozen_dataset.json')
    with pytest.raises(FileExistsError):
        freeze(review_folder)


def test_source_alteration_and_duplicate_ids_rejected(review_folder):
    alter(review_folder, lambda p: p[0]['source']['tags'].update(barrier='no'))
    assert any('Source altered' in e for e in status(review_folder)['errors'])
    alter(review_folder, lambda p: p.__setitem__(1, p[0]))
    assert any('Duplicate' in e for e in status(review_folder)['errors'])


def test_changed_baseline_or_quotas_rejected(review_folder):
    path = review_folder / 'manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    manifest['baseline_sha256']['src/models.py'] = 'changed'
    manifest['quotas'] = {**QUOTAS, 'barrier_absent': 0}
    save_json(path, manifest)
    errors = status(review_folder)['errors']
    assert any('Baseline' in e for e in errors)
    assert any('quotas' in e for e in errors)


@pytest.mark.parametrize('field,value', [('reviewer_kind', 'assistant'), ('reviewer', ''),
    ('reviewed_at', '2026-10-11'), ('input_origin', 'automatic_transcription')])
def test_invalid_attestation_rejected(field, value):
    p = packet(0)
    p['review'][field] = value
    with pytest.raises(ValueError):
        validate_review(p)


def test_missing_output_field_and_fake_tag_rejected():
    p = packet(0)
    del p['review']['expected_attributes']['oneway']
    with pytest.raises(ValueError): validate_review(p)
    p = packet(0)
    p['review']['input']['osm_tags'] = {'barrier': 'no'}
    with pytest.raises(ValueError, match='source subset'): validate_review(p)


def test_no_negative_barriers_fails_coverage(review_folder):
    def change(packets):
        for p in packets:
            if p['review']['expected_attributes']['barrier_present'] is False:
                p['review']['expected_attributes'].update(barrier_present=None, barrier_type='unknown')
    alter(review_folder, change)
    assert any('Coverage barrier_absent: 0' in e for e in status(review_folder)['errors'])


def test_literal_osm_text_not_assistant_paraphrase():
    p = packet(0)
    p['review']['input']['context_description'] = 'Generated text'
    with pytest.raises(ValueError, match='literal'): validate_review(p)


def test_prepare_preserves_existing_human_work(review_folder):
    with pytest.raises(FileExistsError): prepare(review_folder)


def test_source_selection_does_not_invent_absence():
    snapshot = {'elements': [{'type': 'way', 'id': i, 'nodes': [],
                             'tags': {'highway': 'service'}} for i in range(50)]}
    sources = choose_sources(snapshot, {'0'}, {'way:1'})
    assert len(sources) == 40
    assert not {'0', '1'} & {s['way_id'] for s in sources}
    assert all('barrier' not in s['tags'] and not s['connected_barrier_nodes'] for s in sources)
    assert all('expected_attributes' not in s for s in sources)
