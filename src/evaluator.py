"""
Evaluation engine for geospatial prompt outputs.
Computes ground truth precision, recall, F1 metrics, and categorizes errors
according to a domain-specific spatial error taxonomy.
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
import pandas as pd
from src.models import (
    ExtractionResult,
    RoadAttributes,
    SpatialErrorCategory
)


class GeospatialEvaluator:
    """Evaluates extraction results against ground-truth and analyzes error taxonomies."""

    def __init__(self):
        pass

    def evaluate_batch(self, results: List[ExtractionResult]) -> Dict[str, Any]:
        """Runs comprehensive benchmark on the extracted batch."""
        total = len(results)
        if total == 0:
            return {"error": "No results to evaluate"}

        # Collect ground truth vs prediction lists
        y_true_road = []
        y_pred_road = []
        y_true_speed = []
        y_pred_speed = []
        y_true_barrier = []
        y_pred_barrier = []
        y_true_surface = []
        y_pred_surface = []
        y_true_oneway = []
        y_pred_oneway = []
        y_true_anomaly = []
        y_pred_anomaly = []

        error_taxonomy_counts: Dict[str, int] = defaultdict(int)

        for res in results:
            if not res.expected:
                continue

            exp = res.expected
            act = res.extracted

            y_true_road.append(exp.road_type.value)
            y_pred_road.append(act.road_type.value)

            y_true_speed.append(exp.speed_limit_kmh or 0)
            y_pred_speed.append(act.speed_limit_kmh or 0)

            y_true_barrier.append(exp.barrier_present)
            y_pred_barrier.append(act.barrier_present)

            y_true_surface.append(exp.surface.value)
            y_pred_surface.append(act.surface.value)

            y_true_oneway.append(exp.oneway)
            y_pred_oneway.append(act.oneway)

            y_true_anomaly.append(exp.anomaly_flag)
            y_pred_anomaly.append(act.anomaly_flag)

            # Error Taxonomy Classification
            assigned_errors = self._classify_errors(exp, act)
            res.error_categories = assigned_errors
            res.is_exact_match = len(assigned_errors) == 0

            for err in assigned_errors:
                error_taxonomy_counts[err.value] += 1

        # Calculate metrics using scikit-learn
        road_prec, road_rec, road_f1, _ = precision_recall_fscore_support(y_true_road, y_pred_road, average="weighted", zero_division=0)
        barrier_prec, barrier_rec, barrier_f1, _ = precision_recall_fscore_support(y_true_barrier, y_pred_barrier, average="binary", zero_division=0)
        surface_prec, surface_rec, surface_f1, _ = precision_recall_fscore_support(y_true_surface, y_pred_surface, average="weighted", zero_division=0)
        oneway_prec, oneway_rec, oneway_f1, _ = precision_recall_fscore_support(y_true_oneway, y_pred_oneway, average="binary", zero_division=0)

        # Speed limit exact accuracy and tolerance (+- 10 km/h)
        speed_exact = accuracy_score(y_true_speed, y_pred_speed)
        speed_tolerant = sum(abs(t - p) <= 10 for t, p in zip(y_true_speed, y_pred_speed)) / total

        # Anomaly detection accuracy
        anomaly_acc = accuracy_score(y_true_anomaly, y_pred_anomaly)

        metrics = {
            "total_segments_evaluated": total,
            "exact_segment_match_rate": sum(1 for r in results if r.is_exact_match) / total,
            "attributes": {
                "road_type": {
                    "precision": round(float(road_prec), 4),
                    "recall": round(float(road_rec), 4),
                    "f1_score": round(float(road_f1), 4),
                    "accuracy": round(float(accuracy_score(y_true_road, y_pred_road)), 4)
                },
                "speed_limit": {
                    "exact_accuracy": round(float(speed_exact), 4),
                    "within_10kmh_accuracy": round(float(speed_tolerant), 4)
                },
                "barrier_present": {
                    "precision": round(float(barrier_prec), 4),
                    "recall": round(float(barrier_rec), 4),
                    "f1_score": round(float(barrier_f1), 4)
                },
                "surface_type": {
                    "precision": round(float(surface_prec), 4),
                    "recall": round(float(surface_rec), 4),
                    "f1_score": round(float(surface_f1), 4)
                },
                "oneway": {
                    "precision": round(float(oneway_prec), 4),
                    "recall": round(float(oneway_rec), 4),
                    "f1_score": round(float(oneway_f1), 4)
                },
                "anomaly_detection": {
                    "accuracy": round(float(anomaly_acc), 4)
                }
            },
            "error_taxonomy_breakdown": dict(error_taxonomy_counts)
        }
        return metrics

    def _classify_errors(self, expected: RoadAttributes, actual: RoadAttributes) -> List[SpatialErrorCategory]:
        """Maps differences to domain-specific error taxonomies."""
        errors: List[SpatialErrorCategory] = []

        if actual.road_type != expected.road_type:
            errors.append(SpatialErrorCategory.ROAD_CLASS_MISMATCH)

        if expected.speed_limit_kmh and actual.speed_limit_kmh:
            if abs(actual.speed_limit_kmh - expected.speed_limit_kmh) > 10:
                errors.append(SpatialErrorCategory.SPEED_LIMIT_HALLUCINATION)

        if not expected.barrier_present and actual.barrier_present:
            errors.append(SpatialErrorCategory.BARRIER_FALSE_POSITIVE)
        elif expected.barrier_present and not actual.barrier_present:
            errors.append(SpatialErrorCategory.BARRIER_FALSE_NEGATIVE)

        if actual.surface != expected.surface:
            # Check if acceptable equivalence (e.g. paved vs asphalt)
            if not ({actual.surface.value, expected.surface.value}.issubset({"paved", "asphalt"})):
                errors.append(SpatialErrorCategory.SURFACE_AMBIGUITY)

        return errors

    def generate_markdown_report(self, metrics: Dict[str, Any]) -> str:
        """Renders an executive evaluation report in GitHub Markdown."""
        attr = metrics["attributes"]
        errs = metrics["error_taxonomy_breakdown"]
        total = metrics["total_segments_evaluated"]
        exact_rate = metrics["exact_segment_match_rate"] * 100

        err_rows = "\n".join([f"| `{k}` | {v} | {v/total*100:.1f}% |" for k, v in errs.items()]) if errs else "| `none` | 0 | 0.0% |"

        return f"""# 🗺️ Geospatial Prompt Evaluation & Quality Control Report
