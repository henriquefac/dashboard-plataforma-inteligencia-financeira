import requests
from typing import List, Dict, Any, Optional
from app.core.settings import settings
from app.models.metrics import MetricsResponse, TemporalResponse, AvailableMetricsResponse
from app.models.filters import FiltersResponse, FilterParams

from streamlit.runtime.uploaded_file_manager import UploadedFile

class ApiClient:
    def __init__(self, base_url: str = settings.BASE_URL):
        self.base_url = base_url
        self.ingest_id = None

    def list_artifacts(self) -> List[Dict[str, Any]]:
        """Lista todos os artefatos de ingestão disponíveis."""
        response = requests.get(f"{self.base_url}/artifacts/")
        response.raise_for_status()
        return response.json().get("artifacts", [])

    def upload_file(self, file: UploadedFile) -> Dict[str, Any]:
        """Envia um arquivo para ingestão."""
        file_bytes = file.read()
        response = requests.post(f"{self.base_url}/files/upload", files={"file": (file.name, file_bytes)})
        response.raise_for_status()
        data = response.json()
        self.ingest_id = data.get("ingestion_id")
        return data

    def get_filters(self) -> FiltersResponse:
        """Busca os filtros disponíveis para uma ingestão."""
        payload = {"ingestion_id": self.ingest_id}
        response = requests.post(f"{self.base_url}/filters/", json=payload)
        response.raise_for_status()
        return FiltersResponse.model_validate(response.json())

    def get_available_metrics(self) -> AvailableMetricsResponse:
        """Lista todas as métricas disponíveis e seus grupos."""
        response = requests.get(f"{self.base_url}/metrics/available")
        response.raise_for_status()
        return AvailableMetricsResponse.model_validate(response.json())

    def get_metrics(self, ingestion_id: str, filter_params: Optional[FilterParams] = None) -> MetricsResponse:
        """Calcula métricas consolidadas com filtros opcionais."""
        payload = {
            "ingestion_id": ingestion_id,
            "filter_criteria": filter_params.to_dict() if filter_params else None
        }
        response = requests.post(f"{self.base_url}/metrics/", json=payload)
        response.raise_for_status()
        return MetricsResponse.model_validate(response.json())

    def get_temporal(
        self, 
        ingestion_id: str, 
        metric_names: List[str], 
        freq: str = "M", 
        mode: str = "pontual",
        filter_params: Optional[FilterParams] = None
    ) -> TemporalResponse:
        """Calcula evolução temporal para as métricas selecionadas."""
        payload = {
            "ingestion_id": ingestion_id,
            "metric_names": metric_names,
            "freq": freq,
            "mode": mode,
            "filter_criteria": filter_params.root if filter_params else None
        }
        response = requests.post(f"{self.base_url}/metrics/temporal", json=payload)
        response.raise_for_status()
        return TemporalResponse.model_validate(response.json())

client = ApiClient()
