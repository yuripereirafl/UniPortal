# ✅ CHECKLIST DEPLOY PRODUÇÃO

## 📋 Pré-deploy (Concluído)

- [x] **Configurações flexíveis**: IPs parametrizados via .env
- [x] **Docker implementado**: Backend + Frontend + Database
- [x] **Segurança**: Senhas via variáveis de ambiente
- [x] **GitIgnore**: Arquivos sensíveis protegidos
- [x] **Documentação**: Guias completos criados
- [x] **Scripts**: Deploy automático para Linux

## 🐧 Deploy no Linux

### 1. Clonar do GitHub
```bash
git clone https://github.com/yuripereirafl/System_ti-main.git
cd System_ti-main
```

### 2. Instalar Docker (se necessário)
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar
sudo reboot
```

### 3. Configurar Ambiente
```bash
# Dar permissões
chmod +x deploy.sh setup.sh

# Configuração automática
./setup.sh

# Ou manual
cp .env.example .env
nano .env  # Ajustar configurações
```

### 4. Deploy
```bash
# Deploy completo
./deploy.sh

# Verificar
docker-compose ps
docker-compose logs -f
```

## 🔧 Configurações Disponíveis

### Para Docker (Recomendado)
```env
DB_HOST=db
DB_NAME=intelix_rh
DB_USER=postgres
DB_PASSWORD=yourpassword
VUE_APP_API_URL=http://localhost:8000
```

### Para Servidor Específico
```env
DB_HOST=192.168.1.37
DB_NAME=dadosrh
DB_USER=dadosrh
DB_PASSWORD=dadosrh
VUE_APP_API_URL=http://192.168.1.37:8000
```

## 🚀 URLs de Acesso

- **Frontend**: http://servidor:8080
- **Backend**: http://servidor:8000
- **API Docs**: http://servidor:8000/docs

## 📞 Suporte

- **Documentação completa**: `LINUX_DEPLOY.md`
- **Docker**: `DOCKER_README.md`
- **Troubleshooting**: Verificar logs com `docker-compose logs`

---

**Status**: ✅ **PRONTO PARA PRODUÇÃO**
