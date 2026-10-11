"""Local inference checks are mocked and never need a model, GPU or API key."""

import json
import os
import subprocess
import sys
from unittest.mock import Mock

import pytest

from src.config import PROJECT_ROOT, resolve_model
from src.extractor import InvalidOutputError, get_extractor
from src.local_ollama import LocalOllamaExtractor, local_base_url, request_json
from src.models import RoadAttributes, RoadSegmentInput
from src.recording import cache_path, estimate_cost, extract_batch


def fixture_segment():
    return RoadSegmentInput(segment_id="local-fixture", name="Fixture",
                            osm_tags={"highway": "residential"}, context_description="No speed evidence",
                            expected_attributes=RoadAttributes(road_type="residential", confidence_score=0.5,
                                                               reasoning_cot="Reference not visible"))


def mock_server(monkeypatch, changes=None):
    import src.local_ollama as local
    output = fixture_segment().expected_attributes.model_dump(mode="json")
    output["reasoning_cot"] = "Observed highway=residential"
    response = {"done": True, "done_reason": "stop", "message": {"content": json.dumps(output)},
                "prompt_eval_count": 20, "eval_count": 10, **(changes or {})}
    mocked = Mock(side_effect=lambda url, payload=None, timeout=5:
                  {"models": [{"name": "qwen2.5:3b", "digest": "fixture-digest"}]} if payload is None else response)
    monkeypatch.setattr(local, "request_json", mocked)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("LOCAL_CONTEXT_SIZE", "4096")
    return mocked


def test_local_has_no_api_key_requirement_and_never_sends_reference(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    mocked = mock_server(monkeypatch)
    extractor = get_extractor("local", "qwen2.5:3b", "v1")
    output = extractor.extract_attributes(fixture_segment())
    assert output.road_type.value == "residential"
    assert output.speed_limit_kmh is None
    assert extractor.last_token_usage == {"input_tokens": 20, "output_tokens": 10, "total_tokens": 30}
    assert extractor.last_raw_response["local_model_digest"] == "fixture-digest"
    payload = mocked.call_args.args[1]
    assert payload["format"] == RoadAttributes.model_json_schema()
    assert payload["stream"] is False
    assert payload["options"]["num_ctx"] == 4096
    assert [m["role"] for m in payload["messages"]] == ["system", "user", "assistant", "user"]
    assert "Reference not visible" not in json.dumps(payload)
    assert "expected_attributes" not in json.dumps(payload)


@pytest.mark.parametrize("change", [
    {"done": False}, {"done_reason": "length"}, {"message": {"content": "not JSON"}},
    {"message": {"content": '{"road_type":"residential","confidence_score":2,"reasoning_cot":"bad"}'}}
])
def test_local_invalid_response_preserves_raw(monkeypatch, change):
    mock_server(monkeypatch, change)
    with pytest.raises(InvalidOutputError) as caught:
        LocalOllamaExtractor("qwen2.5:3b").extract_attributes(fixture_segment())
    assert caught.value.raw_response["local_model_digest"] == "fixture-digest"
    assert caught.value.token_usage["input_tokens"] == 20


@pytest.mark.parametrize("url", ["https://ollama.com", "http://example.com:11434",
                               "http://127.0.0.1:11434/path", "http://secret@localhost:11434"])
def test_local_rejects_remote_or_ambiguous_urls(monkeypatch, url):
    monkeypatch.setenv("OLLAMA_BASE_URL", url)
    with pytest.raises(ValueError, match="loopback"):
        local_base_url()


def test_local_rejects_cloud_models_before_connecting(monkeypatch):
    import src.local_ollama as local
    mocked = Mock(side_effect=AssertionError("No network expected"))
    monkeypatch.setattr(local, "request_json", mocked)
    with pytest.raises(ValueError, match="Cloud models"):
        LocalOllamaExtractor("some-model:cloud")
    assert not mocked.called


def test_local_missing_model_is_an_actionable_configuration_error(monkeypatch):
    mock_server(monkeypatch)
    with pytest.raises(ValueError, match="ollama pull missing-model"):
        LocalOllamaExtractor("missing-model")


def test_local_cache_changes_with_context_and_replays_without_server(tmp_path, monkeypatch):
    mocked = mock_server(monkeypatch)
    original = cache_path(tmp_path, "local", "qwen2.5:3b", "v1", fixture_segment())
    first = extract_batch([fixture_segment()], "local", "qwen2.5:3b", "v1", tmp_path)
    assert first[0].status == "success" and not first[0].cache_hit
    assert first[0].estimated_cost_usd == 0
    mocked.reset_mock()
    replay = extract_batch([fixture_segment()], "local", "qwen2.5:3b", "v1", tmp_path, cached_only=True)
    assert replay[0].cache_hit and not mocked.called
    monkeypatch.setenv("LOCAL_CONTEXT_SIZE", "2048")
    assert original != cache_path(tmp_path, "local", "qwen2.5:3b", "v1", fixture_segment())


def test_local_connection_error_is_not_a_baseline_prediction(tmp_path, monkeypatch):
    mocked = mock_server(monkeypatch)
    mocked.side_effect = [{"models": [{"name": "qwen2.5:3b"}]}, RuntimeError("Ollama stopped")]
    result = extract_batch([fixture_segment()], "local", "qwen2.5:3b", "v1", tmp_path)[0]
    assert result.status == "api_error" and result.extracted is None


def test_local_cost_is_zero_even_with_provider_prices(monkeypatch):
    monkeypatch.setenv("INPUT_USD_PER_MILLION", "999")
    assert estimate_cost({"input_tokens": 20, "output_tokens": 10}, "local") == 0


def test_local_cli_bad_url_stops_before_prefect():
    environment = {**os.environ, "OLLAMA_BASE_URL": "https://example.com", "LOCAL_MODEL": "qwen2.5:3b",
                   "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}
    completed = subprocess.run([sys.executable, str(PROJECT_ROOT / "run_pipeline.py"), "--mode", "local"],
                               cwd=PROJECT_ROOT, env=environment, capture_output=True, text=True, timeout=15)
    assert completed.returncode == 2
    assert "loopback" in completed.stderr
    assert "Starting temporary server" not in completed.stderr
