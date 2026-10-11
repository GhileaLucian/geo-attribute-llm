# Evidence benchmark

Mode: langchain; prompt: v5; split: test; n=40.
Exact match: 0.0%; failures: 0.0%.

OSM-derived controlled text extraction; synthetic hard scenarios; NOT independently verified map truth.

## Attribute scores

| Field | Precision | Recall | F1 | Known accuracy |
|---|---:|---:|---:|---:|
| road_type | 1.000 | 1.000 | 1.000 | 1.0 |
| speed_limit_kmh | 0.681 | 0.825 | 0.746 | 0.0 |
| surface | 0.226 | 0.475 | 0.306 | 0.0 |
| oneway | 0.810 | 0.900 | 0.853 | 0.0 |
| barrier_present | 0.000 | 0.000 | 0.000 | 0.0 |
| barrier_type | 0.010 | 0.100 | 0.018 | 0.0 |
| anomaly_flag | 1.000 | 1.000 | 1.000 | 1.0 |
| input_instruction_detected | 1.000 | 1.000 | 1.000 | 1.0 |

Error taxonomy: {"surface": 21, "barrier_present": 40, "barrier_type": 36, "speed_limit_kmh": 7, "oneway": 4}

Null/unknown support can inflate exact match. See per-class supports and raw responses.
Confidence is not calibrated. Hybrid guards are Python rules, not prompt improvements.
