# Evidence benchmark

Mode: langchain; prompt: v4; split: hard; n=15.
Exact match: 26.7%; failures: 0.0%.

OSM-derived controlled text extraction; synthetic hard scenarios; NOT independently verified map truth.

## Attribute scores

| Field | Precision | Recall | F1 | Known accuracy |
|---|---:|---:|---:|---:|
| road_type | 1.000 | 1.000 | 1.000 | 1.0 |
| speed_limit_kmh | 0.629 | 0.733 | 0.677 | 0.0 |
| surface | 0.933 | 0.933 | 0.933 | 0.0 |
| oneway | 0.751 | 0.867 | 0.805 | 0.0 |
| barrier_present | 0.444 | 0.667 | 0.533 | 0.0 |
| barrier_type | 0.444 | 0.667 | 0.533 | 0.0 |
| anomaly_flag | 1.000 | 0.500 | 0.667 | 0.9333333333333333 |
| input_instruction_detected | 1.000 | 1.000 | 1.000 | 1.0 |

Error taxonomy: {"barrier_present": 5, "barrier_type": 5, "speed_limit_kmh": 4, "oneway": 2, "surface": 1, "anomaly_flag": 1}

Null/unknown support can inflate exact match. See per-class supports and raw responses.
Confidence is not calibrated. Hybrid guards are Python rules, not prompt improvements.
