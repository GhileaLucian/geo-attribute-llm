"""Regression checks for unknown values, exact matching, denominators and caching."""

import json
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage
from pydantic import ValidationError

from src.config import PROJECT_ROOT
from src.dataset_generator import load_ground_truth_dataset
from src.evaluator import GeospatialEvaluator
from src.extractor import ClaudeExtractor, InvalidOutputError, RuleBasedBaselineExtractor
from src.fetch_osm import build_splits, make_segment
from src.models import RoadAttributes, RoadSegmentInput, ExtractionResult
from src.osm_values import parse_speed, parse_oneway
from src.recording import cache_path, extract_batch, safe_error


def attributes(**changes):
    values = dict(road_type="residential", speed_limit_kmh=30,
                  barrier_present=False, barrier_type="none", surface="asphalt",
                  oneway=False, confidence_score=0.5, reasoning_cot="Fixture")
    values.update(changes)
    return RoadAttributes(**values)


def segment(**changes):
    values = dict(segment_id="fixture-1", name="Fixture", osm_tags={"highway": "residential"},
                  context_description="No observations", expected_attributes=attributes())
    values.update(changes)
    return RoadSegmentInput(**values)


def result(expected=None, actual=None, **changes):
    values = dict(segment_id="fixture-1", expected=expected or attributes(),
                  extracted=actual or attributes(), execution_time_ms=1)
    values.update(changes)
    return ExtractionResult(**values)


@pytest.mark.parametrize("changes", [
    {"speed_limit_kmh": -1}, {"speed_limit_kmh": 301}, {"confidence_score": 1.01},
    {"barrier_present": False, "barrier_type": "gate"},
    {"barrier_present": True, "barrier_type": "none"},
    {"barrier_present": None, "barrier_type": "none"},
    {"extra_attribute": "unexpected"}
])
def test_schema_rejects_invalid_values(changes):
    with pytest.raises(ValidationError):
        attributes(**changes)


@pytest.mark.parametrize("raw, expected", [
    ("30", 30), ("30 km/h", 30), ("30 mph", 48), ("RO:urban", None),
    ("signals", None), (None, None), ("30;50", None), ("400", None)
])
def test_speed_parsing(raw, expected):
    assert parse_speed(raw) == expected


def test_oneway_reverse_and_unknown():
    assert parse_oneway("-1") is True
    assert parse_oneway("no") is False
    assert parse_oneway(None) is None


def test_baseline_does_not_guess_missing_values():
    output = RuleBasedBaselineExtractor().extract_attributes(segment())
    assert output.speed_limit_kmh is None
    assert output.surface.value == "unknown"
    assert output.barrier_present is None
    assert output.oneway is None


def test_pedestrian_is_not_living_street():
    output = RuleBasedBaselineExtractor().extract_attributes(segment(osm_tags={"highway": "pedestrian"}))
    assert output.road_type.value == "pedestrian"


@pytest.mark.parametrize("changes", [
    {"speed_limit_kmh": 35}, {"oneway": True}, {"surface": "paved"},
    {"barrier_present": True, "barrier_type": "gate"}, {"anomaly_flag": True}
])
def test_exact_match_detects_each_field(changes):
    evaluation = GeospatialEvaluator().evaluate_batch([result(actual=attributes(**changes))])
    assert evaluation["exact_segment_match_rate"] == 0


def test_tolerance_is_separate_from_exact_match():
    metrics = GeospatialEvaluator().evaluate_batch([result(actual=attributes(speed_limit_kmh=35))])
    assert metrics["attributes"]["speed_limit"]["exact_accuracy"] == 0
    assert metrics["attributes"]["speed_limit"]["within_10kmh_accuracy"] == 1


def test_failed_predictions_stay_in_denominator():
    failed = result(extracted=None, status="invalid_output")
    metrics = GeospatialEvaluator().evaluate_batch([result(), failed])
    assert metrics["exact_segment_match_rate"] == 0.5
    assert metrics["attributes"]["road_type"]["accuracy"] == 0.5
    assert metrics["attributes"]["speed_limit"]["within_10kmh_accuracy"] == 0.5
    assert metrics["invalid_output_rate"] == 0.5


