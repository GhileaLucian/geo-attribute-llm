"""Prepare/status/freeze reviewed data only; this command never evaluates models."""
import argparse
import json
from src.benchmark_review import DEFAULT_FOLDER, prepare, status, freeze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'status', 'freeze'])
    args = parser.parse_args()
    try:
        result = {'prepare': prepare, 'status': status, 'freeze': freeze}[args.action](DEFAULT_FOLDER)
    except (ValueError, FileExistsError, FileNotFoundError) as exc:
        parser.exit(2, str(exc) + '\n')
    # Compact status: the first few reasons are sufficient; JSON has all details.
    if args.action != 'freeze':
        result['error_count'] = len(result['errors'])
        result['errors'] = result['errors'][:5]
        result['folder'] = str(DEFAULT_FOLDER)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
