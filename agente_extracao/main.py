"""Main application file for the Streamlit web interface of the File Processing Agent."""

import os

import streamlit as st
from dotenv import load_dotenv

from agents.query_agent import answer_query
from agents.workflow import process_file, process_multiple_files, process_zip_file
from services.db_service import listar_arquivos, deletar_arquivo_por_id, obter_registro
from services.file_service import (
    detectar_tipo_arquivo,
    get_supported_file_type,
    save_uploaded_file,
)
from services.logging_service import logging_service
from services.db_service import init_db

load_dotenv()
init_db()

API_KEY = os.getenv("API_KEY")

logging_service.log_application_start()


st.set_page_config(
    page_title="Agente Extração - Processamento de Arquivos",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Agente Extração - Processamento de Arquivos com IA")

with st.sidebar:
    st.header("📊 Estatísticas")
    try:
        stats = logging_service.get_processing_stats()
        if "error" not in stats:
            st.metric("Total de Operações", stats.get("total_operations", 0))
            st.metric("Sucessos", stats.get("successful", 0))
            st.metric("Falhas", stats.get("failed", 0))
            st.metric("ZIPs Processados", stats.get("zip_extractions", 0))
            st.metric("Lotes Processados", stats.get("batch_operations", 0))
        else:
            st.warning("Logs não disponíveis")
    except RuntimeError as e:
        st.error(f"Erro ao carregar estatísticas: {str(e)}")

tab1, tab2, tab3 = st.tabs(["📁 Processamento", "❓ Consultas AI", "🗂 Gestão de Arquivos"])

with tab1:
    st.header("📁 Processamento de Arquivos")
    st.info("💡 Suporte a PDF, CSV, Excel, XML e arquivos ZIP")

    upload_option = st.radio(
        "Escolha o tipo de upload:",
        ["📄 Arquivo Único", "📦 Arquivo ZIP", "📂 Múltiplos Arquivos"],
        horizontal=True,
    )

    if upload_option == "📄 Arquivo Único":
        uploaded_file = st.file_uploader(
            "Selecione um arquivo",
            type=["pdf", "xml", "csv", "xls", "xlsx"],
            help="Arquivos suportados: PDF, XML, CSV, Excel",
        )

        if uploaded_file:
            file_path = save_uploaded_file(uploaded_file, "data")
            file_type = get_supported_file_type(file_path)
            detected_type = detectar_tipo_arquivo(file_path)

            if not file_type:
                st.error(
                    f"❌ Tipo de arquivo não suportado! Detectado: {detected_type}"
                )

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Arquivo", uploaded_file.name)
            with col2:
                st.metric("Tipo Detectado", detected_type)
            with col3:
                st.metric("Tamanho", f"{uploaded_file.size / 1024:.1f} KB")

            if st.button("🚀 Processar Arquivo", type="primary"):
                with st.spinner(f"Processando {uploaded_file.name}..."):
                    result = process_file(file_path, file_type)

                    if result["status"] == "success":
                        st.success(f"✅ {result['file']} processado com sucesso!")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Registros", result["records"])
                        with col2:
                            st.metric("Tempo", f"{result['processing_time']:.2f}s")
                        with col3:
                            st.metric("Status", "✅ Sucesso")

                        # Exibe análise de campos se disponível
                        from services.db_service import ler_dados
                        dados_banco = ler_dados()
                        if dados_banco:
                            analise_campos = dados_banco[-1].get("analise_campos")
                            if analise_campos:
                                with st.expander("🔎 Análise dos Campos do Arquivo"):
                                    st.write(analise_campos)
                    else:
                        st.error(
                            f"❌ Erro ao processar {result['file']}: {result['error']}"
                        )

    elif upload_option == "📦 Arquivo ZIP":
        uploaded_zip = st.file_uploader(
            "Selecione um arquivo ZIP",
            type=["zip"],
            help="O ZIP será extraído e todos os arquivos suportados serão processados",
        )

        if uploaded_zip:
            zip_path = save_uploaded_file(uploaded_zip, "data")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Arquivo ZIP", uploaded_zip.name)
            with col2:
                st.metric("Tamanho", f"{uploaded_zip.size / 1024:.1f} KB")

            if st.button("🚀 Processar ZIP", type="primary"):
                with st.spinner(f"Processando ZIP {uploaded_zip.name}..."):
                    result = process_zip_file(zip_path)

                    if result["status"] == "success":
                        st.success(
                            f"✅ ZIP {result['zip_file']} processado com sucesso!"
                        )
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Arquivos Extraídos", result["extracted_files"])
                        with col2:
                            st.metric("Arquivos Processados", result["processed_files"])
                        with col3:
                            st.metric("Sucessos", result["successful"])
                        with col4:
                            st.metric("Falhas", result["failed"])
                        st.metric("Tempo Total", f"{result['total_time']:.2f}s")
                    elif result["status"] == "warning":
                        st.warning(f"⚠️ {result['message']}")
                    else:
                        st.error(f"❌ Erro ao processar ZIP: {result['error']}")

    elif upload_option == "📂 Múltiplos Arquivos":
        uploaded_files = st.file_uploader(
            "Selecione múltiplos arquivos",
            type=["pdf", "xml", "csv", "xls", "xlsx"],
            accept_multiple_files=True,
            help="Selecione vários arquivos para processar em lote",
        )

        if uploaded_files:
            st.write(f"**Arquivos selecionados:** {len(uploaded_files)}")
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name} ({file.size / 1024:.1f} KB)")

            if st.button("🚀 Processar Todos os Arquivos", type="primary"):
                file_paths = []
                for uploaded_file in uploaded_files:
                    file_path = save_uploaded_file(uploaded_file, "data")
                    file_type = get_supported_file_type(file_path)
                    if file_type:
                        file_paths.append(
                            {
                                "path": file_path,
                                "name": uploaded_file.name,
                                "type": file_type,
                                "size": uploaded_file.size,
                            }
                        )

                if file_paths:
                    with st.spinner(f"Processando {len(file_paths)} arquivos..."):
                        result = process_multiple_files(file_paths)
                        st.success("✅ Processamento em lote concluído!")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total", result["total_files"])
                        with col2:
                            st.metric("Sucessos", result["successful"])
                        with col3:
                            st.metric("Falhas", result["failed"])
                        with col4:
                            st.metric("Tempo", f"{result['total_time']:.2f}s")
                        with st.expander("📋 Detalhes dos Resultados"):
                            for i, file_result in enumerate(result["results"]):
                                if file_result["status"] == "success":
                                    st.success(
                                        f"✅ {file_result['file']} - {file_result['records']} registros"
                                    )
                                else:
                                    st.error(
                                        f"❌ {file_result['file']} - {file_result['error']}"
                                    )
                else:
                    st.warning("⚠️ Nenhum arquivo suportado encontrado!")


