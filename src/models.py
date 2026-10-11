"""Schemas for extraction, reference labels and recorded attempts."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


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
    PEDESTRIAN = "pedestrian"
    FOOTWAY = "footway"
    CYCLEWAY = "cycleway"
    STEPS = "steps"
    UNCLASSIFIED = "unclassified"
    MOTORWAY_LINK = "motorway_link"
    TRUNK_LINK = "trunk_link"
    PRIMARY_LINK = "primary_link"
    SECONDARY_LINK = "secondary_link"
    TERTIARY_LINK = "tertiary_link"
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
    PAVING_STONES = "paving_stones"
    FINE_GRAVEL = "fine_gravel"
    GROUND = "ground"
    GRASS = "grass"
    SAND = "sand"
    UNKNOWN = "unknown"


class SpatialErrorCategory(str, Enum):
    NONE = "none"
    SPEED_LIMIT_HALLUCINATION = "speed_limit_hallucination"
    SPEED_LIMIT_MISMATCH = "speed_limit_mismatch"
    SPEED_LIMIT_MISSING = "speed_limit_missing"
    ROAD_CLASS_MISMATCH = "road_class_mismatch"
    BARRIER_FALSE_NEGATIVE = "barrier_false_negative"
    BARRIER_FALSE_POSITIVE = "barrier_false_positive"
    BARRIER_TYPE_MISMATCH = "barrier_type_mismatch"
    BARRIER_PRESENCE_MISMATCH = "barrier_presence_mismatch"
    SURFACE_AMBIGUITY = "surface_ambiguity"
    ONEWAY_MISMATCH = "oneway_mismatch"
    ANOMALY_MISMATCH = "anomaly_mismatch"
    INVALID_OUTPUT = "invalid_output"
    API_ERROR = "api_error"


EVALUATION_FIELDS = [
    "road_type", "speed_limit_kmh", "barrier_present", "barrier_type",
    "surface", "oneway", "anomaly_flag"
]


class RoadAttributes(BaseModel):
    model_config = ConfigDict(extra="forbid")
    road_type: RoadType
    speed_limit_kmh: Optional[int] = Field(
        None, ge=0, le=300,
        description="Speed recorded in tags or explicitly in text, in km/h. Null when unsupported."
    )
    barrier_present: Optional[bool] = Field(
        None, description="True/false with evidence about a barrier; null when unknown."
    )
    barrier_type: BarrierType = BarrierType.UNKNOWN
    surface: SurfaceType = SurfaceType.UNKNOWN
    oneway: Optional[bool] = Field(
        None, description="True includes oneway=-1; false for explicit two-way; null when unknown."
    )
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Self-assessment, not calibrated probability."
    )
    reasoning_cot: str = Field(
        ..., description="Brief evidence summary citing tags or text, not a private reasoning trace."
    )
    anomaly_flag: bool = False

    @model_validator(mode="after")
    def consistent_barrier(self):
        if self.barrier_present is False and self.barrier_type != BarrierType.NONE:
            raise ValueError("An absent barrier must have barrier_type=none")
        if self.barrier_present is True and self.barrier_type == BarrierType.NONE:
            raise ValueError("A present barrier cannot have barrier_type=none")
        if self.barrier_present is None and self.barrier_type != BarrierType.UNKNOWN:
            raise ValueError("An unknown barrier must have barrier_type=unknown")
        return self


class RoadSegmentInput(BaseModel):
    segment_id: str
    name: Optional[str] = "Unnamed Road"
    osm_tags: Dict[str, str] = Field(default_factory=dict)
    context_description: str
    expected_attributes: Optional[RoadAttributes] = None
    source: str = "hand-curated-unverified"
    osm_way_id: Optional[int] = None
    collected_at: Optional[str] = None
    hidden_attributes: List[str] = Field(default_factory=list)
    evaluation_fields: List[str] = Field(default_factory=lambda: list(EVALUATION_FIELDS))


class ExtractionResult(BaseModel):
    segment_id: str
    extracted: Optional[RoadAttributes] = None
    expected: Optional[RoadAttributes] = None
    execution_time_ms: float
    error_categories: List[SpatialErrorCategory] = Field(default_factory=list)
    is_exact_match: bool = False
    status: str = "success"
    error_message: Optional[str] = None
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    evaluation_fields: List[str] = Field(default_factory=lambda: list(EVALUATION_FIELDS))
    raw_response: Optional[Dict[str, Any]] = None
    token_usage: Dict[str, Any] = Field(default_factory=dict)
    cache_hit: bool = False
    estimated_cost_usd: Optional[float] = None
