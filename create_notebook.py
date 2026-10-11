"""Generate a notebook that analyzes saved runs without API calls."""

import json
from pathlib import Path
from src.config import PROJECT_ROOT


def markdown(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text.splitlines(keepends=True)}


def main():
    notebook = {
        "cells": [
            markdown("# GeoAttribute-LLM: saved benchmark analysis\n\nThis notebook reads local reports and predictions. It does not call an API. Unknown-label support and the development/test split matter when interpreting scores.\n"),
            code("""import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

root = Path.cwd()
if not (root / 'reports').exists():
    root = root.parent
paths = sorted((root / 'reports').glob('*/metrics_summary.json'))
runs = [json.loads(path.read_text(encoding='utf-8')) for path in paths]
if not runs:
    raise RuntimeError('Run python run_pipeline.py --mode baseline first')
comparison = pd.DataFrame([{
    'run': path.parent.name, 'dataset': m['dataset_file'],
    'dataset_sha256': m['dataset_sha256'], 'mode': m['extractor_mode'],
    'model': m['model_name'], 'prompt': m['prompt_version'],
    'n': m['total_segments_evaluated'], 'exact_match': m['exact_segment_match_rate'],
    'failure_rate': m['failure_rate'],
    'speed_known_exact': m['attributes']['speed_limit']['known_exact_accuracy']
} for path, m in zip(paths, runs)])
display(comparison)
if not any(m['extractor_mode'] == 'claude' for m in runs):
    print('No Claude benchmark has been run. No Claude result is inferred.')
"""),
            markdown("## Choose a saved run\n\nChange run_index to inspect another completed run. Per-class support shows where a score has little evidence.\n"),
            code("""run_index = 0
run_path = paths[run_index].parent
metrics = runs[run_index]
print(metrics['dataset_file'], metrics['model_name'], metrics['prompt_version'])
predictions = json.loads((run_path / 'predictions.json').read_text(encoding='utf-8'))
display(pd.DataFrame([
    {'attribute': name, 'n': values.get('count'),
     'accuracy': values.get('accuracy', values.get('exact_accuracy')),
     'f1': values.get('f1_score'),
     'known_accuracy': values.get('known_reference_accuracy')}
    for name, values in metrics['attributes'].items()
]))
"""),
            markdown("## Confusion matrix\n\nRows are reference labels; columns are predicted labels. Failed outputs have a separate label.\n"),
            code("""attribute = 'surface_type'
values = metrics['attributes'][attribute]
matrix = values['confusion_matrix']
labels = matrix['labels']
if labels:
    fig, ax = plt.subplots(figsize=(8, 6))
    plot = ax.imshow(matrix['values'], cmap='Blues', vmin=0)
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha='right')
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel('Prediction')
    ax.set_ylabel('Reference')
    ax.set_title(attribute)
    fig.colorbar(plot, ax=ax)
    plt.tight_layout()
    plt.show()
    display(pd.DataFrame(values['per_class']).T)
else:
    print('Attribute not evaluated on this dataset')
"""),
            markdown("## Recorded errors\n"),
            code("""display(pd.DataFrame([
    {'category': key, 'count': value}
    for key, value in metrics['error_taxonomy_breakdown'].items()
]))
display(Markdown((run_path / 'error_examples.md').read_text(encoding='utf-8')))
"""),
            markdown("## Development and hold-out results\n\nPrompt versions should be compared on development data. Inspect the selected model on the hold-out once. Keep fictional hard cases separate.\n"),
            code("""osm_runs = comparison[comparison['dataset'].isin(['osm_dev.json', 'osm_test.json'])]
display(osm_runs[['mode', 'model', 'prompt', 'dataset', 'n', 'exact_match', 'speed_known_exact']])
if not (osm_runs['dataset'] == 'osm_test.json').any():
    print('The hold-out has not been evaluated. No test score is available.')
""")
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"}
        }, "nbformat": 4, "nbformat_minor": 4
    }
    output = PROJECT_ROOT / "notebooks" / "evaluation_analysis.ipynb"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(notebook, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Notebook generated at {output}")


if __name__ == "__main__":
    main()
