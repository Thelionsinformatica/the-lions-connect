'''
# 🏛️ **Arquitetura do The Lions Connect**

## **Visão Geral**

O The Lions Connect foi projetado para ser um sistema de acesso remoto **simples, seguro e resiliente**. A arquitetura se baseia no conceito de **túnel reverso SSH**, onde a conexão é sempre iniciada pelo cliente (servidor a ser acessado) em direção a um ponto central (servidor de salto), eliminando a necessidade de abrir portas de entrada no firewall do cliente.

Isso o torna ideal para ambientes com restrições de rede, como NAT, CGNAT ou firewalls corporativos, seguindo o princípio "se tem internet, conecta".

---

## 🧱 **Componentes Principais**

```mermaid
graph TD
    subgraph Cliente (Servidor Remoto)
        A[Serviço Systemd: the-lions-connect.service] --> B{Script: connect.sh};
        B --> C{Comando SSH};
    end

    subgraph Servidor Central (Jump Host - MikroTik)
        D[Servidor SSH na porta 2220];
    end

    subgraph Admin (Manus AI)
        E[Acesso via SSH];
    end

    C --"Túnel Reverso<br>-R porta_dinamica:localhost:22"--> D;
    E --"Acessa túnel<br>ssh -p porta_dinamica localhost"--> C;

    style Cliente fill:#cde4ff,stroke:#333,stroke-width:2px
    style Admin fill:#d2ffd2,stroke:#333,stroke-width:2px
```

1.  **Cliente (Servidor a ser Acessado)**:
    *   **`install.sh`**: Script de instalação que configura o ambiente, gera chaves SSH e cria o serviço.
    *   **`the-lions-connect.service`**: Um serviço `systemd` que garante que a conexão seja persistente e reinicie automaticamente em caso de falha ou após o boot do sistema.
    *   **`connect.sh`**: O script principal que executa o comando `ssh` para estabelecer o túnel reverso.
    *   **Chave SSH (`/root/.ssh/id_manus`)**: Chave dedicada para autenticação segura e sem senha com o servidor central.

2.  **Servidor Central (Jump Host)**:
    *   Atualmente, é o seu roteador **MikroTik (`thelions.redirectme.net`)**.
    *   Ele executa um servidor SSH em uma porta não padrão (**2220**) que atua como ponto de encontro para todos os clientes.
    *   Ele não armazena dados, apenas encaminha as conexões tuneladas.

3.  **Administrador (Manus AI)**:
    *   Para acessar um cliente, o administrador (Manus) se conecta ao túnel reverso estabelecido no Servidor Central.
    *   O acesso é feito via `ssh -p <porta_dinamica> localhost`, onde a `<porta_dinamica>` é uma porta única mapeada para aquele cliente específico.

---

## 🌊 **Fluxo da Conexão**

1.  **Instalação**: O usuário executa o `install.sh` no servidor cliente.
2.  **Geração de ID**: O script gera um ID único para o dispositivo (ex: `tlg-a1b2c3d4`) e uma chave SSH.
3.  **Cálculo da Porta**: Uma porta remota dinâmica (entre 10000 e 65535) é calculada deterministicamente a partir do ID do dispositivo. Isso garante que cada cliente tenha sua própria porta de acesso, sem colisões.
4.  **Início do Serviço**: O serviço `the-lions-connect.service` é iniciado.
5.  **Estabelecimento do Túnel**: O `connect.sh` executa o comando `ssh` para conectar ao Servidor Central (MikroTik) e solicita um túnel reverso:
    ```bash
    ssh -R <porta_dinamica>:localhost:22 jarvis@thelions.redirectme.net -p 2220
    ```
    *   `-R <porta_dinamica>:localhost:22`: Instrução para o servidor remoto (MikroTik). "Qualquer tráfego que chegar na sua `<porta_dinamica>`, encaminhe para o `localhost:22` deste cliente."
6.  **Conexão Persistente**: O serviço `systemd` e as opções `ServerAliveInterval` no comando SSH garantem que a conexão permaneça ativa e se restabeleça automaticamente.
7.  **Acesso Remoto**: O administrador (Manus) agora pode acessar o cliente executando um comando SSH para a porta dinâmica no Servidor Central. O tráfego é então tunelado de volta para o cliente.

---

## 🔐 **Segurança**

-   **Conexão Iniciada pelo Cliente**: O firewall do cliente não precisa de nenhuma porta de entrada aberta, pois a conexão é de saída (outbound).
-   **Autenticação por Chave**: O acesso é feito exclusivamente via chaves SSH, desabilitando a autenticação por senha, o que previne ataques de força bruta.
-   **Porta Não Padrão**: O uso da porta 2220 para o servidor SSH central reduz a exposição a scans automatizados que visam a porta 22.
-   **Isolamento**: Cada cliente tem seu próprio túnel e porta dedicada. Um cliente não tem acesso a outro.
-   **Mínimo Privilégio**: O usuário `jarvis` no servidor central tem permissões limitadas, apenas o suficiente para estabelecer os túneis.
'''
