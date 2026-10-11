"""Example only: serve a scheduled baseline development run."""

from src.config import PROJECT_ROOT
from src.pipeline_flow import run_geospatial_pipeline


if __name__ == "__main__":
    from prefect.client.schemas.schedules import CronSchedule
    run_geospatial_pipeline.serve(
        name="baseline-development-example",
        schedule=CronSchedule(cron="0 9 * * *", timezone="Europe/Bucharest"),
        parameters={
            "data_dir": str(PROJECT_ROOT / "data"),
            "reports_dir": str(PROJECT_ROOT / "reports"),
            "dataset_file": str(PROJECT_ROOT / "data" / "osm_dev.json"),
            "results_dir": str(PROJECT_ROOT / "results"),
            "mode": "baseline", "model_name": "rule_based_baseline", "prompt_version": "v1"
        }
    )
