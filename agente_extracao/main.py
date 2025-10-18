import streamlit as st
import os
import time
from services.file_service import (
    save_uploaded_file, 
    detect_file_type, 
    get_supported_file_type,
    detectar_tipo_arquivo,
    extract_zip_file, 
    create_temp_directory, 
    cleanup_temp_directory,
    get_supported_files_from_directory
)
from agents.workflow import process_file, process_multiple_files, process_zip_file
from agents.query_agent import answer_query
from services.logging_service import logging_service
from services.config_service import config_service
from dotenv import load_dotenv

# Carrega as variaveis do .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "data/banco.db")

# Inicializa logging
logging_service.log_application_start()

def main():
    st.set_page_config(
        page_title="Agente Extração - Processamento de Arquivos",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Agente Extração - Processamento de Arquivos com IA")
    st.markdown("---")
    
    # Sidebar com configurações e estatísticas
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Botão para configurar LLM
        if st.button("🔧 Configurar LLM", type="primary"):
            st.session_state.show_llm_config = True
        
        # Mostra LLM atual
        st.info(config_service.get_current_llm_info())
        
        st.markdown("---")
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
        except Exception as e:
            st.error(f"Erro ao carregar estatísticas: {str(e)}")
    
    # Modal de configuração do LLM
    if st.session_state.get('show_llm_config', False):
        with st.container():
            st.markdown("---")
            if config_service.show_config_modal():
                st.session_state.show_llm_config = False
                st.rerun()
    
    # Interface principal simplificada
    tab1, tab2 = st.tabs(["📁 Processamento de Arquivos", "❓ Consultas AI"])
    
    with tab1:
        st.header("📁 Processamento de Arquivos")
        st.info("💡 Suporte a PDF, CSV, Excel, XML e arquivos ZIP")
        
        # Opções de upload
        upload_option = st.radio(
            "Escolha o tipo de upload:",
            ["📄 Arquivo Único", "📦 Arquivo ZIP", "📂 Múltiplos Arquivos"],
            horizontal=True
        )
        
        if upload_option == "📄 Arquivo Único":

            uploaded_file = st.file_uploader(
                "Selecione um arquivo",
                type=["pdf", "xml", "csv", "xls", "xlsx"],
                help="Arquivos suportados: PDF, XML, CSV, Excel"
            )
            
            if uploaded_file:
                file_path = save_uploaded_file(uploaded_file, "data")
                        
                # Usa detecção melhorada de tipo
                file_type = get_supported_file_type(file_path)
                detected_type = detectar_tipo_arquivo(file_path)
                        
                if not file_type:
                    st.error(f"❌ Tipo de arquivo não suportado! Detectado: {detected_type}")
                    return
                        
                # Mostra informações do arquivo
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
                        else:
                            st.error(f"❌ Erro ao processar {result['file']}: {result['error']}")
        
        elif upload_option == "📦 Arquivo ZIP":

            uploaded_zip = st.file_uploader(
                "Selecione um arquivo ZIP",
                type=["zip"],
                help="O ZIP será extraído e todos os arquivos suportados serão processados"
            )
            
            if uploaded_zip:
                zip_path = save_uploaded_file(uploaded_zip, "data")
                
                # Mostra informações do ZIP
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Arquivo ZIP", uploaded_zip.name)
                with col2:
                    st.metric("Tamanho", f"{uploaded_zip.size / 1024:.1f} KB")
                
                if st.button("🚀 Processar ZIP", type="primary"):
                    with st.spinner(f"Processando ZIP {uploaded_zip.name}..."):
                        result = process_zip_file(zip_path)
                        
                        if result["status"] == "success":
                            st.success(f"✅ ZIP {result['zip_file']} processado com sucesso!")
                            
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
                help="Selecione vários arquivos para processar em lote"
            )
            
            if uploaded_files:
                # Mostra lista de arquivos
                st.write(f"**Arquivos selecionados:** {len(uploaded_files)}")
                for i, file in enumerate(uploaded_files, 1):
                    st.write(f"{i}. {file.name} ({file.size / 1024:.1f} KB)")
                
                if st.button("🚀 Processar Todos os Arquivos", type="primary"):
                    # Salva todos os arquivos
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        file_path = save_uploaded_file(uploaded_file, "data")
                        file_type = get_supported_file_type(file_path)
                        if file_type:
                            file_paths.append({
                                'path': file_path,
                                'name': uploaded_file.name,
                                'type': file_type,
                                'size': uploaded_file.size
                            })
                    
                    if file_paths:
                        with st.spinner(f"Processando {len(file_paths)} arquivos..."):
                            result = process_multiple_files(file_paths)
                            
                            st.success(f"✅ Processamento em lote concluído!")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total", result["total_files"])
                            with col2:
                                st.metric("Sucessos", result["successful"])
                            with col3:
                                st.metric("Falhas", result["failed"])
                            with col4:
                                st.metric("Tempo", f"{result['total_time']:.2f}s")
                            
                            # Mostra detalhes dos resultados
                            with st.expander("📋 Detalhes dos Resultados"):
                                for i, file_result in enumerate(result["results"]):
                                    if file_result["status"] == "success":
                                        st.success(f"✅ {file_result['file']} - {file_result['records']} registros")
                                    else:
                                        st.error(f"❌ {file_result['file']} - {file_result['error']}")
                    else:
                        st.warning("⚠️ Nenhum arquivo suportado encontrado!")
    
    with tab2:
        st.header("🤖 Consultas com Inteligência Artificial")
        st.info("💡 Faça perguntas sobre os dados processados usando linguagem natural")
        
        # Verifica se LLM está configurado
        config = config_service.get_current_config()
        if not config['configured']:
            st.warning("⚠️ Configure um LLM primeiro na sidebar para usar as consultas AI")
            if st.button("🔧 Configurar LLM Agora"):
                st.session_state.show_llm_config = True
                st.rerun()
        else:
            query = st.text_input(
                "Digite sua pergunta:",
                placeholder="Ex: Quantos registros temos? Qual é o arquivo mais recente?",
                help="Use linguagem natural para fazer perguntas sobre os dados"
            )
            
            if query:
                with st.spinner("Processando sua pergunta..."):
                    resposta = answer_query(query)
                    st.write("**Resposta:**")
                    st.write(resposta)
    
    # Footer
    st.markdown("---")
    st.markdown("🔧 **Agente Extração** - Sistema de processamento de arquivos com IA")

if __name__ == "__main__":
    main()

