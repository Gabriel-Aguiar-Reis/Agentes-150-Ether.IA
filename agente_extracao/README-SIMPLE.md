# 📄 Agente Extração - Versão Simplificada

Sistema de processamento de arquivos com IA usando **apenas OpenRouter**.

## 🚀 Funcionalidades

- **Processamento de arquivos**: PDF, CSV, Excel, XML, ZIP
- **IA integrada**: Consultas em linguagem natural
- **OpenRouter**: Acesso a 100+ modelos de IA
- **Interface simples**: Fácil de usar
- **Configuração automática**: API key via interface ou ambiente

## ⚡ Instalação Rápida

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Execute a aplicação
streamlit run main.py
```

## 🔧 Configuração

### Opção 1: Via Interface (Recomendado)
1. Execute a aplicação
2. Na sidebar, insira sua OpenRouter API key
3. Escolha o modelo desejado
4. Pronto!

### Opção 2: Via Arquivo .env
```env
OPENROUTER_API_KEY=sua_api_key_aqui
```

## 🌐 Obter API Key do OpenRouter

1. Acesse [OpenRouter.ai](https://openrouter.ai/)
2. Faça login ou crie uma conta
3. Vá para "Keys" no dashboard
4. Clique em "Create Key"
5. Copie a chave gerada

## 📁 Formatos Suportados

- **PDF**: Extração de texto com análise por páginas
- **CSV**: Análise estrutural com estatísticas
- **Excel**: Suporte a múltiplas planilhas
- **XML**: Parsing hierárquico
- **ZIP**: Extração e processamento automático

## 🤖 Modelos Disponíveis

- **GPT-4**: `openai/gpt-4o`, `openai/gpt-4o-mini`
- **Claude**: `anthropic/claude-3.5-sonnet`, `anthropic/claude-3-opus`
- **Gemini**: `google/gemini-pro`
- **Llama**: `meta-llama/llama-3.1-70b-instruct`
- **Mistral**: `mistralai/mistral-7b-instruct`
- E muitos outros!

## 🧪 Teste a Instalação

```bash
python test_llm.py
```

## 💡 Vantagens do OpenRouter

- **100+ modelos** de diferentes provedores
- **Preços competitivos**
- **Interface unificada**
- **Fácil troca de modelos**
- **Sem necessidade de múltiplas API keys**

## 🔍 Como Usar

1. **Configure sua API key** (primeira vez)
2. **Faça upload de arquivos** (PDF, CSV, Excel, XML, ZIP)
3. **Faça perguntas** sobre os dados processados
4. **Obtenha respostas** em linguagem natural

## 🛠️ Solução de Problemas

### Erro de API Key
- Verifique se a API key está correta
- Teste a conexão com `python test_llm.py`

### Erro de Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro de Banco de Dados
- O banco é criado automaticamente
- Verifique permissões na pasta `data/`

## 📞 Suporte

- **Logs**: Verifique `logs/application.log`
- **Teste**: Execute `python test_llm.py`
- **Documentação**: Consulte `TROUBLESHOOTING.md`

---

**🎉 Pronto para usar!** Execute `streamlit run main.py` e comece a processar seus arquivos com IA!
