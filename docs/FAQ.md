
# ❓ **FAQ - Perguntas Frequentes**

### **1. O que é o Manus Connect?**

O Manus Connect é um sistema de acesso remoto que permite conectar um servidor a uma rede central de forma segura e sem a necessidade de configurar firewalls ou portas de entrada. Ele usa um túnel SSH reverso, o que significa que a conexão é sempre iniciada de dentro do seu servidor para fora.

### **2. É seguro?**

Sim. A segurança é baseada em três pilares:
- **Autenticação por Chave SSH**: Apenas dispositivos com uma chave autorizada podem se conectar.
- **Conexão de Saída**: Seu servidor não fica com nenhuma porta aberta para a internet, prevenindo ataques diretos.
- **Criptografia SSH**: Todo o tráfego dentro do túnel é criptografado pelo protocolo SSH.

### **3. Preciso abrir alguma porta no meu firewall?**

Não. Você só precisa garantir que seu servidor tenha permissão para iniciar conexões de **saída** (outbound) para a porta `2220` (ou a porta configurada) do servidor central `thelions.redirectme.net`.

### **4. Como o Manus Connect é diferente de uma VPN tradicional (como OpenVPN ou WireGuard)?**

Uma VPN tradicional cria uma interface de rede virtual e roteia o tráfego através dela, fazendo com que seu servidor se torne parte de uma rede privada virtual. O Manus Connect, por outro lado, foca em um único objetivo: fornecer acesso SSH reverso. Ele não cria uma interface de rede nem altera suas rotas. É uma solução mais leve e focada especificamente no acesso remoto para gerenciamento.

### **5. O que acontece se a minha conexão com a internet cair?**

O serviço `manus-connect` foi projetado para ser resiliente. Assim que sua conexão com a internet for restaurada, ele tentará se reconectar automaticamente ao servidor central.

### **6. O que é o "ID do Dispositivo"?**

O ID do Dispositivo (ex: `tlg-a1b2c3d4`) é um identificador único gerado durante a instalação. Ele é usado para:
- Identificar seu servidor na rede central.
- Calcular uma porta de acesso remoto única e determinística para o seu túnel.

### **7. Por que preciso enviar a chave pública para um administrador?**

O Servidor Central usa uma lista de chaves autorizadas para controlar quem pode se conectar. Enviar sua chave pública permite que o administrador adicione seu servidor a essa lista. Sem essa autorização, o servidor central recusará a conexão, mesmo que você tenha o endereço e a porta corretos.

### **8. Posso instalar o Manus Connect em um servidor Windows?**

Atualmente, o Manus Connect é projetado exclusivamente para sistemas baseados em Linux (Debian, Ubuntu, Proxmox). O suporte para Windows não está disponível no momento.

### **9. Como posso ver os logs de conexão?**

Você pode ver os logs em tempo real do serviço com o comando:
```bash
journalctl -u manus-connect -f
```
Isso é útil para diagnosticar problemas de conexão.

### **10. A desinstalação remove tudo?**

O script `uninstall.sh` remove todos os arquivos e configurações do Manus Connect do **seu servidor cliente**. No entanto, ele **não** remove a sua chave pública da lista de autorização do **Servidor Central**. Isso deve ser feito manualmente por um administrador para garantir que a chave antiga não possa mais ser usada.
