"""Normalize explicit OSM values. Missing tags stay unknown."""

import re
from src.models import RoadType, SurfaceType, BarrierType


def enum_or_unknown(enum_class, raw):
    try:
        return enum_class(raw)
    except ValueError:
        return enum_class.UNKNOWN


def parse_speed(raw):
    if raw is None:
        return None
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(km/h|kmh|mph)?\s*", str(raw).lower())
    if not match:
        return None
    value = float(match.group(1))
    if match.group(2) == "mph":
        value *= 1.609344
    value = round(value)
    return value if 0 <= value <= 300 else None


def parse_oneway(raw):
    if raw is None:
        return None
    raw = str(raw).lower()
    if raw in {"yes", "1", "true", "-1"}:
        return True
    if raw in {"no", "0", "false"}:
        return False
    return None


def parse_surface(raw):
    aliases = {"bitumen": "asphalt", "sett": "cobblestone", "earth": "dirt"}
    return enum_or_unknown(SurfaceType, aliases.get(raw, raw or "unknown"))


def parse_barrier(raw):
    if raw is None or raw == "":
        return None, BarrierType.UNKNOWN
    if raw.lower() in {"no", "none"}:
        return False, BarrierType.NONE
    return True, enum_or_unknown(BarrierType, raw.lower())


def explicit_values(tags):
    present, barrier_type = parse_barrier(tags.get("barrier"))
    return {
        "road_type": enum_or_unknown(RoadType, tags.get("highway", "unknown")),
        "speed_limit_kmh": parse_speed(tags.get("maxspeed")),
        "barrier_present": present,
        "barrier_type": barrier_type,
        "surface": parse_surface(tags.get("surface")),
        "oneway": parse_oneway(tags.get("oneway"))
    }
