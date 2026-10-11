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
    "reasoning_cot": "Tags indicate a residential road with 2 lanes and named Aleea Bizușa, no surface or speed is provided.",
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
    "reasoning_cot": "Highway=residential indicates a trunk road with 2 lanes and named 'Centura Apahida-Vâlcele' with reference 'DN1N'.",
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
    "reasoning_cot": "Tags indicate highway=secondary_link and lanes=1, suggesting a two-lane secondary road.",
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
    "reasoning_cot": "Tags indicate a residential road with 2 lanes and named Aleea Bizușa, no surface or speed is provided.",
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
    "reasoning_cot": "Tags indicate highway=service and access=private, suggesting a private service road.",
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
    "reasoning_cot": "Highway=residential indicates a trunk road with 2 lanes and named 'Centura Apahida-Vâlcele' with reference 'DN1N'.",
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
    "reasoning_cot": "Tags indicate highway=service and access=private, suggesting a private service road.",
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
    "reasoning_cot": "Highway=residential indicates a trunk road with 2 lanes and named 'Centura Apahida-Vâlcele' with reference 'DN1N'.",
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
    "surface": "paved",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Tags indicate highway=secondary_link, lit=yes, and name=Drumul Sfântul Ioan. No other attributes are provided.",
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

## barrier_presence_mismatch

```json
{
  "segment_id": "1137007236",
  "input": {
    "name": "Lărgire DN",
    "osm_tags": {
      "bridge": "yes",
      "highway": "construction",
      "lanes": "2",
      "name": "Lărgire DN"
    },
    "context_description": "Downloaded road way. Visible tags: {\"bridge\": \"yes\", \"highway\": \"construction\", \"lanes\": \"2\", \"name\": \"Lărgire DN\"}"
  },
  "prediction": {
    "road_type": "unknown",
    "speed_limit_kmh": null,
    "barrier_present": true,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.8,
    "reasoning_cot": "Highway=construction and name=Lărgire DN indicate this is a construction road, with no specific speed limit or surface provided.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "unknown",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
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
  "segment_id": "1149985564",
  "input": {
    "name": "Drum de legatura Baciu- TransRegio Feleac",
    "osm_tags": {
      "bridge": "yes",
      "highway": "proposed",
      "lanes": "2",
      "name": "Drum de legatura Baciu- TransRegio Feleac"
    },
    "context_description": "Downloaded road way. Visible tags: {\"bridge\": \"yes\", \"highway\": \"proposed\", \"lanes\": \"2\", \"name\": \"Drum de legatura Baciu- TransRegio Feleac\"}"
  },
  "prediction": {
    "road_type": "unknown",
    "speed_limit_kmh": null,
    "barrier_present": true,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Highway is proposed and name contains 'Drum de legatura Baciu- TransRegio Feleac', suggesting it's a proposed road with a name that might be a Romanian term for a road.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "unknown",
    "speed_limit_kmh": null,
    "barrier_present": null,
    "barrier_type": "unknown",
    "surface": "unknown",
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
  "segment_id": "807979520",
  "input": {
    "name": "Centura Apahida-Vâlcele",
    "osm_tags": {
      "bridge": "yes",
      "highway": "trunk",
      "lanes": "2",
      "name": "Centura Apahida-Vâlcele",
      "ref": "DN1N"
    },
    "context_description": "Downloaded road way. Visible tags: {\"bridge\": \"yes\", \"highway\": \"trunk\", \"lanes\": \"2\", \"name\": \"Centura Apahida-Vâlcele\", \"ref\": \"DN1N\"}"
  },
  "prediction": {
    "road_type": "trunk",
    "speed_limit_kmh": null,
    "barrier_present": true,
    "barrier_type": "unknown",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Highway=residential is not present, but highway=trunk is. Name and reference number provide context.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "trunk",
    "speed_limit_kmh": 90,
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
