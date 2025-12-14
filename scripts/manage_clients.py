#!/usr/bin/env python3
"""
THE LIONS CONNECT v2.0 - Client Management Script
Gerenciamento de clientes WireGuard via API do MikroTik
"""

import sys
import argparse
from librouteros import connect

# Configurações do MikroTik
MIKROTIK_HOST = "thelions.redirectme.net"
MIKROTIK_PORT = 3540
MIKROTIK_USER = "jarvis"
MIKROTIK_PASSWORD = "Andre@311407"
WG_INTERFACE = "the-lions-wg"
VPN_NETWORK = "10.99.0"


def connect_mikrotik():
    """Conecta ao MikroTik via API"""
    try:
        api = connect(
            username=MIKROTIK_USER,
            password=MIKROTIK_PASSWORD,
            host=MIKROTIK_HOST,
            port=MIKROTIK_PORT
        )
        return api
    except Exception as e:
        print(f"❌ Erro ao conectar ao MikroTik: {e}")
        sys.exit(1)


def get_next_ip(api):
    """Retorna o próximo IP disponível na rede VPN"""
    peers = api.path('/interface/wireguard/peers')
    used_ips = []
    
    for peer in peers:
        allowed = peer.get('allowed-address', '')
        if allowed:
            # Extrair IP (formato: 10.99.0.X/32)
            ip = allowed.split('/')[0]
            if ip.startswith(VPN_NETWORK):
                last_octet = int(ip.split('.')[-1])
                used_ips.append(last_octet)
    
    # Encontrar primeiro IP livre (começando de .2, .1 é o servidor)
    for i in range(2, 255):
        if i not in used_ips:
            return f"{VPN_NETWORK}.{i}"
    
    raise Exception("Sem IPs disponíveis na rede VPN!")


def list_clients(api):
    """Lista todos os clientes conectados"""
    peers = api.path('/interface/wireguard/peers')
    
    print("\n" + "="*80)
    print("  THE LIONS CONNECT - Clientes Conectados")
    print("="*80)
    print(f"{'Device ID':<20} {'Hostname':<20} {'IP VPN':<15} {'Status':<10}")
    print("-"*80)
    
    for peer in peers:
        comment = peer.get('comment', '')
        allowed_ip = peer.get('allowed-address', '').split('/')[0]
        rx = peer.get('rx', 0)
        tx = peer.get('tx', 0)
        
        # Extrair device-id e hostname do comentário (formato: TLC-device-id-hostname)
        if comment.startswith('TLC-'):
            parts = comment.replace('TLC-', '').split('-', 1)
            device_id = parts[0] if len(parts) > 0 else 'N/A'
            hostname = parts[1] if len(parts) > 1 else 'N/A'
        else:
            device_id = 'N/A'
            hostname = comment
        
        # Status baseado em tráfego
        status = "🟢 Ativo" if (rx > 0 or tx > 0) else "🔴 Inativo"
        
        print(f"{device_id:<20} {hostname:<20} {allowed_ip:<15} {status:<10}")
    
    print("="*80 + "\n")


def approve_client(api, device_id, public_key, hostname):
    """Aprova um novo cliente"""
    try:
        # Obter próximo IP disponível
        ip = get_next_ip(api)
        
        # Adicionar peer
        peers = api.path('/interface/wireguard/peers')
        peers.add(
            interface=WG_INTERFACE,
            **{'public-key': public_key},
            **{'allowed-address': f"{ip}/32"},
            comment=f"TLC-{device_id}-{hostname}"
        )
        
        print("\n" + "="*80)
        print("  ✅ CLIENTE APROVADO COM SUCESSO!")
        print("="*80)
        print(f"  Device ID:    {device_id}")
        print(f"  Hostname:     {hostname}")
        print(f"  IP VPN:       {ip}")
        print(f"  Public Key:   {public_key[:40]}...")
        print("="*80)
        print("\n📝 PRÓXIMO PASSO:")
        print(f"\nNo cliente, execute:\n")
        print(f"  sudo sed -i 's/Address = 10.99.0.PENDING/Address = {ip}/' /etc/wireguard/the-lions.conf")
        print(f"  sudo systemctl enable wg-quick@the-lions")
        print(f"  sudo systemctl start wg-quick@the-lions")
        print(f"  sudo wg show")
        print(f"  ping -c 5 10.99.0.1\n")
        
    except Exception as e:
        print(f"❌ Erro ao aprovar cliente: {e}")
        sys.exit(1)


