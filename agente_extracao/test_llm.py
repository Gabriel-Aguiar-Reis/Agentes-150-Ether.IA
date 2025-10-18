#!/usr/bin/env python3
"""
Script de teste para verificar a configuração do LLM
Execute este script para testar se sua configuração está funcionando
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_openrouter():
    """Testa OpenRouter"""
    try:
        from langchain.chat_models import ChatOpenAI
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("❌ OPENROUTER_API_KEY não encontrada no .env")
            print("💡 Configure a API key na aplicação ou no arquivo .env")
            return False
        
        llm = ChatOpenAI(
            model_name="openai/gpt-4o-mini",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0
        )
        response = llm.invoke("Olá, este é um teste")
        print(f"✅ OpenRouter funcionando: {response.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro no OpenRouter: {str(e)}")
        return False

def test_openai():
    """Testa OpenAI"""
    try:
        from langchain.chat_models import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY não encontrada no .env")
            return False
        
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key, temperature=0)
        response = llm.invoke("Olá, este é um teste")
        print(f"✅ OpenAI funcionando: {response.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro no OpenAI: {str(e)}")
        return False

def test_anthropic():
    """Testa Anthropic"""
    try:
        from langchain_anthropic import ChatAnthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ ANTHROPIC_API_KEY não encontrada no .env")
            return False
        
        llm = ChatAnthropic(model="claude-3-sonnet", anthropic_api_key=api_key, temperature=0)
        response = llm.invoke("Olá, este é um teste")
        print(f"✅ Anthropic funcionando: {response.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro no Anthropic: {str(e)}")
        return False

def test_google():
    """Testa Google"""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY não encontrada no .env")
            return False
        
        llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0)
        response = llm.invoke("Olá, este é um teste")
        print(f"✅ Google funcionando: {response.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro no Google: {str(e)}")
        return False

def test_sql_chain():
    """Testa SQLDatabaseChain"""
    try:
        from langchain.chat_models import ChatOpenAI
        from langchain_experimental.sql import SQLDatabaseChain
        from langchain_community.utilities import SQLDatabase
        
        # Cria banco de teste
        db_path = "data/banco.db"
        if not os.path.exists(db_path):
            print("❌ Banco de dados não encontrado. Execute a aplicação primeiro.")
            return False
        
        db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
        chain = SQLDatabaseChain.from_llm(llm, db, verbose=False)
        
        response = chain.run("Quantos registros existem na tabela?")
        print(f"✅ SQLDatabaseChain funcionando: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro no SQLDatabaseChain: {str(e)}")
        return False

def main():
    print("🔧 Testando configuração do OpenRouter...")
    print("=" * 50)
    
    # Testa OpenRouter
    openrouter_ok = test_openrouter()
    
    print("\n" + "=" * 50)
    print("🧪 Testando SQLDatabaseChain...")
    sql_ok = test_sql_chain()
    
    print("\n" + "=" * 50)
    print("📊 Resumo dos Testes:")
    print(f"OpenRouter: {'✅' if openrouter_ok else '❌'}")
    print(f"SQLDatabaseChain: {'✅' if sql_ok else '❌'}")
    
    if not openrouter_ok:
        print("\n⚠️ OpenRouter não configurado!")
        print("💡 Configure sua API key na aplicação ou no arquivo .env")
        print("🔗 Obtenha sua API key em: https://openrouter.ai/")
    elif not sql_ok:
        print("\n⚠️ SQLDatabaseChain com problemas!")
        print("Verifique se há dados no banco de dados")
    else:
        print("\n🎉 Tudo funcionando corretamente!")

if __name__ == "__main__":
    main()
