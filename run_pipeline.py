"""Run saved-data extraction. Defaults to the development set, never the hold-out."""

import argparse
import os
from pathlib import Path
import sys
from src.config import PROJECT_ROOT, load_configuration

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def main():
    load_configuration()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["baseline", "claude", "openai"], default="baseline")
    parser.add_argument("--split", choices=["dev", "test", "hard", "legacy"], default="dev")
    parser.add_argument("--dataset", type=Path, help="An explicit dataset file overrides --split")
    parser.add_argument("--data-dir", type=Path, default=PROJECT_ROOT / "data")
    parser.add_argument("--reports-dir", type=Path, default=PROJECT_ROOT / "reports")
    parser.add_argument("--results-dir", type=Path, default=PROJECT_ROOT / "results")
    parser.add_argument("--model", help="Override ANTHROPIC_MODEL / OPENAI_MODEL")
    parser.add_argument("--prompt-version", choices=["v1", "v2", "v3"], default="v1")
    parser.add_argument("--cached-only", action="store_true", help="Replay saved responses with no API calls")
    parser.add_argument("--retry-failed", action="store_true", help="Retry only previously failed responses")
    args = parser.parse_args()
    if args.cached_only and args.retry_failed:
        parser.error("--cached-only cannot be combined with --retry-failed")
    filenames = {"dev": "osm_dev.json", "test": "osm_test.json", "hard": "hard_cases.json", "legacy": "osm_ground_truth_cluj.json"}
    dataset = args.dataset or args.data_dir / filenames[args.split]
    if not dataset.exists():
        parser.error(f"Dataset does not exist: {dataset}. Download it with python -m src.fetch_osm.")
    if args.mode != "baseline" and not args.cached_only:
        key = "ANTHROPIC_API_KEY" if args.mode == "claude" else "OPENAI_API_KEY"
        if not os.getenv(key):
            parser.error(f"{key} is missing. Copy .env.example to .env and set it locally. Baseline needs no key.")
    model = "rule_based_baseline" if args.mode == "baseline" else (
        args.model or os.getenv("ANTHROPIC_MODEL" if args.mode == "claude" else "OPENAI_MODEL") or
        ("claude-sonnet-5-5" if args.mode == "claude" else "gpt-4o")
    )
    # Import Prefect only after inexpensive configuration checks.
    from src.pipeline_flow import run_geospatial_pipeline
    from src.evaluator import percentage
    try:
        metrics = run_geospatial_pipeline(
            data_dir=args.data_dir, reports_dir=args.reports_dir, mode=args.mode,
            dataset_file=dataset, model_name=model, prompt_version=args.prompt_version,
            results_dir=args.results_dir, cached_only=args.cached_only, retry_failed=args.retry_failed
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"Run stopped: {exc}", file=sys.stderr)
        return 1
    print(f"\nModel: {model}; prompt: {args.prompt_version}; dataset: {dataset.name}")
    print(f"Labeled attempts: {metrics['total_segments_evaluated']}")
    print(f"Exact segment match: {percentage(metrics['exact_segment_match_rate'])}")
    print(f"Invalid-output rate: {percentage(metrics['invalid_output_rate'])}")
    print(f"API-error rate: {percentage(metrics['api_error_rate'])}")
    print(f"Estimated new API cost (USD): {metrics['estimated_new_api_cost_usd']}")
    print("Largest error categories:", sorted(metrics["error_taxonomy_breakdown"].items(), key=lambda item: -item[1])[:3])
    print(f"Saved report: {Path(metrics['report_directory']) / 'evaluation_report.md'}")
    return 1 if metrics["failed_outputs"] else 0


if __name__ == "__main__":
    sys.exit(main())
