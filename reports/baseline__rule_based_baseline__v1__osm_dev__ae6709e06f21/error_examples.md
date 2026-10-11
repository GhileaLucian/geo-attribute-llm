# Error examples from saved predictions

## speed_limit_missing

```json
{
  "segment_id": "389714616",
  "input": {
    "name": "Aleea Bizușa",
    "osm_tags": {
      "highway": "residential",
      "lanes": "2",
      "name": "Aleea Bizușa",
      "sidewalk": "left"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"residential\", \"lanes\": \"2\", \"name\": \"Aleea Bizușa\", \"sidewalk\": \"left\"}"
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
    "surface": "asphalt",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Reference labels normalized from the downloaded OSM way tags.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```

```json
{
  "segment_id": "134752130",
  "input": {
    "name": "Centura Apahida-Vâlcele",
    "osm_tags": {
      "highway": "trunk",
      "lanes": "2",
      "name": "Centura Apahida-Vâlcele",
      "ref": "DN1N"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"trunk\", \"lanes\": \"2\", \"name\": \"Centura Apahida-Vâlcele\", \"ref\": \"DN1N\"}"
  },
  "prediction": {
    "road_type": "trunk",
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
    "road_type": "trunk",
    "speed_limit_kmh": 70,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "asphalt",
    "oneway": false,
    "confidence_score": 1.0,
    "reasoning_cot": "Reference labels normalized from the downloaded OSM way tags.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```

```json
{
  "segment_id": "1341277055",
  "input": {
    "name": "Unnamed road",
    "osm_tags": {
      "highway": "secondary_link",
      "lanes": "1"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"secondary_link\", \"lanes\": \"1\"}"
  },
  "prediction": {
    "road_type": "secondary_link",
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
    "road_type": "secondary_link",
    "speed_limit_kmh": 50,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "asphalt",
    "oneway": true,
    "confidence_score": 1.0,
    "reasoning_cot": "Reference labels normalized from the downloaded OSM way tags.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```

## surface_ambiguity

```json
{
  "segment_id": "389714616",
  "input": {
    "name": "Aleea Bizușa",
    "osm_tags": {
      "highway": "residential",
      "lanes": "2",
      "name": "Aleea Bizușa",
      "sidewalk": "left"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"residential\", \"lanes\": \"2\", \"name\": \"Aleea Bizușa\", \"sidewalk\": \"left\"}"
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
    "surface": "asphalt",
    "oneway": null,
    "confidence_score": 1.0,
    "reasoning_cot": "Reference labels normalized from the downloaded OSM way tags.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```

```json
{
  "segment_id": "679251376",
  "input": {
    "name": "Unnamed road",
    "osm_tags": {
      "access": "private",
      "highway": "service"
    },
    "context_description": "Downloaded road way. Visible tags: {\"access\": \"private\", \"highway\": \"service\"}"
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
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "asphalt",
    "oneway": true,
    "confidence_score": 1.0,
    "reasoning_cot": "Reference labels normalized from the downloaded OSM way tags.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```

```json
{
  "segment_id": "134752130",
  "input": {
    "name": "Centura Apahida-Vâlcele",
    "osm_tags": {
      "highway": "trunk",
      "lanes": "2",
      "name": "Centura Apahida-Vâlcele",
      "ref": "DN1N"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"trunk\", \"lanes\": \"2\", \"name\": \"Centura Apahida-Vâlcele\", \"ref\": \"DN1N\"}"
  },
  "prediction": {
    "road_type": "trunk",
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
    "road_type": "trunk",
    "speed_limit_kmh": 70,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "asphalt",
    "oneway": false,
    "confidence_score": 1.0,
    "reasoning_cot": "Reference labels normalized from the downloaded OSM way tags.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```

## oneway_mismatch

```json
{
  "segment_id": "679251376",
  "input": {
    "name": "Unnamed road",
    "osm_tags": {
      "access": "private",
      "highway": "service"
    },
    "context_description": "Downloaded road way. Visible tags: {\"access\": \"private\", \"highway\": \"service\"}"
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
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "asphalt",
    "oneway": true,
    "confidence_score": 1.0,
    "reasoning_cot": "Reference labels normalized from the downloaded OSM way tags.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```

```json
{
  "segment_id": "134752130",
  "input": {
    "name": "Centura Apahida-Vâlcele",
    "osm_tags": {
      "highway": "trunk",
      "lanes": "2",
      "name": "Centura Apahida-Vâlcele",
      "ref": "DN1N"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"trunk\", \"lanes\": \"2\", \"name\": \"Centura Apahida-Vâlcele\", \"ref\": \"DN1N\"}"
  },
  "prediction": {
    "road_type": "trunk",
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
    "road_type": "trunk",
    "speed_limit_kmh": 70,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "asphalt",
    "oneway": false,
    "confidence_score": 1.0,
    "reasoning_cot": "Reference labels normalized from the downloaded OSM way tags.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```

```json
{
  "segment_id": "26634240",
  "input": {
    "name": "Drumul Sfântul Ioan",
    "osm_tags": {
      "highway": "secondary_link",
      "lanes": "2",
      "lit": "yes",
      "name": "Drumul Sfântul Ioan",
      "ref": "DJ107R",
      "sidewalk": "right"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"secondary_link\", \"lanes\": \"2\", \"lit\": \"yes\", \"name\": \"Drumul Sfântul Ioan\", \"ref\": \"DJ107R\", \"sidewalk\": \"right\"}"
  },
  "prediction": {
    "road_type": "secondary_link",
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
    "road_type": "secondary_link",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "asphalt",
    "oneway": true,
    "confidence_score": 1.0,
    "reasoning_cot": "Reference labels normalized from the downloaded OSM way tags.",
    "anomaly_flag": false
  },
  "status": "success",
  "error": null,
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```
