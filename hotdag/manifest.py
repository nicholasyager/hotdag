import json
import os
from typing import Dict, Optional

from dbt.contracts.graph.manifest import Manifest
from starlette.exceptions import HTTPException

from hotdag.dbt_cloud import DbtCloud
from hotdag.dbt_core import CompiledNode, Node, SlimNode, deserialize_manifest


class AbstractManifestLoader:
    """An abstract class for loading manifests from specific data sources,"""

    def __init__(self):
        pass

    def load(self, *args, **kwargs) -> Manifest:
        """Load a manifest from the specified source."""
        raise NotImplementedError

    @staticmethod
    def _dematerialize_manifest_dict(manifest_dict: Dict) -> Manifest:
        """Convert a dictionary containing manifest content, and create a dbt-core Manifest."""

        return Manifest(
            nodes={
                unique_id: CompiledNode(**value)
                for unique_id, value in manifest_dict.get("nodes").items()
            },
            sources={
                unique_id: Node(**value)
                for unique_id, value in manifest_dict.get("sources").items()
            },
            macros={
                unique_id: SlimNode(**value)
                for unique_id, value in manifest_dict.get("macros").items()
            },
            docs={
                unique_id: Node(**value)
                for unique_id, value in manifest_dict.get("docs").items()
            },
            exposures={
                unique_id: SlimNode(**value)
                for unique_id, value in manifest_dict.get("exposures").items()
            },
            selectors={
                unique_id: value
                for unique_id, value in manifest_dict.get("selectors").items()
            },
        )


class DictManifestLoader(AbstractManifestLoader):
    """DictManifestLoader handles loading Manifests from a Dict in memory"""

    def __init__(self):
        super().__init__()

    def load(self, dict: Dict) -> Manifest:
        """Load a Manifest from a path on the local filesystem."""

        return self._dematerialize_manifest_dict(dict)


class FileManifestLoader(AbstractManifestLoader):
    """FileManifestLoader handles loading Manifests from the local filesystem."""

    def __init__(self):
        super().__init__()

    def load(self, file) -> Manifest:
        """Load a Manifest from a path on the local filesystem."""

        manifest_json = json.load(file)
        return self._dematerialize_manifest_dict(manifest_json)


class URLManifestLoader(AbstractManifestLoader):
    """URLManifestLoader handles loading Manifests from a remote system via URL."""

    def __init__(self):
        super().__init__()

    def load(self, url: str) -> Manifest:
        """Load a Manifest from a path on the local filesystem."""

        import requests

        response = requests.get(url, headers={"Content-Type": "application/json"})

        if response.status_code >= 400:
            raise HTTPException(
                status_code=421,
                detail=f"HotDAG was unable to load a manifest.json file from the provided URL. The "
                f"destination responded with a {response.status_code} status code.",
            )

        manifest = response.json()
        return deserialize_manifest(manifest)


class DBTCloudLoader(AbstractManifestLoader):
    """Load a manifest from dbt Cloud via the API."""

    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            api_key = os.environ.get("DBT_CLOUD_API_KEY")
            if api_key is None:
                raise Exception(
                    "Loading from dbt Cloud requires an API key. "
                    "Please set it in the `DBT_CLOUD_API_KEY` environment variable."
                )

        super().__init__()
        self._client = DbtCloud(api_key=api_key)

    def load(self, account_id: int, job_id: int) -> Manifest:
        """Load a Manifest from a job on dbt Cloud."""

        run = self._client.list_runs(
            account_id, job_id, params={"status": 10, "order_by": "-id", "limit": 1}
        )

        manifest = self._client.get_artifact(
            account_id=account_id,
            run_id=run["data"][0]["id"],
            artifact_name="manifest.json",
        )

        return deserialize_manifest(manifest)


manifest_loaders = {
    "file": FileManifestLoader,
    "url": URLManifestLoader,
    "stdin": FileManifestLoader,
    "dbt_cloud": DBTCloudLoader,
}
