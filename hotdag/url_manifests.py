import requests
from dbt.contracts.graph.manifest import Manifest
from fastapi import HTTPException

from hotdag.dbt_core import deserialize_manifest


def get_manifest_from_url(url: str) -> Manifest:
    """Retrieve a manifest.json file from a URL and deserialize it into a Manifest object."""
    response = requests.get(url, headers={"Content-Type": "application/json"})

    if response.status_code >= 400:
        raise HTTPException(
            status_code=421,
            detail=f"HotDAG was unable to load a manifest.json file from the provided URL. The "
            f"destination responded with a {response.status_code} status code.",
        )

    manifest = response.json()
    return deserialize_manifest(manifest)
