"""
Entrypoint script for GeoAttribute-LLM pipeline.
Usage:
    python run_pipeline.py                     # Runs Rule-based Baseline
    python run_pipeline.py --mode claude       # Runs live Claude Sonnet extraction (requires ANTHROPIC_API_KEY)
    python run_pipeline.py --mode openai       # Runs live OpenAI GPT-4o extraction (requires OPENAI_API_KEY)
"""

import os
import sys
import argparse
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.pipeline_flow import run_geospatial_pipeline


def main():
    parser = argparse.ArgumentParser(description="GeoAttribute-LLM: Geospatial Attribute Extraction & Automated QA Pipeline")
    parser.add_argument(
        "--mode",
        choices=["baseline", "claude", "openai"],
        default="baseline",
        help="Extractor engine to use: 'baseline' (rule heuristics), 'claude' (Anthropic Claude 3.5), or 'openai' (GPT-4o)"
    )
    parser.add_argument("--data-dir", default="data", help="Directory where ground truth data is stored")
    parser.add_argument("--reports-dir", default="reports", help="Directory where reports are saved")
    args = parser.parse_args()

    # Pre-check API keys
    if args.mode == "claude" and not os.getenv("ANTHROPIC_API_KEY"):
        print("\n[ERROR] ANTHROPIC_API_KEY environment variable is not set!")
        print("Please set it in your terminal:")
        print("   Windows CMD:        set ANTHROPIC_API_KEY=your-api-key")
        print("   PowerShell:         $env:ANTHROPIC_API_KEY='your-api-key'")
        print("Or run the rule-based baseline without an API key:")
        print("   python run_pipeline.py --mode baseline\n")
        sys.exit(1)

    if args.mode == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("\n[ERROR] OPENAI_API_KEY environment variable is not set!")
        print("Please set it in your terminal:")
        print("   Windows CMD:        set OPENAI_API_KEY=your-api-key")
        print("   PowerShell:         $env:OPENAI_API_KEY='your-api-key'")
        print("Or run the rule-based baseline without an API key:")
        print("   python run_pipeline.py --mode baseline\n")
        sys.exit(1)

    print("\n" + "="*70)
    print(f"[START] GEOSPATIAL QA PIPELINE (Prefect Orchestrated) | MODE: {args.mode.upper()}")
    print("="*70)

    data_dir = Path(args.data_dir)
    reports_dir = Path(args.reports_dir)

    metrics = run_geospatial_pipeline(
        data_dir=data_dir,
        reports_dir=reports_dir,
        mode=args.mode
    )

    print("\n" + "="*70)
    print(f"[SUCCESS] PIPELINE EXECUTION COMPLETED ({args.mode.upper()})")
    print("="*70)
    attr = metrics["attributes"]
    print(f"Evaluated Segments:       {metrics['total_segments_evaluated']}")
    print(f"Exact Segment Match Rate: {metrics['exact_segment_match_rate']*100:.1f}%")
    print(f"Road Type F1-Score:       {attr['road_type']['f1_score']*100:.1f}%")
    print(f"Speed (+-10km/h Acc):     {attr['speed_limit']['within_10kmh_accuracy']*100:.1f}%")
    print(f"Barrier F1-Score:         {attr['barrier_present']['f1_score']*100:.1f}%")
    print(f"Surface F1-Score:         {attr['surface_type']['f1_score']*100:.1f}%")
    print(f"Anomaly Detection Acc:    {attr['anomaly_detection']['accuracy']*100:.1f}%")
    print(f"\nArtifacts generated:")
    print(f"   - Report:  {reports_dir / 'evaluation_report.md'}")
    print(f"   - Metrics: {reports_dir / 'metrics_summary.json'}")
    print(f"   - Chart:   {reports_dir / 'evaluation_metrics_chart.png'}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
