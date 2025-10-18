# Agente Extração - Sistema de Processamento de Arquivos com IA

Sistema avançado de processamento de arquivos com suporte a múltiplos formatos e consultas em linguagem natural usando IA.

## 🚀 Funcionalidades Principais

### 1. **Suporte a Arquivos ZIP**
- Upload e extração automática de arquivos ZIP
- Processamento em lote de todos os arquivos suportados dentro do ZIP
- Limpeza automática de arquivos temporários

### 2. **Processamento de Múltiplos Arquivos**
- Upload simultâneo de vários arquivos
- Processamento em lote com estatísticas detalhadas
- Interface intuitiva com métricas de performance

### 3. **Sistema de Logging Avançado**
- Logs categorizados por funcionalidade
- Estatísticas em tempo real na interface
- Monitoramento de performance e erros
- Logs separados para diferentes operações

### 4. **Configuração Flexível de LLM**
- Suporte a múltiplos provedores (OpenRouter, OpenAI, Anthropic, Google)
- **OpenRouter**: Acesso a 100+ modelos de diferentes provedores
- Configuração segura de API keys
- Interface intuitiva para troca de LLM
- Teste de conexão integrado

### 5. **Detecção Inteligente de Arquivos**
- Análise de MIME types
- Detecção de PDF texto vs imagem
- Identificação automática de tipos de arquivo
- Suporte a múltiplos formatos Excel

## 📁 Formatos Suportados

- **PDF**: Extração de texto com análise por páginas
- **CSV**: Análise estrutural com estatísticas de colunas
- **Excel**: Suporte a múltiplas planilhas (.xls, .xlsx)
- **XML**: Parsing hierárquico com namespace
- **ZIP**: Extração e processamento automático

## 🛠️ Instalação

1. **Clone o repositório**
```bash
git clone <repository-url>
cd agente_extracao
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**
```bash
cp .env.template .env
# Edite o arquivo .env com suas configurações
```

4. **Execute a aplicação**
```bash
streamlit run main.py
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```env
OPENAI_API_KEY=your_openai_api_key_here
DB_PATH=data/banco.db
LOG_LEVEL=INFO
LOG_DIR=logs
```

### Estrutura de Logs
```
logs/
├── application.log      # Logs gerais da aplicação
├── file_processing.log # Logs de processamento de arquivos
├── database.log        # Logs de operações de banco
└── ai_queries.log      # Logs de consultas AI
```

## 📊 Interface do Usuário

### Interface Simplificada:
1. **📁 Processamento de Arquivos**: 
   - Upload único, ZIP ou múltiplos arquivos
   - Detecção inteligente de tipos
   - Processamento em lote
2. **❓ Consultas AI**: 
   - Perguntas em linguagem natural
   - Suporte a múltiplos LLMs

### Sidebar com Configurações:
- **🔧 Configurar LLM**: Botão para configurar provedor e API key
- **📊 Estatísticas**: Métricas em tempo real
- **🤖 LLM Atual**: Mostra configuração atual

### Configuração de LLM:
- **Provedores Suportados**: OpenRouter, OpenAI, Anthropic, Google
- **Modelos Disponíveis**: 
  - **OpenRouter**: 100+ modelos (GPT-4, Claude, Gemini, Llama, Mistral, etc.)
  - **OpenAI**: GPT-3.5/4, GPT-4 Turbo
  - **Anthropic**: Claude-3 Sonnet/Opus/Haiku
  - **Google**: Gemini Pro, Gemini Pro Vision
- **Segurança**: API keys armazenadas em sessão
- **Teste**: Validação de conexão integrada

## 🔍 Funcionalidades de Logging

### Tipos de Logs:
- **Upload de arquivos**: Nome, tipo, tamanho
- **Processamento**: Início, sucesso, falhas, tempo
- **ZIP**: Extração e arquivos processados
- **Lote**: Estatísticas de processamento em massa
- **Banco de dados**: Operações de inserção
- **AI**: Consultas e tempo de resposta

### Métricas Disponíveis:
- Tempo de processamento
- Número de registros inseridos
- Taxa de sucesso
- Estatísticas de uso

## 🧪 Testes

Execute os testes com:
```bash
pytest tests/ -v
```

## 📈 Performance

### Otimizações Implementadas:
- Processamento assíncrono de arquivos
- Limpeza automática de arquivos temporários
- Logging eficiente com rotação
- Interface responsiva com métricas em tempo real

## 🔒 Segurança

- Validação de tipos de arquivo
- Limpeza de diretórios temporários
- Logs de auditoria
- Tratamento de erros robusto

## 📝 Logs de Exemplo

```
2024-01-15 10:30:15 - file_processing - INFO - Arquivo enviado: documento.pdf | Tipo: pdf | Tamanho: 1024000 bytes
2024-01-15 10:30:16 - file_processing - INFO - Iniciando processamento: documento.pdf (pdf)
2024-01-15 10:30:18 - file_processing - INFO - Processamento concluído: documento.pdf | Registros: 150 | Tempo: 2.34s
2024-01-15 10:30:18 - database - INFO - DB INSERT: dados | Registros: 150
```

## 🚀 Próximas Melhorias

- [ ] Suporte a mais formatos de arquivo
- [ ] Processamento assíncrono
- [ ] Cache de resultados
- [ ] API REST
- [ ] Dashboard de monitoramento
- [ ] Notificações em tempo real

## 📞 Suporte

Para dúvidas ou problemas, consulte os logs em `logs/` ou abra uma issue no repositório.
