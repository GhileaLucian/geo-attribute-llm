"""Download OSM ways and create reproducible masked tag-completion sets."""

import argparse
from collections import defaultdict, deque, Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
from urllib.request import Request, urlopen
from urllib.parse import urlencode

from src.config import PROJECT_ROOT
from src.models import RoadAttributes, RoadSegmentInput
from src.osm_values import explicit_values

BBOX = "46.70,23.48,46.82,23.70"
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
HIDDEN = ["maxspeed", "surface", "barrier", "oneway"]
# Whitelist avoids aliases such as maxspeed:forward and free-text notes.
VISIBLE = {
    "highway", "name", "ref", "lanes", "junction", "access", "motor_vehicle",
    "bridge", "tunnel", "lit", "sidewalk", "tracktype"
}
TARGET_FIELDS = ["speed_limit_kmh", "surface", "barrier_present", "barrier_type", "oneway"]


def select_ways(elements, count=100, seed=42):
    ways = sorted(
        [e for e in elements if e.get("type") == "way" and e.get("tags", {}).get("highway")],
        key=lambda e: e["id"]
    )
    if len(ways) < count:
        raise ValueError(f"Only {len(ways)} road ways downloaded; requested {count}")
    rng = random.Random(seed)
    rng.shuffle(ways)
    groups = defaultdict(deque)
    for way in ways:
        groups[way["tags"]["highway"]].append(way)
    selected = []
    # Include way-level barrier tags if available, without claiming node coverage.
    for way in ways:
        if way["tags"].get("barrier") and len(selected) < min(10, count):
            selected.append(way)
    used = {way["id"] for way in selected}
    while len(selected) < count:
        for key in sorted(groups):
            while groups[key] and groups[key][0]["id"] in used:
                groups[key].popleft()
            if groups[key] and len(selected) < count:
                way = groups[key].popleft()
                used.add(way["id"])
                selected.append(way)
    rng.shuffle(selected)
    return selected


def make_segment(way, collected_at):
    original = {str(k): str(v) for k, v in way["tags"].items()}
    visible = {k: v for k, v in original.items() if k in VISIBLE}
    expected = RoadAttributes(
        **explicit_values(original),
        confidence_score=1,
        reasoning_cot="Reference labels normalized from the downloaded OSM way tags.",
        anomaly_flag=False
    )
    # This text is built exclusively from the visible payload.
    description = "Downloaded road way. Visible tags: " + json.dumps(visible, ensure_ascii=False, sort_keys=True)
    return RoadSegmentInput(
        segment_id=str(way["id"]), osm_way_id=way["id"],
        name=original.get("name", "Unnamed road"), osm_tags=visible,
        context_description=description, expected_attributes=expected,
        source="OpenStreetMap/Overpass", collected_at=collected_at,
        hidden_attributes=HIDDEN, evaluation_fields=TARGET_FIELDS
    ).model_dump(mode="json")


def build_splits(raw, count=100, seed=42):
    ways = select_ways(raw["elements"], count, seed)
    records = [make_segment(way, raw["collected_at"]) for way in ways]
    dev_count = max(1, round(len(records) * 0.4))
    return ways, records[:dev_count], records[dev_count:]


def download(endpoint=None):
    query = f'[out:json][timeout:40];way["highway"]({BBOX});out tags;'
    failures = []
    for url in [endpoint] if endpoint else ENDPOINTS:
        request = Request(
            url, data=urlencode({"data": query}).encode(),
            headers={"User-Agent": "GeoAttribute-LLM learning benchmark", "Accept": "application/json"}
        )
        try:
            with urlopen(request, timeout=50) as response:
                raw = json.load(response)
            if raw.get("remark"):
                raise RuntimeError(f"Overpass reported an incomplete response: {raw['remark']}")
            if not raw.get("elements"):
                raise RuntimeError("No elements returned")
            raw.update(
                collected_at=datetime.now(timezone.utc).isoformat(),
                endpoint=url, query=query,
                attribution="OpenStreetMap contributors, ODbL 1.0",
                license_url="https://www.openstreetmap.org/copyright"
            )
            return raw
        except Exception as exc:
            failures.append(f"{url}: {type(exc).__name__}: {exc}")
    raise RuntimeError("OSM download failed. No data was generated. " + "; ".join(failures))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "data")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--endpoint")
    parser.add_argument("--force", action="store_true", help="Replace an existing downloaded snapshot")
    args = parser.parse_args()
    if args.count < 3:
        parser.error("--count must be at least 3")
    out = args.output_dir
    if any((out / name).exists() for name in ["osm_raw.json", "osm_dev.json", "osm_test.json"]) and not args.force:
        parser.error("Snapshot already exists. Use a separate output directory, or --force to replace it.")
    raw = download(args.endpoint)
    ways, dev, test = build_splits(raw, args.count, args.seed)
    # Retain original downloaded way records for the selected sample.
    snapshot = {k: v for k, v in raw.items() if k != "elements"}
    snapshot["downloaded_way_count"] = len(raw["elements"])
    snapshot["elements"] = ways
    out.mkdir(parents=True, exist_ok=True)
    for name, value in [("osm_raw.json", snapshot), ("osm_dev.json", dev), ("osm_test.json", test)]:
        (out / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    split_manifest = {
        "seed": args.seed, "collected_at": raw["collected_at"],
        "dev_count": len(dev), "test_count": len(test),
        "raw_sha256": hashlib.sha256((out / "osm_raw.json").read_bytes()).hexdigest(),
        "dev_ids": [x["segment_id"] for x in dev],
        "test_ids": [x["segment_id"] for x in test],
        "highway_counts": dict(Counter(way["tags"]["highway"] for way in ways)),
        "hidden_attributes": HIDDEN,
        "task": "masked tag completion",
        "limitations": [
            "Not independently checked on the ground.",
            "Missing OSM tag means unknown, not absence.",
            "Barrier tags on nodes are not collected.",
            "Sampling balances highway types; it is not a random sample of the city.",
            "Different ways can belong to the same road; dev/test may share road names."
        ]
    }
    (out / "split_manifest.json").write_text(json.dumps(split_manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Downloaded {len(raw['elements'])} ways; selected {len(ways)}; dev={len(dev)}, test={len(test)}")
    print(f"Source: {raw['endpoint']}; collected at {raw['collected_at']}")


if __name__ == "__main__":
    main()
