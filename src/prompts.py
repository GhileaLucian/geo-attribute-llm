"""
Prompt templates and few-shot examples for geospatial attribute extraction.
Implements Chain-of-Thought (CoT) and strict JSON schema output formatting.
"""

from typing import List, Dict, Any

GEOSPATIAL_SYSTEM_PROMPT = """You are an expert Geospatial Data Engineer and OpenStreetMap (OSM) Quality Assurance Specialist.
Your objective is to analyze raw OSM tags, street attributes, and contextual roadway descriptions to extract structured attributes:
1. road_type: Standard OSM classification (motorway, trunk, primary, secondary, tertiary, residential, living_street, service, track, path).
2. speed_limit_kmh: Explicit speed limit or legal default for the road category in the territory (e.g. Romania: Urban=50 km/h, Rural/County=90 km/h, Expressway=120 km/h, Motorway=130 km/h, Residential/Living Street=30 km/h or 20 km/h).
3. barrier_present: Boolean flag indicating if access is physically restricted, gated, or blocked.
4. barrier_type: Specific barrier type (bollard, gate, lift_gate, guard_rail, fence, block, toll_booth, or none).
5. surface: Road surface material (asphalt, paved, concrete, unpaved, gravel, cobblestone, dirt, unknown).
6. oneway: Boolean flag indicating single-direction vehicle flow.
7. confidence_score: Numeric score between 0.0 and 1.0 based on how conclusive the evidence is.
8. reasoning_cot: Step-by-step reasoning explaining how tags and descriptions lead to the values.
9. anomaly_flag: Set to true if tags present logical conflicts (e.g., motorway with pedestrian path tags, or speed limit >130 on residential road).

CRITICAL OPERATIONAL RULES:
- If 'maxspeed' tag is absent, infer the statutory speed limit based on road_type and territorial context (urban residential = 50 km/h unless stated otherwise).
- Distinguish between traffic bollards (bollard), estate gates (gate), and highway crash barriers (guard_rail).
- If tags explicitly state 'highway=residential' but description mentions unpaved gravel road, classify surface as 'gravel' or 'unpaved' and road_type as 'residential'.
- Always return valid JSON matching the requested schema.
"""

FEW_SHOT_EXAMPLES: List[Dict[str, Any]] = [
    {
        "input": {
            "name": "Bulevardul 21 Decembrie 1989, Cluj-Napoca",
            "osm_tags": {
                "highway": "primary",
                "lanes": "4",
                "lit": "yes",
                "maxspeed": "50",
                "name": "Bulevardul 21 Decembrie 1989",
                "oneway": "no",
                "surface": "asphalt"
            },
            "context_description": "Major urban arterial boulevard in central Cluj-Napoca with multiple lanes, dedicated bus corridor, asphalt surface, and standard urban speed limit."
        },
        "output": {
            "road_type": "primary",
            "speed_limit_kmh": 50,
            "barrier_present": False,
            "barrier_type": "none",
            "surface": "asphalt",
            "oneway": False,
            "confidence_score": 0.98,
            "reasoning_cot": "The 'highway=primary' tag and urban boulevard context confirm road_type='primary'. Tag 'maxspeed=50' matches urban standard. Surface is explicitly 'asphalt'. No barriers detected.",
            "anomaly_flag": False
        }
    },
    {
        "input": {
            "name": "Aleea Parcului Central (Zonă Pietonală)",
            "osm_tags": {
                "highway": "pedestrian",
                "access": "delivery",
                "bollard": "rising",
                "surface": "cobblestone"
            },
            "context_description": "Pedestrian pathway in the central park. Retractable hydraulic bollards restrict motorized entry except for early morning delivery vehicles."
        },
        "output": {
            "road_type": "living_street",
            "speed_limit_kmh": 20,
            "barrier_present": True,
            "barrier_type": "bollard",
            "surface": "cobblestone",
            "oneway": False,
            "confidence_score": 0.95,
            "reasoning_cot": "Pedestrian area with controlled vehicular access maps to living_street/pedestrian speed (20 km/h). Explicit 'bollard=rising' indicates physical barrier present with type 'bollard'. Surface is cobblestone.",
            "anomaly_flag": False
        }
    },
    {
        "input": {
            "name": "Drum Forestier Făget Dealul Melcilor",
            "osm_tags": {
                "highway": "track",
                "tracktype": "grade3",
                "barrier": "gate",
                "motor_vehicle": "forestry"
            },
            "context_description": "Unpaved forestry access track in Făget forest. Padlocked metal forest ranger gate installed at trailhead to prevent unauthorized off-road vehicles."
        },
        "output": {
            "road_type": "track",
            "speed_limit_kmh": 30,
            "barrier_present": True,
            "barrier_type": "gate",
            "surface": "unpaved",
            "oneway": False,
            "confidence_score": 0.96,
            "reasoning_cot": "Tag 'highway=track' and 'tracktype=grade3' confirm forestry track with unpaved/dirt surface. 'barrier=gate' confirms physical barrier of type 'gate'. Speed limit inferred as 30 km/h forest track maximum.",
            "anomaly_flag": False
        }
    }
]


def format_extraction_prompt(segment_name: str, osm_tags: Dict[str, str], description: str) -> str:
    """Formats the user prompt for a specific OSM road segment."""
    tag_str = "\n".join([f"  - {k}: {v}" for k, v in osm_tags.items()]) if osm_tags else "  (No explicit tags available)"
    return f"""Analyze this road segment and extract the structured attributes according to the schema:

Road Name: {segment_name}
OpenStreetMap Tags:
{tag_str}

Context Description:
{description}

Provide your structured output with step-by-step reasoning (Chain-of-Thought)."""
