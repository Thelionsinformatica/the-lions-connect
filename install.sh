#!/bin/bash
#
# The Lions Connect - The Lions Group Network
# "Tem Internet? Já Era!" - Acesso Remoto Automático
#
# Uso: curl -fsSL connect.thelions.net/install | bash
#

set -e

# Configurações
CENTRAL_SERVER="thelions.redirectme.net"
CENTRAL_PORT="2220"
CENTRAL_USER="jarvis"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

# Banner
clear
echo -e "${CYAN}${BOLD}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           🦁  THE LIONS GROUP - MANUS CONNECT  🦁            ║
║                                                               ║
║          "Tem Internet? Já Era!" - Acesso Remoto             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar root
[ "$EUID" -ne 0 ] && { log_error "Execute como root"; exit 1; }

# Detectar OS
log_info "Detectando sistema..."
[ -f /etc/os-release ] && . /etc/os-release || { log_error "OS não suportado"; exit 1; }
log_success "Sistema: $PRETTY_NAME"

# Gerar ID
DEVICE_ID="tlg-$(cat /proc/sys/kernel/random/uuid | cut -d'-' -f1)"
HOSTNAME=$(hostname)
IP_LOCAL=$(ip route get 1 2>/dev/null | awk '{print $7;exit}' || echo "N/A")
IP_PUBLIC=$(curl -s --max-time 5 ifconfig.me || echo "N/A")

echo -e "   ${BOLD}ID:${NC} ${GREEN}$DEVICE_ID${NC}"
echo -e "   Hostname: $HOSTNAME"
echo -e "   IP: $IP_LOCAL / $IP_PUBLIC"
echo ""

# Instalar dependências
log_info "Instalando dependências..."
if [ "$ID" = "ubuntu" ] || [ "$ID" = "debian" ]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq > /dev/null 2>&1
    apt-get install -y -qq openssh-client sshpass curl > /dev/null 2>&1
elif [ "$ID" = "centos" ] || [ "$ID" = "rhel" ] || [ "$ID" = "fedora" ]; then
    yum install -y -q openssh-clients sshpass curl > /dev/null 2>&1
fi
log_success "Dependências OK"

# Criar diretório
mkdir -p /opt/the-lions-connect
cd /opt/the-lions-connect

# Gerar chave SSH
if [ ! -f /root/.ssh/id_manus ]; then
    log_info "Gerando chave SSH..."
    ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_manus -N '' -q -C "manus-$DEVICE_ID"
    log_success "Chave gerada"
fi

SSH_PUBKEY=$(cat /root/.ssh/id_manus.pub)

# Configuração
cat > config.json << EOF
{
  "device_id": "$DEVICE_ID",
  "hostname": "$HOSTNAME",
  "ip_local": "$IP_LOCAL",
  "ip_public": "$IP_PUBLIC",
  "os": "$PRETTY_NAME",
  "installed_at": "$(date -Iseconds)",
  "ssh_pubkey": "$SSH_PUBKEY"
}
EOF

# Script de conexão
cat > connect.sh << 'CONNECT_EOF'
#!/bin/bash
CONFIG="/opt/the-lions-connect/config.json"
DEVICE_ID=$(grep -o '"device_id": "[^"]*' $CONFIG | cut -d'"' -f4)
REMOTE_PORT=$((10000 + $(echo -n "$DEVICE_ID" | md5sum | cut -c1-4 | tr 'a-f' '0-5' | sed 's/^0*//' | head -c4)))

echo "[$(date)] Conectando... Porta: $REMOTE_PORT"

ssh -i /root/.ssh/id_manus \
    -o StrictHostKeyChecking=no \
    -o ServerAliveInterval=60 \
    -o ServerAliveCountMax=3 \
    -N -T \
    -R ${REMOTE_PORT}:localhost:22 \
    jarvis@thelions.redirectme.net -p 2220
CONNECT_EOF

chmod +x connect.sh

# Serviço systemd
cat > /etc/systemd/system/the-lions-connect.service << 'SERVICE_EOF'
[Unit]
Description=The Lions Connect - The Lions Group Network
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/opt/the-lions-connect/connect.sh
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl enable the-lions-connect.service > /dev/null 2>&1
log_success "Serviço configurado"

# Resultado
echo ""
echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║              ✅  INSTALAÇÃO CONCLUÍDA!  ✅                   ║${NC}"
echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}${BOLD}📋 ID DO DISPOSITIVO:${NC} ${GREEN}${BOLD}$DEVICE_ID${NC}"
echo ""
echo -e "${YELLOW}${BOLD}⚠️  PRÓXIMOS PASSOS:${NC}"
echo -e "   1. Envie o ID acima para o administrador"
echo -e "   2. Aguarde aprovação"
echo -e "   3. Inicie: ${BOLD}systemctl start the-lions-connect${NC}"
echo ""
echo -e "${CYAN}📄 Chave SSH:${NC}"
echo -e "${BLUE}$SSH_PUBKEY${NC}"
echo ""