def remove_client(api, device_id):
    """Remove um cliente"""
    try:
        peers = api.path('/interface/wireguard/peers')
        
        # Encontrar peer pelo device-id no comentário
        for peer in peers:
            comment = peer.get('comment', '')
            if f"TLC-{device_id}" in comment:
                peer_id = peer.get('.id')
                peers.remove(peer_id)
                print(f"✅ Cliente {device_id} removido com sucesso!")
                return
        
        print(f"❌ Cliente {device_id} não encontrado!")
        
    except Exception as e:
        print(f"❌ Erro ao remover cliente: {e}")
        sys.exit(1)


def status_client(api, device_id):
    """Mostra status detalhado de um cliente"""
    try:
        peers = api.path('/interface/wireguard/peers')
        
        for peer in peers:
            comment = peer.get('comment', '')
            if f"TLC-{device_id}" in comment:
                print("\n" + "="*80)
                print(f"  Status do Cliente: {device_id}")
                print("="*80)
                print(f"  Comentário:       {comment}")
                print(f"  Public Key:       {peer.get('public-key', 'N/A')}")
                print(f"  IP Permitido:     {peer.get('allowed-address', 'N/A')}")
                print(f"  Endpoint:         {peer.get('endpoint-address', 'N/A')}:{peer.get('endpoint-port', 'N/A')}")
                print(f"  RX (Recebido):    {peer.get('rx', 0)} bytes")
                print(f"  TX (Enviado):     {peer.get('tx', 0)} bytes")
                print(f"  Last Handshake:   {peer.get('last-handshake', 'Never')}")
                print("="*80 + "\n")
                return
        
        print(f"❌ Cliente {device_id} não encontrado!")
        
    except Exception as e:
        print(f"❌ Erro ao obter status: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='THE LIONS CONNECT v2.0 - Gerenciamento de Clientes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Listar todos os clientes
  python3 manage_clients.py list

  # Aprovar novo cliente
  python3 manage_clients.py approve tlg-abc123 "PUBLIC_KEY_AQUI" "hostname-do-cliente"

  # Ver status de um cliente
  python3 manage_clients.py status tlg-abc123

  # Remover cliente
  python3 manage_clients.py remove tlg-abc123
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')
    
    # Comando: list
    subparsers.add_parser('list', help='Listar todos os clientes')
    
    # Comando: approve
    approve_parser = subparsers.add_parser('approve', help='Aprovar novo cliente')
    approve_parser.add_argument('device_id', help='Device ID do cliente (ex: tlg-abc123)')
    approve_parser.add_argument('public_key', help='Chave pública WireGuard do cliente')
    approve_parser.add_argument('hostname', help='Hostname do cliente')
    
    # Comando: remove
    remove_parser = subparsers.add_parser('remove', help='Remover cliente')
    remove_parser.add_argument('device_id', help='Device ID do cliente')
    
    # Comando: status
    status_parser = subparsers.add_parser('status', help='Ver status de um cliente')
    status_parser.add_argument('device_id', help='Device ID do cliente')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Conectar ao MikroTik
    api = connect_mikrotik()
    
    # Executar comando
    if args.command == 'list':
        list_clients(api)
    elif args.command == 'approve':
        approve_client(api, args.device_id, args.public_key, args.hostname)
    elif args.command == 'remove':
        remove_client(api, args.device_id)
    elif args.command == 'status':
        status_client(api, args.device_id)


if __name__ == '__main__':
    main()
