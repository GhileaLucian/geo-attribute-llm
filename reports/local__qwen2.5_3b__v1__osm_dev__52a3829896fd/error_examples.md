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
    "reasoning_cot": "Highway=residential, lanes=2, and name=Aleea Bizușa provide evidence for a residential road with two lanes. Sidewalk=left indicates the presence of a sidewalk on the left side.",
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
    "reasoning_cot": "Highway=residential indicates a trunk road, lanes=2 provides the number of lanes, and name=Centura Apahida-Vâlcele and ref=DN1N provide the name and reference of the road.",
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
    "reasoning_cot": "Highway tag is explicitly provided as secondary_link and lanes tag confirms it is a single lane road.",
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
    "reasoning_cot": "Highway=residential, lanes=2, and name=Aleea Bizușa provide evidence for a residential road with two lanes. Sidewalk=left indicates the presence of a sidewalk on the left side.",
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
    "reasoning_cot": "The highway tag is 'service' and access tag is 'private', indicating this is a private service road.",
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
    "reasoning_cot": "Highway=residential indicates a trunk road, lanes=2 provides the number of lanes, and name=Centura Apahida-Vâlcele and ref=DN1N provide the name and reference of the road.",
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
    "reasoning_cot": "The highway tag is 'service' and access tag is 'private', indicating this is a private service road.",
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
    "reasoning_cot": "Highway=residential indicates a trunk road, lanes=2 provides the number of lanes, and name=Centura Apahida-Vâlcele and ref=DN1N provide the name and reference of the road.",
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
    "reasoning_cot": "Highway=secondary_link, lanes=2, lit=yes, name=Drumul Sfântul Ioan, ref=DJ107R, sidewalk=right provide sufficient information.",
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
    "barrier_type": "bollard",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Highway=construction and name=Lărgire DN indicate this is a construction road. No other attributes are provided.",
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
    "reasoning_cot": "Highway is proposed and name is Drum de legatura Baciu- TransRegio Feleac, which suggests it's a proposed road with a name that might be a local or official designation.",
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
  "segment_id": "386550590",
  "input": {
    "name": "Strada Valea Gârbăului",
    "osm_tags": {
      "highway": "unclassified",
      "lanes": "2",
      "motor_vehicle": "yes",
      "name": "Strada Valea Gârbăului"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"unclassified\", \"lanes\": \"2\", \"motor_vehicle\": \"yes\", \"name\": \"Strada Valea Gârbăului\"}"
  },
  "prediction": {
    "road_type": "unclassified",
    "speed_limit_kmh": 50,
    "barrier_present": true,
    "barrier_type": "guard_rail",
    "surface": "paved",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Highway tag is unclassified and motor_vehicle is yes, indicating a road with vehicles but not a motorway. Lanes are 2, suggesting a two-lane road. Name is provided, but does not affect speed or surface determination.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "unclassified",
    "speed_limit_kmh": null,
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

## barrier_type_mismatch

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
    "barrier_type": "bollard",
    "surface": "unknown",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Highway=construction and name=Lărgire DN indicate this is a construction road. No other attributes are provided.",
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
  "segment_id": "386550590",
  "input": {
    "name": "Strada Valea Gârbăului",
    "osm_tags": {
      "highway": "unclassified",
      "lanes": "2",
      "motor_vehicle": "yes",
      "name": "Strada Valea Gârbăului"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"unclassified\", \"lanes\": \"2\", \"motor_vehicle\": \"yes\", \"name\": \"Strada Valea Gârbăului\"}"
  },
  "prediction": {
    "road_type": "unclassified",
    "speed_limit_kmh": 50,
    "barrier_present": true,
    "barrier_type": "guard_rail",
    "surface": "paved",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Highway tag is unclassified and motor_vehicle is yes, indicating a road with vehicles but not a motorway. Lanes are 2, suggesting a two-lane road. Name is provided, but does not affect speed or surface determination.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "unclassified",
    "speed_limit_kmh": null,
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

## speed_limit_hallucination

```json
{
  "segment_id": "386550590",
  "input": {
    "name": "Strada Valea Gârbăului",
    "osm_tags": {
      "highway": "unclassified",
      "lanes": "2",
      "motor_vehicle": "yes",
      "name": "Strada Valea Gârbăului"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"unclassified\", \"lanes\": \"2\", \"motor_vehicle\": \"yes\", \"name\": \"Strada Valea Gârbăului\"}"
  },
  "prediction": {
    "road_type": "unclassified",
    "speed_limit_kmh": 50,
    "barrier_present": true,
    "barrier_type": "guard_rail",
    "surface": "paved",
    "oneway": null,
    "confidence_score": 0.9,
    "reasoning_cot": "Highway tag is unclassified and motor_vehicle is yes, indicating a road with vehicles but not a motorway. Lanes are 2, suggesting a two-lane road. Name is provided, but does not affect speed or surface determination.",
    "anomaly_flag": false
  },
  "reference": {
    "road_type": "unclassified",
    "speed_limit_kmh": null,
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
