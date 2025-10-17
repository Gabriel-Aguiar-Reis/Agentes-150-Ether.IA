import os
import time
from langchain.llms import OpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from services.logging_service import logging_service
from services.config_service import config_service


def get_llm_instance():
    """Retorna instância do LLM baseada na configuração atual"""
    config = config_service.get_llm_config_for_langchain()
    
    if not config:
        # Fallback para OpenAI padrão
        return OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    provider = config['provider']
    model = config['model']
    api_key = config['api_key']
    
    if provider == "OpenAI":
        return OpenAI(model_name=model, openai_api_key=api_key, temperature=0)
    elif provider == "Anthropic":
        return ChatAnthropic(model=model, anthropic_api_key=api_key, temperature=0)
    elif provider == "Google":
        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0)
    else:
        # Fallback
        return OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))


def get_query_chain():
    db_path = os.getenv("DB_PATH", "data/banco.db")
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    llm = get_llm_instance()
    return SQLDatabaseChain.from_llm(llm, db, verbose=True)

def answer_query(query):
    """Responde uma query usando AI com logging"""
    start_time = time.time()
    
    try:
        chain = get_query_chain()
        response = chain.run(query)
        
        # Log do sucesso
        response_time = time.time() - start_time
        logging_service.log_ai_query(query, response_time, success=True)
        
        return response
        
    except Exception as e:
        # Log do erro
        response_time = time.time() - start_time
        logging_service.log_ai_query(query, response_time, success=False)
        logging_service.log_application_error(f"Erro na query AI: {str(e)}")
        
        return f"Erro ao processar a query: {str(e)}"

