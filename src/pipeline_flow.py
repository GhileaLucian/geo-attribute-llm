"""
Prefect workflow orchestration for geospatial attribute extraction and benchmarking.
Defines cached and retriable tasks for robust execution.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
from prefect import task, flow
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.models import RoadSegmentInput, ExtractionResult
from src.dataset_generator import load_ground_truth_dataset
from src.extractor import get_extractor
from src.evaluator import GeospatialEvaluator


@task(name="load-osm-ground-truth", retries=2, retry_delay_seconds=2)
def load_osm_ground_truth_task(data_path: Path) -> List[RoadSegmentInput]:
    """Loads OpenStreetMap ground-truth dataset strictly from JSON file."""
    dataset = load_ground_truth_dataset(data_path)
    print(f"Loaded {len(dataset)} verified road segments from {data_path.name}")
    return dataset


@task(name="extract-attributes-batch", retries=2, retry_delay_seconds=3)
def extract_attributes_batch_task(
    dataset: List[RoadSegmentInput],
    mode: str = "baseline"
) -> List[ExtractionResult]:
    """Runs batch attribute extraction using selected extractor (baseline, claude, openai)."""
    extractor = get_extractor(mode=mode)
    results: List[ExtractionResult] = []

    print(f"Beginning attribute extraction for {len(dataset)} segments using [{extractor.name}]...")
    for segment in dataset:
        t0 = time.time()
        extracted = extractor.extract_attributes(segment)
        latency_ms = (time.time() - t0) * 1000

        results.append(ExtractionResult(
            segment_id=segment.segment_id,
            extracted=extracted,
            expected=segment.expected_attributes,
            execution_time_ms=round(latency_ms, 2)
        ))

    print(f"Extraction completed for {len(results)} segments.")
    return results


@task(name="benchmark-and-evaluate")
def benchmark_and_evaluate_task(results: List[ExtractionResult], mode_name: str = "baseline") -> Dict[str, Any]:
    """Benchmarks predictions against ground-truth and classifies errors."""
    evaluator = GeospatialEvaluator()
    metrics = evaluator.evaluate_batch(results)
    metrics["extractor_mode"] = mode_name
    return metrics


@task(name="generate-visualizations")
def generate_visualizations_task(metrics: Dict[str, Any], output_path: Path) -> None:
    """Generates precision/recall bar chart and metrics plot."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    attr = metrics["attributes"]
    mode_name = metrics.get("extractor_mode", "baseline").upper()

    categories = ["Road Type", "Barrier", "Surface", "One-Way"]
    precision_vals = [
        attr["road_type"]["precision"] * 100,
        attr["barrier_present"]["precision"] * 100,
        attr["surface_type"]["precision"] * 100,
        attr["oneway"]["precision"] * 100
    ]
    recall_vals = [
        attr["road_type"]["recall"] * 100,
        attr["barrier_present"]["recall"] * 100,
        attr["surface_type"]["recall"] * 100,
        attr["oneway"]["recall"] * 100
    ]

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    x = range(len(categories))
    width = 0.35

    ax.bar([i - width/2 for i in x], precision_vals, width, label="Precision (%)", color="#0284c7")
    ax.bar([i + width/2 for i in x], recall_vals, width, label="Recall (%)", color="#0f766e")

    ax.set_ylabel("Score (%)", fontsize=10, fontweight="bold")
    ax.set_title(f"Attribute Extraction: Precision & Recall [{mode_name}]", fontsize=11, fontweight="bold", pad=12)
    ax.set_xticks(list(x))
    ax.set_xticklabels(categories, fontsize=9, fontweight="bold")
    ax.set_ylim(0, 110)
    ax.legend(frameon=True, loc="lower right")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    for i in x:
        ax.annotate(f"{precision_vals[i]:.1f}%", (i - width/2, precision_vals[i] + 2), ha='center', fontsize=8, fontweight="bold")
        ax.annotate(f"{recall_vals[i]:.1f}%", (i + width/2, recall_vals[i] + 2), ha='center', fontsize=8, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Chart saved to {output_path}")


@task(name="export-artifacts")
def export_artifacts_task(metrics: Dict[str, Any], reports_dir: Path) -> None:
    """Exports metrics JSON and Markdown summary report."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    evaluator = GeospatialEvaluator()
    md_content = evaluator.generate_markdown_report(metrics)

    with open(reports_dir / "evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    with open(reports_dir / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Reports successfully exported to {reports_dir}")


@flow(name="geospatial-attribute-qa-flow")
def run_geospatial_pipeline(
    data_dir: Path = Path("data"),
    reports_dir: Path = Path("reports"),
    mode: str = "baseline"
) -> Dict[str, Any]:
    """End-to-end Prefect pipeline coordinating dataset loading, extraction, and evaluation."""
    data_file = data_dir / "osm_ground_truth_cluj.json"
    dataset = load_osm_ground_truth_task(data_file)
    results = extract_attributes_batch_task(dataset, mode=mode)
    metrics = benchmark_and_evaluate_task(results, mode_name=mode)
    generate_visualizations_task(metrics, reports_dir / "evaluation_metrics_chart.png")
    export_artifacts_task(metrics, reports_dir)
    return metrics
