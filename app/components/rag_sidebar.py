import streamlit as st
from app.api.v1.client import client

class RAGSidebar:
    def __init__(self):
        # Inicializar estados se não existirem
        if "rag_question" not in st.session_state:
            st.session_state.rag_question = ""
        if "rag_last_question" not in st.session_state:
            st.session_state.rag_last_question = None
        if "rag_last_answer" not in st.session_state:
            st.session_state.rag_last_answer = None
        if "rag_is_loading" not in st.session_state:
            st.session_state.rag_is_loading = False

    @st.fragment
    def render(self):
        st.markdown("### 🤖 Assistente Analítico")
        st.caption("Pergunte qualquer coisa sobre seus dados financeiros.")
        
        # Estilo customizado para os cards de Q&A
        st.markdown("""
        <style>
        .rag-question-card {
            background: #262730;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #ff4b4b;
            margin-bottom: 10px;
        }
        .rag-answer-card {
            background: #1e1e1e;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #00c0f2;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Container para a pergunta e resposta anterior
        if st.session_state.rag_last_question:
            st.markdown(f'<div class="rag-question-card"><b>Sua pergunta:</b><br>{st.session_state.rag_last_question}</div>', unsafe_allow_html=True)
            
            if st.session_state.rag_last_answer:
                st.markdown(f'<div class="rag-answer-card"><b>Resposta:</b><br>{st.session_state.rag_last_answer}</div>', unsafe_allow_html=True)
            elif st.session_state.rag_is_loading:
                with st.status("Pensando...", expanded=True):
                    st.write("Analisando dados e gerando insights...")

        # Input do usuário
        # Desabilitar se estiver carregando
        with st.form(key="rag_form", clear_on_submit=True):
            user_input = st.text_area(
                "O que você deseja saber?",
                placeholder="Ex: Qual foi o faturamento total em Janeiro?",
                disabled=st.session_state.rag_is_loading,
                key="rag_input_area"
            )
            submit_button = st.form_submit_button(
                "Enviar Pergunta",
                disabled=st.session_state.rag_is_loading or not client.ingest_id
            )

            if submit_button and user_input:
                st.session_state.rag_is_loading = True
                st.session_state.rag_last_question = user_input
                st.session_state.rag_last_answer = None
                st.rerun()

        # Lógica de processamento (se estiver carregando e tiver uma pergunta mas sem resposta)
        if st.session_state.rag_is_loading and st.session_state.rag_last_question and not st.session_state.rag_last_answer:
            try:
                response = client.rag_interpret(client.ingest_id, st.session_state.rag_last_question)
                st.session_state.rag_last_answer = response.get("resposta", "Não foi possível obter uma resposta.")
                st.session_state.rag_is_loading = False
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao processar consulta: {e}")
                st.session_state.rag_is_loading = False
                st.session_state.rag_last_answer = "Erro na comunicação com o assistente."
                st.rerun()
