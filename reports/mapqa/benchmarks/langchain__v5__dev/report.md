# Evidence benchmark

Mode: langchain; prompt: v5; split: dev; n=80.
Exact match: 2.5%; failures: 0.0%.

OSM-derived controlled text extraction; synthetic hard scenarios; NOT independently verified map truth.

## Attribute scores

| Field | Precision | Recall | F1 | Known accuracy |
|---|---:|---:|---:|---:|
| road_type | 1.000 | 1.000 | 1.000 | 1.0 |
| speed_limit_kmh | 0.584 | 0.713 | 0.603 | 0.041666666666666664 |
| surface | 0.631 | 0.500 | 0.357 | 0.047619047619047616 |
| oneway | 0.888 | 0.887 | 0.845 | 0.1 |
| barrier_present | 1.000 | 0.025 | 0.049 | 0.025 |
| barrier_type | 0.440 | 0.188 | 0.087 | 0.029850746268656716 |
| anomaly_flag | 1.000 | 1.000 | 1.000 | 1.0 |
| input_instruction_detected | 1.000 | 1.000 | 1.000 | 1.0 |

Error taxonomy: {"speed_limit_kmh": 23, "surface": 40, "oneway": 9, "barrier_present": 78, "barrier_type": 65}

Null/unknown support can inflate exact match. See per-class supports and raw responses.
Confidence is not calibrated. Hybrid guards are Python rules, not prompt improvements.
