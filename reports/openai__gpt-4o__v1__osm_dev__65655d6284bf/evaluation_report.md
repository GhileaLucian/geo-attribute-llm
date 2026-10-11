# Geospatial extraction evaluation

Dataset: osm_dev.json
Source counts: {'OpenStreetMap/Overpass': 40}
Extractor: openai / gpt-4o / v1
Run time (UTC): 2026-10-11T17:25:11.256890+00:00

Attempts: 40; labeled attempts: 40.
Exact match across each record's evaluation_fields: 0.0%.
Invalid outputs: 0; API errors: 40; all failures: 100.0%.
Failed predictions stay in the denominators. Unlabeled records are excluded from accuracy.

| Attribute | n | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| road_type | 0 | not evaluated | not evaluated | not evaluated | not evaluated |
| surface_type | 40 | 0.0% | 0.0% | 0.0% | 0.0% |
| barrier_present | 40 | 0.0% | 0.0% | 0.0% | 0.0% |
| barrier_type | 40 | 0.0% | 0.0% | 0.0% | 0.0% |
| oneway | 40 | 0.0% | 0.0% | 0.0% | 0.0% |
| anomaly_detection | 0 | not evaluated | not evaluated | not evaluated | not evaluated |
| speed (exact, including unknown) | 40 | - | - | - | 0.0% |

Known speed labels: 6; exact accuracy on known labels: 0.0%; within 10 km/h: 0.0%.
Missing speed labels: 34; numerical predictions without a recorded speed: 0.
A missing OSM speed label does not establish the real legal limit. The historical error name speed_limit_hallucination here means unsupported by the recorded reference.

## Class support and confusion matrices

Per-class precision, recall, F1, support and confusion matrices are in metrics_summary.json.
Unknown matches can dominate a small dataset. Use known_reference_accuracy and class support when interpreting scores.

### surface_type

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| __failed__ | 0 | 0.0% | 0.0% | 0.0% |
| asphalt | 22 | 0.0% | 0.0% | 0.0% |
| concrete | 1 | 0.0% | 0.0% | 0.0% |
| dirt | 2 | 0.0% | 0.0% | 0.0% |
| ground | 1 | 0.0% | 0.0% | 0.0% |
| paving_stones | 1 | 0.0% | 0.0% | 0.0% |
| unknown | 13 | 0.0% | 0.0% | 0.0% |

### barrier_present

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| __failed__ | 0 | 0.0% | 0.0% | 0.0% |
| unknown | 40 | 0.0% | 0.0% | 0.0% |

### barrier_type

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| __failed__ | 0 | 0.0% | 0.0% | 0.0% |
| unknown | 40 | 0.0% | 0.0% | 0.0% |

### oneway

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| __failed__ | 0 | 0.0% | 0.0% | 0.0% |
| false | 2 | 0.0% | 0.0% | 0.0% |
| true | 17 | 0.0% | 0.0% | 0.0% |
| unknown | 21 | 0.0% | 0.0% | 0.0% |

## Error counts

| Category | Count |
| --- | ---: |
| api_error | 40 |

## Execution

Cache hits: 0. Cached responses retain the original latency and token usage.
Tokens: {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}. Usage unavailable for 40 attempts (baseline has no API tokens).
Estimated original API cost (USD): None.
Estimated new API cost (USD): None.
Configured plain token-price estimate, not an invoice. Unknown cost is null.

## Limits

OSM tags are reference labels, not independent field verification. Way-level barriers omit barriers on nodes.
Hand-written scenarios are fictional and reported separately from downloaded data.
The old curated examples expose target tags and may overlap few-shot examples; their scores do not measure tag completion.
Pydantic validates shape and types, not factual accuracy. Confidence scores are not calibrated probabilities.
This report contains only the current run; it does not establish that an LLM beats the baseline.
