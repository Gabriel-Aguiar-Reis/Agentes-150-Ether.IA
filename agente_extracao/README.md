# Agente Extração - Sistema de Processamento de Arquivos com IA

> Sistema para processamento inteligente de arquivos (PDF, CSV, Excel, XML, ZIP) e consultas em linguagem natural via IA. Interface web via Streamlit.

## 🚀 Funcionalidades

- Upload e processamento de arquivos únicos, múltiplos ou ZIP
- Detecção automática de tipo de arquivo
- Processamento em lote com métricas detalhadas
- Consultas em linguagem natural sobre os dados processados
- Logging avançado por operação
- Suporte a OpenRouter para múltiplos modelos LLM (OpenAI, Anthropic, Google)

## 📁 Estrutura do Projeto

```plain_text
agente_extracao/
├── main.py                  # Interface Streamlit
├── agents/                  # Lógica dos agentes de processamento
│   ├── db_agent.py
│   ├── formatter_agent.py
│   ├── query_agent.py
│   ├── reader_agent.py
│   └── workflow.py
├── logs/                    # Logs da aplicação
│   ├── application.log
│   ├── file_processing.log
│   ├── database.log
│   └── ai_queries.log
├── services/                # Serviços de apoio (DB, arquivos, logging)
│   ├── db_service.py
│   ├── file_service.py
│   └── logging_service.py
├── requirements.txt         # Dependências completas
├── README.md                # Este arquivo
```

## 🛠️ Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/Gabriel-Aguiar-Reis/Agentes-150-Ether.IA
   cd agente_extracao
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente (crie um arquivo `.env` na raiz):

   ```env
   API_KEY="sua_chave_api"
   MODEL_NAME="seu_modelo_preferido"
   ```

4. Execute a aplicação:

   ```bash
   streamlit run main.py
   ```

## 📊 Interface

- Upload de arquivos (único, múltiplos, ZIP)
- Métricas de processamento em tempo real
- Consultas AI em linguagem natural
- Estatísticas e logs na sidebar

## Logs

Os logs ficam em `logs/`:

- `application.log` - Geral
- `file_processing.log` - Processamento de arquivos
- `database.log` - Banco de dados
- `ai_queries.log` - Consultas AI

## 📞 Suporte

Em caso de dúvidas, verifique os logs ou abra uma issue.
