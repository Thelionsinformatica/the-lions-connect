# 🔧 THE LIONS CONNECT v2.0 - Troubleshooting

Guia completo de resolução de problemas do THE LIONS CONNECT.

---

## 📋 **Índice**

1. [Problemas de Conectividade](#problemas-de-conectividade)
2. [Problemas de Handshake](#problemas-de-handshake)
3. [Problemas de Firewall](#problemas-de-firewall)
4. [Problemas de DNS](#problemas-de-dns)
5. [Problemas de Instalação](#problemas-de-instalação)
6. [Diagnóstico Geral](#diagnóstico-geral)

---

## 🔌 **Problemas de Conectividade**

### **Sintoma: Ping não funciona (100% packet loss)**

```bash
ping 10.99.0.1
# PING 10.99.0.1 (10.99.0.1) 56(84) bytes of data.
# --- 10.99.0.1 ping statistics ---
# 5 packets transmitted, 0 received, 100% packet loss
```

**Diagnóstico:**

1. **Verificar se WireGuard está rodando:**
   ```bash
   sudo systemctl status wg-quick@the-lions
   ```

2. **Verificar se há handshake:**
   ```bash
   sudo wg show
   # Deve mostrar "latest handshake: X seconds ago"
   ```

3. **Verificar endpoint configurado:**
   ```bash
   sudo cat /etc/wireguard/the-lions.conf | grep Endpoint
   ```

**Soluções:**

#### **Solução 1: Endpoint Incorreto**

Se você está na **mesma rede local** (172.31.1.x) que o servidor:
```bash
sudo sed -i 's/Endpoint = .*/Endpoint = 172.31.1.1:13231/' /etc/wireguard/the-lions.conf
sudo systemctl restart wg-quick@the-lions
```

Se você está em **rede externa**:
```bash
sudo sed -i 's/Endpoint = .*/Endpoint = 190.15.98.231:13231/' /etc/wireguard/the-lions.conf
sudo systemctl restart wg-quick@the-lions
```

#### **Solução 2: Reiniciar WireGuard**

```bash
sudo systemctl restart wg-quick@the-lions
sleep 3
sudo wg show
ping -c 5 10.99.0.1
```

#### **Solução 3: Verificar Firewall do Cliente**

```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow out 13231/udp

# CentOS/RHEL
sudo firewall-cmd --list-all
sudo firewall-cmd --add-port=13231/udp --permanent
sudo firewall-cmd --reload
```

---

## 🤝 **Problemas de Handshake**

### **Sintoma: RX=0, TX=0 ou "latest handshake: never"**

```bash
sudo wg show
# transfer: 0 B received, 148 B sent
# latest handshake: never
```

**Causa:** O handshake WireGuard não está acontecendo.

**Diagnóstico:**

1. **Verificar se porta UDP 13231 está acessível:**
   ```bash
   nc -vzu 190.15.98.231 13231
   # Connection to 190.15.98.231 13231 port [udp/*] succeeded!
   ```

2. **Verificar chave pública do servidor:**
   ```bash
   sudo cat /etc/wireguard/the-lions.conf | grep PublicKey
   # Deve ser: 2DN8lgjtjUaR+xQ4pmKySGZoii0QdYOJ8Pa5QaS4iBU=
   ```

**Soluções:**

#### **Solução 1: Chave Pública Incorreta**

```bash
sudo sed -i 's/PublicKey = .*/PublicKey = 2DN8lgjtjUaR+xQ4pmKySGZoii0QdYOJ8Pa5QaS4iBU=/' /etc/wireguard/the-lions.conf
sudo systemctl restart wg-quick@the-lions
```

#### **Solução 2: Firewall do MikroTik Bloqueando**

Verificar no MikroTik se há regra para aceitar UDP 13231:

```routeros
/ip/firewall/filter/print where dst-port=13231
```

Se não houver, adicionar:

```routeros
/ip/firewall/filter add chain=input protocol=udp dst-port=13231 action=accept comment="TLC - WireGuard Port"
```

#### **Solução 3: Peer Não Aprovado**

Verificar se o peer existe no MikroTik:

```routeros
/interface/wireguard/peers/print
```

Se não existir, aprovar o cliente (ver README.md).

---

## 🔥 **Problemas de Firewall**

### **Sintoma: Handshake OK mas ping não funciona**

```bash
sudo wg show
# latest handshake: 10 seconds ago
# transfer: 0 B received, 296 B sent

ping 10.99.0.1
# 100% packet loss
```

**Causa:** Firewall do MikroTik bloqueando tráfego FORWARD ou INPUT.

**Diagnóstico:**

No MikroTik, verificar regras de firewall:

```routeros
/ip/firewall/filter/print where comment~"TLC"
```

**Soluções:**

#### **Solução 1: Adicionar Regras de Firewall**

Execute no MikroTik:

```routeros
# INPUT
/ip/firewall/filter add chain=input in-interface=the-lions-wg action=accept comment="TLC - Input from WireGuard" place-before=[find chain=input comment~"DROP"]

# FORWARD
/ip/firewall/filter add chain=forward in-interface=the-lions-wg action=accept comment="TLC - Forward from WireGuard" place-before=[find chain=forward comment~"DROP"]

/ip/firewall/filter add chain=forward out-interface=the-lions-wg action=accept comment="TLC - Forward to WireGuard" place-before=[find chain=forward comment~"DROP"]

# Exceção para bogons
/ip/firewall/filter add chain=forward src-address=10.99.0.0/24 action=accept comment="TLC - Allow WireGuard Network" place-before=[find chain=forward comment~"bogon"]

/ip/firewall/filter add chain=forward dst-address=10.99.0.0/24 action=accept comment="TLC - Allow to WireGuard Network" place-before=[find chain=forward comment~"bogon"]

# OUTPUT
/ip/firewall/filter add chain=output out-interface=the-lions-wg action=accept comment="TLC - Output to WireGuard"
```

#### **Solução 2: Mover Regras para Posição Correta**

As regras TLC devem estar **ANTES** das regras de DROP!

```routeros
# Listar regras com números
/ip/firewall/filter print

# Mover regra (exemplo: mover regra 50 para antes da 10)
/ip/firewall/filter move 50 10
```

---

## 🌐 **Problemas de DNS**

### **Sintoma: "Temporary failure in name resolution"**

```bash
ping thelions.redirectme.net
# ping: thelions.redirectme.net: Temporary failure in name resolution
```

**Causa:** DNS não está resolvendo o domínio.

**Solução:**

O script v2.0 já usa IP direto automaticamente. Se ainda tiver problema:

```bash
sudo sed -i 's/Endpoint = thelions.redirectme.net:13231/Endpoint = 190.15.98.231:13231/' /etc/wireguard/the-lions.conf
sudo systemctl restart wg-quick@the-lions
```

---

## 📦 **Problemas de Instalação**

### **Sintoma: "WireGuard not found" após instalação**

**Solução:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y wireguard wireguard-tools

# CentOS/RHEL
sudo yum install -y wireguard-tools

# Verificar
wg --version
```

### **Sintoma: "Permission denied" ao executar script**

**Solução:**

```bash
# Executar com sudo
curl -fsSL https://raw.githubusercontent.com/Thelionsinformatica/the-lions-connect/main/install-v2.sh | sudo bash
```

---

## 🔍 **Diagnóstico Geral**

### **Checklist Completo**

Execute os seguintes comandos para diagnóstico completo:

```bash
echo "=== SISTEMA ==="
uname -a
cat /etc/os-release | grep PRETTY_NAME

echo -e "\n=== WIREGUARD ==="
wg --version
sudo systemctl status wg-quick@the-lions

echo -e "\n=== CONFIGURAÇÃO ==="
sudo cat /etc/wireguard/the-lions.conf

echo -e "\n=== STATUS WIREGUARD ==="
sudo wg show

echo -e "\n=== CONECTIVIDADE ==="
ping -c 3 8.8.8.8
nc -vzu 190.15.98.231 13231

echo -e "\n=== ROTAS ==="
ip route | grep 10.99

echo -e "\n=== LOGS ==="
sudo journalctl -u wg-quick@the-lions -n 20 --no-pager
```

### **Enviar Diagnóstico para Suporte**

```bash
# Salvar diagnóstico em arquivo
bash diagnostico.sh > /tmp/diagnostico-wireguard.txt 2>&1

# Enviar para suporte
cat /tmp/diagnostico-wireguard.txt
```

---

## 📞 **Suporte**

Se nenhuma solução acima resolver:

1. Execute o diagnóstico completo
2. Abra uma issue no GitHub: https://github.com/Thelionsinformatica/the-lions-connect/issues
3. Ou entre em contato: suporte@thelions.com.br

---

**Desenvolvido com 🦁 por The Lions Informática**