def test_unlabeled_rows_do_not_change_accuracy():
    unlabeled = result()
    unlabeled.expected = None
    metrics = GeospatialEvaluator().evaluate_batch([result(), unlabeled])
    assert metrics["total_segments_evaluated"] == 1
    assert metrics["unlabeled_segments_excluded"] == 1
    assert metrics["exact_segment_match_rate"] == 1


def test_hand_checked_binary_metrics():
    # Positive reference twice, predicted positive once correctly and once incorrectly.
    records = [
        result(expected=attributes(oneway=True), actual=attributes(oneway=True)),
        result(expected=attributes(oneway=True), actual=attributes(oneway=False)),
        result(expected=attributes(oneway=False), actual=attributes(oneway=True)),
    ]
    values = GeospatialEvaluator().evaluate_batch(records)["attributes"]["oneway"]
    assert values["precision"] == 0.5
    assert values["recall"] == 0.5
    assert values["f1_score"] == 0.5
    assert values["per_class"]["true"]["support"] == 2
    assert values["confusion_matrix"] == {"labels": ["false", "true"], "values": [[0, 1], [1, 1]]}


def test_missing_speed_does_not_become_zero_for_tolerance():
    records = [
        result(expected=attributes(speed_limit_kmh=None), actual=attributes(speed_limit_kmh=5)),
        result(expected=attributes(speed_limit_kmh=30), actual=attributes(speed_limit_kmh=30))
    ]
    speed = GeospatialEvaluator().evaluate_batch(records)["attributes"]["speed_limit"]
    assert speed["known_reference_count"] == 1
    assert speed["within_10kmh_accuracy"] == 1
    assert speed["predicted_when_reference_missing_count"] == 1
    assert speed["exact_accuracy"] == 0.5


