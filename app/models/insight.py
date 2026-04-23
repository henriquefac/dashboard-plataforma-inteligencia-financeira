from typing import Union, Dict, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict
import re

# Representação da resposta do endpoint: /insights/metrics/
# Exemplo:

"""
200
{
  "metricas_basicas": {
    "receita": {
      "receita_total": 10103809.95,
      "receita_real": 7068900.65,
      "receita_inadimplente": 1000195.79
    },
    "ticket": {
      "ticket_medio": 2525.9524874999997,
      "ticket_medio_pendente": 2034713.5099999998,
      "ticket_medio_pago": 7068900.65,
      "ticket_medio_inadimplente": 1000195.79
    },
    "taxa": {
      "taxa_inadimplencia": 9.62,
      "taxa_pago": 70.08,
      "taxa_pendente": 20.3
    }
  },
  "metricas_avancadas": {
    "taxa_conversao_receita_total": {
      "valor": 0.6996272381390152,
      "descricao": "Percentual da receita potencial convertido em receita real",
      "unidade": "%",
      "interpretacao": "Aten\u00e7\u00e3o"
    },
    "receita_perdida_total": {
      "valor": 3034909.299999999,
      "descricao": "Valor de receita potencial n\u00e3o convertido em receita real",
      "unidade": "R$",
      "interpretacao": "Cr\u00edtica"
    },
    "taxa_conversao_por_cliente_top_10": {
      "valor": {
        "startup x": 0.7230255906538943,
        "empresa a": 0.7091851772130413,
        "empresa c": 0.6997654760606296,
        "loja y": 0.6967805834063907,
        "empresa d": 0.6901557645265008,
        "empresa b": 0.6811834124543593
      },
      "descricao": "Top 10 clientes com maior taxa de convers\u00e3o de receita",
      "unidade": "%",
      "interpretacao": null
    },
    ...
"""

ValorMetrica = Union[
    float,
    Dict[str, float],
    list[dict]
]

class Metrica(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    nome: str
    valor: ValorMetrica
    descricao: str
    unidade: Optional[str] = None
    interpretacao: Optional[str] = None

    @property
    def tipo(self) -> str:
        if isinstance(self.valor, dict):
            return "distribuicao"
        return "escalar"

# Representação da resposta do endpoint: /insights/anomalies/
# Exemplo:
"""
200
{
  "anomalias": [
    {
      "tipo": "outlier",
      "descricao": "Ticket médio pendente significativamente maior que o ticket médio pago.",
      "evidencia": "ticket_medio_pendente: 2034713.51, ticket_medio_pago: 7068900.65",
      "risco": "alto",
      "recomendacao": "Investigar a origem dos tickets pendentes. Pode indicar problemas no processo de cobrança, erros de lançamento ou clientes com dificuldades financeiras."
    }
  ],
  "padroes": [
    {
      "tipo": "segmentacao",
      "descricao": "O segmento 'licenca' apresenta a maior taxa de inadimplência (10.42%) e a menor frequência de transações (816), indicando um perfil de risco mais elevado.",
      "evidencia": "risco_inadimplencia_percentual_por_segmento: licenca - 10.42, frequencia_transacoes_por_segmento: licenca - 816"
    }
  ]
}
"""

class Anomalia(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    tipo: str
    descricao: str
    evidencia: str
    risco: str
    recomendacao: str

class Padrao(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    tipo: str
    descricao: str
    evidencia: str

class AnomaliesResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    anomalias: List[Anomalia] = Field(default_factory=list)
    padroes: List[Padrao] = Field(default_factory=list)

# Representação do modelo para a resposta do endpoint: /insights/

"""
200
{
  "insights": [
    {
      "titulo": "Baixo índice de conversão",
      "observacao": "Receita real abaixo de 70% do potencial das vendas",
      "impacto": "Prevalência direta na perda de receita e crescimento limitado",
      "acao": "Investir em otimização de canais de venda e redução de fricção",
      "severidade": "alta"
    }
  ]
}
"""

class Insight(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    titulo: str
    observacao: str
    impacto: str
    acao: str
    severidade: str 

class InsightsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    insights: List[Insight] = Field(default_factory=list)

class InsightMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    metricas_basicas: Dict[str, Dict[str, float]]
    metricas_avancadas: List[Metrica] = Field(default_factory=list)

def is_interval_key(s: str) -> bool:
    return isinstance(s, str) and (
        s.startswith("(") or s.startswith("[")
    ) and "," in s


def parse_intervalo(s: str):
    pattern = r"([\(\[])(.*), (.*)([\)\]])"
    match = re.match(pattern, s)

    if not match:
        return None

    left, min_val, max_val, right = match.groups()

    return {
        "min": float(min_val),
        "max": float(max_val),
        "label": s,
        "fechado_esquerda": left == "[",
        "fechado_direita": right == "]",
    }

def normalize_valor(valor):
    # caso escalar
    if not isinstance(valor, dict):
        return valor

    # verifica se é distribuição por intervalo
    if not valor:
        return valor
        
    first_key = next(iter(valor.keys()))

    if is_interval_key(first_key):
        resultado = []

        for faixa, v in valor.items():
            intervalo = parse_intervalo(faixa)
            if intervalo:
                intervalo["valor"] = v
                resultado.append(intervalo)

        # ordena corretamente
        return sorted(resultado, key=lambda x: x["min"])

    # caso distribuição normal
    return valor

def parse_metrics_response(json_data: dict) -> InsightMetricsResponse:
    metricas_basicas = json_data.get("metricas_basicas", {})
    metricas_avancadas_dict = json_data.get("metricas_avancadas", {})
    
    metricas_avancadas = []
    for nome, m in metricas_avancadas_dict.items():
        valor_normalizado = normalize_valor(m["valor"])
        metricas_avancadas.append(
            Metrica(
                nome=nome,
                valor=valor_normalizado,
                descricao=m["descricao"],
                unidade=m.get("unidade"),
                interpretacao=m.get("interpretacao"),
            )
        )
    
    return InsightMetricsResponse(
        metricas_basicas=metricas_basicas,
        metricas_avancadas=metricas_avancadas
    )

def parse_anomalies_response(json_data: dict) -> AnomaliesResponse:
    return AnomaliesResponse.model_validate(json_data)

def parse_insights_response(json_data: dict) -> InsightsResponse:
    return InsightsResponse.model_validate(json_data)