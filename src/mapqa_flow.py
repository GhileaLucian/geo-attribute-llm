"""Offline-first Prefect flow; inference is explicit and local-only."""
from pathlib import Path
from prefect import flow, task
from src.config import PROJECT_ROOT
from src.mapqa_data import DEFAULT_DATA, read_snapshot
from src.mapqa_geo import export_geometry
from src.mapqa_evidence import build_evidence_dataset
from src.mapqa_ml import run_ml
from src.mapqa_review import audit_references
from src.mapqa_benchmark import OUTPUT, benchmark
import hashlib
import importlib.metadata
import platform
from src.mapqa_data import save_json


@task(name='read-versioned-geometry', retries=0)
def load_snapshot(data_dir):
    return read_snapshot(Path(data_dir))


@task(name='metric-gis-and-evidence', retries=0)
def analyze(snapshot, data_dir, output):
    data_dir, output=Path(data_dir),Path(output)
    roads,barriers,associations,geometry=export_geometry(snapshot,output)
    sha=hashlib.sha256((data_dir/'snapshot.json').read_bytes()).hexdigest()
    evidence=build_evidence_dataset(roads,associations,data_dir,sha)
    from src.mapqa_final_holdout import reserve_final
    final=reserve_final(roads,associations,data_dir)
    audit=audit_references(roads,associations,data_dir,output)
    ml=run_ml(roads,output)
    save_json(output/'run_environment.json',{'python':platform.python_version(),'snapshot_sha256':sha,
              'packages':{name:importlib.metadata.version(name) for name in ('prefect','sqlalchemy','langchain-core',
                          'langchain-ollama','pydantic','geopandas','shapely','pyproj','scikit-learn','pandas','numpy')}})
    return {'geometry':geometry,'evidence':evidence,'audit':audit,'ml':ml,'final_holdout':final}


@task(name='evaluate-explicit-evidence', retries=0)
def evaluate_saved(mode,version,split,data_dir,output,cached_only):
    return benchmark(split,mode,version,data_dir=Path(data_dir),output=Path(output),cached_only=cached_only)


@flow(name='map-quality-evidence-flow',log_prints=True)
def mapqa_flow(data_dir=str(DEFAULT_DATA),output=str(OUTPUT),mode='rules',version='v4',
               split='dev',cached_only=True):
    snapshot=load_snapshot(data_dir)
    summary=analyze(snapshot,data_dir,output)
    summary['benchmark']=evaluate_saved(mode,version,split,data_dir,output,cached_only)
    return {'roads':summary['geometry']['roads'],'exact_match_rate':summary['benchmark']['exact_match_rate'],
            'manual_field_verification':False,'mode':mode}
