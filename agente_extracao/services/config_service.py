import streamlit as st
import os
from typing import Dict, Optional
from services.logging_service import logging_service

class ConfigService:
    """Serviço de configuração para LLM e API keys"""
    
    def __init__(self):
        # Simplified to only OpenRouter
        self.available_models = [
            "openai/gpt-4o",
            "openai/gpt-4o-mini", 
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-haiku",
            "google/gemini-pro",
            "google/gemini-pro-vision",
            "meta-llama/llama-3.1-405b-instruct",
            "meta-llama/llama-3.1-70b-instruct",
            "mistralai/mistral-7b-instruct",
            "microsoft/phi-3-medium-128k-instruct",
            "google/gemma-3-27b-it:free"
        ]
        self.default_model = "openai/gpt-4o-mini"
    
    def get_current_config(self) -> Dict:
        """Retorna configuração atual do session state"""
        if 'llm_config' not in st.session_state:
            # Check if API key exists in environment
            env_api_key = os.getenv("OPENROUTER_API_KEY")
            st.session_state.llm_config = {
                'model': self.default_model,
                'api_key': env_api_key or '',
                'configured': bool(env_api_key)
            }
        return st.session_state.llm_config
    
    def save_config(self, model: str, api_key: str) -> bool:
        """Salva configuração do LLM"""
        try:
            # Valida se a chave não está vazia
            if not api_key.strip():
                st.error("❌ API Key não pode estar vazia!")
                return False
            
            # Atualiza session state
            st.session_state.llm_config = {
                'model': model,
                'api_key': api_key,
                'configured': True
            }
            
            # Define variável de ambiente para a sessão
            os.environ["OPENROUTER_API_KEY"] = api_key
            
            # Log da configuração
            logging_service.app_logger.info(f"OpenRouter configurado: {model}")
            
            return True
            
        except Exception as e:
            logging_service.log_application_error(f"Erro ao salvar configuração: {str(e)}")
            st.error(f"❌ Erro ao salvar configuração: {str(e)}")
            return False
    
    def get_llm_config_for_langchain(self) -> Dict:
        """Retorna configuração formatada para LangChain"""
        config = self.get_current_config()
        
        if not config['configured']:
            return None
        
        return {
            'model': config['model'],
            'api_key': config['api_key']
        }
    
    def show_config_modal(self) -> bool:
        """Mostra modal de configuração do LLM"""
        config = self.get_current_config()
        
        with st.form("llm_config_form"):
            st.subheader("🔧 Configuração do OpenRouter")
            st.markdown("Configure o modelo e sua API key do OpenRouter:")
            
            # Seleção do modelo
            model = st.selectbox(
                "Modelo:",
                self.available_models,
                index=self.available_models.index(config['model']) if config['model'] in self.available_models else 0
            )
            
            # Campo para API Key
            api_key = st.text_input(
                "OpenRouter API Key:",
                value=config['api_key'] if config['configured'] else "",
                type="password",
                help="Insira sua OpenRouter API Key"
            )
            
            # Informações sobre onde obter a API key
            with st.expander("ℹ️ Como obter sua OpenRouter API Key"):
                st.markdown("""
                **OpenRouter API Key:**
                1. Acesse [OpenRouter](https://openrouter.ai/)
                2. Faça login ou crie uma conta
                3. Vá para "Keys" no dashboard
                4. Clique em "Create Key"
                5. Copie a chave gerada
                
                **Vantagens do OpenRouter:**
                - Acesso a 100+ modelos de diferentes provedores
                - Preços competitivos
                - Interface unificada
                - Modelos como GPT-4, Claude, Gemini, Llama, etc.
                """)
            
            # Botões de ação
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                save_clicked = st.form_submit_button("💾 Salvar", type="primary")
            
            with col2:
                test_clicked = st.form_submit_button("🧪 Testar")
            
            with col3:
                cancel_clicked = st.form_submit_button("❌ Cancelar")
            
            # Processa ações
            if save_clicked:
                if self.save_config(model, api_key):
                    st.success("✅ Configuração salva com sucesso!")
                    st.rerun()
                return True
            
            elif test_clicked:
                if api_key.strip():
                    # Testa a configuração
                    if self.test_llm_connection(model, api_key):
                        st.success("✅ Conexão testada com sucesso!")
                    else:
                        st.error("❌ Falha na conexão. Verifique sua API Key.")
                else:
                    st.warning("⚠️ Insira uma API Key para testar.")
                return False
            
            elif cancel_clicked:
                return False
        
        return False
    
    def test_llm_connection(self, model: str, api_key: str) -> bool:
        """Testa conexão com o OpenRouter"""
        try:
            from langchain.chat_models import ChatOpenAI
            
            # Testa conexão com OpenRouter
            llm = ChatOpenAI(
                model_name=model,
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=0
            )
            response = llm.invoke("Teste de conexão")
            return True
            
        except Exception as e:
            logging_service.log_application_error(f"Erro ao testar conexão OpenRouter: {str(e)}")
            return False
    
    def get_current_llm_info(self) -> str:
        """Retorna informação sobre o LLM atual"""
        config = self.get_current_config()
        if config['configured']:
            return f"🤖 OpenRouter - {config['model']}"
        else:
            return "⚠️ OpenRouter não configurado"

# Instância global do serviço de configuração
config_service = ConfigService()


