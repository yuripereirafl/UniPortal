#!/usr/bin/env bash
set -euo pipefail

# deploy.sh (versão simples, sem backups)
# Atualiza/clona a branch indicada e sobe o stack via docker compose
# Uso: ./deploy.sh [branch] [use_compose]
#  branch: nome da branch a clonar/atualizar (padrão: Portal_atual)
#  use_compose: "true"|"false" - quando true (padrão) o script define DB_HOST=db no .env

BRANCH=${1:-Portal_atual}
USE_COMPOSE=${2:-true}
TARGET_DIR="${HOME}/uniportal-main-fresh"
REPO_URL="https://github.com/yuripereirafl/UniPortal.git"

echo "-> Deploy simplified: branch=${BRANCH}, use_compose=${USE_COMPOSE}, target=${TARGET_DIR}"

command -v git >/dev/null 2>&1 || { echo "git não encontrado; instale git e reexecute."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "docker não encontrado; instale docker e reexecute."; exit 1; }

cd "$HOME"

if [ -d "$TARGET_DIR" ]; then
  cd "$TARGET_DIR"
  if [ -d .git ]; then
    echo "Atualizando repositório existente..."
    git fetch origin
    git checkout "$BRANCH"
    git reset --hard "origin/${BRANCH}"
    git clean -fd
  else
    echo "Diretório existe mas não é um repositório git. Removendo e clonando..."
    rm -rf "$TARGET_DIR"
    git clone --branch "$BRANCH" "$REPO_URL" "$TARGET_DIR"
    cd "$TARGET_DIR"
  fi
else
  echo "Clonando repositório..."
  git clone --branch "$BRANCH" "$REPO_URL" "$TARGET_DIR"
  cd "$TARGET_DIR"
fi

if [ -f .env ]; then
  echo ".env encontrado (não será feito backup)."
else
  echo "Atenção: .env não encontrado no repositório. Crie um arquivo .env com suas variáveis de ambiente." 
fi

if [ "$USE_COMPOSE" = "true" ] || [ "$USE_COMPOSE" = "True" ]; then
  # Quando o stack for iniciado via docker-compose, o host do DB no backend deve ser 'db'
  if grep -q '^DB_HOST=' .env 2>/dev/null; then
    sed -i 's/^DB_HOST=.*/DB_HOST=db/' .env
    echo "Ajustado DB_HOST=db no .env para uso com docker-compose"
  else
    echo "DB_HOST=db" >> .env
    echo "Adicionada linha DB_HOST=db no .env"
  fi
fi

echo "Subindo containers (rebuild)..."
sudo docker compose up -d --build --remove-orphans

echo "Aguardando alguns segundos para o startup..."
sleep 5

echo "Containers ativos:"
sudo docker compose ps

echo "Logs iniciais (backend - últimas 80 linhas):"
sudo docker compose logs --no-color --tail=80 backend || true

echo "Deploy finalizado. Verifique / abra os logs com: sudo docker compose logs -f backend"

echo "=== DEPLOY SYSTEM TI - DOCKER ==="

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

echo "✅ Docker está rodando"

# Verificar se existe arquivo .env
if [ ! -f ".env" ]; then
    echo "⚠️ Arquivo .env não encontrado. Criando configuração padrão..."
    echo "💡 Execute ./setup.sh para configuração automática"
    cp .env.example .env
fi

# Carregar variáveis do .env
source .env

echo ""
echo "🚀 Deploy concluído!"
echo "📱 Frontend: http://$HOST_IP:${FRONTEND_PORT:-8080}"
echo "🔧 Backend: http://$HOST_IP:${BACKEND_PORT:-8000}"
echo "🗄️ Database: $HOST_IP:${DATABASE_PORT:-5432}"
echo ""
echo "Para ver logs em tempo real: docker-compose logs -f"
echo "Para parar os serviços: docker-compose down"
