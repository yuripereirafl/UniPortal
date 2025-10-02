# System TI - Deploy com Docker

## 🐳 Configuração Docker

Este projeto agora inclui configuração completa com Docker para facilitar o deploy e eliminar problemas de configuração de IPs.

### Pré-requisitos

- Docker instalado
- Docker Compose instalado

### Estrutura Docker

```
System_ti-main/
├── docker-compose.yml          # Orquestração dos serviços
├── .env                        # Variáveis de ambiente
├── deploy.sh                   # Script de deploy (Linux/Mac)
├── deploy.ps1                  # Script de deploy (Windows)
├── backend/
│   ├── Dockerfile             # Container do backend
│   └── .dockerignore
└── frontend/
    ├── Dockerfile             # Container do frontend
    └── .dockerignore
```

### Serviços

1. **Backend** - FastAPI (Porta 8000)
2. **Frontend** - Vue.js (Porta 8080)
3. **Database** - PostgreSQL (Porta 5432)

### Como usar

#### Deploy Rápido

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows PowerShell:**
```powershell
./deploy.ps1
```

#### Deploy Manual

```bash
# Construir e iniciar todos os serviços
docker-compose up --build -d

# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### Configurações

Edite o arquivo `.env` para alterar:
- IPs e portas
- Credenciais do banco
- URLs da API

### Acesso

- **Frontend:** http://192.168.1.37:8080
- **Backend API:** http://192.168.1.37:8000
- **Database:** 192.168.1.37:5432

### Comandos Úteis

```bash
# Ver logs específicos
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Reiniciar um serviço específico
docker-compose restart backend

# Reconstruir sem cache
docker-compose build --no-cache

# Limpar tudo
docker-compose down --rmi all --volumes
```

### Vantagens do Docker

✅ **Portabilidade** - Roda em qualquer ambiente  
✅ **Consistência** - Mesmo ambiente em dev/prod  
✅ **Facilidade** - Deploy com um comando  
✅ **Isolamento** - Não interfere no sistema host  
✅ **Escalabilidade** - Fácil de escalar serviços  

### Solução de Problemas

1. **Porta já em uso:**
   ```bash
   sudo netstat -tulpn | grep :8080
   docker-compose down
   ```

2. **Banco não conecta:**
   - Verificar credenciais no `.env`
   - Aguardar inicialização completa do PostgreSQL

3. **Frontend não carrega:**
   - Verificar se backend está rodando
   - Verificar variável VUE_APP_API_URL
