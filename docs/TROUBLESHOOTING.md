
# 🔧 **Solução de Problemas (Troubleshooting)**

Se você está enfrentando problemas com o The Lions Connect, este guia pode ajudar a diagnosticar e resolver as questões mais comuns.

---

### **Problema 1: O serviço `the-lions-connect` não inicia ou falha imediatamente.**

Primeiro, verifique o status e os logs do serviço.

```bash
# Verificar o status
systemctl status the-lions-connect

# Ver os logs detalhados
journalctl -u the-lions-connect -n 50 --no-pager
```

#### **Causa Comum 1: Chave SSH não autorizada**

Se os logs mostrarem um erro de `Permission denied (publickey)`, isso significa que a chave pública do seu servidor não foi adicionada corretamente ao Servidor Central.

- **Solução**: Contate o administrador da rede, confirme que ele recebeu a chave pública correta (do arquivo `/root/.ssh/id_manus.pub`) e peça para ele adicioná-la à lista de chaves autorizadas no servidor `thelions.redirectme.net`.

#### **Causa Comum 2: Problema de rede ou firewall**

Se os logs mostrarem um erro de `Connection timed out` ou `Network is unreachable`, o seu servidor não está conseguindo se comunicar com o Servidor Central.

- **Solução**:
  1.  **Teste a conectividade**: Tente pingar e se conectar manualmente ao servidor central. Substitua `2220` pela porta correta, se for diferente.
      ```bash
      ping thelions.redirectme.net
      nc -zv thelions.redirectme.net 2220
      ```
  2.  **Verifique o Firewall**: Certifique-se de que o firewall do seu servidor ou da sua rede permite tráfego de **saída** (outbound) para o endereço `thelions.redirectme.net` na porta TCP `2220`.

#### **Causa Comum 3: Arquivos de configuração corrompidos**

Se os logs mostrarem erros relacionados a arquivos não encontrados ou com formato inválido dentro de `/opt/the-lions-connect`.

- **Solução**: A maneira mais fácil de corrigir isso é reinstalar o The Lions Connect. Primeiro, execute o script de desinstalação e, em seguida, execute o comando de instalação novamente.
  ```bash
  /opt/the-lions-connect/uninstall.sh
  curl -fsSL https://connect.thelions.net/install | bash
  ```
  > **Lembre-se**: A reinstalação gerará um novo ID e uma nova chave SSH. Você precisará enviar as novas informações ao administrador novamente.

---

### **Problema 2: O serviço está `active (running)`, mas o acesso remoto não funciona.**

Isso geralmente indica que o túnel foi estabelecido, mas há um problema no lado do administrador ou no encaminhamento da porta.

#### **Causa Comum 1: Porta incorreta**

O administrador pode estar tentando se conectar à porta errada.

- **Solução**: Verifique o ID do seu dispositivo (no arquivo `/opt/the-lions-connect/config.json`) e peça ao administrador para confirmar qual porta dinâmica foi calculada para esse ID.

#### **Causa Comum 2: Firewall no Servidor Central**

Pode haver uma regra de firewall no Servidor Central (MikroTik) que está bloqueando o acesso à porta dinâmica do seu túnel.

- **Solução**: Peça ao administrador para verificar as regras de firewall no MikroTik e garantir que não há uma regra de `drop` que impeça o acesso à sua porta específica.

---

### **Problema 3: A conexão cai frequentemente.**

O serviço foi projetado para se reconectar, mas quedas frequentes podem indicar um problema de instabilidade na rede.

- **Diagnóstico**: Use ferramentas como `mtr` ou `ping` contínuo para verificar a estabilidade da sua conexão com o servidor `thelions.redirectme.net`.
  ```bash
  mtr thelions.redirectme.net
  ```
- **Solução**: Se for detectada perda de pacotes ou alta latência, o problema provavelmente está na sua rede local ou no seu provedor de internet. Contate o suporte da sua rede.

---

### **Coletando Informações para Suporte**

Se você não conseguir resolver o problema, colete as seguintes informações antes de pedir ajuda ao administrador:

1.  A saída do comando `systemctl status the-lions-connect`.
2.  As últimas 50 linhas dos logs: `journalctl -u the-lions-connect -n 50 --no-pager`.
3.  O conteúdo do arquivo de configuração: `cat /opt/the-lions-connect/config.json`.
4.  O resultado do teste de conectividade: `nc -zv thelions.redirectme.net 2220`.

Fornecer essas informações ajudará a diagnosticar o problema muito mais rapidamente.
