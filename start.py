# -*- coding: utf-8 -*-
import subprocess
import os
import time

MAC_NAO = "b8-b7-f1-15-f7-75"

def get_ip_from_arp(mac_address):
    try:
        cmd = f'arp -a | findstr "{mac_address}" '
        returned_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        linha = returned_output.decode('latin1').strip()
        ip = linha.split()[0]
        print(f"✅ IP do NAO encontrado: {ip}")
        return ip
    except subprocess.CalledProcessError:
        print("❌ MAC do NAO não encontrado.")
        return None

def salvar_ip(ip, arquivo="ip.txt"):
    with open(arquivo, "w") as f:
        f.write(ip)

def main():
    ip = get_ip_from_arp(MAC_NAO)
    if not ip:
        ip = raw_input("Digite o IP do NAO manualmente: ").strip()

    salvar_ip(ip)
    print(f"📁 IP salvo em ip.txt: {ip}")

    # Caminho para scripts NAO.py e NAO27.py
    caminho_scripts = os.path.abspath(os.path.join(os.getcwd()))

    # Iniciar NAO.py com py312
    print("▶️ Iniciando NAO.py com py312...")
    comando_nao = f"start cmd /k \"conda activate py312 && python NAO.py\""
    subprocess.run(comando_nao, shell=True, cwd=caminho_scripts)

    time.sleep(2)

    # Iniciar NAO27.py com py27
    print("▶️ Iniciando NAO27.py com py27...")
    comando_nao27 = f"start cmd /k \"conda activate py27 && python NAO27.py\""
    subprocess.run(comando_nao27, shell=True, cwd=caminho_scripts)

if __name__ == "__main__":
    main()
