import streamlit as st
from app.api.v1.client import client
from app.core.settings import settings
from app.models.upload import DataStatus

# Se o cliente aind não tiver
# um ingest_id, então mostre a tela de upload.
# setiver, upload nunca vai aparecer

# Como os outros componenetes dependem da condição inversa
# essa vir uma tela de bloqueio

# precisa ter uma forma de mostra para o usuário que está processando os dados.


class UploadScream:
    def __init__(self):
        self.placeholder = None

    def render(self):
        if client.ingest_id:
            return
        self.placeholder = st.empty()

        with self.placeholder:
            st.title("Bem-vindo a PLataforma de Ingeligencia Financeira da Vicio!")
            st.text("A plataforma possibilita que os usuários façam upload de arquivos CSV ou XLSX.")
            st.text("Após o upload, os dados serão processados e disponibilizados para análise.")
            st.text("Utilize o widget de upload abaixo para iniciar.")
            file = st.file_uploader(f"Escolha um arquivo {', '.join(settings.ALLOWED_EXTENSIONS)}", type=settings.ALLOWED_EXTENSIONS)

            if file is not None:
                with st.spinner("Processando arquivo..."):
                    data = client.upload_file(file)
                
                # Verificar se o upload funcionou
                if data.get("status") == DataStatus.ERROR:
                    st.error("Erro ao processar arquivo!")
                
                st.success("Arquivo enviado com sucesso!")
                
                self.placeholder.empty()