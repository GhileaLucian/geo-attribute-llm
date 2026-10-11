"""Run a fixed offline classification audit with/without coordinates."""
import argparse
import json
from pathlib import Path
from src.config import PROJECT_ROOT
from src.spatial_ml_audit import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=PROJECT_ROOT / 'reports/spatial_ml_audit')
    args = parser.parse_args()
    try:
        result = run(args.output)
    except (ValueError, FileExistsError) as exc:
        parser.exit(2, str(exc) + '\n')
    compact = {}
    for split in ('grouped_split', 'geographic_split'):
        block = result[split]
        compact[split] = {'train_n': block['train_n'], 'test_n': block['test_n'],
                          'weighted_f1': {k: v['classification_report']['weighted avg']['f1-score']
                                          for k, v in block['models'].items()}}
    compact['reports'] = str(args.output)
    print(json.dumps(compact, indent=2))


if __name__ == '__main__':
    main()
