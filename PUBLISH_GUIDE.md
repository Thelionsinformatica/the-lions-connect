# 📤 **Guia de Publicação no GitHub**

Este guia explica como publicar o projeto The Lions Connect no GitHub.

---

## 🔑 **Pré-requisitos**

1. Ter uma conta no GitHub
2. Ter o GitHub CLI (`gh`) instalado e autenticado
3. Ter acesso à organização `Thelionsinformatica` no GitHub

---

## 📋 **Passos para Publicação**

### **1. Autenticar no GitHub CLI**

Se ainda não estiver autenticado, execute:

```bash
gh auth login
```

Siga as instruções para autenticar com sua conta GitHub.

### **2. Criar o Repositório no GitHub**

No diretório do projeto, execute:

```bash
cd /home/ubuntu/the-lions-connect

# Criar repositório público na organização
gh repo create Thelionsinformatica/the-lions-connect \
  --public \
  --source=. \
  --description="🦁 Sistema plug-and-play de acesso remoto - Funciona através de qualquer firewall/NAT" \
  --push
```

### **3. Verificar a Publicação**

Acesse o repositório no navegador:

```bash
gh repo view --web
```

Ou acesse diretamente: https://github.com/Thelionsinformatica/the-lions-connect

### **4. Configurar GitHub Pages (Opcional)**

Para habilitar o GitHub Pages e servir a documentação:

1. Acesse: https://github.com/Thelionsinformatica/the-lions-connect/settings/pages
2. Em "Source", selecione: `main` branch
3. Clique em "Save"

A documentação estará disponível em:
`https://thelionsinformatica.github.io/the-lions-connect/`

### **5. Testar a Instalação**

Após a publicação, teste o comando de instalação:

```bash
curl -fsSL https://raw.githubusercontent.com/Thelionsinformatica/the-lions-connect/main/install.sh | bash
```

---

## 🏷️ **Criar uma Release (Versão)**

Para criar uma versão oficial:

```bash
cd /home/ubuntu/the-lions-connect

# Criar tag
git tag -a v1.0.0 -m "The Lions Connect v1.0.0 - Initial Release"

# Enviar tag para o GitHub
git push origin v1.0.0

# Criar release no GitHub
gh release create v1.0.0 \
  --title "The Lions Connect v1.0.0" \
  --notes "🎉 **Primeira versão oficial do The Lions Connect!**

## ✨ Funcionalidades

- ✅ Instalação com um comando
- ✅ Túnel SSH reverso automático
- ✅ Reconexão automática
- ✅ Zero configuração de firewall
- ✅ Gerenciamento de clientes
- ✅ Documentação completa

## 📦 Instalação

\`\`\`bash
curl -fsSL https://raw.githubusercontent.com/Thelionsinformatica/the-lions-connect/main/install.sh | bash
\`\`\`"
```

---

## 🔄 **Atualizações Futuras**

Para publicar atualizações:

```bash
cd /home/ubuntu/the-lions-connect

# Fazer alterações...

# Adicionar e commitar
git add .
git commit -m "Descrição das alterações"

# Enviar para o GitHub
git push origin main
```

---

## ✅ **Checklist de Publicação**

- [ ] Repositório criado no GitHub
- [ ] Código enviado (push)
- [ ] README.md visível na página principal
- [ ] Documentação acessível na pasta `docs/`
- [ ] Script de instalação testado via URL do GitHub
- [ ] Release v1.0.0 criada
- [ ] GitHub Pages configurado (opcional)

---

**🦁 The Lions Group - Transformando infraestrutura em inteligência**
