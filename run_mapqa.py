"""Prepare GIS, benchmark local evidence, or serve a scheduled offline QA flow."""
import argparse
import json
import os
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','analyze','benchmark','select','generate','notebook','serve','schedule-smoke','all'])
    parser.add_argument('--mode',choices=['rules','langchain','hybrid'],default='rules')
    parser.add_argument('--prompt',choices=['v4','v5','v6'],default='v6')
    parser.add_argument('--split',choices=['dev','hard','test','test_final'],default='dev')
    parser.add_argument('--cached-only',action='store_true')
    parser.add_argument('--allow-holdout',action='store_true')
    parser.add_argument('--interval',type=int,default=3600)
    parser.add_argument('--details',action='store_true',help='Print the full JSON report rather than a compact summary')
    args=parser.parse_args()
    # No accidental remote tracing of local prompts/data.
    os.environ['LANGSMITH_TRACING']='false'
    os.environ['LANGCHAIN_TRACING_V2']='false'
    from src.mapqa_data import DEFAULT_DATA, download_snapshot
    from src.mapqa_benchmark import OUTPUT, benchmark, freeze_selection
    from src.mapqa_flow import mapqa_flow
    if args.action=='prepare':
        if not (DEFAULT_DATA/'snapshot.json').exists(): download_snapshot()
        result=mapqa_flow()
    elif args.action in ('analyze','all'):
        result=mapqa_flow(mode=args.mode,version=args.prompt,split=args.split,cached_only=args.cached_only)
        if args.action=='all':
            from create_mapqa_notebook import build_notebook
            build_notebook()
    elif args.action=='benchmark':
        result=benchmark(args.split,args.mode,args.prompt,cached_only=args.cached_only,allow_holdout=args.allow_holdout)
    elif args.action=='select':
        if args.prompt=='v6':
            from src.mapqa_final_holdout import freeze_v6
            result=freeze_v6(OUTPUT)
        else: result=freeze_selection()
    elif args.action=='generate':
        from src.mapqa_review import generate_proposals
        result=generate_proposals(OUTPUT)
    elif args.action=='notebook':
        from create_mapqa_notebook import build_notebook
        result={'notebook':str(build_notebook())}
    elif args.action=='serve':
        if args.interval<60: parser.error('Use interval >=60 seconds; no needless tight-loop jobs')
        from prefect.settings import PREFECT_API_URL
        from urllib.parse import urlparse
        api=PREFECT_API_URL.value()
        if not api or urlparse(api).hostname not in ('127.0.0.1','localhost','::1'):
            parser.error('Start a local server: python -m prefect server start. In another terminal set PREFECT_API_URL=http://127.0.0.1:4200/api before serve.')
        mapqa_flow.serve(name='local-mapqa-offline',interval=args.interval,
                        parameters={'mode':'rules','cached_only':True},pause_on_shutdown=True)
        return
    else:
        from src.mapqa_schedule import smoke_schedule
        result=smoke_schedule()
    if not args.details and isinstance(result,dict):
        if 'attributes' in result:
            result={k:result[k] for k in ('mode','prompt','split','n','exact_match_rate','failure_rate','error_taxonomy')}
            result['reports']=str(OUTPUT/'benchmarks')
        elif 'scenarios' in result:
            result={k:result[k] for k in ('status','benchmark_eligible','model','token_usage')}
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
