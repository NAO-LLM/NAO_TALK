<div align="center">

🤖 Integração Robô NAO com LLM 🧠

Um projeto que conecta o robô NAO a um modelo de linguagem grande (LLM) da OpenAI, permitindo interação por voz em tempo real.

</div>

📖 Visão Geral

Este projeto permite que o robô NAO ouça um comando de voz, o transcreva para texto, envie para a API da OpenAI para gerar uma resposta inteligente e, em seguida, vocalize essa resposta para o usuário. A comunicação entre o ambiente legado do robô (

Python 2.7) e o script de processamento moderno (Python 3) é realizada de forma eficiente via sockets.

O fluxo de trabalho é o seguinte:

1_ Detecção: O robô NAO aguarda até detectar um rosto.

2_ Gravação: Ao detectar alguém, ele avisa que está ouvindo e grava o áudio do usuário.

3_ Comunicação: O script do NAO (NAO27.py) transfere o áudio gravado e sinaliza para o servidor Python 3.

4_ Processamento: O servidor Python 3 transcreve o áudio para texto e o envia para a API.

5_ Resposta: A resposta do LLM é salva em um arquivo data.json, e o robô NAO a lê em voz alta para o usuário.

📋 Pré-requisitos

Antes de começar, certifique-se de que você possui:

Python 2.7 e Python 3.x instalados.

O NAOqi SDK para Python 2.7.

Uma conta da OpenAI com uma chave de API válida.

O gerenciador de pacotes 

conda (recomendado para gerenciar os dois ambientes Python).

🚀 Guia de Instalação

Siga os passos abaixo para configurar os ambientes de desenvolvimento.

1. Clonar o Repositório:

Bash

    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DO_REPOSITORIO>

2. Configurar o Ambiente Python 3

Este ambiente será responsável por toda a lógica de IA.
Bash

# Crie e ative um ambiente virtual
    python3 -m venv venv3
    source venv3/bin/activate

# Instale as dependências
    pip install -r requirements.txt

3. Configurar a Chave da API OpenAI

Crie um arquivo chamado .env na raiz do projeto e adicione sua chave de API.

    OPENAI_API_KEY="SUA_CHAVE_DE_API_AQUI"

4. Configurar o Ambiente Python 2.7 (NAOqi)

Este ambiente se conecta diretamente ao robô. A configuração varia entre Linux e Windows.

🐧 Para Usuários Linux:

1º Passo: Criar o ambiente com Conda
Bash

    conda create -n py27 python=2.7
    conda activate py27

2º Passo: Extrair o NAOqi SDK
Extraia o conteúdo da pasta pynaoqi-python-2.1.4.13-linux64 para o diretório de pacotes do seu ambiente conda:
"caminho/para/anaconda3"/envs/py27/lib/python2.7/site-packages

3º Passo: Extrair a biblioteca Boost
Extraia o conteúdo da biblioteca boost para o seguinte diretório:
"caminho/para/anaconda3"/envs/py27/lib/python2.7/site-packages/pynaoqi/lib

4º Passo: Configurar as Variáveis de Ambiente
Execute os seguintes comandos no terminal onde você irá rodar o script do NAO.

    Atenção: Substitua "caminho/para/anaconda3" pelo caminho real da sua instalação.



# Exporte as variáveis de ambiente
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ANACONDA_PATH/envs/py27/lib/python2.7/site-packages/pynaoqi/lib
    export PYTHONPATH=$PYTHONPATH:$ANACONDA_PATH/envs/py27/lib/python2.7/site-packages

🪟 Para Usuários Windows:

1º Passo: Criar o ambiente com Conda
Bash

    conda create -n py27 python=2.7
    conda activate py27

2º Passo: Extrair o NAOqi SDK
Extraia o conteúdo da pasta pynaoqi-python-2.1.4.13-win32-vs2010 para o diretório de pacotes do seu ambiente conda:
"caminho\para\anaconda3"\envs\py27\Lib\site-packages

3º Passo: Configurar a Variável de Ambiente
Execute o seguinte comando no terminal (Prompt de Comando) onde você irá rodar o script do NAO.

Atenção: Substitua "caminho\para\anaconda3" pelo caminho real da sua instalação.

DOS

    set PYTHONPATH=%PYTHONPATH%;"caminho\para\anaconda3"\envs\py27\Lib\site-packages

▶️ Como Executar

Para iniciar a aplicação, você precisará de dois terminais abertos simultaneamente.

Terminal 1: Iniciar o Servidor Python 3

Este script inicia o servidor que aguardará a conexão e o áudio do robô.
Bash

# Ative o ambiente Python 3
    source venv3/bin/activate

# Rode o servidor
    python NAO.py

Terminal 2: Executar o Cliente Python 2.7 (NAO)

Este script se conecta ao servidor e controla o robô.

Importante: Antes de executar, certifique-se de que o arquivo ip.txt na raiz do projeto contém o endereço de IP correto do seu robô NAO.

Bash

# Ative o ambiente Python 2.7
    conda activate py27

# Rode o cliente do robô
    python NAO27.py
