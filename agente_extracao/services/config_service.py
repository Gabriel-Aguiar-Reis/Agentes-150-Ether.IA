import streamlit as st
import os
from typing import Dict, Optional
from services.logging_service import logging_service

class ConfigService:
    """Serviço de configuração para LLM e API keys"""
    
    def __init__(self):
        self.llm_providers = {
            "Anthropic": {
                "name": "Anthropic",
                "api_key_env": "ANTHROPIC_API_KEY", 
                "models": ["claude-3-sonnet", "claude-3-opus", "claude-3-haiku"],
                "default_model": "claude-3-sonnet"
            },
            "Google": {
                "name": "Google",
                "api_key_env": "GOOGLE_API_KEY",
                "models": ["gemini-2.5-pro", "gemini-2.5-flash"],
                "default_model": "gemini-2.5-pro"
            },
            "OpenAI": {
                "name": "OpenAI",
                "api_key_env": "OPENAI_API_KEY",
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
                "default_model": "gpt-3.5-turbo"
            }
        }
    
    def get_current_config(self) -> Dict:
        """Retorna configuração atual do session state"""
        if 'llm_config' not in st.session_state:
            st.session_state.llm_config = {
                'provider': 'OpenAI',
                'model': 'gpt-3.5-turbo',
                'api_key': '',
                'configured': False
            }
        return st.session_state.llm_config
    
    def save_config(self, provider: str, model: str, api_key: str) -> bool:
        """Salva configuração do LLM"""
        try:
            # Valida se a chave não está vazia
            if not api_key.strip():
                st.error("❌ API Key não pode estar vazia!")
                return False
            
            # Atualiza session state
            st.session_state.llm_config = {
                'provider': provider,
                'model': model,
                'api_key': api_key,
                'configured': True
            }
            
            # Define variável de ambiente para a sessão
            provider_info = self.llm_providers[provider]
            os.environ[provider_info['api_key_env']] = api_key
            
            # Log da configuração
            logging_service.app_logger.info(
                f"LLM configurado: {provider} - {model}"
            )
            
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
        
        provider_info = self.llm_providers[config['provider']]
        
        return {
            'provider': config['provider'],
            'model': config['model'],
            'api_key': config['api_key'],
            'api_key_env': provider_info['api_key_env']
        }
    
    def show_config_modal(self) -> bool:
        """Mostra modal de configuração do LLM"""
        config = self.get_current_config()
        
        with st.form("llm_config_form"):
            st.subheader("🔧 Configuração do LLM")
            st.markdown("Configure qual LLM usar e sua API key:")
            
            # Seleção do provedor
            provider = st.selectbox(
                "Provedor LLM:",
                list(self.llm_providers.keys()),
                index=list(self.llm_providers.keys()).index(config['provider']) if config['provider'] in self.llm_providers else 0
            )
            
            # Seleção do modelo baseado no provedor
            provider_info = self.llm_providers[provider]            

            model = st.selectbox(
                "Modelo:",
                provider_info['models'],
                index=provider_info['models'].index(config['model']) if config['model'] in provider_info['models'] else 0
            )
            
            # Campo para API Key
            api_key = st.text_input(
                "API Key:",
                value=config['api_key'] if config['configured'] else "",
                type="password",
                help=f"Insira sua {provider} API Key"
            )
            
            # Informações sobre onde obter a API key
            with st.expander("ℹ️ Como obter sua API Key"):
                if provider == "OpenAI":
                    st.markdown("""
                    **OpenAI API Key:**
                    1. Acesse [OpenAI Platform](https://platform.openai.com/)
                    2. Faça login ou crie uma conta
                    3. Vá para "API Keys" no menu
                    4. Clique em "Create new secret key"
                    5. Copie a chave gerada
                    """)
                elif provider == "Anthropic":
                    st.markdown("""
                    **Anthropic API Key:**
                    1. Acesse [Anthropic Console](https://console.anthropic.com/)
                    2. Faça login ou crie uma conta
                    3. Vá para "API Keys"
                    4. Clique em "Create Key"
                    5. Copie a chave gerada
                    """)
                elif provider == "Google":
                    st.markdown("""
                    **Google API Key:**
                    1. Acesse [Google AI Studio](https://makersuite.google.com/)
                    2. Faça login com sua conta Google
                    3. Vá para "Get API Key"
                    4. Clique em "Create API Key"
                    5. Copie a chave gerada
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
                if self.save_config(provider, model, api_key):
                    st.success("✅ Configuração salva com sucesso!")
                    st.rerun()
                return True
            
            elif test_clicked:
                if api_key.strip():
                    # Testa a configuração
                    if self.test_llm_connection(provider, model, api_key):
                        st.success("✅ Conexão testada com sucesso!")
                    else:
                        st.error("❌ Falha na conexão. Verifique sua API Key.")
                else:
                    st.warning("⚠️ Insira uma API Key para testar.")
                return False
            
            elif cancel_clicked:
                return True
        
        return False
    
    def test_llm_connection(self, provider: str, model: str, api_key: str) -> bool:
        """Testa conexão com o LLM"""
        try:
            # Define temporariamente a API key
            provider_info = self.llm_providers[provider]
            original_key = os.environ.get(provider_info['api_key_env'])
            os.environ[provider_info['api_key_env']] = api_key
            
            # Testa conexão baseada no provedor
            if provider == "OpenAI":
                from langchain.llms import OpenAI
                llm = OpenAI(model_name=model, openai_api_key=api_key, temperature=0)
                response = llm("Teste de conexão")
                
            elif provider == "Anthropic":
                from langchain_anthropic import ChatAnthropic
                llm = ChatAnthropic(model=model, anthropic_api_key=api_key, temperature=0)
                response = llm.invoke("Teste de conexão")
                
            elif provider == "Google":
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0)
                response = llm.invoke("Teste de conexão")
            
            # Restaura API key original
            if original_key:
                os.environ[provider_info['api_key_env']] = original_key
            else:
                os.environ.pop(provider_info['api_key_env'], None)
            
            return True
            
        except Exception as e:
            logging_service.log_application_error(f"Erro ao testar conexão LLM: {str(e)}")
            return False
    
    def get_current_llm_info(self) -> str:
        """Retorna informação sobre o LLM atual"""
        config = self.get_current_config()
        if config['configured']:
            return f"🤖 {config['provider']} - {config['model']}"
        else:
            return "⚠️ LLM não configurado"

# Instância global do serviço de configuração
config_service = ConfigService()
