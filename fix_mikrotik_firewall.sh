#!/bin/bash
# Script para adicionar regra de firewall WireGuard no MikroTik
# Execute este script NA JARVIS RL

MIKROTIK_HOST="thelions.redirectme.net"
MIKROTIK_PORT="2220"
MIKROTIK_USER="jarvis"

echo "=========================================="
echo "THE LIONS CONNECT - Firewall Fix"
echo "=========================================="
echo ""
echo "[*] Conectando ao MikroTik via SSH..."
echo ""

# Comando SSH para adicionar a regra
ssh -p $MIKROTIK_PORT $MIKROTIK_USER@$MIKROTIK_HOST << 'EOF'
# Encontrar o número da regra DROP
:local dropNum [/ip firewall filter find chain=forward comment="DROP All Other Forward"]

:if ([:len $dropNum] > 0) do={
    :put "Regra DROP encontrada!"
    
    # Verificar se já existe regra TLC
    :local tlcExists [/ip firewall filter find chain=forward comment~"TLC.*WireGuard"]
    
    :if ([:len $tlcExists] > 0) do={
        :put "Removendo regras TLC antigas..."
        /ip firewall filter remove $tlcExists
    }
    
    # Adicionar regra TLC ANTES da DROP
    :put "Adicionando regra TLC..."
    /ip firewall filter add chain=forward in-interface=the-lions-wg action=accept comment="TLC - WireGuard VPN" place-before=$dropNum
    
    :put "Regra adicionada com sucesso!"
    :put ""
    :put "Verificando regras:"
    /ip firewall filter print where chain=forward and (comment~"TLC" or comment~"DROP All Other")
    
} else={
    :put "ERRO: Regra DROP nao encontrada!"
}
EOF

echo ""
echo "=========================================="
echo "[+] Concluído!"
echo "=========================================="
