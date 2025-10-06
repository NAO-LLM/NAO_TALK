# -*- coding: utf-8 -*-
import subprocess
import os
import time
import speech_recognition as sr
import socket
import os
import json
import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Definição das ferramentas que o NAO pode usar
tools = [
    {
        "name": "speak",
        "description": "Use esta ferramenta para falar uma frase. O argumento é o texto que o robô deve dizer.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "O texto que o robô deve verbalizar."
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "animate",
        "description": "Use esta ferramenta para executar uma animação física, postura ou dança no robô. Use para ações como acenar, chutar, dançar ou descansar.",
        "parameters": {
            "type": "object",
            "properties": {
                "animation_name": {
                    "type": "string",
                    "description": "O nome da animação a ser executada.",
                    "enum": [
                        "fazer_onda", "chutar", "elefante", "saxofone",
                        "tirar_foto", "taichi", "disco", "descansar",
                        "levantar", "sentar"
                    ]
                }
            },
            "required": ["animation_name"]
        }
    }
]


# Prompt do sistema para o agente ReAct
system_prompt = f"""
Você é a mente de um robô NAO. Seu objetivo é interagir com humanos de forma útil e divertida.
Você não responde diretamente ao usuário. Em vez disso, você gera um plano de ações para o robô executar.
O plano deve ser uma lista de comandos no formato JSON.

As ferramentas disponíveis são:
{json.dumps(tools, indent=2)}

Siga estritamente o seguinte processo:
1.  **Pensamento:** Analise a solicitação do usuário e pense em uma sequência de ações (falar e animar) para responder de forma eficaz e envolvente.
2.  **Plano:** Converta seu pensamento em um plano de ação JSON. O plano final deve estar dentro de um objeto JSON com uma única chave "plan".

Exemplo 1:
Usuário: "Olá, tudo bem?"
Pensamento: "O usuário me cumprimentou. Devo cumprimentá-lo de volta com um aceno e depois responder verbalmente que estou bem."
Plano:
{{
  "plan": [
    {{
      "function": "animate",
      "args": {{"animation_name": "fazer_onda"}}
    }},
    {{
      "function": "speak",
      "args": {{"text": "Olá! Tudo ótimo por aqui. Como posso ajudar?"}}
    }}
  ]
}}

Exemplo 2:
Usuário: "Você sabe lutar?"
Pensamento: "O usuário perguntou sobre minhas habilidades de luta. Posso responder verbalmente e depois demonstrar um movimento de Tai Chi para impressioná-lo."
Plano:
JSON

{{
  "plan": [
    {{
      "function": "speak",
      "args": {{"text": "Eu conheço alguns movimentos de artes marciais. Veja só!"}}
    }},
    {{
      "function": "animate",
      "args": {{"animation_name": "taichi"}}
    }}
  ]
}}

Agora, analise a entrada do usuário e gere o plano de ação.
"""

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Modelo Gemini a ser utilizado
llm = genai.GenerativeModel('gemini-2.5-flash')

def carregar_ou_iniciar_historico(caminho_arquivo, system_prompt):
    """
    Carrega o histórico de um arquivo JSON. Se o arquivo não existir,
    cria um novo histórico com a instrução de sistema.
    """
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # O histórico começa com a instrução de sistema
        return [{"role": "user", "parts": [system_prompt]}]

def salvar_historico(caminho_arquivo, historico):
    """Salva o histórico da conversa em um arquivo JSON."""
    # Garante que o diretório exista
    os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)

def run_react_agent(user_prompt, historico):
    """
    Executa o agente ReAct usando um histórico de conversa para manter o contexto.
    """
    print("--- AGENTE ReAct (com Histórico) ---")
    print(f"Recebido do usuário: {user_prompt}")

    # Adiciona a nova mensagem do usuário ao histórico
    historico.append({"role": "user", "parts": [user_prompt]})

    try:
        # Inicia uma sessão de chat com o histórico existente
        chat = llm.start_chat(history=historico)

        # Envia a última mensagem (que é a do usuário)
        # Como já adicionamos ao histórico, podemos apenas enviar a última parte
        response = chat.send_message(historico[-1]['parts'])

        json_text = response.text.split('```json')[1].split('```')[0].strip()
        plan_dict = json.loads(json_text)

        print(f"Plano recebido do LLM: {json.dumps(plan_dict, indent=2)}")

        # Adiciona a resposta do modelo (o plano) ao histórico para a próxima rodada
        historico.append({"role": "model", "parts": [json.dumps(plan_dict)]})

        # Retorna a string do plano para execução e o histórico completo atualizado
        return json.dumps(plan_dict, indent=4, ensure_ascii=False), historico

    except Exception as e:
        print(f"Um erro ocorreu ao chamar a API do Gemini ou processar a resposta: {e}")

    # Plano de fallback em caso de erro
    fallback_plan = {
        "plan": [
            {"function": "speak", "args": {"text": "Desculpe, tive um problema ao processar sua solicitação."}}
        ]
    }
    # Adiciona a resposta de fallback ao histórico
    historico.append({"role": "model", "parts": [json.dumps(fallback_plan)]})
    return json.dumps(fallback_plan, indent=4, ensure_ascii=False), historico

def llm_server():
    """FUNÇÃO QUE ESTABELECE CONEXÃO COM O NAO ATRAVÉS DE UM SOCKET SERVIDOR."""


    #cria e configura o servidor socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 6006))  # Abre o servidor na porta 6000
    server_socket.listen(1)
    print("Servidor aguardando conexões")


    #aguarda a conexão com o  NAO
    conn, addr = server_socket.accept()
    print(f"Connected to: {addr}")


    #sinal de ativação
    var_ativacao = conn.recv(1024).decode()
    print(f"Received from Python 2.7: {var_ativacao}")


    var_resposta = ('ok')
    conn.send(var_resposta.encode('utf-8'))

MAC_NAO = "b8-b7-f1-15-f7-75"

def get_ip_from_arp(mac_address):
    try:
        cmd = f'arp -a | findstr "{mac_address}"'
        returned_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        linha = returned_output.decode('latin1').strip()
        ip = linha.split()[0]
        print(f"IP do NAO encontrado: {ip}")
        return ip
    except subprocess.CalledProcessError:
        print("MAC do NAO não encontrado.")
        return None

def salvar_ip(ip, arquivo="ip.txt"):
    with open(arquivo, "w") as f:
        f.write(ip)

def audio_to_text(audio_file):
    """FUNÇÃO QUE TRANSFORMA UM ARQUIVO DE ÁUDIO WAV EM TEXTO
    PARÂMETRO = ARQUIVO DE ÁUDIO
    SAÍDA = TEXTO TRANSCRITO
    """

    #Cria o objeto que realiza o reconhecimento
    r = sr.Recognizer()


    # Carrega o arquivo de áudio
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)


    try:
        # Realiza o reconhecimento de fala
        text = r.recognize_google(audio, language='pt-BR')  # Substitua 'pt-BR' pelo idioma desejado
        return text
    

    #tratamentos de erros
    except sr.UnknownValueError:
        print("Não foi possível reconhecer o áudio")
        return "Fale: Eu não entendi"
    
    except sr.RequestError as e:
        print("Erro do serviço de reconhecimento de fala; {0}".format(e))
