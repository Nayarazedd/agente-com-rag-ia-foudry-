[CONTEXT]
Preciso de uma aplicação web em Python com Streamlit para ser usada por estudantes em sala de aula.
Eles NÃO devem mexer no código ou na arquitetura. Eles usarão apenas a interface gráfica para consultar dados de unidades de um site.
A aplicação deve fazer o scraping/RAG em segundo plano do site "https://gratuitos.netlify.app/" e responder dúvidas do usuário (como endereços de unidades) usando a API da AZURE FOUNDRY (`openai/gpt`).

adicione conceitos de RETRIVEL E GENERATION NA APLICAÇÃO.  




[OBJECTIVE]
Gerar o código completo e executável do arquivo `app.py`. A aplicação deve:

1. Ter uma interface extremamente simples, limpa e intuitiva para o aluno.
2. Ocultar totalmente chaves de API, scripts de scraping e detalhes técnicos.
3. Conter um campo de texto para a dúvida e um botão visível "Buscar Unidade / Perguntar".
4. Fazer o scraping automático do site "https://gratuitos.netlify.app/" em cache (usando @st.cache_data) para não travar a navegação.
5. Enviar a pergunta do aluno junto com o contexto raspado para a API da Groq e exibir a resposta de forma clara na tela.

[STYLE]
Código Python production-ready, totalmente funcional, usando `streamlit`, `azure foundry`, `requests` e `beautifulsoup4`.

[TONE]
Direto, instrutivo e limpo.

[AUDIENCE]
Professor que vai rodar o servidor localmente (ou na nuvem) e disponibilizar apenas o link final do navegador para os estudantes usarem.

[RESPONSE FORMAT]
Entregue a resposta no seguinte formato:

1. Lista de comandos `pip install` necessários.
2. Código Python completo do `app.py`
3. Instruções curtas de como o professor deve rodar o projeto.
Sem textos teóricos ou introduções desnecessárias.
4. VARIAVES DO AMBIENTE DEVEM SE CHAMAR:
ENDPOINT = 
API_KEY = 
API_VERSION =
GPT5_MODEL = 
5. UTILIZE O CÓDIGO BASE, E INTRODUZA O WEBSCAPING, ACRESCENTE O RAG A UM pdf também, chamado arquivo.pdf.
6. 


----------------------- INTRODUZA AS MELHORIAS NO CÓDIGO ABAIXO -----------------------


import os
from dotenv import load_dotenv
from openai import AzureOpenAI, APIError
import sqlite3
import pandas as pd



dados_csv = pd.read_csv('dados.csv')

T =  pd.read_csv('tic.csv')



con = sqlite3.connect('banco.db')
cursor  =  con.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS vendas(
               
                 venda REAL,
                 vendedor TEXT,
                 id TEXT
                        

               
               
               )
''')

con.commit()


cursor.execute('INSERT INTO vendas VALUES(?,?,?)', (1000,'Thiago',1))
cursor.execute('INSERT INTO vendas VALUES(?,?,?)', (10000,'Maria',2))
cursor.execute('INSERT INTO vendas VALUES(?,?,?)', (1220,'Fernando',3))
cursor.execute('INSERT INTO vendas VALUES(?,?,?)', (1220,'Maria',4))

# crud
 
con.commit()


cursor.execute('SELECT * FROM vendas')
dados  =  cursor.fetchall()
contexto =  f'{dados[0]}, {dados[1]}, {dados[2]}'

lista  =  []

for x  in dados:
    lista.extend(x)

prompt = ''' 
----[DADOS 1]----
{dados_csv}
----[DADOS 2]----
{lista}
----[DADOS 3]----
{T}
'''

load_dotenv(override=True)

client = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT"),
    api_key=os.getenv("API_KEY"),
 
    api_version=os.getenv("API_VERSION", "2025-04-01-preview")
)


deployment_name = os.getenv("GPT5_MODEL")


def validar_configuracao():
    faltando = []
    if not os.getenv("ENDPOINT"):
        faltando.append("ENDPOINT")
    if not os.getenv("API_KEY"):
        faltando.append("API_KEY")
    if not deployment_name:
        faltando.append("GPT5_MODEL")

    if faltando:
        print("\n[Erro de configuração] As seguintes variáveis não foram definidas no .env:")
        for var in faltando:
            print(f"  - {var}")
        print("\nPreencha o arquivo .env e tente novamente.")
        return False
    return True


def main():
    if not validar_configuracao():
        return


    api_key = os.getenv("API_KEY", "")
    api_key_mascarada = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "(vazia ou muito curta)"
    # print(" diagnostico ... ")
    # print(f"ENDPOINT  : {os.getenv('ENDPOINT')!r}")
    # print(f"API_VERSION : {os.getenv('API_VERSION')!r}")
    # print(f"GPT5_MODEL: {os.getenv('GPT5_MODEL')!r}")
    # print(f"API_KEY : {api_key_mascarada}")
    # print("------------------------------------")

    print("--- Agente de Atendimento Iniciado ---")

    while True:
        pergunta = input("\nDigite sua pergunta ou sair: ").strip()

        if pergunta.lower() == "sair":
            print("Atendimento finalizado. Até logo!")
            break

        if not pergunta:
            print("Por favor, digite uma pergunta válida.")
            continue

        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": pergunta
                    }
                ]
  
            )

            resposta_texto = response.choices[0].message.content
            print(f"\nResposta:\n{resposta_texto}")

        except APIError as e:
        
            print(f"\n[Erro na API]: {e}")
        except Exception as e:
            print(f"\n[Erro inesperado]: {e}")


if __name__ == "__main__":
    main()