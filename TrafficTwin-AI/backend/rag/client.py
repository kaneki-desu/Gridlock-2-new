from datetime import datetime
import os
from typing import Dict, List, Optional

import requests

DEFAULT_RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8001")


class RAGClient:
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        self.base_url = (base_url or DEFAULT_RAG_SERVICE_URL).rstrip("/")
        self.timeout = timeout

    def _post(self, endpoint: str, payload: Dict):
        url = f"{self.base_url}{endpoint}"
        print("post1\n ", payload, type(payload))
        response = requests.post(url, json=payload, timeout=self.timeout)
        print("post2\n")
        response.raise_for_status()
        return response.json()

    def retrieve_similar(self, incident_dict: Dict, k: int = 5) -> List[Dict]:
        serialized_incident = {}

        for key, value in incident_dict.items():
            if isinstance(value, datetime):
                serialized_incident[key] = value.isoformat()
            else:
                serialized_incident[key] = value

        payload = {
            "incident": serialized_incident,
            "k": k
        }

        print("rag1\n", payload)

        result = self._post("/search", payload)

        print("rag2\n")

        return result.get("similar_incidents", result)

    def index_incident(self, incident_dict: Dict, incident_id: int) -> Dict:
        payload = {"incident": incident_dict, "incident_id": incident_id}
        return self._post("/index", payload)

    def health_check(self) -> Dict:
        url = f"{self.base_url}/health"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
