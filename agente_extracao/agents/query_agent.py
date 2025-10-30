import os
import time
import sqlite3
from openai import OpenAI
from services.db_service import DB_PATH
from services.logging_service import logging_service

def get_database_info():
    """Obtém informações do banco de dados de forma otimizada"""
    try:
        conn = sqlite3.connect(DB_PATH)
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

def answer_query(query):
    """Responde uma query usando AI, seguindo lógica de instruções para uso de ferramentas (tools)"""
    start_time = time.time()
    try:
        db_info = get_database_info()
        if not db_info:
            return "❌ Erro ao acessar o banco de dados"

        # Monta análise resumida para o prompt
        analysis = (
            f"Total de registros: {db_info['total_records']}\n"
            f"Registros de exemplo: {db_info['sample_records']}\n"
            f"Comprimento médio dos registros: {db_info['average_content_length']}"
        )

        prompt = (
            f"Dados analisados: {analysis}\n"
            f"Pergunta: {query}\n"
            "\nResponda de forma clara, útil e em português brasileiro. Seja específico e forneça informações detalhadas.\n"
            "Resposta: "
        )

        api_key = os.getenv("API_KEY")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        completion = client.chat.completions.create(
            extra_body={},
            model=os.getenv("MODEL_NAME", "deepseek/deepseek-r1-0528:free"),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        response = completion.choices[0].message.content or "Erro ao obter resposta do LLM."
        response_time = time.time() - start_time
        logging_service.log_ai_query(query, response_time, success=True)
        
        return response
    
    except Exception as e:
        
        logging_service.log_application_error(f"Erro ao acessar banco de dados: {str(e)}")
        response_time = time.time() - start_time
        logging_service.log_ai_query(query, response_time, success=False)
        logging_service.log_application_error(f"Erro na query AI: {str(e)}")
        
        error_msg = str(e)
        if "Input required: specify" in error_msg:
            return "❌ Erro na configuração do LLM. Verifique sua API key."
        elif "API key" in error_msg.lower():
            return "❌ Erro de autenticação. Verifique sua API key."
        else:
            return f"❌ Erro ao processar a query: {error_msg}"