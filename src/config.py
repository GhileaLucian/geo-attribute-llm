"""Read project configuration without printing API keys."""

from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_configuration():
    # Process environment takes priority over the local .env file.
    load_dotenv(PROJECT_ROOT / ".env", override=False)
