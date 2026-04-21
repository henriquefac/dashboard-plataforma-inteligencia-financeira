from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union

class MetricValue(BaseModel):
    value: float
    formatted: str

class MetricsResponse(BaseModel):
    ingestion_id: str
    total_registros: int
    metricas: Dict[str, Dict[str, float | None]]

class TemporalResult(BaseModel):
    metric_name: str
    datas: List[str]
    valores: List[float]
    freq: str
    mode: str
    error: Optional[str] = None

class TemporalResponse(BaseModel):
    ingestion_id: str
    total_registros: int
    freq: str
    mode: str
    evolucao: Dict[str, List[TemporalResult]]

class MetricMetadata(BaseModel):
    name: str
    group: str

class AvailableMetricsResponse(BaseModel):
    metrics: List[MetricMetadata]
    groups: Dict[str, List[str]]
