#!/bin/bash
#
# Manus Connect - Uninstaller
#

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

# Banner
clear
echo -e "${RED}${BOLD}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🦁  THE LIONS GROUP - MANUS CONNECT UNINSTALLER 🦁      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar root
[ "$EUID" -ne 0 ] && { log_error "Execute como root"; exit 1; }

log_info "Parando e desabilitando o serviço manus-connect..."
systemctl stop manus-connect.service > /dev/null 2>&1 || true
systemctl disable manus-connect.service > /dev/null 2>&1 || true
log_success "Serviço parado e desabilitado."

log_info "Removendo arquivos do sistema..."
rm -f /etc/systemd/system/manus-connect.service
systemctl daemon-reload
log_success "Arquivo de serviço removido."

log_info "Removendo diretório de instalação..."
rm -rf /opt/manus-connect
log_success "Diretório /opt/manus-connect removido."

log_info "Removendo chave SSH..."
rm -f /root/.ssh/id_manus
rm -f /root/.ssh/id_manus.pub
log_success "Chave SSH do Manus Connect removida."

echo ""
echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║           ✅  DESINSTALAÇÃO CONCLUÍDA!  ✅                  ║${NC}"
echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
log_info "Obrigado por usar o Manus Connect!"
