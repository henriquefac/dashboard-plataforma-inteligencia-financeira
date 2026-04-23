import streamlit as st
import pandas as pd
from typing import Optional, List, Dict
from app.api.v1.client import client
from app.models.filters import FilterParams
from app.models.metrics import AvailableMetricsResponse, TemporalResponse

class TemporalEvolution:
    def __init__(self):
        # Inicializa estados no session_state se não existirem
        if "temp_group" not in st.session_state:
            st.session_state.temp_group = None
        if "temp_metrics" not in st.session_state:
            st.session_state.temp_metrics = []
        if "temp_metrics_selector" not in st.session_state:
            st.session_state.temp_metrics_selector = []
        if "temp_mode" not in st.session_state:
            st.session_state.temp_mode = "pontual"
        if "temp_freq" not in st.session_state:
            st.session_state.temp_freq = "M"

    def _fetch_available_metrics(self) -> AvailableMetricsResponse:
        """Busca métricas disponíveis."""
        try:
            return client.get_available_metrics()
        except Exception as e:
            st.error(f"Erro ao buscar métricas disponíveis: {e}")
            return None

    def _get_chart_data(self, ingestion_id: str, metric_names: List[str], mode: str, freq: str, filters: Optional[FilterParams]):
        """Busca dados de evolução temporal e formata para o Streamlit."""
        if not metric_names:
            return None
        try:
            response = client.get_temporal(
                ingestion_id=ingestion_id,
                metric_names=metric_names,
                mode=mode,
                freq=freq,
                filter_params=filters
            )
            
            all_series = {}
            dates = []
            
            for group_name, results in response.evolucao.items():
                for res in results:
                    if not dates:
                        dates = res.datas
                    all_series[res.metric_name] = res.valores
            
            if not all_series:
                return None
                
            df = pd.DataFrame(all_series, index=pd.to_datetime(dates))
            return df
            
        except Exception as e:
            st.error(f"Erro ao carregar dados temporais: {e}")
            return None

    def render(self, filters: Optional[FilterParams] = None):
        st.subheader("📈 Evolução Temporal")
        
        available = self._fetch_available_metrics()
        if not available:
            return

        # 1. Seleção de Grupo (Um por vez)
        groups = list(available.groups.keys())
        if not st.session_state.temp_group or st.session_state.temp_group not in groups:
            st.session_state.temp_group = groups[0] if groups else None

        # Usando radio horizontal para seleção de grupo (estilo abas)
        selected_group = st.radio(
            "Selecione o Grupo de Métricas",
            options=groups,
            index=groups.index(st.session_state.temp_group) if st.session_state.temp_group in groups else 0,
            horizontal=True,
            key="temp_group_selector",
            label_visibility="collapsed"
        )
        
        # Se mudar o grupo, resetamos as métricas selecionadas para incluir todas do grupo novo
        if selected_group != st.session_state.temp_group:
            st.session_state.temp_group = selected_group
            new_metrics = available.groups.get(selected_group, [])
            st.session_state.temp_metrics = new_metrics
            # Sincroniza explicitamente a chave do widget multiselect
            st.session_state.temp_metrics_selector = new_metrics
            st.rerun()

        # 2. Configurações e Filtros de Métricas
        col_opts, col_mode, col_freq = st.columns([2, 1, 1])
        
        with col_opts:
            group_metrics = available.groups.get(st.session_state.temp_group, [])
            
            # Garante que a chave do seletor esteja populada se estiver vazia e houver métricas
            if not st.session_state.temp_metrics_selector and group_metrics:
                st.session_state.temp_metrics_selector = group_metrics

            st.multiselect(
                "Métricas para exibir",
                options=group_metrics,
                key="temp_metrics_selector"
            )
            # O st.session_state.temp_metrics_selector é atualizado automaticamente pelo widget
            st.session_state.temp_metrics = st.session_state.temp_metrics_selector

        with col_mode:
            # Alternar entre Acumulado e Período
            mode_options = {"pontual": "Por Período", "acumulativo": "Acumulado"}
            current_mode_label = mode_options.get(st.session_state.temp_mode, "Por Período")
            
            new_mode_label = st.radio(
                "Tipo de Cálculo",
                options=list(mode_options.values()),
                index=list(mode_options.values()).index(current_mode_label),
                key="temp_mode_selector"
            )
            
            # Inverter o map para salvar o valor técnico
            reverse_mode = {v: k for k, v in mode_options.items()}
            st.session_state.temp_mode = reverse_mode[new_mode_label]

        with col_freq:
            # Alternar entre Semanal e Mensal
            freq_options = {"W": "Semanal", "M": "Mensal"}
            current_freq_label = freq_options.get(st.session_state.temp_freq, "Mensal")
            
            new_freq_label = st.radio(
                "Periodicidade",
                options=list(freq_options.values()),
                index=list(freq_options.values()).index(current_freq_label),
                key="temp_freq_selector"
            )
            
            reverse_freq = {v: k for k, v in freq_options.items()}
            st.session_state.temp_freq = reverse_freq[new_freq_label]

        # 3. Renderização do Gráfico
        if not st.session_state.temp_metrics:
            st.info("Selecione pelo menos uma métrica para visualizar o gráfico.")
            return

        with st.spinner("Carregando gráfico..."):
            df_chart = self._get_chart_data(
                client.ingest_id, 
                st.session_state.temp_metrics, 
                st.session_state.temp_mode, 
                st.session_state.temp_freq,
                filters
            )
            
            if df_chart is not None and not df_chart.empty:
                st.line_chart(df_chart, use_container_width=True)
            else:
                st.warning("Não há dados suficientes para gerar o gráfico com os filtros atuais.")
