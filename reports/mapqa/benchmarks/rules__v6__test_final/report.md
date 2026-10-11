# Evidence benchmark

Mode: rules; prompt: v6; split: test_final; n=40.
Exact match: 87.5%; failures: 0.0%.

OSM-derived controlled text extraction; synthetic hard scenarios; NOT independently verified map truth.

## Attribute scores

| Field | Precision | Recall | F1 | Known accuracy |
|---|---:|---:|---:|---:|
| road_type | 1.000 | 1.000 | 1.000 | 1.0 |
| speed_limit_kmh | 1.000 | 1.000 | 1.000 | N/A |
| surface | 0.904 | 0.950 | 0.926 | 0.8888888888888888 |
| oneway | 1.000 | 1.000 | 1.000 | 1.0 |
| barrier_present | 1.000 | 0.925 | 0.961 | 0.925 |
| barrier_type | 1.000 | 1.000 | 1.000 | 1.0 |
| anomaly_flag | 1.000 | 1.000 | 1.000 | 1.0 |
| input_instruction_detected | 1.000 | 1.000 | 1.000 | 1.0 |

Error taxonomy: {"barrier_present": 3, "surface": 2}

Null/unknown support can inflate exact match. See per-class supports and raw responses.
Confidence is not calibrated. Hybrid guards are Python rules, not prompt improvements.
