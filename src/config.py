"""Read project configuration without printing API keys."""

from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MODELS = {
    "baseline": "rule_based_baseline",
    "claude": "claude-sonnet-5-5",
    "openai": "gpt-4o",
    "local": "qwen2.5:3b",
}


def resolve_model(mode, override=None):
    import os
    if mode == "baseline":
        return DEFAULT_MODELS[mode]
    variable = {"claude": "ANTHROPIC_MODEL", "openai": "OPENAI_MODEL", "local": "LOCAL_MODEL"}[mode]
    return override or os.getenv(variable) or DEFAULT_MODELS[mode]


def load_configuration():
    # Process environment takes priority over the local .env file.
    load_dotenv(PROJECT_ROOT / ".env", override=False)
