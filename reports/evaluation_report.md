# 🗺️ Geospatial Prompt Evaluation & Quality Control Report
**Dataset:** OpenStreetMap Cluj-Napoca & Transylvania Ground-Truth Benchmark  
**Total Evaluated Segments:** 50  
**Overall Exact Segment Match Rate:** 94.0%  

---

## 1. Quantitative Performance per Road Attribute

| Road Attribute | Precision | Recall | F1-Score | Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| **Road Classification (`road_type`)** | **98.2%** | **98.0%** | **98.0%** | 98.0% |
| **Speed Limit (`speed_limit_kmh`)** | - | - | - | **96.0%** (±10km/h) |
| **Physical Barrier (`barrier_present`)** | **100.0%** | **100.0%** | **100.0%** | - |
| **Pavement Surface (`surface`)** | **96.4%** | **98.0%** | **97.1%** | - |
| **One-Way Directionality (`oneway`)** | **100.0%** | **100.0%** | **100.0%** | - |
| **Quality Anomaly Detection** | - | - | - | **100.0%** |

---

## 2. Spatial Error Taxonomy Breakdown

The pipeline categorizes prediction discrepancies into structured error taxonomies to guide prompt iteration:

| Error Category | Occurrences | % of Total Segments |
| :--- | :---: | :---: |
| `road_class_mismatch` | 1 | 2.0% |
| `speed_limit_hallucination` | 2 | 4.0% |
| `surface_ambiguity` | 1 | 2.0% |

---

## 3. Engineering Insights & Prompt Iteration Takeaways

1. **Structured Output Resilience:** Enforcing Pydantic schemas eliminates formatting variance and guarantees valid JSON down the pipeline.
2. **Contextual Speed Limit Inference:** Territorial defaults (e.g. Romanian urban statutory 50 km/h) effectively fill metadata gaps when explicit `maxspeed` tags are missing.
3. **Barrier Disambiguation:** Differentiating between vehicular access bollards, property gates, and crash guardrails requires few-shot examples highlighting tag combinations (e.g. `barrier=bollard` vs `barrier=guard_rail`).
