# Geospatial extraction evaluation

Dataset: osm_dev.json
Source counts: {'OpenStreetMap/Overpass': 40}
Extractor: local / qwen2.5:3b / v1
Run time (UTC): 2026-10-11T17:46:38.927458+00:00

Attempts: 40; labeled attempts: 40.
Exact match across each record's evaluation_fields: 22.5%.
Invalid outputs: 0; API errors: 0; all failures: 0.0%.
Failed predictions stay in the denominators. Unlabeled records are excluded from accuracy.

| Attribute | n | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| road_type | 0 | not evaluated | not evaluated | not evaluated | not evaluated |
| surface_type | 40 | 11.8% | 30.0% | 17.0% | 30.0% |
| barrier_present | 40 | 100.0% | 92.5% | 96.1% | 92.5% |
| barrier_type | 40 | 100.0% | 95.0% | 97.4% | 95.0% |
| oneway | 40 | 26.9% | 50.0% | 35.0% | 50.0% |
| anomaly_detection | 0 | not evaluated | not evaluated | not evaluated | not evaluated |
| speed (exact, including unknown) | 40 | - | - | - | 82.5% |

Known speed labels: 6; exact accuracy on known labels: 0.0%; within 10 km/h: 0.0%.
Missing speed labels: 34; numerical predictions without a recorded speed: 1.
A missing OSM speed label does not establish the real legal limit. The historical error name speed_limit_hallucination here means unsupported by the recorded reference.

## Class support and confusion matrices

Per-class precision, recall, F1, support and confusion matrices are in metrics_summary.json.
Unknown matches can dominate a small dataset. Use known_reference_accuracy and class support when interpreting scores.

### surface_type

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| asphalt | 22 | 0.0% | 0.0% | 0.0% |
| concrete | 1 | 0.0% | 0.0% | 0.0% |
| dirt | 2 | 0.0% | 0.0% | 0.0% |
| ground | 1 | 0.0% | 0.0% | 0.0% |
| paved | 0 | 0.0% | 0.0% | 0.0% |
| paving_stones | 1 | 0.0% | 0.0% | 0.0% |
| unknown | 13 | 36.4% | 92.3% | 52.2% |

### barrier_present

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| true | 0 | 0.0% | 0.0% | 0.0% |
| unknown | 40 | 100.0% | 92.5% | 96.1% |

### barrier_type

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| bollard | 0 | 0.0% | 0.0% | 0.0% |
| guard_rail | 0 | 0.0% | 0.0% | 0.0% |
| unknown | 40 | 100.0% | 95.0% | 97.4% |

### oneway

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| false | 2 | 0.0% | 0.0% | 0.0% |
| true | 17 | 0.0% | 0.0% | 0.0% |
| unknown | 21 | 51.3% | 95.2% | 66.7% |

## Error counts

| Category | Count |
| --- | ---: |
| speed_limit_missing | 6 |
| surface_ambiguity | 28 |
| oneway_mismatch | 20 |
| barrier_presence_mismatch | 3 |
| barrier_type_mismatch | 2 |
| speed_limit_hallucination | 1 |

## Execution

Cache hits: 40. Cached responses retain the original latency and token usage.
Tokens: {'input_tokens': 41856, 'output_tokens': 3564, 'total_tokens': 45420}. Usage unavailable for 0 attempts (baseline has no API tokens).
Estimated original API cost (USD): 0.0.
Estimated new API cost (USD): 0.
Local inference: provider API cost is zero. Hardware, electricity and download costs are not included.

## Limits

OSM tags are reference labels, not independent field verification. Way-level barriers omit barriers on nodes.
Hand-written scenarios are fictional and reported separately from downloaded data.
The old curated examples expose target tags and may overlap few-shot examples; their scores do not measure tag completion.
Pydantic validates shape and types, not factual accuracy. Confidence scores are not calibrated probabilities.
This report contains only the current run; it does not establish that an LLM beats the baseline.
