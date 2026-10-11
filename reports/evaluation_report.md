# Geospatial Prompt Evaluation & Quality Control Report
**Dataset:** OpenStreetMap Cluj-Napoca & Transylvania Ground-Truth Benchmark  
**Total Evaluated Segments:** 30  
**Overall Exact Segment Match Rate:** 100.0%  

---

## 1. Quantitative Performance per Road Attribute

| Road Attribute | Precision | Recall | F1-Score | Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| **Road Classification (`road_type`)** | **100.0%** | **100.0%** | **100.0%** | 100.0% |
| **Speed Limit (`speed_limit_kmh`)** | - | - | - | **100.0%** (±10km/h) |
| **Physical Barrier (`barrier_present`)** | **100.0%** | **100.0%** | **100.0%** | - |
| **Pavement Surface (`surface`)** | **100.0%** | **100.0%** | **100.0%** | - |
| **One-Way Directionality (`oneway`)** | **100.0%** | **100.0%** | **100.0%** | - |
| **Quality Anomaly Detection** | - | - | - | **100.0%** |

---

## 2. Spatial Error Taxonomy Breakdown

The pipeline categorizes prediction discrepancies into structured error taxonomies to guide prompt iteration:

| Error Category | Occurrences | % of Total Segments |
| :--- | :---: | :---: |
| `none` | 0 | 0.0% |

---

## 3. Engineering Insights & Prompt Iteration Takeaways

1. **Structured Output Resilience:** Enforcing Pydantic schemas eliminates formatting variance and guarantees valid JSON down the pipeline.
2. **Contextual Speed Limit Inference:** Territorial defaults (e.g. Romanian urban statutory 50 km/h) effectively fill metadata gaps when explicit `maxspeed` tags are missing.
3. **Barrier Disambiguation:** Differentiating between vehicular access bollards, property gates, and crash guardrails requires few-shot examples highlighting tag combinations (e.g. `barrier=bollard` vs `barrier=guard_rail`).
