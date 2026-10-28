# 🤖 Assistente Virtual Unificado (RAG + Chatbot)

Aplicação desenvolvida com **Streamlit** e **Azure AI Foundry (OpenAI)** que atua como um assistente inteligente unificado. O sistema realiza consultas e cruzamento de dados em tempo real utilizando múltiplas fontes de conhecimento: raspagem de dados web, leitura de arquivos PDF, planilhas CSV locais e um banco de dados SQLite.

## 🚀 Funcionalidades
- **Interface de Chat Nativa**: Layout interativo em formato de chatbot utilizando os componentes modernos do Streamlit.
- **RAG Multi-Base (Retrieval-Augmented Generation)**:
  - Scraping automatizado de dados institucionais via BeautifulSoup (`https://gratuitos.netlify.app/`).
  - Leitura e extração de texto de documentos PDF (`arquivo.pdf`).
  - Análise de dados tabulares de múltiplos arquivos CSV (`dados.csv` e `tic.csv`).
  - Persistência e consulta em banco de dados relacional SQLite (`banco.db`).
- **Resiliência a Rate Limits**: Tratamento automático de erros HTTP 429 (excesso de tokens) com novas tentativas programadas.

## 🛠️ Tecnologias Utilizadas
- **Python** (Versão 3.10+)
- **Streamlit** (Interface gráfica web)
- **Azure OpenAI Client** (`openai`)
- **Pandas & SQLite3** (Manipulação e armazenamento de dados)
- **BeautifulSoup4 & pypdf** (Extração de conteúdo web e documentos)

## ⚙️ Configuração e Execução

1. **Clone o repositório ou abra a pasta no VS Code.**
2. **Instale as dependências** executando no terminal:
   ```bash
   pip install -r requirements.txt