"""Metrics over labeled attempts, including failed and invalid outputs."""

from collections import Counter, defaultdict
from statistics import mean
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from src.models import SpatialErrorCategory, EVALUATION_FIELDS

ATTRIBUTE_NAMES = {
    "road_type": "road_type", "surface": "surface_type", "barrier_present": "barrier_present",
    "barrier_type": "barrier_type", "oneway": "oneway", "anomaly_flag": "anomaly_detection"
}


def label(value):
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return str(value).lower()
    return str(getattr(value, "value", value))


def classification_metrics(truth, prediction):
    if not truth:
        return {"count": 0, "accuracy": None, "precision": None, "recall": None, "f1_score": None,
                "macro_f1": None, "per_class": {}, "confusion_matrix": {"labels": [], "values": []}}
    labels = sorted(set(truth + prediction))
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, prediction, labels=labels, zero_division=0
    )
    per_class = {
        name: {"precision": float(p), "recall": float(r), "f1_score": float(f), "support": int(n)}
        for name, p, r, f, n in zip(labels, precision, recall, f1, support)
    }
    weighted = precision_recall_fscore_support(truth, prediction, average="weighted", zero_division=0)
    # Binary scores retain the positive-class convention; both classes are still reported.
    positive = per_class.get("true") if set(truth).issubset({"true", "false"}) else None
    present_labels = [name for name in labels if name in set(truth)]
    return {
        "count": len(truth), "accuracy": sum(t == p for t, p in zip(truth, prediction)) / len(truth),
        "precision": positive["precision"] if positive else float(weighted[0]),
        "recall": positive["recall"] if positive else float(weighted[1]),
        "f1_score": positive["f1_score"] if positive else float(weighted[2]),
        "macro_f1": mean(per_class[name]["f1_score"] for name in present_labels),
        "unknown_reference_count": truth.count("unknown"),
        "known_reference_accuracy": (
            sum(t == p for t, p in zip(truth, prediction) if t != "unknown") /
            sum(t != "unknown" for t in truth)
        ) if any(t != "unknown" for t in truth) else None,
        "per_class": per_class,
        "confusion_matrix": {"labels": labels, "values": (
            [[len(truth)]] if len(labels) == 1 else confusion_matrix(truth, prediction, labels=labels).tolist()
        )}
    }


def percentage(value):
    return "not evaluated" if value is None else f"{value * 100:.1f}%"


