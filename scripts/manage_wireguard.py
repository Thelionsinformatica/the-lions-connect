#!/usr/bin/env python3
"""
THE LIONS CONNECT v2.0 - Gerenciamento de Peers WireGuard
"""
import routeros_api
import json
import sys
import argparse
from datetime import datetime

# Configurações do MikroTik
MIKROTIK_HOST = "thelions.redirectme.net"
MIKROTIK_PORT = 3540
MIKROTIK_USER = "jarvis"
MIKROTIK_PASS = "Andre@311407"

# Configurações do WireGuard
WG_INTERFACE = "the-lions-wg"
VPN_NETWORK = "10.99.0"
START_IP = 2  # 10.99.0.2 (10.99.0.1 é o servidor)

# Arquivo de banco de dados de clientes
DB_FILE = "/opt/the-lions-connect/clients_wg.json"

def load_db():
    """Carregar banco de dados de clientes"""
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"clients": [], "last_ip": START_IP - 1}

def save_db(db):
    """Salvar banco de dados de clientes"""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def get_next_ip(db):
    """Obter próximo IP disponível"""
    db['last_ip'] += 1
    return f"{VPN_NETWORK}.{db['last_ip']}"

def connect_mikrotik():
    """Conectar ao MikroTik"""
    connection = routeros_api.RouterOsApiPool(
        MIKROTIK_HOST,
        username=MIKROTIK_USER,
        password=MIKROTIK_PASS,
        port=MIKROTIK_PORT,
        plaintext_login=True
    )
    return connection.get_api()

def approve_client(device_id, hostname, public_key):
    """Aprovar novo cliente"""
    print(f"[*] Aprovando cliente: {device_id}")
    
    # Carregar DB
    db = load_db()
    
    # Verificar se já existe
    for client in db['clients']:
        if client['device_id'] == device_id:
            print(f"[!] Cliente {device_id} já está aprovado!")
            print(f"    IP: {client['vpn_ip']}")
            return
    
    # Obter próximo IP
    vpn_ip = get_next_ip(db)
    
    # Conectar ao MikroTik
    print("[*] Conectando ao MikroTik...")
    api = connect_mikrotik()
    
    # Adicionar peer WireGuard
    print(f"[*] Adicionando peer WireGuard...")
    wg_peers = api.get_resource('/interface/wireguard/peers')
    wg_peers.add(
        interface=WG_INTERFACE,
        **{"public-key": public_key},
        **{"allowed-address": f"{vpn_ip}/32"},
        comment=f"TLC-{device_id}-{hostname}"
    )
    
    # Salvar no banco de dados
    client_data = {
        "device_id": device_id,
        "hostname": hostname,
        "public_key": public_key,
        "vpn_ip": vpn_ip,
        "approved_date": datetime.now().isoformat(),
        "status": "active"
    }
    
    db['clients'].append(client_data)
    save_db(db)
    
    print(f"\n{'='*60}")
    print(f"✅ CLIENTE APROVADO COM SUCESSO!")
    print(f"{'='*60}")
    print(f"Device ID:  {device_id}")
    print(f"Hostname:   {hostname}")
    print(f"VPN IP:     {vpn_ip}")
    print(f"\n📝 Comando para o cliente atualizar a configuração:")
    print(f"   sudo sed -i 's/Address = 10.99.0.PENDING/Address = {vpn_ip}/' /etc/wireguard/the-lions.conf")
    print(f"   sudo systemctl enable wg-quick@the-lions")
    print(f"   sudo systemctl start wg-quick@the-lions")
    print(f"\n🔗 Comando para acessar remotamente:")
    print(f"   ssh root@{vpn_ip}")
    print(f"{'='*60}\n")

def list_clients():
    """Listar todos os clientes"""
    db = load_db()
    
    if not db['clients']:
        print("[!] Nenhum cliente aprovado ainda")
        return
    
    print(f"\n{'='*80}")
    print(f"THE LIONS CONNECT v2.0 - Clientes Aprovados")
    print(f"{'='*80}")
    print(f"{'ID':<15} {'Hostname':<20} {'VPN IP':<15} {'Status':<10}")
    print(f"{'-'*80}")
    
    for client in db['clients']:
        print(f"{client['device_id']:<15} {client['hostname']:<20} {client['vpn_ip']:<15} {client['status']:<10}")
    
    print(f"{'='*80}")
    print(f"Total: {len(db['clients'])} cliente(s)\n")

def remove_client(device_id):
    """Remover cliente"""
    print(f"[*] Removendo cliente: {device_id}")
    
    # Carregar DB
    db = load_db()
    
    # Encontrar cliente
    client = None
    for c in db['clients']:
        if c['device_id'] == device_id:
            client = c
            break
    
    if not client:
        print(f"[!] Cliente {device_id} não encontrado!")
        return
    
    # Conectar ao MikroTik
    print("[*] Conectando ao MikroTik...")
    api = connect_mikrotik()
    
    # Remover peer WireGuard
    print(f"[*] Removendo peer WireGuard...")
    wg_peers = api.get_resource('/interface/wireguard/peers')
    peers = wg_peers.get(**{"public-key": client['public_key']})
    
    for peer in peers:
        wg_peers.remove(id=peer['id'])
    
    # Remover do banco de dados
    db['clients'] = [c for c in db['clients'] if c['device_id'] != device_id]
    save_db(db)
    
    print(f"\n✅ Cliente {device_id} removido com sucesso!\n")

def main():
    parser = argparse.ArgumentParser(description='THE LIONS CONNECT v2.0 - Gerenciamento WireGuard')
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando: approve
    approve_parser = subparsers.add_parser('approve', help='Aprovar novo cliente')
    approve_parser.add_argument('device_id', help='ID do dispositivo')
    approve_parser.add_argument('hostname', help='Nome do host')
    approve_parser.add_argument('public_key', help='Chave pública WireGuard')
    
    # Comando: list
    subparsers.add_parser('list', help='Listar todos os clientes')
    
    # Comando: remove
    remove_parser = subparsers.add_parser('remove', help='Remover cliente')
    remove_parser.add_argument('device_id', help='ID do dispositivo')
    
    args = parser.parse_args()
    
    if args.command == 'approve':
        approve_client(args.device_id, args.hostname, args.public_key)
    elif args.command == 'list':
        list_clients()
    elif args.command == 'remove':
        remove_client(args.device_id)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