**Dataset:** OpenStreetMap Cluj-Napoca & Transylvania Ground-Truth Benchmark  
**Total Evaluated Segments:** {total}  
**Overall Exact Segment Match Rate:** {exact_rate:.1f}%  

---

## 1. Quantitative Performance per Road Attribute

| Road Attribute | Precision | Recall | F1-Score | Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| **Road Classification (`road_type`)** | **{attr['road_type']['precision']*100:.1f}%** | **{attr['road_type']['recall']*100:.1f}%** | **{attr['road_type']['f1_score']*100:.1f}%** | {attr['road_type']['accuracy']*100:.1f}% |
| **Speed Limit (`speed_limit_kmh`)** | - | - | - | **{attr['speed_limit']['within_10kmh_accuracy']*100:.1f}%** (±10km/h) |
| **Physical Barrier (`barrier_present`)** | **{attr['barrier_present']['precision']*100:.1f}%** | **{attr['barrier_present']['recall']*100:.1f}%** | **{attr['barrier_present']['f1_score']*100:.1f}%** | - |
| **Pavement Surface (`surface`)** | **{attr['surface_type']['precision']*100:.1f}%** | **{attr['surface_type']['recall']*100:.1f}%** | **{attr['surface_type']['f1_score']*100:.1f}%** | - |
| **One-Way Directionality (`oneway`)** | **{attr['oneway']['precision']*100:.1f}%** | **{attr['oneway']['recall']*100:.1f}%** | **{attr['oneway']['f1_score']*100:.1f}%** | - |
| **Quality Anomaly Detection** | - | - | - | **{attr['anomaly_detection']['accuracy']*100:.1f}%** |

---

## 2. Spatial Error Taxonomy Breakdown

The pipeline categorizes prediction discrepancies into structured error taxonomies to guide prompt iteration:

| Error Category | Occurrences | % of Total Segments |
| :--- | :---: | :---: |
{err_rows}

---

## 3. Engineering Insights & Prompt Iteration Takeaways

1. **Structured Output Resilience:** Enforcing Pydantic schemas eliminates formatting variance and guarantees valid JSON down the pipeline.
2. **Contextual Speed Limit Inference:** Territorial defaults (e.g. Romanian urban statutory 50 km/h) effectively fill metadata gaps when explicit `maxspeed` tags are missing.
3. **Barrier Disambiguation:** Differentiating between vehicular access bollards, property gates, and crash guardrails requires few-shot examples highlighting tag combinations (e.g. `barrier=bollard` vs `barrier=guard_rail`).
"""
