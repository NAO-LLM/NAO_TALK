import json
import utils
import time
import os
import datetime

sessao_ativa = None
caminho_historico_atual = None

while True:
    # Conexão via socket (início de um turno)
    utils.llm_server()

    audio_file = "audio.wav"
    audio_detectado = False
    for _ in range(30):
        if os.path.exists(audio_file):
            print("Arquivo de áudio detectado! Processando...")
            audio_detectado = True
            break
        time.sleep(0.5)

    if not audio_detectado:
        print("Erro: O arquivo de áudio não foi criado a tempo!")
        continue

    # Transcreve o áudio para obter a pergunta
    pergunta = utils.audio_to_text(audio_file)
    print(f"Pergunta transcrita: {pergunta}")

    #Bloco de gerenciamento de sessão
    if sessao_ativa is None:
        # É uma nova conversa!
        print("Iniciando nova sessão de chat...")

        # 1. Criar o nome do arquivo de log
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_historico_atual = f"latest_talks/conversa_{timestamp}.json"

        # 2. Criar a sessão de chat (usando o 'llm' do utils)
        sessao_ativa = utils.llm.chats.create(model='gemini-2.5-flash')

        # 3. ENVIAR O PROMPT DE SISTEMA
        # O histórico agora começa com o prompt do sistema enviado.
        print("Configurando o agente ReAct (enviando system_prompt)...")
        # Ignoramos a resposta a isso, pois é apenas a configuração
        sessao_ativa.send_message(utils.system_prompt)

    # Roda o agente react
    plano_json_string = utils.run_react_agent(pergunta, sessao_ativa)

    # Salva o histórico atualizado
    utils.salvar_historico(caminho_historico_atual, sessao_ativa)
    # Salvar o plano de ação em data.json para o NAO executar
    with open('data.json', 'w', encoding='utf-8') as file:
        file.write(plano_json_string)

    # Limpa o arquivo de áudio
    if os.path.exists(audio_file):
        os.remove(audio_file)

    # Condição de parada
    if "tchau" in pergunta.lower():
        print("Condição de parada detectada. Encerrando e limpando histórico da memória.")
        sessao_ativa = None
        caminho_historico_atual = None
        break