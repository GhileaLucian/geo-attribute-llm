"""
Attribute extraction engines for geospatial road features.
Provides:
1. RuleBasedBaselineExtractor (Deterministic rule baseline for benchmarking)
2. ClaudeExtractor (LangChain ChatAnthropic with few-shot prompts and structured output)
3. OpenAIExtractor (LangChain ChatOpenAI with few-shot prompts and structured output)
"""

import os
import time
from typing import Optional
from src.models import (
    RoadSegmentInput,
    RoadAttributes,
    RoadType,
    BarrierType,
    SurfaceType
)
from src.prompts import build_chat_messages


class RuleBasedBaselineExtractor:
    """
    Deterministic rule-based baseline extractor.
    Parses OpenStreetMap tags and keyword heuristics without invoking a neural LLM.
    Used as the comparison baseline to evaluate the value added by LLM extraction.
    """

    def __init__(self):
        self.name = "rule_based_baseline"

    def extract_attributes(self, segment: RoadSegmentInput) -> RoadAttributes:
        tags = segment.osm_tags
        desc_lower = segment.context_description.lower()
        name_lower = (segment.name or "").lower()

        # 1. Road classification
        raw_hw = tags.get("highway", "").lower()
        if raw_hw == "motorway":
            road_type = RoadType.MOTORWAY
        elif raw_hw == "trunk":
            road_type = RoadType.TRUNK
        elif raw_hw == "primary":
            road_type = RoadType.PRIMARY
        elif raw_hw == "secondary":
            road_type = RoadType.SECONDARY
        elif raw_hw == "tertiary":
            road_type = RoadType.TERTIARY
        elif raw_hw in ["residential", "unclassified"]:
            road_type = RoadType.RESIDENTIAL
        elif raw_hw in ["living_street", "pedestrian"]:
            road_type = RoadType.LIVING_STREET
        elif raw_hw == "service":
            road_type = RoadType.SERVICE
        elif raw_hw == "track":
            road_type = RoadType.TRACK
        else:
            road_type = RoadType.UNKNOWN

        # 2. Speed limit
        speed_limit = None
        if "maxspeed" in tags:
            try:
                speed_limit = int(tags["maxspeed"])
            except ValueError:
                pass

        if speed_limit is None:
            if road_type == RoadType.MOTORWAY:
                speed_limit = 130
            elif road_type == RoadType.TRUNK:
                speed_limit = 90
            elif road_type in [RoadType.PRIMARY, RoadType.SECONDARY, RoadType.TERTIARY, RoadType.RESIDENTIAL]:
                speed_limit = 50
            elif road_type in [RoadType.LIVING_STREET, RoadType.SERVICE]:
                speed_limit = 20
            elif road_type == RoadType.TRACK:
                speed_limit = 30
            else:
                speed_limit = 50

        # 3. Barrier detection
        barrier_present = False
        barrier_type = BarrierType.NONE
        raw_barrier = tags.get("barrier", "").lower()

        if raw_barrier:
            barrier_present = True
            if "bollard" in raw_barrier:
                barrier_type = BarrierType.BOLLARD
            elif "lift_gate" in raw_barrier:
                barrier_type = BarrierType.LIFT_GATE
            elif "gate" in raw_barrier:
                barrier_type = BarrierType.GATE
            elif "guard_rail" in raw_barrier:
                barrier_type = BarrierType.GUARD_RAIL
            elif "block" in raw_barrier:
                barrier_type = BarrierType.BLOCK
            else:
                barrier_type = BarrierType.GATE
        elif "bollard" in tags or "bollard" in desc_lower:
            barrier_present = True
            barrier_type = BarrierType.BOLLARD

        # 4. Surface
        raw_surf = tags.get("surface", "").lower()
        if raw_surf in ["asphalt", "bitumen"]:
            surface = SurfaceType.ASPHALT
        elif raw_surf in ["cobblestone", "sett"]:
            surface = SurfaceType.COBBLESTONE
        elif raw_surf == "gravel":
            surface = SurfaceType.GRAVEL
        elif raw_surf == "dirt":
            surface = SurfaceType.DIRT
        elif raw_surf == "concrete":
            surface = SurfaceType.CONCRETE
        elif raw_surf == "paved":
            surface = SurfaceType.PAVED
        elif raw_surf == "compacted":
            surface = SurfaceType.COMPACTED
        elif raw_surf == "unpaved":
            surface = SurfaceType.UNPAVED
        else:
            surface = SurfaceType.ASPHALT

        # 5. One-way
        oneway = tags.get("oneway", "").lower() in ["yes", "1", "true"]

        # 6. Anomaly check
        anomaly = False
        if road_type == RoadType.RESIDENTIAL and speed_limit > 80:
            anomaly = True
            speed_limit = 50

        cot = (
            f"[Rule Baseline] Tag highway='{raw_hw}' -> road_type='{road_type.value}'. "
            f"maxspeed='{tags.get('maxspeed', 'none')}' -> inferred {speed_limit} km/h. "
            f"barrier='{raw_barrier}' -> present={barrier_present} ({barrier_type.value}). "
            f"surface='{raw_surf}' -> {surface.value}."
        )

        return RoadAttributes(
            road_type=road_type,
            speed_limit_kmh=speed_limit,
            barrier_present=barrier_present,
            barrier_type=barrier_type,
            surface=surface,
            oneway=oneway,
            confidence_score=0.90 if not anomaly else 0.40,
            reasoning_cot=cot,
            anomaly_flag=anomaly
        )


