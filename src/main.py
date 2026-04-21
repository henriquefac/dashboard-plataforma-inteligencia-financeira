import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# ---------------------------
# MOCK DE DADOS
# ---------------------------
np.random.seed(42)

df = pd.DataFrame({
    "cliente": np.random.choice(["Empresa", "Startup", "Loja"], 200),
    "valor": np.random.uniform(100, 5000, 200),
    "status": np.random.choice(["pago", "inadimplente"], 200, p=[0.8, 0.2]),
    "data": pd.date_range(start="2024-01-01", periods=200, freq="D")
})

# ---------------------------
# SIDEBAR (FILTROS)
# ---------------------------
st.sidebar.header("Filtros")

clientes = st.sidebar.multiselect(
    "Cliente",
    options=df["cliente"].unique(),
    default=df["cliente"].unique()
)

status = st.sidebar.multiselect(
    "Status",
    options=df["status"].unique(),
    default=df["status"].unique()
)

date_range = st.sidebar.date_input(
    "Período",
    [df["data"].min(), df["data"].max()]
)

# ---------------------------
# FILTRAGEM
# ---------------------------
df_filtrado = df[
    (df["cliente"].isin(clientes)) &
    (df["status"].isin(status)) &
    (df["data"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# ---------------------------
# MÉTRICAS
# ---------------------------
receita_potencial = df_filtrado["valor"].sum()

receita_efetiva = df_filtrado[df_filtrado["status"] == "pago"]["valor"].sum()

receita_inadimplente = df_filtrado[df_filtrado["status"] == "inadimplente"]["valor"].sum()

ticket_medio = df_filtrado["valor"].mean() if not df_filtrado.empty else 0

taxa_inadimplencia = (
    len(df_filtrado[df_filtrado["status"] == "inadimplente"]) / len(df_filtrado)
    if len(df_filtrado) > 0 else 0
)

# ---------------------------
# PAINEL PRINCIPAL
# ---------------------------
st.title("📊 Dashboard Financeiro")

# KPIs linha 1
col1, col2, col3 = st.columns(3)

col1.metric("Receita Potencial", f"R$ {receita_potencial:,.2f}")
col2.metric("Receita Efetiva", f"R$ {receita_efetiva:,.2f}")
col3.metric("Receita Inadimplente", f"R$ {receita_inadimplente:,.2f}")

# KPIs linha 2
col4, col5 = st.columns(2)

col4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
col5.metric("Taxa de Inadimplência", f"{taxa_inadimplencia:.2%}")

# ---------------------------
# TABELA (DETALHE)
# ---------------------------
st.subheader("Transações")
st.dataframe(df_filtrado)