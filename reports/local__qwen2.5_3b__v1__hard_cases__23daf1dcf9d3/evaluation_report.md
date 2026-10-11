# Geospatial extraction evaluation

Dataset: hard_cases.json
Source counts: {'hand-written': 15}
Extractor: local / qwen2.5:3b / v1
Run time (UTC): 2026-10-11T17:47:05.107268+00:00

Attempts: 15; labeled attempts: 15.
Exact match across each record's evaluation_fields: 66.7%.
Invalid outputs: 0; API errors: 0; all failures: 0.0%.
Failed predictions stay in the denominators. Unlabeled records are excluded from accuracy.

| Attribute | n | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| road_type | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| surface_type | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| barrier_present | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| barrier_type | 15 | 100.0% | 100.0% | 100.0% | 100.0% |
| oneway | 15 | 87.1% | 93.3% | 90.1% | 93.3% |
| anomaly_detection | 15 | 50.0% | 50.0% | 50.0% | 86.7% |
| speed (exact, including unknown) | 15 | - | - | - | 86.7% |

Known speed labels: 3; exact accuracy on known labels: 100.0%; within 10 km/h: 100.0%.
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
| false | 1 | 100.0% | 100.0% | 100.0% |
| true | 1 | 0.0% | 0.0% | 0.0% |
| unknown | 13 | 92.9% | 100.0% | 96.3% |

### anomaly_detection

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| false | 13 | 92.3% | 92.3% | 92.3% |
| true | 2 | 50.0% | 50.0% | 50.0% |

## Error counts

| Category | Count |
| --- | ---: |
| oneway_mismatch | 1 |
| speed_limit_hallucination | 2 |
| anomaly_mismatch | 2 |

## Execution

Cache hits: 15. Cached responses retain the original latency and token usage.
Tokens: {'input_tokens': 15191, 'output_tokens': 1310, 'total_tokens': 16501}. Usage unavailable for 0 attempts (baseline has no API tokens).
Estimated original API cost (USD): 0.0.
Estimated new API cost (USD): 0.
Local inference: provider API cost is zero. Hardware, electricity and download costs are not included.

## Limits

OSM tags are reference labels, not independent field verification. Way-level barriers omit barriers on nodes.
Hand-written scenarios are fictional and reported separately from downloaded data.
The old curated examples expose target tags and may overlap few-shot examples; their scores do not measure tag completion.
Pydantic validates shape and types, not factual accuracy. Confidence scores are not calibrated probabilities.
This report contains only the current run; it does not establish that an LLM beats the baseline.
