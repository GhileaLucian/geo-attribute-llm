"""Load labeled data from disk; never generate labels during evaluation."""

import json
from pathlib import Path
from src.config import PROJECT_ROOT
from src.models import RoadSegmentInput, EVALUATION_FIELDS


def load_ground_truth_dataset(filepath=None):
    filepath = Path(filepath) if filepath else PROJECT_ROOT / "data" / "osm_ground_truth_cluj.json"
    with filepath.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, list) or not raw:
        raise ValueError("Dataset must be a non-empty JSON list")
    dataset = [RoadSegmentInput.model_validate(item) for item in raw]
    ids = [item.segment_id for item in dataset]
    if len(ids) != len(set(ids)):
        raise ValueError("Dataset contains duplicate segment IDs")
    for item in dataset:
        if item.expected_attributes is None:
            raise ValueError(f"Missing reference labels for {item.segment_id}")
        unknown = set(item.evaluation_fields) - set(EVALUATION_FIELDS)
        if unknown or not item.evaluation_fields:
            raise ValueError(f"Invalid evaluation_fields for {item.segment_id}: {unknown}")
        if set(item.hidden_attributes).intersection(item.osm_tags):
            raise ValueError(f"Hidden attributes leaked into tags for {item.segment_id}")
    return dataset
