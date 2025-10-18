#!/usr/bin/env python3
"""
Script de instalação para o Agente Extração
Execute este script para instalar as dependências necessárias
"""

import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências do requirements.txt"""
    try:
        print("🔧 Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def install_minimal():
    """Instala apenas as dependências essenciais"""
    try:
        print("🔧 Instalando dependências mínimas...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-minimal.txt"])
        print("✅ Dependências mínimas instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências mínimas: {e}")
        return False

def check_python_version():
    """Verifica a versão do Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou superior é necessário!")
        print(f"Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True

def create_directories():
    """Cria diretórios necessários"""
    directories = ["data", "logs"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Diretório criado: {directory}")
        else:
            print(f"📁 Diretório já existe: {directory}")

def main():
    print("🚀 Instalador do Agente Extração")
    print("=" * 50)
    
    # Verifica versão do Python
    if not check_python_version():
        return
    
    # Cria diretórios
    create_directories()
    
    # Pergunta qual instalação fazer
    print("\nEscolha o tipo de instalação:")
    print("1. Instalação completa (recomendada)")
    print("2. Instalação mínima (apenas essencial)")
    print("3. Sair")
    
    choice = input("\nDigite sua escolha (1-3): ").strip()
    
    if choice == "1":
        if install_requirements():
            print("\n🎉 Instalação completa finalizada!")
            print("Execute: streamlit run main.py")
    elif choice == "2":
        if install_minimal():
            print("\n🎉 Instalação mínima finalizada!")
            print("Execute: streamlit run main.py")
    elif choice == "3":
        print("👋 Saindo...")
    else:
        print("❌ Escolha inválida!")

if __name__ == "__main__":
    main()

