import streamlit as st
import pandas as pd
from typing import Optional
from app.api.v1.client import client
from app.models.filters import FilterParams

class ItemsTable:
    def __init__(self):
        pass

    def render(self, filters: Optional[FilterParams] = None):
        if not client.ingest_id:
            return

        st.markdown("### 📋 Detalhamento dos Dados")
        
        try:
            df = client.get_itens(client.ingest_id, filters)
        except Exception as e:
            st.error(f"Erro ao carregar itens: {e}")
            return
        
        if df is None or df.empty:
            st.info("Nenhum item encontrado para os filtros selecionados.")
            return

        # Container para a tabela
        with st.container():
            # Exibir resumo rápido e botão de download
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"Foram encontrados **{len(df)}** registros baseados nos filtros aplicados.")
            with col2:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar CSV",
                    data=csv,
                    file_name=f"extrato_{client.ingest_id}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            # Renderizar a tabela principal
            # O Streamlit dataframe já oferece busca, ordenação e redimensionamento
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )
