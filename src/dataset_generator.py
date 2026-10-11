"""
Dataset loader for OpenStreetMap ground truth.
Loads hand-curated road segments strictly from disk (data/osm_ground_truth_cluj.json).
"""

import json
from pathlib import Path
from typing import List
from src.models import RoadSegmentInput, RoadAttributes, RoadType, BarrierType, SurfaceType


def load_ground_truth_dataset(filepath: Path = None) -> List[RoadSegmentInput]:
    """Loads ground-truth segments strictly from the JSON dataset file."""
    if filepath is None:
        filepath = Path(__file__).resolve().parent.parent / "data" / "osm_ground_truth_cluj.json"

    if not filepath.exists():
        raise FileNotFoundError(f"Ground truth dataset not found at: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        raw_list = json.load(f)

    dataset: List[RoadSegmentInput] = []
    for item in raw_list:
        gt = item.get("expected_attributes")
        expected_attr = None
        if gt:
            expected_attr = RoadAttributes(
                road_type=RoadType(gt["road_type"]),
                speed_limit_kmh=gt.get("speed_limit_kmh"),
                barrier_present=gt["barrier_present"],
                barrier_type=BarrierType(gt["barrier_type"]),
                surface=SurfaceType(gt["surface"]),
                oneway=gt["oneway"],
                confidence_score=gt["confidence_score"],
                reasoning_cot=gt["reasoning_cot"],
                anomaly_flag=gt["anomaly_flag"]
            )

        dataset.append(RoadSegmentInput(
            segment_id=item["segment_id"],
            name=item["name"],
            osm_tags=item["osm_tags"],
            context_description=item["context_description"],
            expected_attributes=expected_attr
        ))

    return dataset
