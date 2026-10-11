"""
Prompt templates and few-shot examples for geospatial attribute extraction.
Provides structured prompt construction for Claude (Anthropic) and OpenAI.
"""

import json
from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

GEOSPATIAL_SYSTEM_PROMPT = """You are an expert Geospatial Data Engineer and OpenStreetMap (OSM) Quality Assurance Specialist.
Your objective is to analyze raw OSM tags, street metadata, and contextual roadway descriptions to extract structured attributes:
1. road_type: Standard OSM classification (motorway, trunk, primary, secondary, tertiary, residential, living_street, service, track, path).
2. speed_limit_kmh: Legal maximum speed limit in km/h. Default to territorial defaults (Romania: Urban=50, Rural/County=90, Expressway=120, Motorway=130, Living Street=20) if omitted.
3. barrier_present: Boolean flag indicating if vehicular access is physically restricted by a barrier, bollard, or gate.
4. barrier_type: Specific barrier type (bollard, gate, lift_gate, guard_rail, fence, block, toll_booth, none).
5. surface: Pavement surface (asphalt, concrete, paved, unpaved, gravel, cobblestone, compacted, dirt, unknown).
6. oneway: Boolean flag indicating single-direction vehicle flow.
7. confidence_score: Numeric score between 0.0 and 1.0 reflecting certainty.
8. reasoning_cot: Step-by-step chain-of-thought explanation.
9. anomaly_flag: Boolean flag set to true if metadata contains explicit contradictions (e.g. residential street with 140 km/h speed limit).

CRITICAL DOMAIN RULES:
- If 'maxspeed' tag is absent, infer statutory default based on road_type and territorial context.
- Distinguish between traffic bollards (bollard), estate gates (gate), boom arms (lift_gate), and highway crash barriers (guard_rail).
- If tags contradict obvious reality (e.g., maxspeed 140 on a residential cul-de-sac), set anomaly_flag to true and assign safe statutory speed.
"""

FEW_SHOT_PAIRS: List[Dict[str, Any]] = [
    {
        "user_input": {
            "name": "Bulevardul 21 Decembrie 1989, Cluj-Napoca",
            "osm_tags": {
                "highway": "primary",
                "lanes": "4",
                "maxspeed": "50",
                "oneway": "yes",
                "surface": "asphalt",
                "busway": "lane"
            },
            "context_description": "Four-lane major arterial boulevard in central Cluj-Napoca with dedicated bus lane, dense traffic, and standard urban speed regulations."
        },
        "model_output": {
            "road_type": "primary",
            "speed_limit_kmh": 50,
            "barrier_present": False,
            "barrier_type": "none",
            "surface": "asphalt",
            "oneway": True,
            "confidence_score": 0.98,
            "reasoning_cot": "Primary urban arterial in central corridor. Tagged maxspeed=50 matches statutory urban limit. One-way confirmed. Surface is asphalt. No barriers present.",
            "anomaly_flag": False
        }
    },
    {
        "user_input": {
            "name": "Aleea Parcului Central Simion Bărnuțiu",
            "osm_tags": {
                "highway": "pedestrian",
                "surface": "compacted",
                "barrier": "bollard",
                "access": "no"
            },
            "context_description": "Compacted gravel park promenade protected by anti-vehicle bollards at both entrances."
        },
        "model_output": {
            "road_type": "living_street",
            "speed_limit_kmh": 20,
            "barrier_present": True,
            "barrier_type": "bollard",
            "surface": "compacted",
            "oneway": False,
            "confidence_score": 0.96,
            "reasoning_cot": "Pedestrian promenade mapped to living_street classification with default 20 km/h pedestrian zone limit. Explicit barrier=bollard confirms barrier. Surface is compacted gravel.",
            "anomaly_flag": False
        }
    },
    {
        "user_input": {
            "name": "Drum Forestier Făget Dealul Melcilor",
            "osm_tags": {
                "highway": "track",
                "tracktype": "grade3",
                "barrier": "gate",
                "motor_vehicle": "forestry"
            },
            "context_description": "Unpaved forestry access track in Făget forest. Padlocked metal forest ranger gate installed at trailhead to prevent unauthorized vehicles."
        },
        "model_output": {
            "road_type": "track",
            "speed_limit_kmh": 30,
            "barrier_present": True,
            "barrier_type": "gate",
            "surface": "unpaved",
            "oneway": False,
            "confidence_score": 0.95,
            "reasoning_cot": "Forestry track classification. Explicit barrier=gate confirms physical access restriction. Speed limit inferred as 30 km/h forestry track standard. Surface is unpaved.",
            "anomaly_flag": False
        }
    }
]


def format_user_payload(name: str, osm_tags: Dict[str, str], description: str) -> str:
    """Formats the input segment into a clean text block."""
    tags_formatted = "\n".join([f"  - {k}: {v}" for k, v in osm_tags.items()]) if osm_tags else "  (No tags)"
    return f"""Road Name: {name}
Context: {description}
OpenStreetMap Tags:
{tags_formatted}

Analyze the segment and output the structured attributes."""


def build_chat_messages(name: str, osm_tags: Dict[str, str], description: str) -> List[BaseMessage]:
    """
    Constructs a complete LangChain message sequence incorporating:
    1. System prompt
    2. Few-shot input/output examples (HumanMessage + AIMessage)
    3. Target segment HumanMessage
    """
    messages: List[BaseMessage] = [SystemMessage(content=GEOSPATIAL_SYSTEM_PROMPT)]

    for pair in FEW_SHOT_PAIRS:
        inp = pair["user_input"]
        out = pair["model_output"]
        human_text = format_user_payload(inp["name"], inp["osm_tags"], inp["context_description"])
        ai_text = json.dumps(out, indent=2)
        messages.append(HumanMessage(content=human_text))
        messages.append(AIMessage(content=ai_text))

    # Target segment to extract
    target_text = format_user_payload(name, osm_tags, description)
    messages.append(HumanMessage(content=target_text))

    return messages
