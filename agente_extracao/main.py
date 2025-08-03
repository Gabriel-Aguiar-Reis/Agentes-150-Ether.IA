import streamlit as st
from services.file_service import save_uploaded_file, detect_file_type
from agents.workflow import process_file
from agents.query_agent import answer_query
from dotenv import load_dotenv
import os

# Carrega as variaveis do .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "data/banco.db")


def main():
    st.title("Processamento de Arquivos com LangChain")

    uploaded_file = st.file_uploader("Envie um arquivo", type=["pdf","xml","csv","xls","xlsx"])
    if uploaded_file:
        file_path = save_uploaded_file(uploaded_file, "data")
        file_type = detect_file_type(file_path)
        if not file_type:
            st.error("Tipo de arquivo nao suportado!")
            return
        result = process_file(file_path, file_type)
        st.success(result)

    st.markdown("---")
    query = st.text_input("Pergunte sobre os dados carregados")
    if query:
        resposta = answer_query(query)
        st.write(resposta)

if __name__ == "__main__":
    main()

