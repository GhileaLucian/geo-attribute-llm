# Geospatial extraction evaluation

Dataset: hard_cases.json
Source counts: {'hand-written': 15}
Extractor: baseline / rule_based_baseline / v1
Run time (UTC): 2026-10-11T17:39:51.485061+00:00

Attempts: 15; labeled attempts: 15.
Exact match across each record's evaluation_fields: 60.0%.
Invalid outputs: 0; API errors: 0; all failures: 0.0%.
Failed predictions stay in the denominators. Unlabeled records are excluded from accuracy.

| Attribute | n | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| road_type | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| surface_type | 15 | 87.1% | 93.3% | 90.1% | 93.3% |
| barrier_present | 15 | 84.6% | 80.0% | 75.3% | 80.0% |
| barrier_type | 15 | 64.6% | 80.0% | 71.3% | 80.0% |
| oneway | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| anomaly_detection | 15 | 100.0% | 50.0% | 66.7% | 93.3% |
| speed (exact, including unknown) | 15 | - | - | - | 93.3% |

Known speed labels: 3; exact accuracy on known labels: 66.7%; within 10 km/h: 66.7%.
Missing speed labels: 12; numerical predictions without a recorded speed: 0.
A missing OSM speed label does not establish the real legal limit. The historical error name speed_limit_hallucination here means unsupported by the recorded reference.

## Class support and confusion matrices

Per-class precision, recall, F1, support and confusion matrices are in metrics_summary.json.
Unknown matches can dominate a small dataset. Use known_reference_accuracy and class support when interpreting scores.

### road_type

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| pedestrian | 1 | 100.0% | 100.0% | 100.0% |
| primary | 1 | 100.0% | 100.0% | 100.0% |
| residential | 5 | 100.0% | 100.0% | 100.0% |
| secondary | 1 | 100.0% | 100.0% | 100.0% |
| service | 4 | 100.0% | 100.0% | 100.0% |
| track | 2 | 100.0% | 100.0% | 100.0% |
| unknown | 1 | 100.0% | 100.0% | 100.0% |

### surface_type

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| gravel | 1 | 0.0% | 0.0% | 0.0% |
| unknown | 14 | 93.3% | 100.0% | 96.6% |

### barrier_present

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| false | 1 | 100.0% | 100.0% | 100.0% |
| true | 4 | 100.0% | 25.0% | 40.0% |
| unknown | 10 | 76.9% | 100.0% | 87.0% |

### barrier_type

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| bollard | 1 | 0.0% | 0.0% | 0.0% |
| gate | 1 | 0.0% | 0.0% | 0.0% |
| guard_rail | 1 | 100.0% | 100.0% | 100.0% |
| lift_gate | 1 | 0.0% | 0.0% | 0.0% |
| none | 1 | 100.0% | 100.0% | 100.0% |
| unknown | 10 | 76.9% | 100.0% | 87.0% |

### oneway

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| false | 1 | 100.0% | 100.0% | 100.0% |
| true | 1 | 100.0% | 100.0% | 100.0% |
| unknown | 13 | 100.0% | 100.0% | 100.0% |

### anomaly_detection

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| false | 13 | 92.9% | 100.0% | 96.3% |
| true | 2 | 100.0% | 50.0% | 66.7% |

## Error counts

| Category | Count |
| --- | ---: |
| barrier_false_negative | 3 |
| barrier_type_mismatch | 3 |
| speed_limit_missing | 1 |
| anomaly_mismatch | 1 |
| surface_ambiguity | 1 |

## Execution

Cache hits: 0. Cached responses retain the original latency and token usage.
Tokens: {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}. Usage unavailable for 15 attempts (baseline has no API tokens).
Estimated original API cost (USD): 0.0.
Estimated new API cost (USD): 0.0.
Configured plain token-price estimate, not an invoice. Unknown cost is null.

## Limits

OSM tags are reference labels, not independent field verification. Way-level barriers omit barriers on nodes.
Hand-written scenarios are fictional and reported separately from downloaded data.
The old curated examples expose target tags and may overlap few-shot examples; their scores do not measure tag completion.
Pydantic validates shape and types, not factual accuracy. Confidence scores are not calibrated probabilities.
This report contains only the current run; it does not establish that an LLM beats the baseline.
