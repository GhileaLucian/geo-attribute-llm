# Geospatial extraction evaluation

Dataset: hard_cases.json
Source counts: {'hand-written': 15}
Extractor: local / qwen2.5:3b / v3
Run time (UTC): 2026-10-11T17:53:50.425131+00:00

Attempts: 15; labeled attempts: 15.
Exact match across each record's evaluation_fields: 60.0%.
Invalid outputs: 0; API errors: 0; all failures: 0.0%.
Failed predictions stay in the denominators. Unlabeled records are excluded from accuracy.

| Attribute | n | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| road_type | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| surface_type | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| barrier_present | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| barrier_type | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| oneway | 15 | 75.1% | 86.7% | 80.5% | 86.7% |
| anomaly_detection | 15 | 0.0% | 0.0% | 0.0% | 80.0% |
| speed (exact, including unknown) | 15 | - | - | - | 80.0% |

Known speed labels: 3; exact accuracy on known labels: 66.7%; within 10 km/h: 66.7%.
Missing speed labels: 12; numerical predictions without a recorded speed: 2.
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
| gravel | 1 | 100.0% | 100.0% | 100.0% |
| unknown | 14 | 100.0% | 100.0% | 100.0% |

### barrier_present

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| false | 1 | 100.0% | 100.0% | 100.0% |
| true | 4 | 100.0% | 100.0% | 100.0% |
| unknown | 10 | 100.0% | 100.0% | 100.0% |

### barrier_type

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| bollard | 1 | 100.0% | 100.0% | 100.0% |
| gate | 1 | 100.0% | 100.0% | 100.0% |
| guard_rail | 1 | 100.0% | 100.0% | 100.0% |
| lift_gate | 1 | 100.0% | 100.0% | 100.0% |
| none | 1 | 100.0% | 100.0% | 100.0% |
| unknown | 10 | 100.0% | 100.0% | 100.0% |

### oneway

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| false | 1 | 0.0% | 0.0% | 0.0% |
| true | 1 | 0.0% | 0.0% | 0.0% |
| unknown | 13 | 86.7% | 100.0% | 92.9% |

### anomaly_detection

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| false | 13 | 85.7% | 92.3% | 88.9% |
| true | 2 | 0.0% | 0.0% | 0.0% |

## Error counts

| Category | Count |
| --- | ---: |
| speed_limit_mismatch | 1 |
| anomaly_mismatch | 3 |
| oneway_mismatch | 2 |
| speed_limit_hallucination | 2 |

## Execution

Cache hits: 0. Cached responses retain the original latency and token usage.
Tokens: {'input_tokens': 16166, 'output_tokens': 1359, 'total_tokens': 17525}. Usage unavailable for 0 attempts (baseline has no API tokens).
Estimated original API cost (USD): 0.0.
Estimated new API cost (USD): 0.0.
Local inference: provider API cost is zero. Hardware, electricity and download costs are not included.

## Limits

OSM tags are reference labels, not independent field verification. Way-level barriers omit barriers on nodes.
Hand-written scenarios are fictional and reported separately from downloaded data.
The old curated examples expose target tags and may overlap few-shot examples; their scores do not measure tag completion.
Pydantic validates shape and types, not factual accuracy. Confidence scores are not calibrated probabilities.
This report contains only the current run; it does not establish that an LLM beats the baseline.
