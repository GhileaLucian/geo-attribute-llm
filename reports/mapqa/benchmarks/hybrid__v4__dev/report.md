# Evidence benchmark

Mode: hybrid; prompt: v4; split: dev; n=80.
Exact match: 0.0%; failures: 0.0%.

OSM-derived controlled text extraction; synthetic hard scenarios; NOT independently verified map truth.

## Attribute scores

| Field | Precision | Recall | F1 | Known accuracy |
|---|---:|---:|---:|---:|
| road_type | 1.000 | 1.000 | 1.000 | 1.0 |
| speed_limit_kmh | 0.490 | 0.700 | 0.576 | 0.0 |
| surface | 0.226 | 0.475 | 0.306 | 0.0 |
| oneway | 0.766 | 0.875 | 0.817 | 0.0 |
| barrier_present | 0.000 | 0.000 | 0.000 | 0.0 |
| barrier_type | 0.026 | 0.163 | 0.045 | 0.0 |
| anomaly_flag | 1.000 | 1.000 | 1.000 | 1.0 |
| input_instruction_detected | 1.000 | 1.000 | 1.000 | 1.0 |

Error taxonomy: {"speed_limit_kmh": 24, "surface": 42, "oneway": 10, "barrier_present": 80, "barrier_type": 67}

Null/unknown support can inflate exact match. See per-class supports and raw responses.
Confidence is not calibrated. Hybrid guards are Python rules, not prompt improvements.
