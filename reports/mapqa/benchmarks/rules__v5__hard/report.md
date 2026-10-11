# Evidence benchmark

Mode: rules; prompt: v5; split: hard; n=15.
Exact match: 100.0%; failures: 0.0%.

OSM-derived controlled text extraction; synthetic hard scenarios; NOT independently verified map truth.

## Attribute scores

| Field | Precision | Recall | F1 | Known accuracy |
|---|---:|---:|---:|---:|
| road_type | 1.000 | 1.000 | 1.000 | 1.0 |
| speed_limit_kmh | 1.000 | 1.000 | 1.000 | 1.0 |
| surface | 1.000 | 1.000 | 1.000 | 1.0 |
| oneway | 1.000 | 1.000 | 1.000 | 1.0 |
| barrier_present | 1.000 | 1.000 | 1.000 | 1.0 |
| barrier_type | 1.000 | 1.000 | 1.000 | 1.0 |
| anomaly_flag | 1.000 | 1.000 | 1.000 | 1.0 |
| input_instruction_detected | 1.000 | 1.000 | 1.000 | 1.0 |

Error taxonomy: {}

Null/unknown support can inflate exact match. See per-class supports and raw responses.
Confidence is not calibrated. Hybrid guards are Python rules, not prompt improvements.
