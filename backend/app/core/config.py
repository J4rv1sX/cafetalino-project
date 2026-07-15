from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
import os

_ENV_LOCAL_PATH = Path(__file__).resolve().parent.parent.parent / ".env.local"


@lru_cache
def get_google_maps_api_key() -> str:
    load_dotenv(_ENV_LOCAL_PATH)
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise RuntimeError(
            f"GOOGLE_MAPS_API_KEY is not set. Add it to {_ENV_LOCAL_PATH}."
        )
    return api_key