def test_loader_rejects_duplicates_and_missing_labels(tmp_path):
    path = tmp_path / "bad.json"
    data = segment().model_dump(mode="json")
    path.write_text(json.dumps([data, data]), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_ground_truth_dataset(path)
    data["expected_attributes"] = None
    path.write_text(json.dumps([data]), encoding="utf-8")
    with pytest.raises(ValueError, match="reference"):
        load_ground_truth_dataset(path)


def test_downloaded_splits_have_disjoint_real_ids_and_no_target_leak():
    dev = load_ground_truth_dataset(PROJECT_ROOT / "data" / "osm_dev.json")
    test = load_ground_truth_dataset(PROJECT_ROOT / "data" / "osm_test.json")
    assert len(dev) == 40 and len(test) == 60
    assert not {s.segment_id for s in dev}.intersection(s.segment_id for s in test)
    for item in dev + test:
        assert item.segment_id == str(item.osm_way_id)
        assert item.source == "OpenStreetMap/Overpass"
        assert not set(item.hidden_attributes).intersection(item.osm_tags)
        assert item.context_description == "Downloaded road way. Visible tags: " + json.dumps(item.osm_tags, ensure_ascii=False, sort_keys=True)


def test_masking_removes_aliases_and_free_text_notes():
    way = {"id": 1, "type": "way", "tags": {
        "highway": "primary", "maxspeed": "70", "maxspeed:forward": "70",
        "source:maxspeed": "sign", "note": "Speed 70", "surface": "gravel",
        "description": "Speed is 70", "oneway": "-1"
    }}
    data = make_segment(way, "2026-10-11T00:00:00+00:00")
    assert data["osm_tags"] == {"highway": "primary"}
    assert "70" not in data["context_description"]
    assert data["expected_attributes"]["speed_limit_kmh"] == 70
    assert data["expected_attributes"]["oneway"] is True


def test_split_seed_is_reproducible():
    raw = {"collected_at": "2026-10-11T00:00:00+00:00", "elements": [
        {"type": "way", "id": i, "tags": {"highway": "residential", "surface": "asphalt"}}
        for i in range(10)
    ]}
    assert build_splits(raw, count=10, seed=42) == build_splits(raw, count=10, seed=42)


def test_mock_claude_success_records_raw_usage(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fixture-key")
    import langchain_anthropic
    client = Mock()
    client.with_structured_output.return_value.invoke.return_value = {
        "raw": AIMessage(content="fixture", usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}),
        "parsed": attributes(), "parsing_error": None
    }
    constructor = Mock(return_value=client)
    monkeypatch.setattr(langchain_anthropic, "ChatAnthropic", constructor)
    extractor = ClaudeExtractor("fixture-model")
    assert extractor.extract_attributes(segment()) == attributes()
    assert extractor.last_token_usage["total_tokens"] == 15
    assert extractor.last_raw_response["content"] == "fixture"
    # Reference labels must never appear in the messages passed to the provider.
    messages = client.with_structured_output.return_value.invoke.call_args.args[0]
    assert "expected_attributes" not in "\n".join(msg.content for msg in messages)
    assert "reference" not in messages[-1].content.lower()


def test_mock_claude_invalid_output_preserves_raw(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fixture-key")
    import langchain_anthropic
    client = Mock()
    client.with_structured_output.return_value.invoke.return_value = {
        "raw": AIMessage(content="invalid"), "parsed": None, "parsing_error": ValueError("bad JSON")
    }
    monkeypatch.setattr(langchain_anthropic, "ChatAnthropic", Mock(return_value=client))
    with pytest.raises(InvalidOutputError) as error:
        ClaudeExtractor("fixture-model").extract_attributes(segment())
    assert error.value.raw_response["content"] == "invalid"


def test_cache_replay_needs_no_api_key_and_changed_input_misses(tmp_path, monkeypatch):
    import src.recording as recording
    fake = Mock()
    fake.extract_attributes.return_value = attributes()
    fake.last_raw_response = None
    fake.last_token_usage = {}
    monkeypatch.setattr(recording, "get_extractor", Mock(return_value=fake))
    first = extract_batch([segment()], "claude", "fixture-model", "v1", tmp_path)
    assert first[0].cache_hit is False
    monkeypatch.setattr(recording, "get_extractor", Mock(side_effect=AssertionError("Must not create a client")))
    replay = extract_batch([segment()], "claude", "fixture-model", "v1", tmp_path, cached_only=True)
    assert replay[0].cache_hit is True
    with pytest.raises(FileNotFoundError):
        extract_batch([segment(context_description="Changed input")], "claude", "fixture-model", "v1", tmp_path, cached_only=True)


def test_cache_key_changes_with_model_prompt_and_schema_input(tmp_path):
    original = cache_path(tmp_path, "claude", "model-a", "v1", segment())
    assert original != cache_path(tmp_path, "claude", "model-b", "v1", segment())
    assert original != cache_path(tmp_path, "claude", "model-a", "v2", segment())
    assert original != cache_path(tmp_path, "claude", "model-a", "v1", segment(osm_tags={"highway": "primary"}))


def test_transport_failure_is_reported_and_not_retried_silently(tmp_path, monkeypatch):
    import src.recording as recording
    fake = Mock()
    fake.extract_attributes.side_effect = RuntimeError("network unavailable")
    monkeypatch.setattr(recording, "get_extractor", Mock(return_value=fake))
    output = extract_batch([segment()], "claude", "fixture-model", "v1", tmp_path)
    assert output[0].status == "api_error"
    assert output[0].extracted is None
    assert GeospatialEvaluator().evaluate_batch(output)["api_error_rate"] == 1
    extract_batch([segment()], "claude", "fixture-model", "v1", tmp_path)
    assert fake.extract_attributes.call_count == 1


def test_error_messages_redact_keys(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fixture-secret")
    assert "fixture-secret" not in safe_error(RuntimeError("bad fixture-secret"))


def test_hard_cases_remain_separate():
    dataset = load_ground_truth_dataset(PROJECT_ROOT / "data" / "hard_cases.json")
    assert len(dataset) == 15
    assert all(item.source == "hand-written" and item.osm_way_id is None for item in dataset)
