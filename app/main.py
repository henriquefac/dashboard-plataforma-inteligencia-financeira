import streamlit as st
import pandas as pd
from app.api.v1.client import client
from app.components import UploadScream, FilterSidebar

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
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Inicialização dos Componentes no Session State
if 'upload_screen' not in st.session_state:
    st.session_state.upload_screen = UploadScream()
if 'filter_sidebar' not in st.session_state:
    st.session_state.filter_sidebar = FilterSidebar()

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

# 5. Renderização dos Filtros (Sidebar)
# O componente FilterSidebar utiliza o client.ingest_id definido no passo anterior
st.session_state.filter_sidebar.render()
applied_filters = st.session_state.filter_sidebar.filter_params

# 6. Dashboard Principal (Métricas e Gráficos)
st.title("📊 Dashboard Financeiro")
st.caption(f"ID da Ingestão Atual: `{client.ingest_id}`")

try:
    with st.spinner("Buscando dados consolidados..."):
        # Metadados de métricas disponíveis
        available_info = client.get_available_metrics()
        # Cálculo das métricas com os filtros aplicados
        metrics_data = client.get_metrics(client.ingest_id, applied_filters)
except Exception as e:
    st.error(f"Erro ao carregar métricas: {e}")
    st.stop()

# --- KPIs ---
st.subheader("Indicadores Principais")
m = metrics_data.metricas
all_kpis = []
# Mapeamento de grupos para exibição amigável
for group in ["receita", "ticket", "taxa"]:
    if group in m:
        for name, val in m[group].items():
            if val is not None:
                label = name.replace("_", " ").title()
                fmt = f"{val:.2%}" if "taxa" in name else f"R$ {val:,.2f}"
                all_kpis.append((label, fmt))

if all_kpis:
    cols = st.columns(len(all_kpis))
    for col, (label, val) in zip(cols, all_kpis):
        col.metric(label, val)
else:
    st.info("Ajuste os filtros para visualizar as métricas.")

st.divider()

# --- GRÁFICOS ---
st.subheader("📈 Evolução Temporal")

c1, c2, c3 = st.columns([2, 3, 1])

with c1:
    group_options = list(available_info.groups.keys())
    selected_group = st.selectbox("Grupo de Métricas", options=group_options)

with c2:
    available_metrics = available_info.groups[selected_group]
    selected_metrics = st.multiselect("Métricas no Gráfico", options=available_metrics, default=available_metrics)

with c3:
    freq = st.selectbox("Frequência", options=["W", "M", "Q", "Y"], index=1)

if selected_metrics:
    with st.spinner("Calculando séries temporais..."):
        temporal_data = client.get_temporal(
            client.ingest_id, 
            selected_metrics, 
            freq=freq,
            filter_params=applied_filters
        )
    
    chart_df = pd.DataFrame()
    for group_name, results in temporal_data.evolucao.items():
        if group_name == selected_group:
            for res in results:
                if res.datas:
                    metric_label = res.metric_name.replace("_", " ").title()
                    temp_df = pd.DataFrame({
                        "Data": pd.to_datetime(res.datas),
                        metric_label: res.valores
                    }).set_index("Data")
                    
                    if chart_df.empty:
                        chart_df = temp_df
                    else:
                        chart_df = chart_df.join(temp_df, how="outer")
    
    if not chart_df.empty:
        st.line_chart(chart_df, height=400)
    else:
        st.info("Sem dados para o gráfico com a seleção atual.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.button("🔄 Novo Upload", on_click=lambda: setattr(client, 'ingest_id', None))
st.sidebar.info(f"Registros processados: **{metrics_data.total_registros}**")