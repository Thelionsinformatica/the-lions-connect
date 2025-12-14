# 🦁 THE LIONS CONNECT v2.0

**"Tem Internet? Já Era!"**

Sistema de acesso remoto plug-and-play baseado em WireGuard VPN que permite conectar qualquer dispositivo à rede centralizada através do MikroTik, funcionando de qualquer lugar com internet.

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Version](https://img.shields.io/badge/version-2.0-blue.svg)]()
[![WireGuard](https://img.shields.io/badge/WireGuard-enabled-orange.svg)]()

---

## 🎯 **Visão Geral**

**THE LIONS CONNECT** é uma solução de VPN corporativa que permite:

- ✅ Acesso remoto a qualquer dispositivo de qualquer lugar
- ✅ Funciona mesmo atrás de CGNAT/NAT
- ✅ Instalação automática com um único comando
- ✅ Gerenciamento centralizado via MikroTik
- ✅ Suporte para Linux, Windows, macOS, Android, iOS
- ✅ Zero configuração manual no cliente
- ✅ Detecção automática de rede local vs externa

---

## 🏗️ **Arquitetura**

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERNET                                  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │
              ┌────────────▼────────────┐
              │   MikroTik RouterOS     │
              │   WireGuard Server      │
              │   IP: 10.99.0.1/24      │
              │   Porta: 13231 UDP      │
              └────────────┬────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐   ┌─────▼─────┐
    │ Cliente 1 │    │ Cliente 2 │   │ Cliente N │
    │10.99.0.2  │    │10.99.0.3  │   │10.99.0.x  │
    └───────────┘    └───────────┘   └───────────┘
```

**Componentes:**

- **Servidor WireGuard:** MikroTik RouterOS 7.18.2
- **Rede VPN:** 10.99.0.0/24
- **Porta:** 13231 UDP
- **Clientes:** Qualquer dispositivo com WireGuard

---

## 🚀 **Instalação Rápida**

### **Cliente Linux/macOS**

```bash
curl -fsSL https://raw.githubusercontent.com/Thelionsinformatica/the-lions-connect/main/install-v2.sh | sudo bash
```

### **O que o script faz:**

1. Detecta o sistema operacional
2. Instala WireGuard automaticamente
3. Gera chaves pública/privada únicas
4. Cria Device ID único (formato: `tlg-xxxxxxxx`)
5. **Detecta automaticamente** se está na rede local (172.31.1.x) ou externa
6. Configura endpoint correto automaticamente:
   - **Rede local:** `172.31.1.1:13231`
   - **Rede externa:** `190.15.98.231:13231`
7. Mostra informações para aprovação

### **Após a instalação:**

O script mostrará:

```
═══════════════════════════════════════════════════════════════
   ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
═══════════════════════════════════════════════════════════════

📋 INFORMAÇÕES DO DISPOSITIVO:
   Device ID:    tlg-xxxxxxxx
   Hostname:     nome-da-maquina
   IP Local:     192.168.1.100
   IP Público:   203.0.113.50

🔑 CHAVE PÚBLICA WIREGUARD:
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

📝 PRÓXIMOS PASSOS:
1. Envie as informações acima para o administrador aprovar
2. Após aprovação, você receberá um IP da VPN
3. Execute: systemctl start wg-quick@the-lions
4. Verifique: wg show
```

**Envie Device ID, Hostname e Public Key para o administrador aprovar!**

---

## ⚙️ **Aprovação de Clientes**

### **Método 1: Via Script Python**

```bash
python3 scripts/manage_clients.py approve <device-id> <public-key> <hostname>
```

### **Método 2: Via Terminal MikroTik**

```routeros
/interface/wireguard/peers/add \
  interface=the-lions-wg \
  public-key="CHAVE_PUBLICA_DO_CLIENTE" \
  allowed-address=10.99.0.X/32 \
  comment="TLC-device-id-hostname"
```

### **Após aprovação:**

No cliente, execute:

```bash
# Atualizar IP atribuído
sudo sed -i 's/Address = 10.99.0.PENDING/Address = 10.99.0.X/' /etc/wireguard/the-lions.conf

# Habilitar e iniciar
sudo systemctl enable wg-quick@the-lions
sudo systemctl start wg-quick@the-lions

# Verificar
sudo wg show
ping -c 5 10.99.0.1
```

---

## 🔧 **Configuração do Servidor (MikroTik)**

### **Resumo das Regras Necessárias:**

```routeros
# 1. Interface WireGuard
/interface/wireguard add listen-port=13231 mtu=1420 name=the-lions-wg

# 2. IP da Interface
/ip/address add address=10.99.0.1/24 interface=the-lions-wg comment="TLC - WireGuard Server"

# 3. Firewall INPUT
/ip/firewall/filter add chain=input protocol=udp dst-port=13231 action=accept comment="TLC - WireGuard Port"
/ip/firewall/filter add chain=input in-interface=the-lions-wg action=accept comment="TLC - Input from WireGuard"

# 4. Firewall FORWARD
/ip/firewall/filter add chain=forward in-interface=the-lions-wg action=accept comment="TLC - Forward from WireGuard"
/ip/firewall/filter add chain=forward out-interface=the-lions-wg action=accept comment="TLC - Forward to WireGuard"
/ip/firewall/filter add chain=forward src-address=10.99.0.0/24 action=accept comment="TLC - Allow WireGuard Network"
/ip/firewall/filter add chain=forward dst-address=10.99.0.0/24 action=accept comment="TLC - Allow to WireGuard Network"

# 5. Firewall OUTPUT
/ip/firewall/filter add chain=output out-interface=the-lions-wg action=accept comment="TLC - Output to WireGuard"

# 6. Address List (Opcional)
/ip/firewall/address-list add list=ssh-whitelist address=10.99.0.0/24 comment="TLC - WireGuard Network"
```

**⚠️ IMPORTANTE:** As regras de FORWARD devem estar **ANTES** da regra "DROP All Other Forward"!

---

## 📋 **Gerenciamento de Clientes**

### **Listar Clientes Conectados**

```bash
python3 scripts/manage_clients.py list
```

### **Aprovar Novo Cliente**

```bash
python3 scripts/manage_clients.py approve tlg-xxxxxxxx "PUBLIC_KEY" "hostname"
```

### **Remover Cliente**

```bash
python3 scripts/manage_clients.py remove tlg-xxxxxxxx
```

### **Ver Status de um Cliente**

```bash
python3 scripts/manage_clients.py status tlg-xxxxxxxx
```

---

## 🔍 **Troubleshooting**

### **Problema: Ping não funciona (100% packet loss)**

**Diagnóstico:**
```bash
sudo wg show
# Verificar se há "latest handshake"
```

**Soluções:**

1. **Verificar endpoint correto:**
   - Rede local (172.31.1.x): deve usar `172.31.1.1:13231`
   - Rede externa: deve usar `190.15.98.231:13231`

2. **Verificar firewall do MikroTik:**
   ```routeros
   /ip/firewall/filter/print where comment~"TLC"
   ```

3. **Verificar se peer existe:**
   ```routeros
   /interface/wireguard/peers/print
   ```

4. **Verificar se porta UDP 13231 está aberta:**
   ```bash
   nc -vzu 190.15.98.231 13231
   ```

### **Problema: RX=0, TX=0 no MikroTik**

**Causa:** Firewall bloqueando pacotes UDP 13231 ou interface WireGuard

**Solução:** Verificar regras de firewall INPUT:
```routeros
/ip/firewall/filter/print where chain=input and protocol=udp and dst-port=13231
```

### **Problema: "Temporary failure in name resolution"**

**Causa:** DNS não resolve o domínio

**Solução:** Script v2.0 já usa IP direto automaticamente

---

## 🔒 **Segurança**

- ✅ **Criptografia:** ChaCha20-Poly1305 (WireGuard)
- ✅ **Autenticação:** Chaves públicas/privadas únicas por cliente
- ✅ **Firewall:** Regras restritivas no MikroTik
- ✅ **Isolamento:** Cada cliente tem IP único na VPN
- ✅ **Keepalive:** 25 segundos para manter conexão ativa
- ✅ **Zero Trust:** Apenas peers aprovados podem conectar

---

## 📁 **Estrutura do Projeto**

```
the-lions-connect/
├── README.md                 # Documentação principal (v2.0)
├── README-v1.0.md            # Documentação v1.0 (deprecated)
├── install-v2.sh             # Script de instalação v2.0
├── install.sh                # Script v1.0 (deprecated)
├── scripts/
│   └── manage_clients.py     # Gerenciamento de clientes
├── docs/
│   ├── ARCHITECTURE.md       # Arquitetura detalhada
│   ├── INSTALLATION.md       # Guia de instalação
│   ├── TROUBLESHOOTING.md    # Resolução de problemas
│   └── FAQ.md                # Perguntas frequentes
└── examples/
    └── client.conf           # Exemplo de configuração
```

---

## 📊 **Monitoramento**

### **Ver Status de Todos os Peers (MikroTik)**

```routeros
/interface/wireguard/peers/print detail
```

### **Ver Tráfego**

```routeros
/interface/wireguard/peers/print stats
```

### **Logs do WireGuard (Cliente)**

```bash
sudo journalctl -u wg-quick@the-lions -f
```

---

## 🎉 **Changelog**

### **v2.0** (2024-12-14)
- ✅ Migração de SSH para WireGuard
- ✅ Detecção automática de rede local vs externa
- ✅ Script de instalação automatizado
- ✅ Suporte para múltiplos sistemas operacionais
- ✅ Gerenciamento centralizado via MikroTik
- ✅ Configuração de firewall documentada
- ✅ Troubleshooting completo

### **v1.0** (2024-12-XX)
- ✅ Versão inicial com SSH reverse tunneling
- ❌ Descontinuada (MikroTik não suporta SSH -R)

---

## 🤝 **Contribuindo**

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📞 **Suporte**

- **Email:** suporte@thelions.com.br
- **GitHub Issues:** [Reportar Problema](https://github.com/Thelionsinformatica/the-lions-connect/issues)
- **Website:** https://thelions.com.br

---

## 📄 **Licença**

Este projeto é proprietário da **The Lions Informática**.

---

## 👥 **Autores**

**The Lions Group**
- Website: https://thelions.com.br
- GitHub: [@Thelionsinformatica](https://github.com/Thelionsinformatica)

---

**Desenvolvido com 🦁 por The Lions Informática**

**"Tem Internet? Já Era!"**
