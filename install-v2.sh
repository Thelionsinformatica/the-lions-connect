#!/bin/bash
#
# THE LIONS CONNECT v2.0 - Script de Instalação (WireGuard)
# "Tem Internet? Já Era!" 🦁
#
# Instalação: curl -fsSL https://raw.githubusercontent.com/Thelionsinformatica/the-lions-connect/main/install-v2.sh | sudo bash
#

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
CONFIG_DIR="/opt/the-lions-connect"
WG_CONFIG_FILE="/etc/wireguard/the-lions.conf"
SERVER_ENDPOINT="thelions.redirectme.net:13231"
SERVER_PUBLIC_KEY="2DN8lgjtjUaR+xQ4pmKySGZoii0QdYOJ8Pa5QaS4iBU="
VPN_NETWORK="10.99.0.0/24"

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════"
echo "   THE LIONS CONNECT v2.0 - Instalação WireGuard"
echo "   \"Tem Internet? Já Era!\" 🦁"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[ERRO]${NC} Este script precisa ser executado como root (use sudo)"
  exit 1
fi

# Detectar sistema operacional
echo -e "${BLUE}[*]${NC} Detectando sistema operacional..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
    echo -e "${GREEN}[+]${NC} Sistema: $PRETTY_NAME"
else
    echo -e "${RED}[ERRO]${NC} Sistema operacional não suportado"
    exit 1
fi

# Instalar WireGuard
echo -e "${BLUE}[*]${NC} Instalando WireGuard..."
if command -v wg &> /dev/null; then
    echo -e "${GREEN}[+]${NC} WireGuard já está instalado"
else
    case $OS in
        ubuntu|debian)
            apt-get update -qq
            apt-get install -y -qq wireguard wireguard-tools
            ;;
        centos|rhel|fedora)
            yum install -y wireguard-tools
            ;;
        *)
            echo -e "${RED}[ERRO]${NC} Sistema não suportado: $OS"
            exit 1
            ;;
    esac
    echo -e "${GREEN}[+]${NC} WireGuard instalado com sucesso"
fi

# Criar diretório de configuração
echo -e "${BLUE}[*]${NC} Criando diretórios..."
mkdir -p "$CONFIG_DIR"
mkdir -p /etc/wireguard
chmod 700 /etc/wireguard

# Gerar ID único do dispositivo
echo -e "${BLUE}[*]${NC} Gerando ID único do dispositivo..."
DEVICE_ID="tlg-$(cat /proc/sys/kernel/random/uuid | md5sum | head -c 8)"
echo "$DEVICE_ID" > "$CONFIG_DIR/device-id"
echo -e "${GREEN}[+]${NC} Device ID: ${YELLOW}$DEVICE_ID${NC}"

# Gerar chaves WireGuard
echo -e "${BLUE}[*]${NC} Gerando chaves WireGuard..."
PRIVATE_KEY=$(wg genkey)
PUBLIC_KEY=$(echo "$PRIVATE_KEY" | wg pubkey)

echo "$PRIVATE_KEY" > "$CONFIG_DIR/private.key"
echo "$PUBLIC_KEY" > "$CONFIG_DIR/public.key"
chmod 600 "$CONFIG_DIR/private.key"

echo -e "${GREEN}[+]${NC} Chaves geradas com sucesso"

# Salvar informações do dispositivo
cat > "$CONFIG_DIR/device-info.json" <<EOF
{
  "device_id": "$DEVICE_ID",
  "hostname": "$(hostname)",
  "os": "$PRETTY_NAME",
  "public_key": "$PUBLIC_KEY",
  "install_date": "$(date -Iseconds)",
  "version": "2.0"
}
EOF

# Criar configuração WireGuard (será atualizada após aprovação)
cat > "$WG_CONFIG_FILE" <<EOF
[Interface]
PrivateKey = $PRIVATE_KEY
Address = 10.99.0.PENDING/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $SERVER_ENDPOINT
AllowedIPs = 10.99.0.0/24
PersistentKeepalive = 25
EOF

chmod 600 "$WG_CONFIG_FILE"

echo -e "${GREEN}[+]${NC} Configuração WireGuard criada"

# Obter informações do sistema
HOSTNAME=$(hostname)
LOCAL_IP=$(hostname -I | awk '{print $1}')
PUBLIC_IP=$(curl -s ifconfig.me || echo "N/A")

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 INFORMAÇÕES DO DISPOSITIVO:${NC}"
echo -e "   Device ID:    ${BLUE}$DEVICE_ID${NC}"
echo -e "   Hostname:     $HOSTNAME"
echo -e "   IP Local:     $LOCAL_IP"
echo -e "   IP Público:   $PUBLIC_IP"
echo ""
echo -e "${YELLOW}🔑 CHAVE PÚBLICA WIREGUARD:${NC}"
echo -e "${BLUE}$PUBLIC_KEY${NC}"
echo ""
echo -e "${YELLOW}📝 PRÓXIMOS PASSOS:${NC}"
echo ""
echo -e "1. ${YELLOW}Envie as informações acima${NC} para o administrador aprovar"
echo -e "2. Após aprovação, você receberá um IP da VPN"
echo -e "3. Execute: ${GREEN}systemctl start wg-quick@the-lions${NC}"
echo -e "4. Verifique: ${GREEN}wg show${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
