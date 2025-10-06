# -*- coding: utf-8 -*-
import math
from naoqi import ALProxy

# Importe os movimentos
from motions.taichi import execute_motion

# Variável Global para as Proxies 
# As proxies serão armazenadas aqui após a inicialização.
_GLOBAL_PROXIES = None


#Função de Inicialização das Proxies 

def iniciar_proxies_movimento(ip, port):
    """
    Inicia a conexão com o robô NAO e armazena as proxies de movimento em uma variável global.
    """
    global _GLOBAL_PROXIES  # Declara que estamos modificando a variável global
    print("Conectando ao NAO no IP: {}".format(ip))
    try:
        proxies = {
            "motion_proxy": ALProxy("ALMotion", ip, port),
            "posture_proxy": ALProxy("ALRobotPosture", ip, port),
            "text_to_speech_proxy": ALProxy("ALTextToSpeech", ip, port),
            "audio_player_proxy": ALProxy("ALAudioPlayer", ip, port),
            "camera_proxy": ALProxy("ALVideoDevice", ip, port),
            "auto_life_proxy": ALProxy("ALAutonomousLife", ip, port),
            "audio_proxy": ALProxy("ALAudioDevice", ip, port)
        }
        
        proxies['auto_life_proxy'].setAutonomousAbilityEnabled("All", False)
        proxies['motion_proxy'].wakeUp()
        proxies['text_to_speech_proxy'].say("Olá, eu sou Nao.")
        
        _GLOBAL_PROXIES = proxies  # Atribui o dicionário à variável global
        print("Conexão com o NAO estabelecida e proxies de movimento prontas.")
        return True
    except Exception as e:
        print("Erro ao conectar com o NAO: {}".format(e))
        _GLOBAL_PROXIES = None
        return False

#Ferramentas (Tools) com o decorador @tool 


def fazer_onda():
    """
    Faz o NAO realizar um movimento de onda.
    """
    if _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES and 'text_to_speech_proxy' in _GLOBAL_PROXIES and 'posture_proxy' in _GLOBAL_PROXIES:
        wave.wave(_GLOBAL_PROXIES['motion_proxy'], _GLOBAL_PROXIES['text_to_speech_proxy'])
        _GLOBAL_PROXIES['posture_proxy'].goToPosture("StandInit", 0.5)
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")

def chutar():
    """
    Faz o NAO realizar um movimento de chute.
    """
    if _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES and 'posture_proxy' in _GLOBAL_PROXIES:
        kick.kick(_GLOBAL_PROXIES['motion_proxy'])
        _GLOBAL_PROXIES['posture_proxy'].goToPosture("StandInit", 0.5)
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")

def elefante():
    """
    Faz o NAO realizar a dança do elefante.
    """
    if _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES and 'audio_player_proxy' in _GLOBAL_PROXIES and 'posture_proxy' in _GLOBAL_PROXIES:
        elephant.elephant(_GLOBAL_PROXIES['motion_proxy'], _GLOBAL_PROXIES['audio_player_proxy'])
        _GLOBAL_PROXIES['posture_proxy'].goToPosture("StandInit", 0.5)
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")

def saxofone():
    """
    Faz o NAO simular que está tocando saxofone.
    """
    if _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES and 'audio_player_proxy' in _GLOBAL_PROXIES and 'posture_proxy' in _GLOBAL_PROXIES:
        saxophone.saxophone(_GLOBAL_PROXIES['motion_proxy'], _GLOBAL_PROXIES['audio_player_proxy'])
        _GLOBAL_PROXIES['posture_proxy'].goToPosture("StandInit", 0.5)
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")

def tirar_foto():
    """
    Faz o NAO tirar uma foto.
    """
    if _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES and 'audio_player_proxy' in _GLOBAL_PROXIES and 'camera_proxy' in _GLOBAL_PROXIES and 'posture_proxy' in _GLOBAL_PROXIES:
        picture.take_picture(_GLOBAL_PROXIES['motion_proxy'], _GLOBAL_PROXIES['audio_player_proxy'], _GLOBAL_PROXIES['camera_proxy'])
        _GLOBAL_PROXIES['posture_proxy'].goToPosture("StandInit", 0.5)
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")

def taichi():
    """
    Faz o NAO realizar movimentos de Tai Chi. Que são movimentos de kung-fu
    """
    if _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES and 'posture_proxy' in _GLOBAL_PROXIES:
        execute_motion(_GLOBAL_PROXIES['motion_proxy'])
        _GLOBAL_PROXIES['posture_proxy'].goToPosture("StandInit", 0.5)
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")

def disco():
    """
    Faz o NAO realizar uma dança disco.
    """
    if _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES and 'posture_proxy' in _GLOBAL_PROXIES:
        disco.disco(_GLOBAL_PROXIES['motion_proxy'])
        _GLOBAL_PROXIES['posture_proxy'].goToPosture("StandInit", 0.5)
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")

def descansar():
    """
    Faz o NAO ir para a postura de descanso.
    """
    if _GLOBAL_PROXIES and 'text_to_speech_proxy' in _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES:
        _GLOBAL_PROXIES['text_to_speech_proxy'].say("Até mais")
        _GLOBAL_PROXIES['motion_proxy'].rest()
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")

def levantar():
    """
    Faz o NAO se levantar.
    """
    if _GLOBAL_PROXIES and 'text_to_speech_proxy' in _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES:
        _GLOBAL_PROXIES['text_to_speech_proxy'].say("Levantando")
        _GLOBAL_PROXIES['motion_proxy'].wakeUp()
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")
        
def sentar():
    """
    Faz o NAO se sentar.
    """
    if _GLOBAL_PROXIES and 'text_to_speech_proxy' in _GLOBAL_PROXIES and 'motion_proxy' in _GLOBAL_PROXIES:
        _GLOBAL_PROXIES['text_to_speech_proxy'].say("Sentando")
        _GLOBAL_PROXIES['motion_proxy'].rest()
    else:
        raise ValueError("Proxies necessárias não estão disponíveis.")


if __name__ == "__main__":
    # Defina o IP e a porta do seu NAO
    ip_nao = "10.178.186.225"
    porta_nao = 9559

    if iniciar_proxies_movimento(ip_nao, porta_nao):
        
        taichi()

    else:
        print("Não foi possível conectar. Verifique o IP/Porta.")