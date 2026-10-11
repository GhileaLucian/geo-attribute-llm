"""Build and execute a read-only notebook from saved GIS/ML/LLM artifacts."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from src.config import PROJECT_ROOT


def build_notebook(execute=True):
    nb=nbformat.v4.new_notebook()
    md=nbformat.v4.new_markdown_cell
    code=nbformat.v4.new_code_cell
    nb.cells=[
        md('# Map quality analysis — Cluj-Napoca\n\nActual OSM geometry; controlled text extraction; exploratory ML. No API calls in this notebook. © OpenStreetMap contributors, ODbL. Map flags and generated labels require human review.'),
        code("from pathlib import Path\nimport json\nimport geopandas as gpd\nimport pandas as pd\nimport matplotlib.pyplot as plt\nroot = Path.cwd()\nif not (root / 'reports').exists(): root = root.parent\nout = root / 'reports' / 'mapqa'\nread = lambda name: json.loads((out / name).read_text(encoding='utf-8'))\ngeometry = read('geometry_summary.json')\nml = read('ml_summary.json')\ngeometry"),
        md('## Geometry and barriers\n\nDistances and road lengths use local UTM coordinates in metres. A shared OSM node is a topological connection. A nearest candidate within 10 m is not a verified road barrier.'),
        code("roads = gpd.read_file(out / 'roads.geojson')\nbarriers = gpd.read_file(out / 'barriers.geojson')\nfig, ax = plt.subplots(figsize=(10, 7))\nroads.to_crs(geometry['metric_crs']).plot(ax=ax, color='slategray', linewidth=.35)\nbarriers.to_crs(geometry['metric_crs']).plot(ax=ax, color='crimson', markersize=4)\nax.set_title('OSM roads and barrier nodes — projected metres')\nax.set_axis_off()\nplt.show()"),
        code("associations = pd.DataFrame(read('barrier_associations.json'))\nassociations.groupby('method').agg(road_node_pairs=('node_id','count'), unique_nodes=('node_id','nunique'))"),
        md('## Classification and regression\n\nGroup-separated test sets by road name/way ID. Classification excludes highway; regression excludes maxspeed. Numeric speed labels are OSM tags, not audited legal limits. Nearby-road and mapping-practice correlations remain possible.'),
        code("classification = pd.DataFrame({name: result['report']['weighted avg'] for name, result in ml['classification'].items()}).T\nclassification"),
        code("matrix = ml['classification']['random_forest']['confusion_matrix']\nfig, ax = plt.subplots(figsize=(7, 5))\nax.imshow(matrix['values'], cmap='Blues')\nax.set_xticks(range(len(matrix['labels'])), matrix['labels'], rotation=30, ha='right')\nax.set_yticks(range(len(matrix['labels'])), matrix['labels'])\nax.set_xlabel('Prediction'); ax.set_ylabel('OSM reference')\nax.set_title('Held-out road-family classification')\nplt.tight_layout(); plt.show()"),
        code("pd.DataFrame(ml['regression']['models']).T"),
        md('## Clustering and anomaly suggestions\n\nDBSCAN uses centroids, eps=200 m. IsolationForest flags are suggestions, not independently verified map errors.'),
        code("layers = gpd.read_file(out / 'ml_roads.geojson')\nfig, ax = plt.subplots(figsize=(10, 7))\nlayers.to_crs(geometry['metric_crs']).plot(column='cluster', ax=ax, cmap='tab20', linewidth=.5)\nax.set_axis_off(); ax.set_title('Descriptive DBSCAN centroid clusters'); plt.show()\nml['clustering'], ml['anomalies']"),
        md('## Local LangChain prompt evaluation\n\nCompare only identical splits. v4/v5 operate on supplied evidence, unlike the legacy masked-tag experiment. Hybrid results include deterministic Python guards. Null/unknown support can inflate scores; inspect per-class metrics and errors. Generated proposals are excluded pending human review.'),
        code("runs = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((out / 'benchmarks').glob('*/benchmark_summary.json'))]\npd.DataFrame([{k: r[k] for k in ('mode','prompt','split','n','exact_match_rate','failure_rate')} for r in runs])"),
        code("final = next((r for r in runs if r['mode']=='langchain' and r['prompt']=='v6' and r['split']=='test_final'), None)\nif final:\n    display(pd.DataFrame({f: {'known_reference_n': s['count'] - s['unknown_reference_count'], 'known_accuracy': s['known_reference_accuracy']} for f, s in final['attributes'].items()}).T)\n# Zero known numeric speeds means final numeric-speed extraction is not measured."),
        code("examples = []\nfor p in sorted((out / 'benchmarks').glob('langchain*dev/error_examples.json')):\n    examples.extend(json.loads(p.read_text(encoding='utf-8'))[:2])\nexamples"),
        md('## Reproducibility and limits\n\nSnapshot and split SHA-256 hashes are stored in data/mapqa manifests. v4/v5 omitted optional fields; v6 requires every field. The initial evidence test was consumed; test_final is a new grouped hold-out reserved before freezing v6. Reference integrity is automatic; human field verification remains pending. Cloud Claude/OpenAI benchmarks and professional GIS experience are not claimed. The legacy masked-tag hold-out remains untouched.'),
        code("read('reference_audit.json')")]
    nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
                 'language_info':{'name':'python'}}
    if execute:
        NotebookClient(nb,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(PROJECT_ROOT)}}).execute()
    path=PROJECT_ROOT/'notebooks'/'map_quality_analysis.ipynb'
    path.parent.mkdir(parents=True,exist_ok=True)
    nbformat.write(nb,path)
    return path


if __name__=='__main__': print(build_notebook())