with tab2:
    st.header("🤖 Consultas com Inteligência Artificial (Chat)")
    st.info("💡 Converse sobre os dados já processados. Cada mensagem gera uma nova consulta ao modelo.")

    # Inicializa histórico de chat
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Olá! Faça uma pergunta sobre os dados processados."}
        ]

    # Renderiza histórico
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrada do usuário
    user_input = st.chat_input("Digite sua pergunta")
    if user_input:
        # Adiciona mensagem do usuário
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Mensagem de processamento
        with st.chat_message("assistant"):
            with st.spinner("Consultando modelo..."):
                resposta = answer_query(user_input)
                st.markdown(resposta)
        st.session_state.chat_messages.append({"role": "assistant", "content": resposta})

    # Limpar histórico
    if st.button("🧹 Limpar Chat"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Histórico limpo. Faça nova pergunta."}
        ]
        st.rerun()
    st.markdown("---")
    st.markdown("🔧 **Agente Extração** - Sistema de processamento de arquivos com IA")

with tab3:
    st.header("🗂 Gestão de Arquivos Processados")
    st.info("Visualize e remova arquivos já processados para que não sejam mais considerados em consultas.")

    # Carrega lista de arquivos
    arquivos = listar_arquivos()
    if not arquivos:
        st.warning("Nenhum arquivo processado ainda.")
    else:
        col_search, col_total = st.columns([3,1])
        with col_search:
            filtro = st.text_input("Filtrar por nome ou hash")
        with col_total:
            st.metric("Total", len(arquivos))

        if filtro:
            arquivos_filtrados = [a for a in arquivos if filtro.lower() in (str(a.get("file_name")) + str(a.get("file_hash"))).lower()]
        else:
            arquivos_filtrados = arquivos

        st.subheader(f"Registros ({len(arquivos_filtrados)})")
        for arq in arquivos_filtrados:
            exp_label = f"{arq.get('file_name') or 'SemNome'} | {arq.get('file_type') or '?'} | Registros: {arq.get('record_count')}"
            with st.expander(exp_label):
                col_info, col_actions = st.columns([4,1])
                with col_info:
                    st.write({k: v for k, v in arq.items() if k not in ("record_count",)})
                with col_actions:
                    if st.button("🗑", key=f"del_{arq['id']}", help="Remover este arquivo"):
                        sucesso = deletar_arquivo_por_id(arq['id'])
                        if sucesso:
                            st.success("Removido")
                            st.rerun()
                        else:
                            st.error("Erro ao remover")
                st.caption(f"Hash: {arq.get('file_hash')}")

                # Carregar dados completos sob demanda
                registro = obter_registro(arq['id'])
                if registro:
                    with st.expander("📄 Dados (JSON)"):
                        st.json(registro.get("conteudo"))
                        if registro.get("analise_campos"):
                            st.markdown("**Análise de Campos:**")
                            st.json(registro.get("analise_campos"))
                        if registro.get("metadata"):
                            st.markdown("**Metadata Completa:**")
                            st.json(registro.get("metadata"))

        st.caption("Remover um arquivo exclui seus dados e análises; consultas futuras não o incluirão.")
