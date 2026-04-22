import streamlit as st
import pandas as pd
import altair as alt
from typing import Optional
from app.api.v1.client import client
from app.models.filters import FilterParams

class MetricsDisplay:
    def __init__(self):
        if "metrics_cache" not in st.session_state:
            st.session_state.metrics_cache = None
        if "metrics_last_filters" not in st.session_state:
            st.session_state.metrics_last_filters = None
        if "metrics_expanded" not in st.session_state:
            st.session_state.metrics_expanded = True

    def _get_metrics(self, filters: Optional[FilterParams]):
        """Busca métricas e atualiza o cache se os filtros mudaram."""
        # Convert filters to dict for comparison if it's a FilterParams object
        filters_dict = filters.to_dict() if filters else {}
        
        if (st.session_state.metrics_cache is None or 
            st.session_state.metrics_last_filters != filters_dict):
            
            with st.spinner("Atualizando indicadores..."):
                try:
                    metrics_data = client.get_metrics(client.ingest_id, filters)
                    st.session_state.metrics_cache = metrics_data
                    st.session_state.metrics_last_filters = filters_dict
                except Exception as e:
                    st.error(f"Erro ao carregar métricas: {e}")
        
        return st.session_state.metrics_cache

    def render(self, filters: Optional[FilterParams] = None):
        if not client.ingest_id:
            return

        metrics_data = self._get_metrics(filters)
        if not metrics_data:
            return

        m = metrics_data.metricas

        with st.container():
            # Usando uma div para o CSS sticky funcionar se possível (depende da estrutura do Streamlit)
            
            with st.expander("📊 Indicadores de Desempenho", expanded=st.session_state.metrics_expanded):
                # Row 1: Receita potencial, receita Real, Receita Inadimplente
                r1_c1, r1_c2, r1_c3 = st.columns(3)
                
                # Mapeamento robusto para os nomes solicitados
                # Buscamos no grupo 'receita'
                receita = m.get('receita', {})
                
                with r1_c1:
                    val = receita.get('potencial') or receita.get('receita_total', 0)
                    st.metric("Receita Potencial", f"R$ {val:,.2f}")
                
                with r1_c2:
                    val = receita.get('real') or receita.get('receita_real', 0)
                    st.metric("Receita Real", f"R$ {val:,.2f}", delta_color="normal")
                
                with r1_c3:
                    val = receita.get('inadimplente') or receita.get('receita_inadimplente', 0)
                    st.metric("Receita Inadimplente", f"R$ {val:,.2f}", delta_color="inverse")

                st.divider()

                # Row 2: Taxa de Inadimplência e Ticket Médio
                r2_c1, r2_c2 = st.columns(2)
                
                taxa = m.get('taxa', {})
                ticket = m.get('ticket', {})

                with r2_c1:
                    val = taxa.get('inadimplencia') or taxa.get('taxa_inadimplencia', 0)
                    st.metric("Taxa de Inadimplência", f"{val}%")

                with r2_c2:
                    val = ticket.get('medio') or ticket.get('ticket_medio', 0)
                    st.metric("Ticket Médio", f"R$ {val:,.2f}")

                st.divider()

                # Row 3: Gráficos de Ticket e Taxas
                c1, c2 = st.columns(2)

                val_pago = ticket.get('ticket_medio_pago', 0)
                val_pendente = ticket.get('ticket_medio_pendente', 0)
                val_inadimplente = ticket.get('ticket_medio_inadimplente', 0)

                with c1:
                    st.markdown("#### Ticket Médio por Status")
                    df_tickets = pd.DataFrame({
                        "Valor": [val_pago, val_pendente, val_inadimplente]
                    }, index=["Pago", "Pendente", "Inadimplente"])
                    st.bar_chart(df_tickets, height=300)

                with c2:
                    st.markdown("#### Distribuição de Transações")
                    
                    val_taxa_pago = taxa.get('taxa_pago', 0)
                    val_taxa_pendente = taxa.get('taxa_pendente', 0)
                    val_taxa_inad = taxa.get('inadimplencia') or taxa.get('taxa_inadimplencia', 0)
                    
                    df_taxas = pd.DataFrame({
                        "Status": ["Pago", "Pendente", "Inadimplente"],
                        "Taxa": [val_taxa_pago, val_taxa_pendente, val_taxa_inad]
                    })
                    
                    pie_chart = alt.Chart(df_taxas).mark_arc(innerRadius=60, stroke="#111111", strokeWidth=2).encode(
                        theta=alt.Theta(field="Taxa", type="quantitative"),
                        color=alt.Color(
                            field="Status", 
                            type="nominal", 
                            scale=alt.Scale(range=['#00C49F', '#FFBB28', '#FF8042']), # Cores premium: Verde, Amarelo, Laranja
                            legend=alt.Legend(title=None, orient="bottom")
                        ),
                        tooltip=["Status", alt.Tooltip("Taxa", format=".1f", title="Taxa (%)")]
                    ).properties(height=300)
                    
                    st.altair_chart(pie_chart, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)