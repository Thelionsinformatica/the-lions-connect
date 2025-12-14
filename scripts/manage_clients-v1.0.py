#!/usr/bin/env python3
"""
The Lions Connect - Client Management System
Gerencia a aprovação de novos clientes e suas chaves SSH no servidor central.
"""

import routeros_api
import json
import os
import sys
from datetime import datetime

# Configurações do MikroTik (Servidor Central)
MIKROTIK_HOST = os.getenv("MIKROTIK_HOST", "thelions.redirectme.net")
MIKROTIK_PORT = int(os.getenv("MIKROTIK_PORT", "3540"))
MIKROTIK_USER = os.getenv("MIKROTIK_USER", "jarvis")
MIKROTIK_PASSWORD = os.getenv("MIKROTIK_PASSWORD", "Andre@311407")

# Arquivo de banco de dados de clientes
CLIENTS_DB = "/opt/the-lions-connect/clients_db.json"

def load_clients_db():
    """Carrega o banco de dados de clientes."""
    if os.path.exists(CLIENTS_DB):
        with open(CLIENTS_DB, 'r') as f:
            return json.load(f)
    return {"clients": []}

def save_clients_db(db):
    """Salva o banco de dados de clientes."""
    os.makedirs(os.path.dirname(CLIENTS_DB), exist_ok=True)
    with open(CLIENTS_DB, 'w') as f:
        json.dump(db, f, indent=2)

def add_ssh_key_to_mikrotik(device_id, ssh_pubkey):
    """Adiciona a chave SSH pública ao usuário jarvis no MikroTik."""
    try:
        connection = routeros_api.RouterOsApiPool(
            MIKROTIK_HOST,
            username=MIKROTIK_USER,
            password=MIKROTIK_PASSWORD,
            port=MIKROTIK_PORT,
            plaintext_login=True
        )
        api = connection.get_api()
        
        # No MikroTik, as chaves SSH são adicionadas via /user/ssh-keys
        # Nota: A API do RouterOS pode não suportar isso diretamente
        # Alternativa: usar SSH para executar o comando
        
        print(f"[!] ATENÇÃO: A adição de chaves SSH via API não é suportada.")
        print(f"[*] Você precisa adicionar manualmente a chave ao usuário 'jarvis':")
        print(f"\n    /user ssh-keys import public-key-file=<arquivo> user=jarvis\n")
        
        connection.disconnect()
        return False
        
    except Exception as e:
        print(f"[ERRO] Falha ao conectar ao MikroTik: {e}")
        return False

def approve_client(device_id, hostname, ssh_pubkey, ip_public="N/A"):
    """Aprova um novo cliente e adiciona ao banco de dados."""
    db = load_clients_db()
    
    # Verificar se já existe
    existing = next((c for c in db["clients"] if c["device_id"] == device_id), None)
    if existing:
        print(f"[!] Cliente {device_id} já está aprovado.")
        return False
    
    # Calcular porta dinâmica (mesma lógica do install.sh)
    import hashlib
    hash_obj = hashlib.md5(device_id.encode())
    hash_hex = hash_obj.hexdigest()[:4]
    # Converter hex para decimal e mapear para range 10000-65535
    port_offset = int(hash_hex, 16) % 55536
    remote_port = 10000 + port_offset
    
    # Adicionar ao banco de dados
    client = {
        "device_id": device_id,
        "hostname": hostname,
        "ip_public": ip_public,
        "ssh_pubkey": ssh_pubkey,
        "remote_port": remote_port,
        "approved_at": datetime.now().isoformat(),
        "status": "approved"
    }
    
    db["clients"].append(client)
    save_clients_db(db)
    
    print(f"\n{'='*80}")
    print(f"✅ CLIENTE APROVADO COM SUCESSO!")
    print(f"{'='*80}")
    print(f"  Device ID: {device_id}")
    print(f"  Hostname: {hostname}")
    print(f"  IP Público: {ip_public}")
    print(f"  Porta Remota: {remote_port}")
    print(f"\n  Para acessar este cliente:")
    print(f"    ssh -p {remote_port} root@localhost")
    print(f"\n  ⚠️  IMPORTANTE: Adicione a chave SSH manualmente no MikroTik:")
    print(f"    1. Salve a chave pública em um arquivo (ex: {device_id}.pub)")
    print(f"    2. Faça upload para o MikroTik")
    print(f"    3. Execute: /user ssh-keys import public-key-file={device_id}.pub user=jarvis")
    print(f"{'='*80}\n")
    
    # Salvar a chave em um arquivo para facilitar
    key_file = f"/tmp/{device_id}.pub"
    with open(key_file, 'w') as f:
        f.write(ssh_pubkey)
    print(f"  Chave salva em: {key_file}\n")
    
    return True

def list_clients():
    """Lista todos os clientes aprovados."""
    db = load_clients_db()
    
    if not db["clients"]:
        print("\n[!] Nenhum cliente aprovado ainda.\n")
        return
    
    print(f"\n{'='*100}")
    print(f"CLIENTES APROVADOS ({len(db['clients'])})")
    print(f"{'='*100}\n")
    
    for i, client in enumerate(db["clients"], 1):
        print(f"[{i}] {client['device_id']}")
        print(f"    Hostname: {client['hostname']}")
        print(f"    IP Público: {client.get('ip_public', 'N/A')}")
        print(f"    Porta Remota: {client['remote_port']}")
        print(f"    Aprovado em: {client['approved_at']}")
        print(f"    Comando de acesso: ssh -p {client['remote_port']} root@localhost")
        print()

def remove_client(device_id):
    """Remove um cliente do banco de dados."""
    db = load_clients_db()
    
    original_count = len(db["clients"])
    db["clients"] = [c for c in db["clients"] if c["device_id"] != device_id]
    
    if len(db["clients"]) < original_count:
        save_clients_db(db)
        print(f"\n✅ Cliente {device_id} removido com sucesso.\n")
        print(f"⚠️  Lembre-se de remover a chave SSH do MikroTik manualmente!")
        return True
    else:
        print(f"\n[!] Cliente {device_id} não encontrado.\n")
        return False

def main():
    """Menu principal."""
    if len(sys.argv) < 2:
        print("""
Uso: manage_clients.py <comando> [argumentos]

Comandos:
  approve <device_id> <hostname> <ssh_pubkey> [ip_public]
      Aprova um novo cliente
      
  list
      Lista todos os clientes aprovados
      
  remove <device_id>
      Remove um cliente
      
Exemplos:
  ./manage_clients.py approve tlg-a1b2c3d4 "servidor-web" "ssh-rsa AAAA..."
  ./manage_clients.py list
  ./manage_clients.py remove tlg-a1b2c3d4
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "approve":
        if len(sys.argv) < 5:
            print("[ERRO] Uso: approve <device_id> <hostname> <ssh_pubkey> [ip_public]")
            sys.exit(1)
        
        device_id = sys.argv[2]
        hostname = sys.argv[3]
        ssh_pubkey = sys.argv[4]
        ip_public = sys.argv[5] if len(sys.argv) > 5 else "N/A"
        
        approve_client(device_id, hostname, ssh_pubkey, ip_public)
    
    elif command == "list":
        list_clients()
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("[ERRO] Uso: remove <device_id>")
            sys.exit(1)
        
        device_id = sys.argv[2]
        remove_client(device_id)
    
    else:
        print(f"[ERRO] Comando desconhecido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
