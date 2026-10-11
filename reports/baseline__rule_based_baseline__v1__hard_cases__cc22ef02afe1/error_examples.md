# Error examples from saved predictions

## barrier_false_negative

```json
{
  "segment_id": "hard-01",
  "input": {
    "name": "Romanian bollards",
    "osm_tags": {
      "highway": "pedestrian"
    },
    "context_description": "La intrare sunt stalpisori metalici."
  },
  "prediction": {
    "road_type": "pedestrian",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "pedestrian",
    "speed_limit_kmh": null,
    "barrier_present": true,
    "barrier_type": "bollard",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Hand-written reference for this fictional scenario.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "road_type",
    "speed_limit_kmh",
    "barrier_present",
    "barrier_type",
    "surface",
    "oneway",
    "anomaly_flag"
  ]
}
```

```json
{
  "segment_id": "hard-02",
  "input": {
    "name": "Romanian lift gate",
    "osm_tags": {
      "highway": "service"
    },
    "context_description": "Accesul este blocat de o bariera cu brat."
  },
  "prediction": {
    "road_type": "service",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "service",
    "speed_limit_kmh": null,
    "barrier_present": true,
    "barrier_type": "lift_gate",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Hand-written reference for this fictional scenario.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "road_type",
    "speed_limit_kmh",
    "barrier_present",
    "barrier_type",
    "surface",
    "oneway",
    "anomaly_flag"
  ]
}
```

```json
{
  "segment_id": "hard-03",
  "input": {
    "name": "Romanian gate",
    "osm_tags": {
      "highway": "track"
    },
    "context_description": "La intrare este o poarta inchisa."
  },
  "prediction": {
    "road_type": "track",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "track",
    "speed_limit_kmh": null,
    "barrier_present": true,
    "barrier_type": "gate",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Hand-written reference for this fictional scenario.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "road_type",
    "speed_limit_kmh",
    "barrier_present",
    "barrier_type",
    "surface",
    "oneway",
    "anomaly_flag"
  ]
}
```

## barrier_type_mismatch

```json
{
  "segment_id": "hard-01",
  "input": {
    "name": "Romanian bollards",
    "osm_tags": {
      "highway": "pedestrian"
    },
    "context_description": "La intrare sunt stalpisori metalici."
  },
  "prediction": {
    "road_type": "pedestrian",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "pedestrian",
    "speed_limit_kmh": null,
    "barrier_present": true,
    "barrier_type": "bollard",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Hand-written reference for this fictional scenario.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "road_type",
    "speed_limit_kmh",
    "barrier_present",
    "barrier_type",
    "surface",
    "oneway",
    "anomaly_flag"
  ]
}
```

```json
{
  "segment_id": "hard-02",
  "input": {
    "name": "Romanian lift gate",
    "osm_tags": {
      "highway": "service"
    },
    "context_description": "Accesul este blocat de o bariera cu brat."
  },
  "prediction": {
    "road_type": "service",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "service",
    "speed_limit_kmh": null,
    "barrier_present": true,
    "barrier_type": "lift_gate",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Hand-written reference for this fictional scenario.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "road_type",
    "speed_limit_kmh",
    "barrier_present",
    "barrier_type",
    "surface",
    "oneway",
    "anomaly_flag"
  ]
}
```

```json
{
  "segment_id": "hard-03",
  "input": {
    "name": "Romanian gate",
    "osm_tags": {
      "highway": "track"
    },
    "context_description": "La intrare este o poarta inchisa."
  },
  "prediction": {
    "road_type": "track",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "track",
    "speed_limit_kmh": null,
    "barrier_present": true,
    "barrier_type": "gate",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Hand-written reference for this fictional scenario.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "road_type",
    "speed_limit_kmh",
    "barrier_present",
    "barrier_type",
    "surface",
    "oneway",
    "anomaly_flag"
  ]
}
```

## speed_limit_missing

```json
{
  "segment_id": "hard-05",
  "input": {
    "name": "Romanian speed",
    "osm_tags": {
      "highway": "residential"
    },
    "context_description": "Indicatorul arata limita de viteza 30 km/h."
  },
  "prediction": {
    "road_type": "residential",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "residential",
    "speed_limit_kmh": 30,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Hand-written reference for this fictional scenario.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "road_type",
    "speed_limit_kmh",
    "barrier_present",
    "barrier_type",
    "surface",
    "oneway",
    "anomaly_flag"
  ]
}
```

## anomaly_mismatch

```json
{
  "segment_id": "hard-06",
  "input": {
    "name": "Contradictory speed",
    "osm_tags": {
      "highway": "residential",
      "maxspeed": "30"
    },
    "context_description": "Textul spune limita 50 km/h."
  },
  "prediction": {
    "road_type": "residential",
    "speed_limit_kmh": 30,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "residential",
    "speed_limit_kmh": 30,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Hand-written reference for this fictional scenario.",
    "anomaly_flag": true
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "road_type",
    "speed_limit_kmh",
    "barrier_present",
    "barrier_type",
    "surface",
    "oneway",
    "anomaly_flag"
  ]
}
```

## surface_ambiguity

```json
{
  "segment_id": "hard-13",
  "input": {
    "name": "English surface",
    "osm_tags": {
      "highway": "track"
    },
    "context_description": "The road surface is gravel."
  },
  "prediction": {
    "road_type": "track",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Parsed explicit OSM tags; unknown values kept unknown. English bollard keyword checked.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "track",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "gravel",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Hand-written reference for this fictional scenario.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "road_type",
    "speed_limit_kmh",
    "barrier_present",
    "barrier_type",
    "surface",
    "oneway",
    "anomaly_flag"
  ]
}
```
