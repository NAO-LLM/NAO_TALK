# -*- coding: utf-8 -*-
from naoqi import ALProxy
import os
import time
import socket
import json
import codecs


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



def main():
    # Loop para ativar chatbot do NAO
    n = True
    ip = ler_ip()
    port = 9559
    vol_NAO = 90
    # Configurar o local onde o arquivo de udio ser salvo no robô
    audio_file = "/home/nao/audio.wav"
    channels = [0, 0, 1, 0]  # Usando o microfone frontal


    while n:

        proxies = proxy_init(ip=ip,
                port=port)

        # Parar microfone
        proxies["audio_recorder"].stopMicrophonesRecording()

        # Para restaurar o volume (ajustar para 100, por exemplo)
        proxies["audio_device"].setOutputVolume(vol_NAO)

        detec_rosto(face_detection=proxies["face_detection"], 
                    memoryProxy=proxies["memory"])

        # Aviso do NAO de reconhecimento
        proxies["tts"].say("Estou te ouvindo")
        
        gravar_audio(audio_file=audio_file, proxies=proxies, channels=channels)
        
        # Transferir o arquivo para o seu PC e, em seguida, envi-lo para uma API de transcrico
        os.system("scp nao@{0}:{1} ./".format(ip, audio_file))
        time.sleep(0.5)

        # Para restaurar o volume (ajustar para 100, por exemplo)
        proxies["audio_device"].setOutputVolume(vol_NAO)

        # Ativa o Python 3
        var_resposta = nao_client()
        
        # Retornar
        print "Retornar mensagem do NAO"
        file_path = 'data.json'
        
        response = falar(file_path=file_path, 
                        tts=proxies["tts"])

        if response.lower() == "tchau":
            n = False

if __name__ == "__main__":
    main()