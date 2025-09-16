# System TI - Guia de Deploy no Linux

## 🐧 Deploy no Linux Ubuntu/CentOS

### Pré-requisitos

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# ou
sudo yum update -y  # CentOS/RHEL

# Instalar dependências básicas
sudo apt install -y curl wget git  # Ubuntu
# ou
sudo yum install -y curl wget git  # CentOS
```

### 1. Instalar Docker

```bash
# Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar para aplicar permissões
sudo reboot
```

### 2. Clonar o Repositório

```bash
# Clonar projeto
git clone https://github.com/yuripereirafl/System_ti-main.git
cd System_ti-main

# Dar permissões aos scripts
chmod +x deploy.sh setup.sh
```

### 3. Configuração Automática

```bash
# Executar configurador
./setup.sh

# Ou configurar manualmente:
cp .env.example .env
nano .env  # Editar conforme necessário
```

### 4. Deploy com Docker

```bash
# Deploy completo
./deploy.sh

# Ou manualmente:
docker-compose up --build -d
```

### 5. Verificar Deploy

```bash
# Verificar containers
docker-compose ps

# Ver logs
docker-compose logs -f

# Testar API
curl http://localhost:8000/docs
```

## 🔧 Configurações Linux Específicas

### Firewall (Ubuntu)

```bash
# Abrir portas necessárias
sudo ufw allow 8000/tcp  # Backend
sudo ufw allow 8080/tcp  # Frontend
sudo ufw allow 5432/tcp  # PostgreSQL (se externo)
sudo ufw enable
```

### Systemd Service (Opcional)

Criar `/etc/systemd/system/system-ti.service`:

```ini
[Unit]
Description=System TI Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/System_ti-main
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar serviço
sudo systemctl enable system-ti.service
sudo systemctl start system-ti.service
```

### Nginx Reverse Proxy (Opcional)

```bash
# Instalar Nginx
sudo apt install nginx -y

# Configurar proxy
sudo nano /etc/nginx/sites-available/system-ti
```

Configuração Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/system-ti /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🛠️ Comandos Úteis Linux

```bash
# Monitorar recursos
htop
docker stats

# Limpar Docker
docker system prune -a

# Backup banco de dados
docker exec system-ti-db-1 pg_dump -U postgres intelix_rh > backup.sql

# Restaurar backup
docker exec -i system-ti-db-1 psql -U postgres intelix_rh < backup.sql

# Ver logs do sistema
journalctl -u system-ti.service -f

# Reiniciar serviços
docker-compose restart backend
docker-compose restart frontend
```

## 🔍 Troubleshooting Linux

### Problema: Porta já em uso

```bash
# Verificar processo na porta
sudo netstat -tulpn | grep :8080
sudo lsof -i :8080

# Matar processo
sudo kill -9 <PID>
```

### Problema: Permissões Docker

```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Ou usar sudo
sudo docker-compose up -d
```

### Problema: Firewall bloqueando

```bash
# Ubuntu
sudo ufw status
sudo ufw allow 8000
sudo ufw allow 8080

# CentOS
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

### Problema: Baixa performance

```bash
# Aumentar limites Docker
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Monitorar recursos
docker stats --no-stream
free -h
df -h
```

## 📊 Monitoramento

### Logs centralizados

```bash
# Ver todos os logs
docker-compose logs -f --tail=100

# Logs específicos
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### Health checks

```bash
# Verificar saúde dos containers
docker-compose ps

# Teste de conectividade
curl -f http://localhost:8000/health || echo "Backend down"
curl -f http://localhost:8080 || echo "Frontend down"
```

## 🚀 Deploy Automatizado

Script `auto-deploy.sh`:

```bash
#!/bin/bash
cd /path/to/System_ti-main
git pull origin main
docker-compose down
docker-compose up --build -d
docker-compose logs --tail=20
```

```bash
# Executar deploy automatizado
chmod +x auto-deploy.sh
./auto-deploy.sh
```

---

**Suporte:** Para problemas específicos do Linux, verifique os logs e consulte a documentação do Docker Compose.
