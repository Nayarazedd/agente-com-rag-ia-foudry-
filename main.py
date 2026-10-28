import os
import sqlite3
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI, APIError

load_dotenv(override=True)

client = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT"),
    api_key=os.getenv("API_KEY"),
    api_version=os.getenv("API_VERSION", "2025-04-01-preview")
)
deployment_name = os.getenv("GPT5_MODEL")

# --- GERENCIAMENTO DE MEMÓRIA (BANCO DE DADOS DE HISTÓRICO) ---
def inicializar_banco_historico():
    con = sqlite3.connect('chat_history.db')
    cursor = con.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    ''')
    con.commit()
    con.close()

def salvar_mensagem(role, content):
    con = sqlite3.connect('chat_history.db')
    cursor = con.cursor()
    cursor.execute('INSERT INTO historico (role, content) VALUES (?, ?)', (role, content))
    con.commit()
    con.close()

def carregar_historico():
    con = sqlite3.connect('chat_history.db')
    cursor = con.cursor()
    cursor.execute('SELECT role, content FROM historico')
    mensagens = cursor.fetchall()
    con.close()
    return [{"role": r, "content": c} for r, c in mensagens]

# --- FUNÇÕES DE RETRIEVAL (RAG & SCRAPING) ---

@st.cache_data
def raspar_site():
    url = "https://gratuitos.netlify.app/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text(separator="\n", strip=True)[:3000]
    except Exception as e:
        return f"Erro ao acessar o site: {e}"

@st.cache_data
def ler_pdf():
    caminho_pdf = "arquivo.pdf"
    if not os.path.exists(caminho_pdf):
        return "Arquivo PDF não encontrado."
    try:
        reader = PdfReader(caminho_pdf)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or ""
        return texto[:3000]
    except Exception as e:
        return f"Erro ao ler o PDF: {e}"

def carregar_dados_locais():
    try:
        dados_csv = pd.read_csv('dados.csv').head(50).to_string()
    except Exception:
        dados_csv = "dados.csv não encontrado."

    try:
        t_csv = pd.read_csv('tic.csv').head(50).to_string()
    except Exception:
        t_csv = "tic.csv não encontrado."

    try:
        con = sqlite3.connect('banco.db')
        cursor = con.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS vendas(
                         venda REAL,
                         vendedor TEXT,
                         id TEXT)''')
        con.commit()
        cursor.execute('SELECT * FROM vendas')
        dados_db = str(cursor.fetchall())
        con.close()
    except Exception:
        dados_db = "Banco de dados vazio ou não encontrado."

    return dados_csv, t_csv, dados_db

# --- APLICAÇÃO STREAMLIT ---

def main():
    st.set_page_config(page_title="Agente IA - Atendimento", page_icon="🤖", layout="centered")

    st.title("🤖 Agente Virtual Inteligente")
    st.write("Faça suas perguntas sobre unidades, documentos e dados institucionais.")

    # Inicializa o banco de memória de chat
    inicializar_banco_historico()

    # Carrega bases de conhecimento
    dados_csv, t_csv, dados_db = carregar_dados_locais()
    conteudo_site = raspar_site()
    conteudo_pdf = ler_pdf()

    # Contexto unificado do sistema
    prompt_sistema = f"""
Você é um assistente de atendimento inteligente. Responda à dúvida do usuário utilizando EXCLUSIVAMENTE os contextos abaixo:

----[DADOS DO SITE]----
{conteudo_site}

----[CONTEÚDO DO PDF]----
{conteudo_pdf}

----[DADOS DO CSV 1]----
{dados_csv}

----[DADOS DO CSV 2]----
{t_csv}

----[BANCO DE DADOS DE VENDAS]----
{dados_db}
"""

    # Recupera o histórico salvo no banco de dados SQLite
    historico = carregar_historico()

    # Exibe as mensagens anteriores com rolagem automática na interface
    for mensagem in historico:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    # Campo de entrada de chat do Streamlit (substitui o text_input comum e fica fixo embaixo)
    if pergunta := st.chat_input("Digite sua dúvida ou endereço desejado..."):
        if not os.getenv("ENDPOINT") or not os.getenv("API_KEY") or not deployment_name:
            st.error("Erro de configuração: Variáveis de ambiente da Azure ausentes.")
            return

        # Adiciona a mensagem do usuário na tela e salva no banco de dados de memória
        with st.chat_message("user"):
            st.markdown(pergunta)
        salvar_mensagem("user", pergunta)

        # Prepara o payload de mensagens incluindo o histórico recente para o agente ter memória conversacional
        mensagens_api = [{"role": "system", "content": prompt_sistema}]
        for m in historico[-6:]: # Mantém as últimas 6 interações no contexto da API para poupar tokens
            mensagens_api.append({"role": m["role"], "content": m["content"]})
        mensagens_api.append({"role": "user", "content": pergunta})

        max_tentativas = 3
        resposta_texto = ""

        for tentativa in range(max_tentativas):
            try:
                with st.spinner("Agente pensando..."):
                    response = client.chat.completions.create(
                        model=deployment_name,
                        messages=mensagens_api,
                        max_tokens=800
                    )
                    resposta_texto = response.choices[0].message.content
                    break
            except APIError as e:
                if getattr(e, 'status_code', None) == 429 or "429" in str(e):
                    if tentativa < max_tentativas - 1:
                        time.sleep(5)
                    else:
                        resposta_texto = "O limite de tokens da API foi atingido. Tente novamente em instantes."
                else:
                    resposta_texto = f"Erro na API Azure: {e}"
                    break
            except Exception as e:
                resposta_texto = f"Erro inesperado: {e}"
                break

        # Exibe a resposta do assistente e salva na memória persistente
        with st.chat_message("assistant"):
            st.markdown(resposta_texto)
        salvar_mensagem("assistant", resposta_texto)

if __name__ == "__main__":
    main()