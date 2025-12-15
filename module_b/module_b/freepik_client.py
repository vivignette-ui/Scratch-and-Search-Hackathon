import os
from typing import Dict, Any, List


def freepik_search_stub(query: str) -> List[Dict[str, Any]]:
    """
    Demo stub.
    In production: call Freepik API to search and download images.
    This returns deterministic candidates so the pipeline remains runnable.
    """
    return [
        {"asset_id": "ring_basic", "source": "freepik_or_placeholder"},
        {"asset_id": "crystal_basic", "source": "freepik_or_placeholder"},
        {"asset_id": "sphere_basic", "source": "freepik_or_placeholder"}
    ]


def get_freepik_api_key() -> str:
    return os.getenv("FREEPIK_API_KEY", "")
