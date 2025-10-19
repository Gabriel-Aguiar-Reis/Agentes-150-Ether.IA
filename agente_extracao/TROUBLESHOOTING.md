# 🔧 Guia de Solução de Problemas

## Problemas Comuns e Soluções

### 1. **Erro de Importação de Módulos**

**Problema**: `ModuleNotFoundError` ou `ImportError`

**Soluções**:
```bash
# Instale as dependências
pip install -r requirements.txt

# Ou use a instalação mínima
pip install -r requirements-minimal.txt

# Ou execute o script de instalação
python install.py
```

### 2. **Erro de Versão do Python**

**Problema**: `Python version not supported`

**Solução**:
- Use Python 3.8 ou superior
- Verifique com: `python --version`

### 3. **Erro de Dependências do LangChain**

**Problema**: `langchain` imports failing

**Soluções**:
```bash
# Atualize o pip primeiro
pip install --upgrade pip

# Instale as dependências em ordem
pip install langchain>=0.1.0
pip install langchain-experimental>=0.0.50
pip install langchain-community>=0.0.20
pip install langchain-anthropic>=0.1.0
pip install langchain-google-genai>=1.0.0
```

### 4. **Erro de API Key**

**Problema**: `API key not found` ou `Authentication failed`

**Soluções**:
1. Crie um arquivo `.env` na raiz do projeto
2. Adicione suas API keys:
```env
OPENAI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

### 5. **Erro de Banco de Dados**

**Problema**: `Database not found` ou `SQLite error`

**Soluções**:
```bash
# Crie os diretórios necessários
mkdir data logs

# O banco será criado automaticamente na primeira execução
```

### 6. **Erro de Streamlit**

**Problema**: `streamlit not found`

**Solução**:
```bash
pip install streamlit>=1.28.0
```

### 7. **Erro de Processamento de Arquivos**

**Problema**: `File processing error`

**Soluções**:
- Verifique se os arquivos estão nos formatos suportados
- Verifique permissões de escrita na pasta `data/`
- Verifique se há espaço em disco suficiente

## 🚀 Instalação Passo a Passo

### Opção 1: Instalação Automática
```bash
python install.py
```

### Opção 2: Instalação Manual
```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Crie os diretórios
mkdir data logs

# 3. Configure as API keys (opcional)
cp .env.example .env
# Edite o arquivo .env com suas chaves

# 4. Execute a aplicação
streamlit run main.py
```

### Opção 3: Instalação Mínima
```bash
# Para problemas de dependências, use a versão mínima
pip install -r requirements-minimal.txt
streamlit run main.py
```

## 🔍 Verificação do Sistema

Execute o script de teste para verificar se tudo está funcionando:

```bash
python test_llm.py
```

Este script testará:
- ✅ Conexão com LLMs
- ✅ Processamento de arquivos
- ✅ Banco de dados
- ✅ Todas as dependências

## 📞 Suporte Adicional

Se ainda tiver problemas:

1. **Verifique os logs** em `logs/application.log`
2. **Execute o teste**: `python test_llm.py`
3. **Verifique as dependências**: `pip list`
4. **Verifique a versão do Python**: `python --version`

## 🐛 Logs de Debug

Para debug detalhado, verifique os arquivos em `logs/`:
- `application.log` - Logs gerais
- `file_processing.log` - Processamento de arquivos
- `database.log` - Operações de banco
- `ai_queries.log` - Consultas AI

