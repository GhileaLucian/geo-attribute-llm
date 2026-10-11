"""
Data models and schemas for geospatial attribute extraction.
Defines strict Pydantic models for structured output enforcement.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RoadType(str, Enum):
    MOTORWAY = "motorway"
    TRUNK = "trunk"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    RESIDENTIAL = "residential"
    LIVING_STREET = "living_street"
    SERVICE = "service"
    TRACK = "track"
    PATH = "path"
    UNKNOWN = "unknown"


class BarrierType(str, Enum):
    NONE = "none"
    BOLLARD = "bollard"
    GATE = "gate"
    LIFT_GATE = "lift_gate"
    GUARD_RAIL = "guard_rail"
    FENCE = "fence"
    BLOCK = "block"
    TOLL_BOOTH = "toll_booth"
    UNKNOWN = "unknown"


class SurfaceType(str, Enum):
    PAVED = "paved"
    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    UNPAVED = "unpaved"
    GRAVEL = "gravel"
    COBBLESTONE = "cobblestone"
    COMPACTED = "compacted"
    DIRT = "dirt"
    UNKNOWN = "unknown"


class SpatialErrorCategory(str, Enum):
    NONE = "none"
    SPEED_LIMIT_HALLUCINATION = "speed_limit_hallucination"
    ROAD_CLASS_MISMATCH = "road_class_mismatch"
    BARRIER_FALSE_NEGATIVE = "barrier_false_negative"
    BARRIER_FALSE_POSITIVE = "barrier_false_positive"
    SURFACE_AMBIGUITY = "surface_ambiguity"
    OMITTED_ACCESS_RESTRICTION = "omitted_access_restriction"


class RoadAttributes(BaseModel):
    """Structured extraction target for OpenStreetMap way attributes."""
    
    road_type: RoadType = Field(
        ...,
        description="Standardized OpenStreetMap road classification (e.g. primary, residential, track)"
    )
    speed_limit_kmh: Optional[int] = Field(
        None,
        description="Legal maximum speed limit in km/h. Default to territorial defaults (e.g. 50 in urban) if implied."
    )
    barrier_present: bool = Field(
        False,
        description="Whether a physical barrier, bollard, gate, or blocking device exists along or across the segment."
    )
    barrier_type: BarrierType = Field(
        BarrierType.NONE,
        description="Specific type of barrier if barrier_present is True."
    )
    surface: SurfaceType = Field(
        SurfaceType.UNKNOWN,
        description="Pavement or terrain surface type."
    )
    oneway: bool = Field(
        False,
        description="Whether vehicle traffic is restricted to a single direction."
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model self-confidence score between 0.0 and 1.0 based on context clarity."
    )
    reasoning_cot: str = Field(
        ...,
        description="Chain-of-thought explanation outlining how OSM tags and description map to the attributes."
    )
    anomaly_flag: bool = Field(
        False,
        description="Flag set to True if tags contradict each other (e.g. motorway with 30 km/h speed limit)."
    )


class RoadSegmentInput(BaseModel):
    """Raw input representation of an OpenStreetMap road segment."""
    segment_id: str
    name: Optional[str] = "Unnamed Road"
    osm_tags: Dict[str, str] = Field(default_factory=dict)
    context_description: str
    expected_attributes: Optional[RoadAttributes] = None


class ExtractionResult(BaseModel):
    """Pairing of input segment, extracted attributes, and execution latency."""
    segment_id: str
    extracted: RoadAttributes
    expected: Optional[RoadAttributes] = None
    execution_time_ms: float
    error_categories: List[SpatialErrorCategory] = Field(default_factory=list)
    is_exact_match: bool = False
