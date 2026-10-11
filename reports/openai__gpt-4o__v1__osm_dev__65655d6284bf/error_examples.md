# Error examples from saved predictions

## api_error

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
  "prediction": null,
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
  "status": "api_error",
  "error": "OpenAIRateLimitError: Error code: 429 - {'error': {'message': 'You have no credits remaining. Add credits to continue using the API at https://platform.openai.com/settings/organization/billing/.', 'type': 'insufficient_quota', 'param': None, 'code': 'credit_balance_exhausted'}}",
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
  "prediction": null,
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
  "status": "api_error",
  "error": "OpenAIRateLimitError: Error code: 429 - {'error': {'message': 'You have no credits remaining. Add credits to continue using the API at https://platform.openai.com/settings/organization/billing/.', 'type': 'insufficient_quota', 'param': None, 'code': 'credit_balance_exhausted'}}",
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
  "segment_id": "1181327233",
  "input": {
    "name": "Unnamed road",
    "osm_tags": {
      "highway": "corridor"
    },
    "context_description": "Downloaded road way. Visible tags: {\"highway\": \"corridor\"}"
  },
  "prediction": null,
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
  "status": "api_error",
  "error": "OpenAIRateLimitError: Error code: 429 - {'error': {'message': 'You have no credits remaining. Add credits to continue using the API at https://platform.openai.com/settings/organization/billing/.', 'type': 'insufficient_quota', 'param': None, 'code': 'credit_balance_exhausted'}}",
  "evaluation_fields": [
    "speed_limit_kmh",
    "surface",
    "barrier_present",
    "barrier_type",
    "oneway"
  ]
}
```
