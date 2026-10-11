"""Reproducible local evidence benchmarks. Labels never enter model requests."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from src.config import PROJECT_ROOT
from src.evaluator import classification_metrics, label
from src.mapqa_data import DEFAULT_DATA, save_json
from src.mapqa_evidence import (EvidenceOutput, CompleteEvidenceOutput, LangChainEvidenceExtractor,
                               evidence_messages, evidence_rules, hybrid_guard)
from src.local_ollama import local_settings

OUTPUT = PROJECT_ROOT / 'reports' / 'mapqa'


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def verified_records(split, folder=DEFAULT_DATA):
    if split not in ('dev', 'hard', 'test', 'test_final'):
        raise ValueError('Unknown evidence split')
    name = f'evidence_{split}.json'
    manifest_name='final_holdout_manifest.json' if split=='test_final' else 'evidence_manifest.json'
    manifest = json.loads((folder/manifest_name).read_text(encoding='utf-8'))
    digest = hashlib.sha256((folder/name).read_bytes()).hexdigest()
    if digest != manifest['file_sha256'][name]:
        raise ValueError('Evidence dataset changed: '+name)
    return json.loads((folder/name).read_text(encoding='utf-8')), digest


def evaluate(records, predictions):
    if not records or len(records) != len(predictions):
        raise ValueError('Need aligned nonempty records and predictions')
    fields = records[0]['evaluation_fields']
    errors, examples, details = Counter(), [], Counter()
    attributes = {}
    exact = 0
    for record, result in zip(records, predictions):
        if record['segment_id'] != result['segment_id']:
            raise ValueError('Prediction/reference ID mismatch')
        actual = result['output'] if result['status'] == 'success' else None
        differences = [f for f in fields if actual is None or actual[f] != record['expected_attributes'][f]]
        exact += not differences
        categories = [result['status']] if actual is None else differences
        errors.update(categories)
        detail_categories=[]
        for field in differences:
            if actual is None:
                detail_categories=[result['status']]
                break
            truth,pred=record['expected_attributes'][field],actual[field]
            if field=='speed_limit_kmh':
                category='speed_unsupported_by_reference' if truth is None else ('speed_missing' if pred is None else 'speed_mismatch')
            elif field=='barrier_present':
                category=('barrier_false_negative' if truth is True else
                          'barrier_false_positive' if truth is False and pred is True else
                          'barrier_unsupported_by_reference' if truth is None and pred is True else 'barrier_presence_unknown')
            elif field in ('input_instruction_detected','anomaly_flag'):
                category=field+('_false_negative' if truth else '_false_positive')
            else:
                category=field+'_mismatch'
            detail_categories.append(category)
        details.update(detail_categories)
        if differences:
            examples.append({'segment_id':record['segment_id'], 'input':{
                'osm_tags':record['osm_tags'], 'context_description':record['context_description']},
                'expected':record['expected_attributes'], 'actual':actual, 'errors':categories,
                'detail_categories':detail_categories})
    for field in fields:
        truth = [label(r['expected_attributes'][field]) for r in records]
        predicted = [label(p['output'][field]) if p['status']=='success' else '__failed__' for p in predictions]
        attributes[field] = classification_metrics(truth, predicted)
    known = [(r,p) for r,p in zip(records,predictions) if r['expected_attributes']['speed_limit_kmh'] is not None]
    attributes['speed_limit_kmh']['known_exact_accuracy'] = (
        sum(p['status']=='success' and p['output']['speed_limit_kmh']==r['expected_attributes']['speed_limit_kmh']
            for r,p in known)/len(known)) if known else None
    return {'n':len(records), 'exact_match_rate':exact/len(records),
            'failure_rate':sum(p['status']!='success' for p in predictions)/len(records),
            'invalid_output_rate':sum(p['status']=='invalid_output' for p in predictions)/len(records),
            'error_taxonomy':dict(errors), 'error_detail_taxonomy':dict(details),'attributes':attributes}, examples


def benchmark(split='dev', mode='rules', version='v4', model='qwen2.5:3b',
              data_dir=DEFAULT_DATA, output=OUTPUT, cached_only=False, allow_holdout=False):
    if mode not in ('rules','langchain','hybrid'):
        raise ValueError('Only rules and local LangChain/hybrid are supported; no cloud billing')
    if version not in ('v4','v5','v6'):
        raise ValueError('Use v4, v5 or v6 for the evidence task')
    if split in ('test','test_final'):
        freeze_path=output/('selection_v6.json' if split=='test_final' else 'selection.json')
        if not freeze_path.exists() or not allow_holdout:
            raise ValueError('Freeze a dev-selected prompt first, then explicitly allow the hold-out.')
        selected=json.loads(freeze_path.read_text(encoding='utf-8'))
        if mode!='rules' and (version!=selected['prompt'] or model!=selected['model']):
            raise ValueError('Hold-out only permits the frozen selected prompt/model')
    records, dataset_sha=verified_records(split,data_dir)
    extractor=None
    model_digest='not-applicable'
    if mode != 'rules' and not cached_only:
        extractor=LangChainEvidenceExtractor(version,model)
        model_digest=extractor.digest
    # Code/source digest invalidates stale results after a semantic change.
    code_hash=fingerprint({name:hashlib.sha256((PROJECT_ROOT/'src'/name).read_bytes()).hexdigest()
                           for name in ('mapqa_evidence.py','osm_values.py','models.py')})
    predictions=[]
    for index, record in enumerate(records):
        messages=[m.model_dump(mode='json') for m in evidence_messages(record,version)]
        schema=CompleteEvidenceOutput if version=='v6' else EvidenceOutput
        spec={'messages':messages, 'schema':schema.model_json_schema(), 'model':model,
              'generation':local_settings(), 'code_hash':code_hash}
        # Digest resides inside the response and live reads verify it. Offline reads use request identity.
        key=fingerprint(spec)
        path=PROJECT_ROOT/'results'/'mapqa'/model.replace(':','_')/version/(key+'.json')
        source=None
        if mode != 'rules' and path.exists():
            source=json.loads(path.read_text(encoding='utf-8'))
            if source.get('request_sha256')!=key or (extractor and source['model_digest']!=model_digest):
                source=None
        if mode=='rules':
            result={'status':'success','output':evidence_rules(record).model_dump(mode='json'),
                    'token_usage':{}, 'model_digest':'not-applicable','cache_hit':False}
        else:
            if source is None:
                if cached_only:
                    raise FileNotFoundError('Missing local response: '+str(path))
                start=time.perf_counter()
                try:
                    parsed, details=extractor.extract(record)
                    source={**details,'output':parsed.model_dump(mode='json') if parsed else None}
                except Exception as exc:
                    source={'status':'api_error','output':None,'error':type(exc).__name__+': local inference failed',
                            'model_digest':extractor.digest,'token_usage':{}}
                source.update(request_sha256=key,elapsed_s=time.perf_counter()-start,
                              recorded_at=datetime.now(timezone.utc).isoformat())
                save_json(path,source)
                print(f'{mode}/{version}/{split}: {index+1}/{len(records)} {source["status"]}',flush=True)
                cache_hit=False
            else:
                cache_hit=True
            result={**source,'cache_hit':cache_hit}
            if mode=='hybrid' and result['status']=='success':
                guarded, changes=hybrid_guard(record,EvidenceOutput.model_validate(result['output']))
                result={**result,'output':guarded.model_dump(mode='json'),'guard_fields':changes}
        predictions.append({**result,'segment_id':record['segment_id']})
    summary, examples=evaluate(records,predictions)
    summary.update(mode=mode,prompt=version if mode!='rules' else 'not-applicable',model=model if mode!='rules' else 'rules',
                   split=split,dataset_sha256=dataset_sha,run_at=datetime.now(timezone.utc).isoformat(),
                   model_digests=sorted(set(p['model_digest'] for p in predictions)),
                   cached_responses=sum(p['cache_hit'] for p in predictions),
                   task='OSM-derived controlled text extraction; synthetic hard scenarios; NOT independently verified map truth.')
    folder=output/'benchmarks'/f'{mode}__{version}__{split}'
    save_json(folder/'benchmark_summary.json',summary)
    save_json(folder/'predictions.json',predictions)
    save_json(folder/'error_examples.json',examples)
    report=['# Evidence benchmark', '',f'Mode: {mode}; prompt: {version}; split: {split}; n={summary["n"]}.',
            f'Exact match: {summary["exact_match_rate"]:.1%}; failures: {summary["failure_rate"]:.1%}.',
            '',summary['task'],'', '## Attribute scores','', '| Field | Precision | Recall | F1 | Known accuracy |',
            '|---|---:|---:|---:|---:|']
    for field, score in summary['attributes'].items():
        known=score['known_reference_accuracy']
        report.append(f'| {field} | {score["precision"]:.3f} | {score["recall"]:.3f} | {score["f1_score"]:.3f} | {known if known is not None else "N/A"} |')
    report+=['','Error taxonomy: '+json.dumps(summary['error_taxonomy']), '',
             'Null/unknown support can inflate exact match. See per-class supports and raw responses.',
             'Confidence is not calibrated. Hybrid guards are Python rules, not prompt improvements.']
    (folder/'report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    return summary


def freeze_selection(output=OUTPUT, model='qwen2.5:3b'):
    path=output/'selection.json'
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    candidates=[]
    for version in ('v4','v5'):
        summaries=[json.loads((output/'benchmarks'/f'langchain__{version}__{split}'/'benchmark_summary.json').read_text(encoding='utf-8'))
                   for split in ('dev','hard')]
        if any(s['model']!=model for s in summaries):
            raise ValueError('Selection requires identical models')
        # Predeclared: failures first, then combined development errors, stable v4 tie-break.
        failures=sum(s['failure_rate']*s['n'] for s in summaries)
        matches=sum(s['exact_match_rate']*s['n'] for s in summaries)
        candidates.append((failures,-matches,version,summaries))
    selected=min(candidates,key=lambda c:c[:3])
    result={'prompt':selected[2], 'model':model, 'frozen_at':datetime.now(timezone.utc).isoformat(),
            'criterion':'Fewest failures, then most exact matches across dev+fictional hard; v4 tie-break.',
            'holdout_used_for_selection':False, 'candidates':[
                {'prompt':v,'failures':f,'exact_matches':-m,'dataset_sha256':[s['dataset_sha256'] for s in summaries]}
                for f,m,v,summaries in candidates],
            'limitations':'Development hard cases reused in few-shots; new grouped hold-out used only after selection.'}
    save_json(path,result)
    return result
