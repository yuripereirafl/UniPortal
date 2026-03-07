#!/bin/bash

echo "=== CONFIGURADOR AUTOMÁTICO SYSTEM TI ==="

# Detectar ambiente
echo "Detectando ambiente..."

# Verificar se Docker está disponível
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "✅ Docker detectado"
    USAR_DOCKER=true
else
    echo "❌ Docker não encontrado ou não está rodando"
    USAR_DOCKER=false
fi

# Perguntar tipo de deploy
echo ""
echo "Escolha o tipo de deploy:"
echo "1) Docker (Recomendado - ambiente isolado)"
echo "2) VMware Linux (host específico)"
echo "3) Desenvolvimento local"
read -p "Opção [1-3]: " opcao

case $opcao in
    1)
        echo "🐳 Configurando para Docker..."
        cat > .env << EOF
# Configuração Docker
FRONTEND_PORT=8080
BACKEND_PORT=8000
DATABASE_PORT=5432
DB_HOST=db
DB_NAME=intelix_rh
DB_USER=postgres
DB_PASSWORD=yourpassword
API_URL=http://localhost:8000
VUE_APP_API_URL=http://localhost:8000
COMPOSE_PROJECT_NAME=system-ti
EOF
        echo "✅ Configuração Docker criada"
        
        if [ "$USAR_DOCKER" = true ]; then
            echo "🚀 Iniciando deploy com Docker..."
            ./deploy.sh
        else
            echo "⚠️ Instale o Docker primeiro e execute: ./deploy.sh"
        fi
        ;;
    2)
        # Padronizar IP da VMware
        ip_server="192.168.1.37"
        db_name="dadosrh"
        db_user="dadosrh"
        db_pass="dadosrh"

        echo "🖥️ Configurando para VMware Linux (IP: $ip_server)..."
        cat > .env << EOF
# Configuração VMware Linux
FRONTEND_PORT=8080
BACKEND_PORT=8000
DATABASE_PORT=5432
DB_HOST=$ip_server
DB_NAME=$db_name
DB_USER=$db_user
DB_PASSWORD=$db_pass
API_URL=http://$ip_server:8000
VUE_APP_API_URL=http://$ip_server:8000
COMPOSE_PROJECT_NAME=uniportal-main-fresh
EOF

        # Atualizar frontend .env também
        echo "VUE_APP_API_URL=http://$ip_server:8000" > frontend/.env

        echo "✅ Configuração VMware criada"
        echo "ℹ️ Para aplicar as alterações, execute:"
        echo "   docker compose down"
        echo "   docker compose build"
        echo "   docker compose up -d"
        ;;
    3)
        echo "💻 Configurando para desenvolvimento local..."
        cat > .env << EOF
# Configuração Desenvolvimento Local
FRONTEND_PORT=8080
BACKEND_PORT=8000
DATABASE_PORT=5432
DB_HOST=localhost
DB_NAME=intelix_rh
DB_USER=postgres
DB_PASSWORD=postgres
API_URL=http://localhost:8000
VUE_APP_API_URL=http://localhost:8000
COMPOSE_PROJECT_NAME=system-ti
EOF
        
        echo "VUE_APP_API_URL=http://localhost:8000" > frontend/.env
        
        echo "✅ Configuração local criada"
        echo "ℹ️ Configure seu PostgreSQL local e execute backend/frontend separadamente"
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "🎉 Configuração concluída!"
echo "📁 Arquivo .env criado com as configurações"
echo "📋 Para mais detalhes, consulte DOCKER_README.md"
