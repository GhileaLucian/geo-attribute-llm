"""
Entrypoint script for GeoAttribute-LLM pipeline.
Usage:
    python run_pipeline.py
    python run_pipeline.py --live-api
"""

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
    parser.add_argument("--live-api", action="store_true", help="Use live OpenAI/Claude API (requires OPENAI_API_KEY or ANTHROPIC_API_KEY)")
    parser.add_argument("--data-dir", default="data", help="Directory where ground truth data is stored")
    parser.add_argument("--reports-dir", default="reports", help="Directory where reports are saved")
    args = parser.parse_args()

    print("\n" + "="*70)
    print("[START] RUNNING GEOSPATIAL LLM QA PIPELINE (Prefect Orchestrated)")
    print("="*70)

    data_dir = Path(args.data_dir)
    reports_dir = Path(args.reports_dir)

    metrics = run_geospatial_pipeline(
        data_dir=data_dir,
        reports_dir=reports_dir,
        use_live_api=args.live_api
    )

    print("\n" + "="*70)
    print("[SUCCESS] PIPELINE EXECUTION COMPLETED")
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
