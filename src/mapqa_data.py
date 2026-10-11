"""Separate geometry snapshot: real OSM geometry, never invented observations."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from uuid import uuid4

from src.config import PROJECT_ROOT

BBOX = '46.74,23.54,46.80,23.66'
DEFAULT_DATA = PROJECT_ROOT / 'data' / 'mapqa'


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.' + uuid4().hex + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def download_snapshot(output=DEFAULT_DATA, bbox=BBOX):
    output = Path(output)
    if (output / 'snapshot.json').exists():
        raise FileExistsError('Snapshot already exists; use a different data directory. No overwrite.')
    coordinates = [float(v) for v in bbox.split(',')]
    if len(coordinates) != 4 or not (-90 <= coordinates[0] < coordinates[2] <= 90
                                    and -180 <= coordinates[1] < coordinates[3] <= 180):
        raise ValueError('Expected south,west,north,east bounding box')
    if (coordinates[2]-coordinates[0]) * (coordinates[3]-coordinates[1]) > .02:
        raise ValueError('Use a small bounding box to avoid overloading public Overpass servers.')
    query = f'[out:json][timeout:90];(way["highway"]({bbox});node["barrier"]({bbox}););out body geom;'
    errors = []
    for endpoint in ('https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter'):
        try:
            request = Request(endpoint, data=urlencode({'data': query}).encode(),
                              headers={'User-Agent': 'GeoAttribute-LLM portfolio map-QA/1.0'})
            with urlopen(request, timeout=110) as response:
                raw = json.loads(response.read(40_000_001).decode('utf-8'))
            if raw.get('remark') or not raw.get('elements'):
                raise ValueError('Empty or incomplete Overpass response')
            raw['provenance'] = {'endpoint': endpoint, 'query': query, 'bbox': bbox,
                                 'collected_at': datetime.now(timezone.utc).isoformat(),
                                 'attribution': 'OpenStreetMap contributors, ODbL 1.0',
                                 'license_url': 'https://www.openstreetmap.org/copyright',
                                 'independent_field_verification': False}
            save_json(output / 'snapshot.json', raw)
            save_json(output / 'manifest.json', {
                **raw['provenance'], 'snapshot_sha256': hashlib.sha256((output/'snapshot.json').read_bytes()).hexdigest(),
                'ways': sum(e['type']=='way' for e in raw['elements']),
                'barrier_nodes': sum(e['type']=='node' for e in raw['elements']),
                'server_timestamp': raw.get('osm3s', {}).get('timestamp_osm_base')})
            return raw
        except Exception as exc:
            errors.append(f'{endpoint}: {type(exc).__name__}: {exc}')
    raise RuntimeError('No synthetic fallback. Download failed: ' + '; '.join(errors))


def read_snapshot(data_dir=DEFAULT_DATA):
    folder = Path(data_dir)
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if hashlib.sha256((folder/'snapshot.json').read_bytes()).hexdigest() != manifest['snapshot_sha256']:
        raise ValueError('Snapshot hash mismatch; do not mix changed data with saved reports.')
    return json.loads((folder/'snapshot.json').read_text(encoding='utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=DEFAULT_DATA)
    parser.add_argument('--bbox', default=BBOX)
    args = parser.parse_args()
    download_snapshot(args.data_dir, args.bbox)
    print((args.data_dir/'manifest.json').read_text(encoding='utf-8'))
