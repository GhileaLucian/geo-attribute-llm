# Evidence benchmark

Mode: hybrid; prompt: v4; split: hard; n=15.
Exact match: 66.7%; failures: 0.0%.

OSM-derived controlled text extraction; synthetic hard scenarios; NOT independently verified map truth.

## Attribute scores

| Field | Precision | Recall | F1 | Known accuracy |
|---|---:|---:|---:|---:|
| road_type | 1.000 | 1.000 | 1.000 | 1.0 |
| speed_limit_kmh | 0.938 | 0.933 | 0.924 | 0.6666666666666666 |
| surface | 0.933 | 0.933 | 0.933 | 0.0 |
| oneway | 1.000 | 1.000 | 1.000 | 1.0 |
| barrier_present | 0.846 | 0.800 | 0.753 | 0.4 |
| barrier_type | 0.646 | 0.800 | 0.713 | 0.4 |
| anomaly_flag | 1.000 | 1.000 | 1.000 | 1.0 |
| input_instruction_detected | 1.000 | 1.000 | 1.000 | 1.0 |

Error taxonomy: {"barrier_present": 3, "barrier_type": 3, "speed_limit_kmh": 1, "surface": 1}

Null/unknown support can inflate exact match. See per-class supports and raw responses.
Confidence is not calibrated. Hybrid guards are Python rules, not prompt improvements.
