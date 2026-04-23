import streamlit as st
import pandas as pd
from app.api.v1.client import client
from app.components import UploadScream, FilterSidebar, MetricsDisplay, TemporalEvolution, ItemsTable, InsightsDisplay, RAGSidebar

# 1. Configuração da página
st.set_page_config(
    page_title="Financial Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilo customizado
st.markdown("""
<style>
.stMetric {
    background: #111111; /* levemente acima do preto puro */
    padding: 15px;
    border-radius: 12px;

    /* borda sutil */
    border: 1px solid #2a2a2a;

    /* sombra leve pra destacar do fundo */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);

    /* efeito suave */
    transition: all 0.2s ease-in-out;
}

.stBarChart {
    background: #111111; /* levemente acima do preto puro */
    padding: 15px;
    border-radius: 12px;

    /* borda sutil */
    border: 1px solid #2a2a2a;

    /* sombra leve pra destacar do fundo */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);

    /* efeito suave */
    transition: all 0.2s ease-in-out;
}

/* hover opcional (fica bem bonito) */
.stMetric:hover {
    border-color: #3a3a3a;
    transform: translateY(-2px);
}

/* Insight and Anomaly Cards */
.insight-card, .anomaly-card, .pattern-card {
    background: #1a1a1a;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #2a2a2a;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    transition: all 0.3s ease;
}

.insight-card:hover, .anomaly-card:hover, .pattern-card:hover {
    background: #222222;
    border-color: #444444;
    transform: translateX(5px);
}
</style>
""", unsafe_allow_html=True)

# 3. Inicialização dos Componentes no Session State
if 'upload_screen' not in st.session_state:
    st.session_state.upload_screen = UploadScream()
if 'filter_sidebar' not in st.session_state:
    st.session_state.filter_sidebar = FilterSidebar()
if 'metrics_display' not in st.session_state:
    st.session_state.metrics_display = MetricsDisplay()
if 'temporal_evolution' not in st.session_state:
    st.session_state.temporal_evolution = TemporalEvolution()
if 'items_table' not in st.session_state:
    st.session_state.items_table = ItemsTable()
if 'insights_display' not in st.session_state:
    st.session_state.insights_display = InsightsDisplay()
if 'rag_sidebar' not in st.session_state:
    st.session_state.rag_sidebar = RAGSidebar()

# 4. Fluxo Principal
# Se não houver um ID de ingestão, mostramos apenas a tela de upload
if not client.ingest_id:
    st.session_state.upload_screen.render()
    
    # Se após o render o ID ainda for nulo (usuário não subiu arquivo), paramos aqui
    if not client.ingest_id:
        st.stop()
    else:
        # Se acabou de subir o arquivo, fazemos um rerun para limpar a tela de upload 
        # e iniciar o dashboard
        st.rerun()

# 5. Renderização dos Filtros (Sidebar Esquerda)
st.session_state.filter_sidebar.render()
applied_filters = st.session_state.filter_sidebar.filter_params

# 6. Layout Principal com Colunas (Simulando Sidebar Direita)
col_main, col_spacer, col_rag = st.columns([10, 0.5, 3])

with col_main:
    st.title("📊 Dashboard Financeiro")
    st.caption(f"ID da Ingestão Atual: `{client.ingest_id}`")

    try:
        # Renderizar Componente de Métricas (KPIs)
        metrics_data = st.session_state.metrics_display.render(applied_filters)

        st.divider()

        # Renderizar Evolução Temporal
        st.session_state.temporal_evolution.render(applied_filters)

        st.divider()

        # Renderizar Tabela de Itens
        st.session_state.items_table.render(applied_filters)

        st.divider()

        # Renderizar Insights e Anomalias
        st.session_state.insights_display.render(applied_filters)

    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")
        st.stop()

with col_rag:
    # Renderizar Sidebar do RAG (IA)
    st.session_state.rag_sidebar.render()

st.divider()

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.button("🔄 Novo Upload", on_click=lambda: setattr(client, 'ingest_id', None))
if 'metrics_data' in locals():
    st.sidebar.info(f"Registros processados: **{metrics_data.total_registros}**")