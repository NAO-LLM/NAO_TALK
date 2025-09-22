import json
import utils
import time
import os

while True:
    # Conexão via socket 
    utils.llm_server()

    # 🔹 Aguarda até 15 segundos pelo arquivo de áudio
    audio_file = "audio.wav"
    for _ in range(20):  # Tenta por até 15 segundos (0.5s * 30)
        if os.path.exists(audio_file):
            print("Arquivo de áudio detectado! Processando...")
            break
        print("Aguardando arquivo de áudio...")
        time.sleep(0.5)
    else:
        print("Erro: O arquivo de áudio não foi criado a tempo!")
        continue  # Pula essa iteração e espera a próxima gravação

    # Puxa a pergunta e roda a LLM 
    pergunta = utils.audio_to_text(audio_file)
    print(pergunta)
    response = utils.consultar_chatgpt(pergunta)
    print(response)

    # Limpa o histórico de conversa e fecha a conexão
    if response.lower() == "tchau":  # Condição de parada
        file_path = 'data.json'
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({"message": response}, file, ensure_ascii=False, indent=4)
        utils.limpar_historico
        #python3.socket.close()   
        break

    else:
        # Salvar a string em um arquivo JSON
        file_path = 'data.json'
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({"message": response}, file, ensure_ascii=False, indent=4)
