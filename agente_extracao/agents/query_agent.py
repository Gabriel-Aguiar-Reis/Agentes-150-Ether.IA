import os
import time
import sqlite3
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from services.logging_service import logging_service
from services.config_service import config_service


def get_llm_instance():
    """Retorna instância do OpenRouter LLM"""
    config = config_service.get_llm_config_for_langchain()
    
    if not config:
        # Fallback para OpenAI padrão se OpenRouter não estiver configurado
        return ChatOpenAI(
            model_name="gpt-3.5-turbo", 
            openai_api_key=os.getenv("OPENAI_API_KEY"), 
            temperature=0
        )
    
    model = config['model']
    api_key = config['api_key']
    
    # OpenRouter usa OpenAI-compatible API
    return ChatOpenAI(
        model_name=model,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )


def get_database_info_old():
    """Obtém informações do banco de dados"""
    try:
        db_path = os.getenv("DB_PATH", "data/banco.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtém informações da tabela
        cursor.execute("SELECT COUNT(*) FROM dados")
        total_records = cursor.fetchone()[0]
        
        # Obtém alguns registros de exemplo
        cursor.execute("SELECT conteudo FROM dados LIMIT 5")
        sample_records = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_records": total_records,
            "sample_records": [record[0] for record in sample_records]
        }
    except Exception as e:
        logging_service.log_application_error(f"Erro ao acessar banco de dados: {str(e)}")
        return None

def get_database_info():
    """Obtém informações do banco de dados de forma otimizada"""
    try:
        db_path = os.getenv("DB_PATH", "data/banco.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtém informações da tabela
        cursor.execute("SELECT COUNT(*) FROM dados")
        total_records = cursor.fetchone()[0]
        
        # Obtém apenas alguns registros de exemplo (limitados)
        cursor.execute("SELECT conteudo FROM dados LIMIT 3")
        sample_records = cursor.fetchall()
        
        # Trunca o conteúdo dos registros para evitar tokens excessivos
        truncated_records = []
        for record in sample_records:
            content = record[0]
            # Limita cada registro a 500 caracteres
            if len(content) > 500:
                content = content[:500] + "..."
            truncated_records.append(content)
        
        # Obtém estatísticas básicas
        cursor.execute("SELECT LENGTH(conteudo) FROM dados")
        lengths = [row[0] for row in cursor.fetchall()]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        conn.close()
        
        return {
            "total_records": total_records,
            "sample_records": truncated_records,
            "average_content_length": round(avg_length, 2)
        }
    except Exception as e:
        logging_service.log_application_error(f"Erro ao acessar banco de dados: {str(e)}")
        return None

def test_llm_connection():
    """Testa a conexão com o LLM configurado"""
    try:
        config = config_service.get_current_config()
        if not config['configured']:
            return False, "LLM não configurado"
        
        llm = get_llm_instance()
        response = llm.invoke("Teste de conexão")
        return True, "Conexão OK"
    except Exception as e:
        return False, str(e)


def answer_query(query):
    """Responde uma query usando AI com logging"""
    start_time = time.time()
    
    try:
        # Verifica se há configuração de LLM
        config = config_service.get_current_config()
        if not config['configured']:
            return "⚠️ Configure um LLM primeiro na sidebar para usar as consultas AI"
        
        # Testa conexão antes de processar
        connection_ok, connection_msg = test_llm_connection()
        if not connection_ok:
            return f"❌ Erro de conexão com o LLM: {connection_msg}"
        
        # Obtém informações do banco de dados
        db_info = get_database_info()
        if not db_info:
            return "❌ Erro ao acessar o banco de dados"
        
        # Cria prompt template em português
        prompt_template = """
        Você é um assistente especializado em análise de dados. 
        Use as informações fornecidas para responder à pergunta do usuário em português brasileiro.
        
        Informações do banco de dados:
        - Total de registros: {total_records}
        - Registros de exemplo: {sample_records}
        
        Pergunta do usuário: {question}
        
        Responda de forma clara, útil e em português brasileiro. Seja específico e forneça informações detalhadas.
        """
        
        prompt = PromptTemplate(
            input_variables=["total_records", "sample_records", "question"],
            template=prompt_template
        )
        
        # Cria chain
        llm = get_llm_instance()
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Executa a query
        response = chain.run(
            total_records=db_info["total_records"],
            sample_records=db_info["sample_records"],
            question=query
        )
        
        # Log do sucesso
        response_time = time.time() - start_time
        logging_service.log_ai_query(query, response_time, success=True)
        
        return response
        
    except Exception as e:
        # Log do erro
        response_time = time.time() - start_time
        logging_service.log_ai_query(query, response_time, success=False)
        logging_service.log_application_error(f"Erro na query AI: {str(e)}")
        
        # Retorna erro mais amigável
        error_msg = str(e)
        if "Input required: specify" in error_msg:
            return "❌ Erro na configuração do LLM. Verifique sua API key e tente reconfigurar o LLM."
        elif "API key" in error_msg.lower():
            return "❌ Erro de autenticação. Verifique sua API key."
        else:
            return f"❌ Erro ao processar a query: {error_msg}"