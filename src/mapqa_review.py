"""Trace references to source tags; generated cases stay quarantined for human review."""
from datetime import datetime, timezone
import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from src.mapqa_data import save_json
from src.mapqa_evidence import EvidenceOutput, LangChainEvidenceExtractor, reference_for_way
from langchain_core.messages import SystemMessage, HumanMessage


def audit_references(roads, associations, data_dir, output):
    byid={r.way_id:r for r in roads.itertuples()}
    queue=[]
    groups=[]
    splits=['dev','test']
    if (data_dir/'evidence_test_final.json').exists(): splits.append('test_final')
    for split in splits:
        records=json.loads((data_dir/f'evidence_{split}.json').read_text(encoding='utf-8'))
        groups.append({r['road_group'] for r in records})
        for record in records:
            road=byid[record['osm_way_id']]
            expected=reference_for_way(road,associations).model_dump(mode='json')
            if any(expected[f]!=record['expected_attributes'][f] for f in record['evaluation_fields']):
                raise ValueError('Reference/source mismatch: '+record['segment_id'])
            nodes=[a['node_id'] for a in associations if a['way_id']==road.way_id and a['confirmed_topology']]
            queue.append({'segment_id':record['segment_id'],'split':split,'way_id':road.way_id,
                          'source_tags':road.tags,'connected_barrier_node_ids':nodes,
                          'osm_url':'https://www.openstreetmap.org/way/'+road.way_id,
                          'automatic_source_integrity':'passed','human_review_status':'pending',
                          'reviewer':None,'reviewed_at':None,'notes':None})
    if any(a&b for i,a in enumerate(groups) for b in groups[i+1:]):
        raise ValueError('Road groups overlap between development and hold-out')
    # Never overwrite human review decisions on pipeline reruns.
    review_path=output/'reference_review_queue.json'
    existing=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else []
    reviewed={r['segment_id']:r for r in existing}
    save_json(review_path,[reviewed.get(r['segment_id'],r) for r in queue])
    summary={'records_checked':len(queue),'source_integrity':'passed','group_overlap':0,
             'human_field_verification':False,'checked_at':datetime.now(timezone.utc).isoformat()}
    save_json(output/'reference_audit.json',summary)
    return summary


class ScenarioProposal(BaseModel):
    model_config=ConfigDict(extra='forbid')
    name:str
    osm_tags:dict[str,str]
    context_description:str
    proposed_expected:EvidenceOutput
    purpose:str


class ScenarioBatch(BaseModel):
    model_config=ConfigDict(extra='forbid')
    scenarios:list[ScenarioProposal]=Field(min_length=1,max_length=3)


def generate_proposals(output,model='qwen2.5:3b'):
    path=output/'generated_scenarios_pending_review.json'
    if path.exists(): return json.loads(path.read_text(encoding='utf-8'))
    local=LangChainEvidenceExtractor('v5',model)
    structured=local.llm.with_structured_output(ScenarioBatch,method='json_schema',include_raw=True)
    result=structured.invoke([
        SystemMessage(content='Create fictional bilingual map-quality test scenarios. They are proposals for human review, never independently verified ground truth. Give a short evidence summary, not private reasoning.'),
        HumanMessage(content='Create 2 concise cases: contradictory explicit speed tag versus Romanian prose, and ambiguous barrier evidence without a connected node. Do not use real place names or personal data. Missing facts must be null/unknown.')])
    if result.get('parsing_error') or result.get('parsed') is None:
        raise ValueError('Generated scenarios failed schema validation; not added to benchmark')
    raw=result['raw']
    artifact={'status':'pending_human_review','benchmark_eligible':False,'model':model,
              'model_digest':local.digest,'generated_at':datetime.now(timezone.utc).isoformat(),
              'scenarios':result['parsed'].model_dump(mode='json')['scenarios'],
              'raw_response':raw.model_dump(mode='json'),'token_usage':raw.usage_metadata,
              'policy':'Human must audit labels and approve a separate versioned dataset before evaluation. This file is never loaded by benchmark().'}
    save_json(path,artifact)
    return artifact
