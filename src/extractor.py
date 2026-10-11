"""Local baseline and API extractors with explicit structured-output failures."""

import os
from src.config import load_configuration
from src.models import RoadAttributes, BarrierType
from src.osm_values import explicit_values
from src.prompts import build_chat_messages


class InvalidOutputError(ValueError):
    def __init__(self, message, raw=None, usage=None):
        super().__init__(message)
        self.raw_response = raw
        self.token_usage = usage or {}


class RuleBasedBaselineExtractor:
    name = "rule_based_baseline"

    def extract_attributes(self, segment):
        values = explicit_values(segment.osm_tags)
        # A limited English keyword rule; deliberately no numerical speed guesses.
        if values["barrier_present"] is None and "bollard" in segment.context_description.lower():
            values["barrier_present"] = True
            values["barrier_type"] = BarrierType.BOLLARD
        speed = values["speed_limit_kmh"]
        anomaly = values["road_type"].value == "residential" and speed is not None and speed > 80
        return RoadAttributes(
            **values, confidence_score=0.5 if anomaly else 0.9,
            reasoning_cot="Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
            anomaly_flag=anomaly
        )


class StructuredLLMExtractor:
    def extract_attributes(self, segment):
        messages = build_chat_messages(
            segment.name or "Unnamed road", segment.osm_tags,
            segment.context_description, self.prompt_version
        )
        response = self.structured_llm.invoke(messages)
        raw = response.get("raw")
        self.last_raw_response = raw.model_dump(mode="json") if raw is not None else None
        self.last_token_usage = getattr(raw, "usage_metadata", None) or {}
        parsed = response.get("parsed")
        if response.get("parsing_error") or parsed is None:
            raise InvalidOutputError(
                "Structured response failed schema validation.",
                self.last_raw_response, self.last_token_usage
            )
        try:
            return RoadAttributes.model_validate(parsed)
        except ValueError as exc:
            raise InvalidOutputError(
                "Structured response failed schema validation.",
                self.last_raw_response, self.last_token_usage
            ) from exc


class ClaudeExtractor(StructuredLLMExtractor):
    def __init__(self, model_name=None, prompt_version="v1"):
        load_configuration()
        self.model_name = model_name or os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-5-5"
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is missing. Set it in the local .env file.")
        from langchain_anthropic import ChatAnthropic
        self.name = f"claude ({self.model_name})"
        self.prompt_version = prompt_version
        self.llm = ChatAnthropic(
            model=self.model_name, api_key=api_key, temperature=0,
            max_tokens=1024, timeout=30, max_retries=2
        )
        self.structured_llm = self.llm.with_structured_output(RoadAttributes, include_raw=True)


class OpenAIExtractor(StructuredLLMExtractor):
    def __init__(self, model_name=None, prompt_version="v1"):
        load_configuration()
        self.model_name = model_name or os.getenv("OPENAI_MODEL") or "gpt-4o"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Set it in the local .env file.")
        from langchain_openai import ChatOpenAI
        self.name = f"openai ({self.model_name})"
        self.prompt_version = prompt_version
        self.llm = ChatOpenAI(
            model=self.model_name, api_key=api_key, temperature=0,
            timeout=30, max_retries=2
        )
        self.structured_llm = self.llm.with_structured_output(RoadAttributes, include_raw=True)


def get_extractor(mode="baseline", model_name=None, prompt_version="v1"):
    if mode == "baseline":
        return RuleBasedBaselineExtractor()
    if mode == "claude":
        return ClaudeExtractor(model_name, prompt_version)
    if mode == "openai":
        return OpenAIExtractor(model_name, prompt_version)
    raise ValueError(f"Unknown extractor mode: {mode}")
