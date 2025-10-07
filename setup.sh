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
        read -p "Digite o IP do servidor VMware [192.168.1.37]: " ip_server
        ip_server=${ip_server:-192.168.1.37}
        
        read -p "Digite o nome do banco [dadosrh]: " db_name
        db_name=${db_name:-dadosrh}
        
        read -p "Digite o usuário do banco [dadosrh]: " db_user
        db_user=${db_user:-dadosrh}
        
        read -p "Digite a senha do banco [dadosrh]: " db_pass
        db_pass=${db_pass:-dadosrh}
        
        echo "🖥️ Configurando para VMware Linux..."
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
COMPOSE_PROJECT_NAME=system-ti
EOF
        
        # Atualizar frontend .env também
        echo "VUE_APP_API_URL=http://$ip_server:8000" > frontend/.env
        
        echo "✅ Configuração VMware criada"
        echo "ℹ️ Para deploy manual, execute os comandos de backend e frontend"
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
