"""A missing API key should stop before the Prefect server or paid calls."""

import os
import subprocess
import sys
from src.config import PROJECT_ROOT


def test_missing_claude_key_stops_early():
    environment = dict(os.environ)
    # Empty process value prevents .env from supplying a key during this test.
    environment["ANTHROPIC_API_KEY"] = ""
    completed = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "run_pipeline.py"), "--mode", "claude"],
        cwd=PROJECT_ROOT, env=environment, capture_output=True, text=True, timeout=15
    )
    assert completed.returncode == 2
    assert "ANTHROPIC_API_KEY is missing" in completed.stderr
    assert "Starting temporary server" not in completed.stderr


def test_missing_openai_key_stops_early():
    environment = dict(os.environ)
    environment["OPENAI_API_KEY"] = ""
    completed = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "run_pipeline.py"), "--mode", "openai"],
        cwd=PROJECT_ROOT, env=environment, capture_output=True, text=True, timeout=15
    )
    assert completed.returncode == 2
    assert "OPENAI_API_KEY is missing" in completed.stderr
    assert "Starting temporary server" not in completed.stderr