class GeospatialEvaluator:
    def evaluate_batch(self, results):
        if not results:
            raise ValueError("No results to evaluate")
        evaluated = [r for r in results if r.expected is not None]
        if not evaluated:
            raise ValueError("No reference labels to evaluate")
        truths, predictions = defaultdict(list), defaultdict(list)
        speed_pairs = []
        errors = Counter()
        for result in evaluated:
            actual = result.extracted if result.status == "success" else None
            result.error_categories = self._classify_errors(result.expected, actual, result.evaluation_fields, result.status)
            result.is_exact_match = actual is not None and all(
                getattr(result.expected, field) == getattr(actual, field) for field in result.evaluation_fields
            )
            errors.update(error.value for error in result.error_categories)
            for field, name in ATTRIBUTE_NAMES.items():
                if field in result.evaluation_fields:
                    truths[name].append(label(getattr(result.expected, field)))
                    predictions[name].append(label(getattr(actual, field)) if actual else "__failed__")
            if "speed_limit_kmh" in result.evaluation_fields:
                speed_pairs.append((
                    result.expected.speed_limit_kmh,
                    actual.speed_limit_kmh if actual else "__failed__"
                ))
        attributes = {name: classification_metrics(truths[name], predictions[name]) for name in ATTRIBUTE_NAMES.values()}
        known = [(t, p) for t, p in speed_pairs if t is not None]
        missing = [(t, p) for t, p in speed_pairs if t is None]
        attributes["speed_limit"] = {
            "count": len(speed_pairs),
            "exact_accuracy": sum(t == p for t, p in speed_pairs) / len(speed_pairs) if speed_pairs else None,
            "known_reference_count": len(known),
            "known_exact_accuracy": sum(t == p for t, p in known) / len(known) if known else None,
            "within_10kmh_accuracy": sum(isinstance(p, int) and abs(t - p) <= 10 for t, p in known) / len(known) if known else None,
            "missing_reference_count": len(missing),
            "predicted_when_reference_missing_count": sum(isinstance(p, int) for _, p in missing),
            "predicted_when_reference_missing_rate": sum(isinstance(p, int) for _, p in missing) / len(missing) if missing else None
        }
        failed = sum(r.status != "success" or r.extracted is None for r in results)
        invalid = sum(r.status == "invalid_output" for r in results)
        api_failed = sum(r.status == "api_error" for r in results)
        costs = [r.estimated_cost_usd for r in results]
        fresh_costs = [r.estimated_cost_usd for r in results if not r.cache_hit]
        return {
            "total_segments_attempted": len(results),
            "total_segments_evaluated": len(evaluated),
            "unlabeled_segments_excluded": len(results) - len(evaluated),
            "successful_outputs": len(results) - failed,
            "failed_outputs": failed, "failure_rate": failed / len(results),
            "invalid_outputs": invalid, "invalid_output_rate": invalid / len(results),
            "api_errors": api_failed, "api_error_rate": api_failed / len(results),
            "exact_segment_match_rate": sum(r.is_exact_match for r in evaluated) / len(evaluated),
            "attributes": attributes, "error_taxonomy_breakdown": dict(errors),
            "cache_hits": sum(r.cache_hit for r in results),
            "original_mean_latency_ms": mean(r.execution_time_ms for r in results),
            "token_usage": {
                key: sum(r.token_usage.get(key, 0) for r in results)
                for key in ["input_tokens", "output_tokens", "total_tokens"]
            },
            "token_usage_unavailable_count": sum(not r.token_usage for r in results),
            "estimated_original_api_cost_usd": sum(costs) if all(c is not None for c in costs) else None,
            "estimated_new_api_cost_usd": sum(fresh_costs) if all(c is not None for c in fresh_costs) else None,
            "cost_note": "Configured plain token-price estimate, not an invoice. Unknown cost is null.",
        }

    def _classify_errors(self, expected, actual, fields=None, status="success"):
        fields = set(fields or EVALUATION_FIELDS)
        if actual is None:
            return [SpatialErrorCategory.INVALID_OUTPUT if status == "invalid_output" else SpatialErrorCategory.API_ERROR]
        errors = []
        if "road_type" in fields and actual.road_type != expected.road_type:
            errors.append(SpatialErrorCategory.ROAD_CLASS_MISMATCH)
        if "speed_limit_kmh" in fields and actual.speed_limit_kmh != expected.speed_limit_kmh:
            if expected.speed_limit_kmh is None:
                errors.append(SpatialErrorCategory.SPEED_LIMIT_HALLUCINATION)
            elif actual.speed_limit_kmh is None:
                errors.append(SpatialErrorCategory.SPEED_LIMIT_MISSING)
            else:
                errors.append(SpatialErrorCategory.SPEED_LIMIT_MISMATCH)
        if "barrier_present" in fields and actual.barrier_present != expected.barrier_present:
            if expected.barrier_present is True and actual.barrier_present is not True:
                errors.append(SpatialErrorCategory.BARRIER_FALSE_NEGATIVE)
            elif expected.barrier_present is False and actual.barrier_present is True:
                errors.append(SpatialErrorCategory.BARRIER_FALSE_POSITIVE)
            else:
                errors.append(SpatialErrorCategory.BARRIER_PRESENCE_MISMATCH)
        if "barrier_type" in fields and actual.barrier_type != expected.barrier_type:
            errors.append(SpatialErrorCategory.BARRIER_TYPE_MISMATCH)
        if "surface" in fields and actual.surface != expected.surface:
            errors.append(SpatialErrorCategory.SURFACE_AMBIGUITY)
        if "oneway" in fields and actual.oneway != expected.oneway:
            errors.append(SpatialErrorCategory.ONEWAY_MISMATCH)
        if "anomaly_flag" in fields and actual.anomaly_flag != expected.anomaly_flag:
            errors.append(SpatialErrorCategory.ANOMALY_MISMATCH)
        return errors

    def generate_markdown_report(self, metrics):
        lines = [
            "# Geospatial extraction evaluation", "",
            f"Dataset: {metrics.get('dataset_file', 'unspecified')}",
            f"Source counts: {metrics.get('source_counts', {})}",
            f"Extractor: {metrics.get('extractor_mode')} / {metrics.get('model_name')} / {metrics.get('prompt_version')}",
            f"Run time (UTC): {metrics.get('run_at', 'not recorded')}", "",
            f"Attempts: {metrics['total_segments_attempted']}; labeled attempts: {metrics['total_segments_evaluated']}.",
            f"Exact match across each record's evaluation_fields: {percentage(metrics['exact_segment_match_rate'])}.",
            f"Invalid outputs: {metrics['invalid_outputs']}; API errors: {metrics['api_errors']}; all failures: {percentage(metrics['failure_rate'])}.",
            "Failed predictions stay in the denominators. Unlabeled records are excluded from accuracy.", "",
            "| Attribute | n | Precision | Recall | F1 | Accuracy |",
            "| --- | ---: | ---: | ---: | ---: | ---: |"
        ]
        for name, values in metrics["attributes"].items():
            if name == "speed_limit":
                lines.append(f"| speed (exact, including unknown) | {values['count']} | - | - | - | {percentage(values['exact_accuracy'])} |")
            else:
                lines.append(f"| {name} | {values['count']} | {percentage(values['precision'])} | {percentage(values['recall'])} | {percentage(values['f1_score'])} | {percentage(values['accuracy'])} |")
        speed = metrics["attributes"]["speed_limit"]
        lines += [
            "",
            f"Known speed labels: {speed['known_reference_count']}; exact accuracy on known labels: {percentage(speed['known_exact_accuracy'])}; within 10 km/h: {percentage(speed['within_10kmh_accuracy'])}.",
            f"Missing speed labels: {speed['missing_reference_count']}; numerical predictions without a recorded speed: {speed['predicted_when_reference_missing_count']}.",
            "A missing OSM speed label does not establish the real legal limit. The historical error name speed_limit_hallucination here means unsupported by the recorded reference.", "",
            "## Class support and confusion matrices", "",
            "Per-class precision, recall, F1, support and confusion matrices are in metrics_summary.json.",
            "Unknown matches can dominate a small dataset. Use known_reference_accuracy and class support when interpreting scores.",
        ]
        for name, values in metrics["attributes"].items():
            if "per_class" not in values or not values["per_class"]:
                continue
            lines += ["", f"### {name}", "", "| Class | Support | Precision | Recall | F1 |",
                      "| --- | ---: | ---: | ---: | ---: |"]
            for cls, data in values["per_class"].items():
                lines.append(f"| {cls} | {data['support']} | {percentage(data['precision'])} | {percentage(data['recall'])} | {percentage(data['f1_score'])} |")
        lines += ["", "## Error counts", "", "| Category | Count |", "| --- | ---: |"]
        lines += [f"| {key} | {value} |" for key, value in metrics["error_taxonomy_breakdown"].items()] or ["| none | 0 |"]
        lines += [
            "", "## Execution", "",
            f"Cache hits: {metrics['cache_hits']}. Cached responses retain the original latency and token usage.",
            f"Tokens: {metrics['token_usage']}. Usage unavailable for {metrics['token_usage_unavailable_count']} attempts (baseline has no API tokens).",
            f"Estimated original API cost (USD): {metrics['estimated_original_api_cost_usd']}.",
            f"Estimated new API cost (USD): {metrics['estimated_new_api_cost_usd']}.",
            metrics["cost_note"], "",
            "## Limits", "",
            "OSM tags are reference labels, not independent field verification. Way-level barriers omit barriers on nodes.",
            "Hand-written scenarios are fictional and reported separately from downloaded data.",
            "The old curated examples expose target tags and may overlap few-shot examples; their scores do not measure tag completion.",
            "Pydantic validates shape and types, not factual accuracy. Confidence scores are not calibrated probabilities.",
            "This report contains only the current run; it does not establish that an LLM beats the baseline.", ""
        ]
        return "\n".join(lines)