class ClaudeExtractor:
    """
    Live LLM attribute extractor powered by Anthropic Claude 3.5 Sonnet.
    Uses LangChain ChatAnthropic with system prompts, few-shot demonstration pairs,
    and strict Pydantic structured output validation.
    """

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please export ANTHROPIC_API_KEY='your-key' or run with --mode baseline."
            )
        from langchain_anthropic import ChatAnthropic

        self.name = f"claude ({model_name})"
        self.llm = ChatAnthropic(
            model=model_name,
            temperature=0.0,
            api_key=api_key
        )
        self.structured_llm = self.llm.with_structured_output(RoadAttributes)

    def extract_attributes(self, segment: RoadSegmentInput) -> RoadAttributes:
        messages = build_chat_messages(
            name=segment.name or "Unnamed Road",
            osm_tags=segment.osm_tags,
            description=segment.context_description
        )
        result: RoadAttributes = self.structured_llm.invoke(messages)
        return result


class OpenAIExtractor:
    """
    Live LLM attribute extractor powered by OpenAI GPT-4o.
    Uses LangChain ChatOpenAI with system prompts, few-shot demonstration pairs,
    and strict Pydantic structured output validation.
    """

    def __init__(self, model_name: str = "gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please export OPENAI_API_KEY='your-key' or run with --mode baseline."
            )
        from langchain_openai import ChatOpenAI

        self.name = f"openai ({model_name})"
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.0,
            api_key=api_key
        )
        self.structured_llm = self.llm.with_structured_output(RoadAttributes)

    def extract_attributes(self, segment: RoadSegmentInput) -> RoadAttributes:
        messages = build_chat_messages(
            name=segment.name or "Unnamed Road",
            osm_tags=segment.osm_tags,
            description=segment.context_description
        )
        result: RoadAttributes = self.structured_llm.invoke(messages)
        return result


def get_extractor(mode: str = "baseline"):
    """
    Factory function to instantiate the selected extractor.
    Supported modes: 'baseline', 'claude', 'openai'.
    """
    mode = mode.lower()
    if mode == "claude":
        return ClaudeExtractor()
    elif mode == "openai":
        return OpenAIExtractor()
    elif mode == "baseline":
        return RuleBasedBaselineExtractor()
    else:
        raise ValueError(f"Unknown extractor mode: '{mode}'. Supported: 'baseline', 'claude', 'openai'.")
