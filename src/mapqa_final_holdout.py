"""Reserve a fresh grouped hold-out after diagnosing optional-field omissions."""
from datetime import datetime, timezone
import hashlib
import json
import random
from src.mapqa_evidence import reference_for_way, transcription
from src.mapqa_data import save_json


def reserve_final(roads,associations,data_dir,count=40):
    path=data_dir/'final_holdout_manifest.json'
    if path.exists():
        manifest=json.loads(path.read_text(encoding='utf-8'))
        for name,digest in manifest['file_sha256'].items():
            if hashlib.sha256((data_dir/name).read_bytes()).hexdigest()!=digest:
                raise ValueError('Final hold-out hash mismatch')
        return manifest
    earlier=[]
    for split in ('dev','test'):
        earlier+=json.loads((data_dir/f'evidence_{split}.json').read_text(encoding='utf-8'))
    groups={r['road_group'] for r in earlier}
    candidate=[]
    for road in roads.itertuples():
        group=road.tags.get('name') or 'way:'+road.way_id
        if group in groups: continue
        expected=reference_for_way(road,associations)
        if expected.barrier_present is True:
            candidate.append((road,expected,group))
    random.Random(31415).shuffle(candidate)
    records=[]
    for road,expected,group in candidate:
        if group in groups: continue
        groups.add(group)
        language='ro' if len(records)%2==0 else 'en'
        records.append({'segment_id':'final-'+road.way_id,'osm_way_id':road.way_id,'name':'Road segment',
                        'osm_tags':{},'context_description':transcription(expected,language),
                        'expected_attributes':expected.model_dump(mode='json'),'road_group':group,
                        'language':language,'manual_field_verification':False,
                        'source':'OSM-derived controlled transcription',
                        'evaluation_fields':earlier[0]['evaluation_fields']})
        if len(records)==count: break
    if len(records)!=count: raise ValueError('Not enough fresh road groups')
    name='evidence_test_final.json'
    save_json(data_dir/name,records)
    manifest={'created_at':datetime.now(timezone.utc).isoformat(),'seed':31415,'n':count,
              'file_sha256':{name:hashlib.sha256((data_dir/name).read_bytes()).hexdigest()},
              'excluded_groups':'All evidence_dev and initial evidence_test groups',
              'selection':'Only source-connected barrier roads; nonrepresentative positive-barrier sample.',
              'reason':'Initial hold-out consumed by v5. v6 contract corrected from development raw responses; fresh final test reserved before v6 selection.',
              'independent_field_verification':False}
    save_json(path,manifest)
    return manifest


def freeze_v6(output):
    path=output/'selection_v6.json'
    if path.exists(): return json.loads(path.read_text(encoding='utf-8'))
    scores=[json.loads((output/'benchmarks'/f'langchain__v6__{s}'/'benchmark_summary.json').read_text(encoding='utf-8'))
            for s in ('dev','hard')]
    result={'prompt':'v6','model':scores[0]['model'],'model_digests':scores[0]['model_digests'],
            'frozen_at':datetime.now(timezone.utc).isoformat(),
            'reason':'Explicitly required output fields, diagnosed from development omissions in v4/v5.',
            'development_scores':[{k:s[k] for k in ('split','n','exact_match_rate','failure_rate','dataset_sha256')} for s in scores],
            'initial_holdout_already_used':True,'final_holdout_used_for_selection':False,
            'policy':'No further tuning against evidence_test_final. Reuse its saved outputs only.'}
    save_json(path,result)
    return result
