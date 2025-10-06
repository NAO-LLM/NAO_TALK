import json
import utils
import time
import os
import datetime

# Gera um ID único para esta sessão de conversa baseado no tempo
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
caminho_historico = f"latest_talks/conversa_{timestamp}.json"
historico_da_conversa = None # Inicia vazio

while True:
    # Conexão via socket (início de um turno)
    utils.llm_server()

    # --- Lógica de espera pelo áudio (sem alterações) ---
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
    # --- Fim da lógica de espera ---

    # Carrega o histórico atual ou inicia um novo na primeira vez
    historico_da_conversa = utils.carregar_ou_iniciar_historico(caminho_historico, utils.system_prompt)

    # Transcreve o áudio para obter a pergunta
    pergunta = utils.audio_to_text(audio_file)
    print(f"Pergunta transcrita: {pergunta}")

    # Roda o agente ReAct, passando o histórico e recebendo-o de volta atualizado
    plano_json_string, historico_atualizado = utils.run_react_agent(pergunta, historico_da_conversa)

    # Salva o histórico atualizado para o próximo turno
    utils.salvar_historico(caminho_historico, historico_atualizado)

    # Salvar o plano de ação em data.json para o NAO executar
    with open('data.json', 'w', encoding='utf-8') as file:
        file.write(plano_json_string)

    # Limpa o arquivo de áudio
    if os.path.exists(audio_file):
        os.remove(audio_file)

    # Condição de parada
    if "tchau" in pergunta.lower():
        print("Condição de parada detectada. Encerrando e limpando histórico da memória.")
        # O arquivo .json permanece salvo, mas a variável em memória é limpa.
        historico_da_conversa = None
        break