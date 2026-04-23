import requests
import streamlit as st
from typing import List, Dict, Any, Optional
import pandas as pd
from app.core.settings import settings
from app.models.metrics import MetricsResponse, TemporalResponse, AvailableMetricsResponse
from app.models.filters import FiltersResponse, FilterParams
from app.models.insight import (
    parse_metrics_response, 
    parse_anomalies_response, 
    parse_insights_response,
    InsightsResponse,
    AnomaliesResponse,
    InsightMetricsResponse
)
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
        # Limpa o cache ao fazer um novo upload para garantir dados frescos
        st.cache_data.clear()
        if "ai_insights_data" in st.session_state:
            st.session_state.ai_insights_data = None
        if "ai_anomalies_data" in st.session_state:
            st.session_state.ai_anomalies_data = None
            
        file_bytes = file.read()
        response = requests.post(f"{self.base_url}/files/upload", files={"file": (file.name, file_bytes)})
        response.raise_for_status()
        data = response.json()
        self.ingest_id = data.get("ingestion_id")
        return data

    @st.cache_data(show_spinner="Buscando filtros...")
    def get_filters(_self) -> FiltersResponse:
        """Busca os filtros disponíveis para uma ingestão."""
        payload = {"ingestion_id": _self.ingest_id}
        response = requests.post(f"{_self.base_url}/filters/", json=payload)
        response.raise_for_status()
        return FiltersResponse.model_validate(response.json())

    @st.cache_data(show_spinner="Carregando lista de métricas...")
    def get_available_metrics(_self) -> AvailableMetricsResponse:
        """Lista todas as métricas disponíveis e seus grupos."""
        response = requests.get(f"{_self.base_url}/metrics/available")
        response.raise_for_status()
        return AvailableMetricsResponse.model_validate(response.json())

    def get_metrics(self, ingestion_id: str, filter_params: Optional[FilterParams] = None) -> MetricsResponse:
        """Calcula métricas consolidadas com filtros opcionais."""
        return self._get_metrics_cached(ingestion_id, filter_params.to_dict() if filter_params else None)

    @st.cache_data(show_spinner="Calculando indicadores...")
    def _get_metrics_cached(_self, ingestion_id: str, filter_params_dict: Optional[dict] = None) -> MetricsResponse:
        payload = {
            "ingestion_id": ingestion_id,
            "filter_criteria": filter_params_dict
        }
        response = requests.post(f"{_self.base_url}/metrics/", json=payload)
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
        return self._get_temporal_cached(
            ingestion_id, metric_names, freq, mode, filter_params.to_dict() if filter_params else None
        )

    @st.cache_data(show_spinner="Gerando evolução temporal...")
    def _get_temporal_cached(
        _self, 
        ingestion_id: str, 
        metric_names: List[str], 
        freq: str, 
        mode: str,
        filter_params_dict: Optional[dict]
    ) -> TemporalResponse:
        payload = {
            "ingestion_id": ingestion_id,
            "metric_names": metric_names,
            "freq": freq,
            "mode": mode,
            "filter_criteria": filter_params_dict
        }
        response = requests.post(f"{_self.base_url}/metrics/temporal", json=payload)
        response.raise_for_status()
        return TemporalResponse.model_validate(response.json())

    def get_itens(
        self,
        ingestion_id: str,
        filter_params: Optional[FilterParams] = None,
    )-> pd.DataFrame:
        return self._get_itens_cached(ingestion_id, filter_params.to_dict() if filter_params else None)

    @st.cache_data(show_spinner="Carregando dados...")
    def _get_itens_cached(
        _self,
        ingestion_id: str,
        filter_params_dict: Optional[dict] = None,
    )-> pd.DataFrame:
        payload = {
            "ingestion_id": ingestion_id,
            "filter_criteria": filter_params_dict
        }
        response = requests.get(f"{_self.base_url}/itens/", json=payload)
        response.raise_for_status()

        data = response.json()["data"]
        return pd.DataFrame(data)

    def get_insight(
        self,
        ingestion_id: str,
        filter_params: Optional[FilterParams] = None,
    )-> InsightsResponse:
        return self._get_insight_cached(ingestion_id, filter_params.to_dict() if filter_params else None)

    @st.cache_data(ttl=3600, show_spinner="🤖 IA Gerando Insights...")
    def _get_insight_cached(
        _self,
        ingestion_id: str,
        filter_params_dict: Optional[dict] = None,
    )-> InsightsResponse:
        payload = {
            "ingestion_id": ingestion_id,
            "filter_criteria": filter_params_dict
        }
        response = requests.post(f"{_self.base_url}/insights", json=payload)
        response.raise_for_status()

        data = response.json()
        return parse_insights_response(data)

    def get_insights_anomalies(
        self,
        ingestion_id: str,
        filter_params: Optional[FilterParams] = None,
    )-> AnomaliesResponse:
        return self._get_insights_anomalies_cached(ingestion_id, filter_params.to_dict() if filter_params else None)

    @st.cache_data(ttl=3600, show_spinner="🔍 IA Analisando Anomalias...")
    def _get_insights_anomalies_cached(
        _self,
        ingestion_id: str,
        filter_params_dict: Optional[dict] = None,
    )-> AnomaliesResponse:
        payload = {
            "ingestion_id": ingestion_id,
            "filter_criteria": filter_params_dict
        }
        response = requests.post(f"{_self.base_url}/insights/anomalies", json=payload)
        response.raise_for_status()

        data = response.json()
        return parse_anomalies_response(data)

    def get_insights_metrics(
        self,
        ingestion_id: str,
        filter_params: Optional[FilterParams] = None,
    )-> InsightMetricsResponse:
        return self._get_insights_metrics_cached(ingestion_id, filter_params.to_dict() if filter_params else None)

    @st.cache_data(ttl=3600, show_spinner="📊 IA Processando Métricas...")
    def _get_insights_metrics_cached(
        _self,
        ingestion_id: str,
        filter_params_dict: Optional[dict] = None,
    )-> InsightMetricsResponse:
        payload = {
            "ingestion_id": ingestion_id,
            "filter_criteria": filter_params_dict
        }
        response = requests.post(f"{_self.base_url}/insights/metrics", json=payload)
        response.raise_for_status()

        data = response.json()
        return parse_metrics_response(data)

    @st.cache_data(ttl=3600, show_spinner="🤖 IA Interpretando Dados...")
    def rag_interpret(_self, ingestion_id: str, question: str) -> Dict[str, Any]:
        """Consulta o RAG para interpretar dados em linguagem natural."""
        payload = {
            "ingestion_id": ingestion_id,
            "question": question
        }
        response = requests.post(f"{_self.base_url}/rag/analytics/interpret", json=payload)
        response.raise_for_status()
        return response.json()

client = ApiClient()
