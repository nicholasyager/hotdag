from typing import Dict, Optional

import requests


class DbtCloud:
    """A minimalist HTTP client for dbt Cloud"""

    def __init__(self, api_key: str, host: str = "https://cloud.getdbt.com/api/v2"):
        self._host = host
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {api_key}",
        }

    def _get(self, endpoint: str, **kwargs) -> Dict:
        response = requests.get(self._host + endpoint, headers=self._headers, **kwargs)

        if response.status_code >= 400:
            raise Exception(response.text)

        return response.json()

    def get_artifact(
        self,
        account_id: int,
        run_id: int,
        artifact_name: str,
        params: Optional[Dict] = None,
    ) -> Dict:
        """Get an artifact by name from a run."""
        response = self._get(
            f"/accounts/{account_id}/runs/{run_id}/artifacts/{artifact_name}",
            params=params,
        )

        return response

    def list_runs(
        self, account_id: int, job_id: int, params: Optional[Dict] = None
    ) -> Dict:
        """List the runs for a given Job."""

        response = self._get(
            f"/accounts/{account_id}/runs",
            params={"job_definition_id": job_id, **(params if params else {})},
        )

        return response
