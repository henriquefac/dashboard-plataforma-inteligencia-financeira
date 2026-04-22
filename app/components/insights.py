import streamlit as st
from typing import Optional
from app.api.v1.client import client
from app.models.filters import FilterParams
from app.models.insight import InsightsResponse, AnomaliesResponse

class InsightsDisplay:
    def __init__(self):
        if "insights_cache" not in st.session_state:
            st.session_state.insights_cache = None
        if "anomalies_cache" not in st.session_state:
            st.session_state.anomalies_cache = None
        if "insights_last_ingest_id" not in st.session_state:
            st.session_state.insights_last_ingest_id = None
        if "insights_expanded" not in st.session_state:
            st.session_state.insights_expanded = True
        if "anomalies_expanded" not in st.session_state:
            st.session_state.anomalies_expanded = True

    def _fetch_data(self, filters: Optional[FilterParams], force: bool = False):
        """Busca insights e anomalias do backend."""
        if force or st.session_state.insights_cache is None or st.session_state.insights_last_ingest_id != client.ingest_id:
            with st.spinner("🤖 IA Gerando Insights Estratégicos..."):
                try:
                    # Buscando ambos os endpoints
                    st.session_state.insights_cache = client.get_insight(client.ingest_id, filters)
                    st.session_state.anomalies_cache = client.get_insights_anomalies(client.ingest_id, filters)
                    st.session_state.insights_last_ingest_id = client.ingest_id
                except Exception as e:
                    st.error(f"Erro ao gerar insights: {e}")

    def render(self, filters: Optional[FilterParams] = None):
        if not client.ingest_id:
            return

        # Auto-fetch se for a primeira vez para este ingest_id
        if st.session_state.insights_last_ingest_id != client.ingest_id:
            self._fetch_data(filters)

        # Se não houver dados mesmo após o fetch (erro), não renderiza
        if not st.session_state.insights_cache and not st.session_state.anomalies_cache:
            if st.button("🔄 Tentar Gerar Insights (AI)", use_container_width=True):
                self._fetch_data(filters, force=True)
                st.rerun()
            return

        # Botão para re-geração manual (sempre visível após o primeiro carregamento)
        col_title, col_btn = st.columns([4, 1])
        with col_btn:
            if st.button("🔄 Atualizar IA", use_container_width=True, help="Solicita que a IA processe os dados novamente com os filtros atuais."):
                self._fetch_data(filters, force=True)
                st.rerun()

        # Render Insights
        self._render_insights_panel()
        
        # Render Anomalies
        self._render_anomalies_panel()

    def _render_insights_panel(self):
        insights_data = st.session_state.insights_cache
        if not insights_data:
            return

        with st.expander("💡 Insights Estratégicos (AI)", expanded=st.session_state.insights_expanded):
            if not insights_data.insights:
                st.info("Nenhum insight estratégico identificado no momento.")
            else:
                for insight in insights_data.insights:
                    severity_color = self._get_severity_color(insight.severidade)
                    st.markdown(f"""
                    <div class="insight-card" style="border-left: 5px solid {severity_color};">
                        <h4 style="margin-top: 0; color: {severity_color};">{insight.titulo}</h4>
                        <p style="margin-bottom: 8px;"><strong>Observação:</strong> {insight.observacao}</p>
                        <p style="margin-bottom: 8px;"><strong>Impacto:</strong> {insight.impacto}</p>
                        <p style="margin-bottom: 8px;"><strong>Ação Recomendada:</strong> {insight.acao}</p>
                        <div style="text-align: right;">
                            <span style="font-size: 0.75em; color: #888; background: #262626; padding: 2px 8px; border-radius: 10px;">
                                Severidade: {insight.severidade.upper()}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    def _render_anomalies_panel(self):
        anomalies_data = st.session_state.anomalies_cache
        if not anomalies_data:
            return

        with st.expander("🔍 Anomalias e Padrões (AI)", expanded=st.session_state.anomalies_expanded):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🚨 Anomalias")
                if not anomalies_data.anomalias:
                    st.info("Nenhuma anomalia crítica detectada.")
                else:
                    for anomalia in anomalies_data.anomalias:
                        risk_color = self._get_severity_color(anomalia.risco)
                        st.markdown(f"""
                        <div class="anomaly-card" style="border-left: 4px solid {risk_color};">
                            <h5 style="margin: 0; color: {risk_color};">{anomalia.tipo.upper()}</h5>
                            <p style="margin: 8px 0; font-size: 0.95em;">{anomalia.descricao}</p>
                            <p style="font-size: 0.85em; color: #aaa;"><strong>Evidência:</strong> <code>{anomalia.evidencia}</code></p>
                            <p style="font-size: 0.9em; margin-bottom: 0; color: #ddd; border-top: 1px solid #333; padding-top: 8px; margin-top: 8px;">
                                <strong>💡 Recomendação:</strong> {anomalia.recomendacao}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📊 Padrões")
                if not anomalies_data.padroes:
                    st.info("Nenhum padrão estatístico relevante encontrado.")
                else:
                    for padrao in anomalies_data.padroes:
                        st.markdown(f"""
                        <div class="pattern-card" style="border-left: 4px solid #00C49F;">
                            <h5 style="margin: 0; color: #00C49F;">{padrao.tipo.upper()}</h5>
                            <p style="margin: 8px 0; font-size: 0.95em;">{padrao.descricao}</p>
                            <p style="font-size: 0.85em; color: #aaa; margin-bottom: 0;"><strong>Evidência:</strong> <code>{padrao.evidencia}</code></p>
                        </div>
                        """, unsafe_allow_html=True)

    def _get_severity_color(self, severity: str) -> str:
        s = severity.lower()
        if any(word in s for word in ['alta', 'crítica', 'critica', 'alto', 'high']):
            return "#FF4B4B" # Vermelho
        if any(word in s for word in ['média', 'media', 'atencao', 'atenção', 'medio', 'medium']):
            return "#FFA500" # Laranja
        return "#007BFF" # Azul
