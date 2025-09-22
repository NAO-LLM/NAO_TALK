# -*- coding: utf-8 -*-
import subprocess
import os
import time
import speech_recognition as sr
import socket
import os
import json
import datetime


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


def salvar_conversa(pergunta, resposta):
    """Função que salva a pergunta e resposta no arquivo TXT"""
    global aux
    global file_path
    
    # Garante que a pasta Conversas/ existe
    if not os.path.exists("Conversas"):
        os.makedirs("Conversas")
    
    if aux == True: 
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"Conversas/conversa_{timestamp}.txt"
        aux = False

    if file_path:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(f"Pergunta: {pergunta}\n")
            file.write(f"Resposta: {resposta}\n")
            file.write("="*40 + "\n")