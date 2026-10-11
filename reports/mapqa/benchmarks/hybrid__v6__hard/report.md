# Evidence benchmark

Mode: hybrid; prompt: v6; split: hard; n=15.
Exact match: 86.7%; failures: 6.7%.

OSM-derived controlled text extraction; synthetic hard scenarios; NOT independently verified map truth.

## Attribute scores

| Field | Precision | Recall | F1 | Known accuracy |
|---|---:|---:|---:|---:|
| road_type | 1.000 | 0.933 | 0.962 | 0.9285714285714286 |
| speed_limit_kmh | 1.000 | 0.933 | 0.965 | 1.0 |
| surface | 1.000 | 0.933 | 0.965 | 1.0 |
| oneway | 0.933 | 0.933 | 0.933 | 0.5 |
| barrier_present | 0.933 | 0.933 | 0.933 | 0.8 |
| barrier_type | 0.933 | 0.933 | 0.933 | 0.8 |
| anomaly_flag | 1.000 | 1.000 | 1.000 | 0.9333333333333333 |
| input_instruction_detected | 0.500 | 1.000 | 0.667 | 0.8666666666666667 |

Error taxonomy: {"input_instruction_detected": 1, "invalid_output": 1}

Null/unknown support can inflate exact match. See per-class supports and raw responses.
Confidence is not calibrated. Hybrid guards are Python rules, not prompt improvements.
