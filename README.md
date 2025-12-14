# 🦁 Manus Connect

**Sistema plug-and-play para conectar servidores à Rede The Lions Group**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

---

## 📋 **O que é?**

**Manus Connect** é um sistema de conexão automática que permite integrar qualquer servidor Linux à **Rede The Lions Group** de forma simples e segura, similar ao ZeroTier.

Com apenas **um comando**, seu servidor:
- ✅ Conecta automaticamente à rede central
- ✅ Configura túnel SSH reverso seguro
- ✅ Permite acesso remoto gerenciado pela IA Manus
- ✅ Reconecta automaticamente se a conexão cair
- ✅ Zero configuração manual de firewall

---

## 🚀 **Instalação Rápida**

### **No servidor que deseja conectar:**

```bash
curl -fsSL https://raw.githubusercontent.com/Thelionsinformatica/manus-connect/main/install.sh | bash
```

**Ou usando a URL curta (em breve):**

```bash
curl -fsSL connect.thelions.net | bash
```

**Pronto!** Seu servidor está conectado à **Rede The Lions Group**.

---

## 📖 **Como Funciona**

```
┌─────────────────────────────────────────────────────────────┐
│                   REDE THE LIONS GROUP                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Seu Servidor                                               │
│       │                                                     │
│       ├─ Executa install.sh                                │
│       ├─ Configura túnel SSH reverso                       │
│       ├─ Conecta ao Manus (IA)                             │
│       │                                                     │
│       ▼                                                     │
│  Manus (IA Central)                                        │
│       │                                                     │
│       ├─ Gerencia acesso                                   │
│       ├─ Monitora status                                   │
│       ├─ Executa tarefas                                   │
│       └─ Mantém conexão ativa                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ **Características**

### **🔒 Segurança**
- Túnel SSH reverso (conexão iniciada de dentro para fora)
- Autenticação por chave SSH (sem senha)
- Porta customizada (não-padrão)
- Criptografia end-to-end

### **🚀 Facilidade**
- Instalação com 1 comando
- Zero configuração manual
- Auto-detecção de ambiente
- Compatível com Proxmox, Ubuntu, Debian

### **🔄 Confiabilidade**
- Auto-reconexão se cair
- Serviço systemd (inicia no boot)
- Monitoramento contínuo
- Logs detalhados

### **📊 Gerenciamento**
- Status em tempo real
- Comandos de controle simples
- Fácil desinstalação
- Sem impacto na rede existente

---

## 📦 **Requisitos**

- **Sistema Operacional:** Linux (Ubuntu 20.04+, Debian 10+, Proxmox 6+)
- **Acesso:** root ou sudo
- **Conectividade:** Acesso à internet
- **Portas:** Saída TCP porta 52222 (configurável)

---

## 🔧 **Comandos Úteis**

### **Ver status da conexão:**
```bash
systemctl status manus-connect
```

### **Parar conexão:**
```bash
systemctl stop manus-connect
```

### **Iniciar conexão:**
```bash
systemctl start manus-connect
```

### **Reiniciar conexão:**
```bash
systemctl restart manus-connect
```

### **Ver logs:**
```bash
journalctl -u manus-connect -f
```

### **Desinstalar:**
```bash
/opt/manus-connect/uninstall.sh
```

---

## 📚 **Documentação**

- [Guia de Instalação](docs/INSTALLATION.md)
- [Solução de Problemas](docs/TROUBLESHOOTING.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [FAQ](docs/FAQ.md)

---

## 🛠️ **Arquitetura**

```
manus-connect/
├── install.sh              # Script de instalação principal
├── manus-agent.py          # Agente de gerenciamento
├── config/
│   ├── mikrotik_rules.rsc  # Regras de firewall MikroTik
│   └── systemd.service     # Serviço systemd
├── scripts/
│   ├── configure_mikrotik.py   # Configura MikroTik via API
│   ├── setup_tunnel.sh         # Configura túnel SSH
│   └── uninstall.sh            # Script de desinstalação
└── docs/
    └── ...                 # Documentação completa
```

---

## 🤝 **Suporte**

- **Issues:** [GitHub Issues](https://github.com/Thelionsinformatica/manus-connect/issues)
- **Email:** suporte@thelions.com.br
- **Website:** https://thelions.com.br

---

## 📄 **Licença**

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 👥 **Autores**

**The Lions Group**
- Website: https://thelions.com.br
- GitHub: [@Thelionsinformatica](https://github.com/Thelionsinformatica)

---

## 🙏 **Agradecimentos**

Desenvolvido com ❤️ pela equipe The Lions Group e powered by **Manus AI**.

---

**🦁 The Lions Group - Transformando infraestrutura em inteligência**
