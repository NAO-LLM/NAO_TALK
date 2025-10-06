# -*- coding: utf-8 -*-
from naoqi import ALProxy
import os
import time
import socket
import json
import codecs
from motions import taichi, disco, descansar, fazer_onda

# 2. Dicionario que mapeia o nome da animacao (do JSON) para a funcao correta
ACTION_MAP = {
    "taichi": taichi.execute_motion,
    "disco": disco.execute_motion,
    "descansar": descansar.execute_motion,
    "fazer_onda": fazer_onda.execute_motion,
}

# Criar um socket cliente
def nao_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Aguarda ate 10 segundos pelo servidor
    server_ready = False
    for _ in range(20):  # Tenta conectar por ate 10 segundos
        try:
            client_socket.connect(('127.0.0.1', 6006))  # Conecta ao servidor Python 3
            server_ready = True
            break
        except socket.error:
            print("Aguardando servidor Python 3...")
            time.sleep(0.5)

    if not server_ready:
        print("Erro: No foi possvel conectar ao servidor Python 3!")
        return None

    var_ativacao = "ok"  #Varivel de ativaco
    client_socket.send(var_ativacao.encode())  # Ativa o Python 3
    response = client_socket.recv(1024).decode('utf-8')  # Retorna a resposta do Python 3

    client_socket.close()
    return response

# Conectar ao NAO

# Lendo o IP do arquivo
def ler_ip(arquivo="ip.txt"):
    with open(arquivo, "r") as f:
        return f.read().strip()


def proxy_init(ip,port):
    print "Conectando ao NAO no IP: {}".format(ip)
    try:
        proxies = {
            "audio_recorder": ALProxy("ALAudioRecorder", ip, port),
            "face_detection": ALProxy("ALFaceDetection", ip, port),
            "memory": ALProxy("ALMemory", ip, port),
            "tts": ALProxy("ALTextToSpeech", ip, port),
            "audio_device": ALProxy("ALAudioDevice", ip, port)
        }
        print "Conexao com o NAO estabelecida com sucesso."
        return proxies
    except Exception as e:
        print "Erro ao conectar com o NAO: {}".format(e)
        return None


def detec_rosto(face_detection, memoryProxy):

    # Identificar rosto
    face_detection.subscribe("Test_face", 500, 0.0)
    memValue = "FaceDetected"

    # Loop para reconhecer rosto
    rosto_detectado = False
    while not rosto_detectado:
        # Verifica se houve alguma deteccao de rosto na memoria
        face_data = memoryProxy.getData(memValue)
        
        # Verifica se algum rosto foi detectado
        if face_data and isinstance(face_data, list) and len(face_data) > 0:
            print "Rosto detectado"
            rosto_detectado = True
        else:
            print "Nenhum rosto detectado."

        time.sleep(0.5)

def gravar_audio(proxies, audio_file, channels):
    # Silenciar o autofalante (definir volume para 0)
    proxies["audio_device"].setOutputVolume(0)

    # Comecar a gravar
    proxies["audio_recorder"].startMicrophonesRecording(audio_file, "wav", 16000, channels)

    # Aviso de gravacao
    print "Gravando."

    # Teste de decibeis
    for i in range(0, 8):
        time.sleep(0.5)
        som = proxies["audio_device"].getFrontMicEnergy()
        print som

    # Parar a gravaco
    proxies["audio_recorder"].stopMicrophonesRecording()

def falar(file_path, tts):
    """Abrir o arquivo JSON e carregar o conteudo em uma varivel Python (usando codecs para UTF-8)"""

    try:
        time.sleep(6)
        with codecs.open(file_path, 'r', 'utf-8') as file:
            json_data = json.load(file)
        response = json_data["message"].encode('utf-8')
        tts.say(response)
        return response
    except:
        tts.say("No Entendi")

def executar_plano(file_path, proxies):
    """
    Le o plano de acao do arquivo JSON e executa cada tarefa em sequencia.
    """
    print "Iniciando a execucao do plano de acoes..."
    try:
        # Aguarda um momento para garantir que o arquivo data.json foi escrito
        time.sleep(1)
        with codecs.open(file_path, 'r', 'utf-8') as f:
            plano_data = json.load(f)

        # Pega a lista de tarefas da chave "plan"
        lista_de_tarefas = plano_data.get("plan", [])
        if not lista_de_tarefas:
            proxies["tts"].say("Recebi um plano de acoes vazio.")
            return

        # Itera sobre cada tarefa da lista
        for tarefa in lista_de_tarefas:
            funcao = tarefa.get("function")
            args = tarefa.get("args")

            if funcao == "speak":
                # A acao de falar usa a proxy 'tts' que ja temos
                texto_para_falar = args.get("text", "").encode('utf-8')
                print "Executando tarefa [Falar]:", texto_para_falar
                proxies["tts"].say(texto_para_falar)

            elif funcao == "animate":
                # A acao de animar busca a funcao no ACTION_MAP
                nome_animacao = args.get("animation_name")
                print "Executando tarefa [Animar]:", nome_animacao
                if nome_animacao in ACTION_MAP:
                    # Chama a funcao de movimento importada.
                    # Conforme a restricao, nenhuma proxy de movimento e passada.
                    # O script da animacao (ex: taichi.py) e responsavel por si mesmo.
                    ACTION_MAP[nome_animacao]()
                else:
                    proxies["tts"].say("Desculpe, eu nao conheco a animacao {}.".format(nome_animacao).encode('utf-8'))
            
            # Uma pequena pausa entre as acoes para dar um ritmo melhor
            time.sleep(0.5)

    except Exception as e:
        print "Ocorreu um erro ao executar o plano:", e
        proxies["tts"].say("Desculpe, tive um problema ao tentar executar minhas acoes.")

def main():
    # Loop para ativar chatbot do NAO
    n = True
    ip = ler_ip()
    port = 9559
    vol_NAO = 90
    # Configurar o local onde o arquivo de audio sera salvo no robo
    audio_file = "/home/nao/audio.wav"
    channels = [0, 0, 1, 0]  # Usando o microfone frontal

    proxies = proxy_init(ip=ip, port=port)
    if not proxies:
        print "Nao foi possivel inicializar as proxies. Encerrando."
        return

    while n:
        # Garante que o microfone nao esteja gravando do ciclo anterior
        proxies["audio_recorder"].stopMicrophonesRecording()

        # Restaura o volume padrao
        proxies["audio_device"].setOutputVolume(vol_NAO)

        # 1. Detecta o rosto
        detec_rosto(face_detection=proxies["face_detection"],
                    memoryProxy=proxies["memory"])

        # Aviso do NAO de reconhecimento
        proxies["tts"].say("Estou te ouvindo")
        
        # 2. Grava o audio
        gravar_audio(audio_file=audio_file, proxies=proxies, channels=channels)
        
        # 3. Transfere o arquivo para o PC
        os.system("scp nao@{0}:{1} ./".format(ip, audio_file))
        time.sleep(0.5)

        # 4. Ativa o Python 3 (que cria o data.json)
        nao_client()
        
        # 5. Espera e executa o plano do data.json
        print "Aguardando e executando o plano do ambiente Python 3..."
        file_path = 'data.json'
        executar_plano(file_path=file_path, proxies=proxies)

        print "Ciclo de interacao concluido. Aguardando novo rosto..."
        # O loop continua para a proxima interacao

if __name__ == "__main__":
    main()