#!/bin/bash

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

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Remover imagens antigas (opcional)
read -p "Deseja remover imagens antigas? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removendo imagens antigas..."
    docker-compose down --rmi all
fi

# Construir e iniciar serviços
echo "🔨 Construindo e iniciando serviços..."
docker-compose up --build -d

# Verificar status
echo "📊 Status dos containers:"
docker-compose ps

# Mostrar logs (últimas 20 linhas)
echo "📝 Logs dos serviços:"
docker-compose logs --tail=20

# Detectar IP do host para exibir URLs corretas
HOST_IP=${DB_HOST:-localhost}
if [ "$HOST_IP" = "db" ]; then
    HOST_IP="localhost"
fi

echo ""
echo "🚀 Deploy concluído!"
echo "📱 Frontend: http://$HOST_IP:${FRONTEND_PORT:-8080}"
echo "🔧 Backend: http://$HOST_IP:${BACKEND_PORT:-8000}"
echo "🗄️ Database: $HOST_IP:${DATABASE_PORT:-5432}"
echo ""
echo "Para ver logs em tempo real: docker-compose logs -f"
echo "Para parar os serviços: docker-compose down"
