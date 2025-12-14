'''
# 🚀 **Guia de Instalação do Manus Connect**

Este guia detalha o processo de instalação, configuração e uso do Manus Connect para integrar seu servidor à Rede The Lions Group.

---

## 📋 **Pré-requisitos**

Antes de começar, garanta que seu sistema atende aos seguintes requisitos:

- **Sistema Operacional**: Linux (Ubuntu 20.04+, Debian 10+, ou Proxmox 6+)
- **Acesso**: Privilégios de `root` ou `sudo`.
- **Conectividade**: Acesso à internet para baixar o script e estabelecer a conexão.
- **Firewall**: Permissão para tráfego de **saída** (outbound) na porta TCP `2220` (ou a porta configurada no servidor central).

---

## ⚡ **Instalação com Um Comando**

A forma mais simples e recomendada de instalar o Manus Connect é através do nosso script de instalação automatizado.

Abra o terminal no servidor que você deseja conectar e execute o seguinte comando:

```bash
curl -fsSL https://connect.thelions.net/install | bash
```

> **Nota**: O domínio `connect.thelions.net` ainda está em desenvolvimento. Por enquanto, o link aponta para o repositório do GitHub, mas será substituído pelo domínio final.

O script fará o seguinte automaticamente:
1.  Verificará as permissões e o sistema operacional.
2.  Instalará as dependências necessárias (`openssh-client`, `curl`).
3.  Gerará uma chave SSH única para o dispositivo em `/root/.ssh/id_manus`.
4.  Criará um ID de dispositivo único (ex: `tlg-a1b2c3d4`).
5.  Configurará o serviço `systemd` (`manus-connect.service`) para garantir a persistência da conexão.
6.  Exibirá o **ID do Dispositivo** e a **chave pública SSH**.

---

## 🛠️ **Próximos Passos Após a Instalação**

Após a execução do script, a instalação está quase completa. Siga estes passos cruciais:

### **1. Envie o ID e a Chave para o Administrador**

Copie o **ID do Dispositivo** e a **Chave Pública SSH** exibidos no final da instalação e envie-os para o administrador da rede (Manus AI ou um administrador humano).

-   O **ID do Dispositivo** é usado para identificar seu servidor na rede.
-   A **Chave Pública SSH** é necessária para autorizar a conexão do seu servidor no Servidor Central.

### **2. Aguarde a Aprovação**

O administrador precisa adicionar sua chave pública à lista de chaves autorizadas no Servidor Central. **O serviço não funcionará até que esta etapa seja concluída.**

### **3. Inicie o Serviço**

Assim que o administrador confirmar que sua chave foi autorizada, você pode iniciar o serviço de conexão com o seguinte comando:

```bash
systemctl start manus-connect
```

**Pronto!** Seu servidor agora está conectado de forma segura à Rede The Lions Group.

---

## ⚙️ **Verificando o Status da Conexão**

Para verificar se o serviço está rodando corretamente, use o comando:

```bash
systemctl status manus-connect
```

Uma saída bem-sucedida se parecerá com isto:

```
● manus-connect.service - Manus Connect - The Lions Group Network
     Loaded: loaded (/etc/systemd/system/manus-connect.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2025-12-14 14:30:00 UTC; 10min ago
   Main PID: 12345 (connect.sh)
      Tasks: 2 (limit: 4662)
     Memory: 1.2M
     CGroup: /system.slice/manus-connect.service
             ├─12345 /bin/bash /opt/manus-connect/connect.sh
             └─12346 ssh -i /root/.ssh/id_manus -o StrictHostKeyChecking=no ...
```

Se o status for `active (running)`, a conexão está funcionando.

---

## 🗑️ **Desinstalação**

Se você precisar remover o Manus Connect do seu servidor, fornecemos um script de desinstalação simples.

Execute o seguinte comando como `root`:

```bash
/opt/manus-connect/uninstall.sh
```

O script irá:
- Parar e desabilitar o serviço `manus-connect`.
- Remover todos os arquivos de configuração e scripts de `/opt/manus-connect`.
- Remover o arquivo de serviço de `/etc/systemd/system`.
- Remover as chaves SSH geradas (`id_manus` e `id_manus.pub`).

> **Atenção**: A desinstalação não remove a chave pública do Servidor Central. Peça ao administrador para removê-la manualmente.
'''
