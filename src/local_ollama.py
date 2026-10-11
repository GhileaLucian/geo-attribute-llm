"""Schema-constrained inference on a loopback Ollama server; no cloud or API key."""

import ipaddress
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, ProxyHandler

from src.config import load_configuration, resolve_model
from src.extractor import InvalidOutputError
from src.models import RoadAttributes
from src.prompts import build_chat_messages


def local_settings():
    context = int(os.getenv("LOCAL_CONTEXT_SIZE") or "4096")
    if not 1024 <= context <= 8192:
        raise ValueError("LOCAL_CONTEXT_SIZE must be between 1024 and 8192.")
    return {"temperature": 0, "seed": 42, "num_ctx": context, "num_predict": 1024}


def local_base_url():
    url = (os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
    parsed = urlsplit(url)
    try:
        loopback = parsed.hostname == "localhost" or ipaddress.ip_address(parsed.hostname).is_loopback
    except (ValueError, TypeError):
        loopback = False
    if (parsed.scheme != "http" or not loopback or parsed.username or parsed.password
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise ValueError("Local mode requires a loopback HTTP Ollama URL, e.g. http://127.0.0.1:11434.")
    return url


def request_json(url, payload=None, timeout=5):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    # Do not route road data or credentials through an environment-configured proxy.
    opener = build_opener(ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", errors="replace")
        raise RuntimeError(f"Local Ollama HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("Cannot reach local Ollama. Start Ollama and check http://127.0.0.1:11434.") from exc


class LocalOllamaExtractor:
    def __init__(self, model_name=None, prompt_version="v1"):
        load_configuration()
        self.model_name = resolve_model("local", model_name)
        if ":cloud" in self.model_name.lower():
            raise ValueError("Cloud models are not allowed in local mode. Use qwen2.5:3b.")
        self.base_url = local_base_url()
        self.options = local_settings()
        self.prompt_version = prompt_version
        self.name = f"local ({self.model_name})"
        self.last_raw_response = None
        self.last_token_usage = {}
        try:
            models = request_json(self.base_url + "/api/tags").get("models", [])
        except RuntimeError as exc:
            raise ValueError(str(exc)) from exc
        names = {item.get("name") or item.get("model") for item in models}
        if self.model_name not in names:
            raise ValueError(f"Local model {self.model_name} is not installed. Run: ollama pull {self.model_name}")
        self.model_digest = next((item.get("digest") for item in models
                                  if (item.get("name") or item.get("model")) == self.model_name), None)

    def extract_attributes(self, segment):
        schema = RoadAttributes.model_json_schema()
        roles = {"system": "system", "human": "user", "ai": "assistant"}
        messages = [{"role": roles[item.type], "content": item.content}
                    for item in build_chat_messages(segment.name or "Unnamed road", segment.osm_tags,
                                                    segment.context_description, self.prompt_version)]
        # Both the prompt and the constrained sampler see the same schema.
        messages[0]["content"] += "\nReturn one JSON object matching this schema:\n" + json.dumps(schema)
        self.last_raw_response = None
        self.last_token_usage = {}
        response = request_json(self.base_url + "/api/chat", {
            "model": self.model_name, "messages": messages, "format": schema,
            "stream": False, "options": self.options, "keep_alive": "5m"
        }, timeout=180)
        self.last_raw_response = {**response, "local_model_digest": self.model_digest,
                                  "generation_options": self.options}
        input_tokens, output_tokens = response.get("prompt_eval_count"), response.get("eval_count")
        if isinstance(input_tokens, int) and isinstance(output_tokens, int):
            self.last_token_usage = {"input_tokens": input_tokens, "output_tokens": output_tokens,
                                    "total_tokens": input_tokens + output_tokens}
        try:
            if not response.get("done") or response.get("done_reason") == "length":
                raise ValueError("Incomplete response")
            return RoadAttributes.model_validate_json(response["message"]["content"])
        except (ValueError, KeyError, TypeError) as exc:
            raise InvalidOutputError("Local structured response failed schema validation or was truncated.",
                                     self.last_raw_response, self.last_token_usage) from exc
