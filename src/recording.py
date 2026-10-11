"""Save each attempt and reuse responses only for identical model inputs."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time

from src.extractor import get_extractor, InvalidOutputError
from src.models import ExtractionResult, RoadAttributes
from src.prompts import build_chat_messages


def input_payload(segment):
    return {
        "name": segment.name,
        "osm_tags": segment.osm_tags,
        "context_description": segment.context_description
    }


def safe_error(exc):
    message = f"{type(exc).__name__}: {exc}"
    for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        secret = os.getenv(key)
        if secret:
            message = message.replace(secret, "[redacted]")
    return re.sub(r"sk-[A-Za-z0-9_-]+", "[redacted]", message)[:1000]


def cache_path(root, mode, model, version, segment):
    request = {
        "mode": mode, "model": model, "prompt_version": version,
        "input": input_payload(segment),
        "schema": RoadAttributes.model_json_schema(),
        "extractor_code": hashlib.sha256(Path(__file__).with_name("extractor.py").read_bytes()).hexdigest(),
        "normalization_code": hashlib.sha256(Path(__file__).with_name("osm_values.py").read_bytes()).hexdigest(),
        "settings": {"temperature": 0, "max_tokens": 1024},
        "prompt": [msg.model_dump(mode="json") for msg in build_chat_messages(
            segment.name or "Unnamed road", segment.osm_tags,
            segment.context_description, version
        )] if mode != "baseline" else None
    }
    if mode == "local":
        from src.local_ollama import local_base_url, local_settings
        request["local_settings"] = local_settings()
        request["local_base_url"] = local_base_url()
        request["local_code"] = hashlib.sha256(Path(__file__).with_name("local_ollama.py").read_bytes()).hexdigest()
    digest = hashlib.sha256(json.dumps(request, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    model_slug = re.sub(r"[^a-zA-Z0-9_.-]", "_", model)
    segment_slug = re.sub(r"[^a-zA-Z0-9_.-]", "_", segment.segment_id)
    return Path(root) / "raw" / mode / model_slug / version / digest / f"{segment_slug}.json"


def estimate_cost(usage, mode):
    if mode in ("baseline", "local"):
        return 0.0
    input_rate = os.getenv("INPUT_USD_PER_MILLION")
    output_rate = os.getenv("OUTPUT_USD_PER_MILLION")
    if not input_rate or not output_rate or "input_tokens" not in usage or "output_tokens" not in usage:
        return None
    # Prompt-cache pricing requires separate accounting. Do not understate it.
    details = usage.get("input_token_details") or {}
    if any(details.get(k, 0) for k in ("cache_read", "cache_creation")):
        return None
    rates = [float(input_rate), float(output_rate)]
    if any(rate < 0 for rate in rates):
        raise ValueError("Token prices cannot be negative")
    return (usage["input_tokens"] * rates[0] + usage["output_tokens"] * rates[1]) / 1_000_000


def extract_batch(dataset, mode, model, version, results_dir, cached_only=False, retry_failed=False):
    results = []
    extractor = None
    for index, segment in enumerate(dataset, 1):
        path = cache_path(results_dir, mode, model, version, segment)
        record = None
        if path.exists():
            record = json.loads(path.read_text(encoding="utf-8"))
            if retry_failed and record.get("status") != "success":
                record = None
        hit = record is not None
        if record is None:
            if cached_only:
                raise FileNotFoundError(f"No cached response for {segment.segment_id}; no API call was made.")
            # Configuration errors abort before making a batch of identical failures.
            if extractor is None:
                extractor = get_extractor(mode, model_name=model, prompt_version=version)
            started = time.perf_counter()
            try:
                extracted = extractor.extract_attributes(segment)
                record = {
                    "status": "success", "extracted": extracted.model_dump(mode="json"),
                    "raw_response": getattr(extractor, "last_raw_response", None),
                    "token_usage": getattr(extractor, "last_token_usage", {}),
                    "error_message": None
                }
            except InvalidOutputError as exc:
                record = {
                    "status": "invalid_output", "extracted": None,
                    "raw_response": exc.raw_response, "token_usage": exc.token_usage,
                    "error_message": safe_error(exc)
                }
            except Exception as exc:
                record = {
                    "status": "api_error", "extracted": None, "raw_response": None,
                    "token_usage": {}, "error_message": safe_error(exc)
                }
            record.update(
                segment_id=segment.segment_id, model=model, mode=mode,
                prompt_version=version, input_payload=input_payload(segment),
                execution_time_ms=round((time.perf_counter() - started) * 1000, 2),
                recorded_at=datetime.now(timezone.utc).isoformat()
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[{index}/{len(dataset)}] {mode} / {segment.segment_id}: {record['status']}"
              f" ({'cached' if hit else 'new'}, {record['execution_time_ms']:.0f} ms)", flush=True)
        results.append(ExtractionResult(
            segment_id=segment.segment_id, expected=segment.expected_attributes,
            extracted=RoadAttributes.model_validate(record["extracted"]) if record.get("extracted") else None,
            execution_time_ms=record["execution_time_ms"], status=record["status"],
            error_message=record.get("error_message"), raw_response=record.get("raw_response"),
            token_usage=record.get("token_usage") or {}, input_payload=input_payload(segment),
            evaluation_fields=segment.evaluation_fields, cache_hit=hit,
            estimated_cost_usd=estimate_cost(record.get("token_usage") or {}, mode)
        ))
    return results
