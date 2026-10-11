"""Prefect tasks for saved predictions and geospatial evaluation."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import shutil
from pathlib import Path

from prefect import flow, task
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.dataset_generator import load_ground_truth_dataset
from src.evaluator import GeospatialEvaluator, percentage
from src.recording import extract_batch


@task(name="load-road-dataset", retries=2, retry_delay_seconds=2, persist_result=False)
def load_osm_ground_truth_task(data_path):
    dataset = load_ground_truth_dataset(data_path)
    print(f"Loaded {len(dataset)} labeled records from {data_path.name}")
    return dataset


@task(name="extract-attributes-batch", persist_result=False)
def extract_attributes_batch_task(dataset, mode, model_name, prompt_version, results_dir, cached_only=False, retry_failed=False):
    # Per-response disk cache prevents a partial batch failure from repeating all calls.
    return extract_batch(dataset, mode, model_name, prompt_version, results_dir, cached_only, retry_failed)


@task(name="benchmark-and-evaluate", persist_result=False)
def benchmark_and_evaluate_task(results):
    return GeospatialEvaluator().evaluate_batch(results)


def generate_visualizations(metrics, output_path):
    categories, precision, recall = [], [], []
    for name, values in metrics["attributes"].items():
        if values.get("precision") is not None:
            categories.append(name)
            precision.append(values["precision"] * 100)
            recall.append(values["recall"] * 100)
    fig, ax = plt.subplots(figsize=(9, 4), dpi=150)
    positions = range(len(categories))
    ax.bar([i - 0.18 for i in positions], precision, 0.36, label="Precision")
    ax.bar([i + 0.18 for i in positions], recall, 0.36, label="Recall")
    ax.set_xticks(list(positions), categories, rotation=20, ha="right")
    ax.set_ylim(0, 105)
    ax.set_ylabel("Percent")
    ax.set_title(f"{metrics['extractor_mode']} / {metrics['dataset_file']}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


@task(name="export-artifacts", persist_result=False)
def export_artifacts_task(metrics, results, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "evaluation_report.md").write_text(
        GeospatialEvaluator().generate_markdown_report(metrics), encoding="utf-8"
    )
    for filename, value in [
        ("metrics_summary.json", metrics),
        ("predictions.json", [result.model_dump(mode="json") for result in results])
    ]:
        (output_dir / filename).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    grouped = defaultdict(list)
    for result in results:
        for category in result.error_categories:
            if len(grouped[category.value]) < 3:
                grouped[category.value].append(result)
    lines = ["# Error examples from saved predictions", ""]
    for category, examples in grouped.items():
        lines += [f"## {category}", ""]
        for result in examples:
            case = {
                "segment_id": result.segment_id, "input": result.input_payload,
                "prediction": result.extracted.model_dump(mode="json") if result.extracted else None,
                "reference": result.expected.model_dump(mode="json"),
                "status": result.status, "error": result.error_message,
                "evaluation_fields": result.evaluation_fields
            }
            lines += ["```json", json.dumps(case, indent=2, ensure_ascii=False), "```", ""]
    if not grouped:
        lines += ["No discrepancies were recorded in this run.", ""]
    (output_dir / "error_examples.md").write_text("\n".join(lines), encoding="utf-8")
    generate_visualizations(metrics, output_dir / "evaluation_metrics_chart.png")
    # Keep the original top-level report paths as an explicit latest-run view.
    for filename in ("evaluation_report.md", "metrics_summary.json", "evaluation_metrics_chart.png"):
        shutil.copyfile(output_dir / filename, output_dir.parent / filename)


def report_directory(reports_dir, mode, model, version, dataset_file):
    # Dataset and implementation hash keep results from different revisions apart.
    from src.recording import cache_path
    dataset = load_ground_truth_dataset(dataset_file)
    cache_digest = cache_path(Path("."), mode, model, version, dataset[0]).parent.name
    digest = hashlib.sha256(dataset_file.read_bytes() + cache_digest.encode()).hexdigest()[:12]
    model_slug = "".join(char if char.isalnum() or char in "-_." else "_" for char in model)
    return Path(reports_dir) / f"{mode}__{model_slug}__{version}__{dataset_file.stem}__{digest}"


def update_comparison(reports_dir):
    summaries = []
    for path in sorted(Path(reports_dir).glob("*/metrics_summary.json")):
        metrics = json.loads(path.read_text(encoding="utf-8"))
        summaries.append((path.parent.name, metrics))
    lines = [
        "# Saved runs", "",
        "Recorded runs appear below, including failed API attempts. Compare rows only when dataset SHA-256 and evaluation fields match.",
        "An all-unknown prediction can score well if reference tags are often missing; inspect known-label metrics.", "",
        "| Run | Data | Mode / model / prompt | n | Exact | Speed known exact | Surface accuracy | Failure rate |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"
    ]
    for folder, metrics in summaries:
        attr = metrics["attributes"]
        lines.append(
            f"| [{folder}]({folder}/evaluation_report.md) | {metrics['dataset_file']} | "
            f"{metrics['extractor_mode']} / {metrics['model_name']} / {metrics['prompt_version']} | "
            f"{metrics['total_segments_evaluated']} | {percentage(metrics['exact_segment_match_rate'])} | "
            f"{percentage(attr['speed_limit']['known_exact_accuracy'])} | "
            f"{percentage(attr['surface_type']['accuracy'])} | {percentage(metrics['failure_rate'])} |"
        )
    (Path(reports_dir) / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


@flow(name="geospatial-attribute-qa-flow", persist_result=False)
def run_geospatial_pipeline(
    data_dir=Path("data"), reports_dir=Path("reports"), mode="baseline",
    dataset_file=None, model_name="rule_based_baseline", prompt_version="v1",
    results_dir=Path("results"), cached_only=False, retry_failed=False
):
    data_file = Path(dataset_file) if dataset_file else Path(data_dir) / "osm_dev.json"
    dataset = load_osm_ground_truth_task(data_file)
    results = extract_attributes_batch_task(
        dataset, mode, model_name, prompt_version, results_dir, cached_only, retry_failed
    )
    metrics = benchmark_and_evaluate_task(results)
    output_dir = report_directory(reports_dir, mode, model_name, prompt_version, data_file)
    metrics.update(
        extractor_mode=mode, model_name=model_name, prompt_version=prompt_version,
        dataset_file=data_file.name,
        dataset_sha256=hashlib.sha256(data_file.read_bytes()).hexdigest(),
        source_counts=dict(Counter(segment.source for segment in dataset)),
        evaluation_field_sets=[list(fields) for fields in sorted({tuple(s.evaluation_fields) for s in dataset})],
        run_at=datetime.now(timezone.utc).isoformat(), report_directory=str(output_dir)
    )
    if mode == "local":
        metrics["cost_note"] = "Local inference: provider API cost is zero. Hardware, electricity and download costs are not included."
    export_artifacts_task(metrics, results, output_dir)
    update_comparison(reports_dir)
    return metrics
