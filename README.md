# UniPortal - Sistema de Gestão Organizacional

> **Versão 2.0** - Sistema simplificado e otimizado para gestão empresarial

## 🎯 **Sobre o Sistema**

O **UniPortal** é uma plataforma integrada para gestão de colaboradores, controle de acessos e análise de desempenho organizacional. Esta versão foi completamente limpa e reorganizada para máxima eficiência.

## ⚡ **Características Principais**

- 🏢 **Gestão Completa de Colaboradores** - Cadastro, edição e controle
- 🔐 **Sistema de Permissões Avançado** - Controle granular de acessos 
- 📊 **Dashboard Analítico** - Métricas e indicadores em tempo real
- 💼 **Gestão de Sistemas e Grupos** - Organização por departamentos
- 📈 **Relatórios e Performance** - Análises detalhadas de produtividade
- 🚀 **Deploy Simplificado** - Configuração automática por ambiente

## 🏗️ **Arquitetura**

```
UniPortal/
├── 📁 backend/          # API FastAPI + PostgreSQL
├── 📁 frontend/         # Interface Vue.js 3
├── 📁 config/           # Configurações centralizadas  
├── 📁 scripts/          # Scripts de manutenção e análise
├── 📁 _removed_components/ # Componentes desabilitados
├── 🐳 docker-compose.yml   # Deploy containerizado
└── 📄 .env                 # Configuração única
```

### **Stack Tecnológica:**
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** Vue.js 3 + Composition API + Axios  
- **Deploy:** Docker + Docker Compose
- **Banco:** PostgreSQL (servidor externo)

## 🚀 **Quick Start**

### **1. Configuração**
```bash
# Clonar e configurar
git clone [repo]
cd UniPortal-Portal_atual

# Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações
```

### **2. Execução com Docker (Recomendado)**
```bash
# Subir toda a aplicação
docker-compose up -d

# Acessar:
# Frontend: http://192.168.1.37:8080
# Backend: http://192.168.1.37:8000
```

### **3. Desenvolvimento Local**
```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (terminal separado)
cd frontend  
npm install
npm run serve
```

## 📋 **Funcionalidades Disponíveis**

### ✅ **Módulos Ativos**
- **👥 Funcionários** - CRUD completo com hierarquia
- **🔧 Sistemas** - Gestão de softwares e acessos
- **🏢 Setores** - Organização departamental
- **📧 Grupos de Email** - Listas de distribuição
- **📁 Grupos de Pasta** - Controle de diretórios compartilhados
- **💬 Grupos WhatsApp** - Gestão de comunicação
- **👤 Usuários** - Autenticação e permissões
- **💼 Cargos** - Hierarquia organizacional
- **📊 Dashboard** - Métricas e KPIs em tempo real
- **📈 Performance** - Análise de produtividade
- **🏆 Ranking** - Classificação por desempenho
- **💰 Vendas** - Dados comerciais
- **⭐ NPS/CSAT** - Indicadores de satisfação
- **💵 Orçamentos** - Controle financeiro
- **💎 Comissões** - Cálculo de remuneração variável

### ❌ **Módulos Desabilitados**
- ~~Quadro de Colaboradores~~ (funcionalidade removida)
- ~~Meta de Colaboradores~~ (sistema simplificado)
- ~~Meta de Unidades~~ (foco em outros indicadores)

## 🔧 **Configuração**

O sistema utiliza **configuração centralizada** através do arquivo [`config/settings.py`](config/settings.py):

### **Por Ambiente:**
```python
# Development
ENVIRONMENT=development
DB_HOST=192.168.1.37  # Sempre servidor externo

# Production  
ENVIRONMENT=production
DB_HOST=192.168.1.37  # Servidor otimizado

# Testing
ENVIRONMENT=testing
DB_HOST=192.168.1.37  # Base de testes isolada
```

### **Variáveis Principais:**
```bash
# Banco de Dados (SEMPRE externo)
DB_HOST=192.168.1.37
DB_PORT=5432
DB_USER=dadosrh
DB_PASSWORD=dadosrh
DB_NAME=dadosrh

# Aplicação
BACKEND_PORT=8000
FRONTEND_PORT=8080
SECRET_KEY=sua-chave-secreta

# Docker
COMPOSE_PROJECT_NAME=uniportal
```

## 🛠️ **Scripts Utilitários**

O sistema inclui scripts organizados para manutenção:

```bash
# Análise de dados
cd scripts/analysis
python verificar_meses.py
python analise_vendas_filial.py

# Manutenção do sistema
cd scripts/maintenance  
python check_user_permissions.py
python grant_admin_to_user.py
```

## 📊 **Dashboard e Métricas**

### **Indicadores Principais:**
- 👥 **Total de Funcionários** por setor e sistema
- 📧 **Grupos Ativos** (email, pasta, WhatsApp)
- 📈 **Performance Geral** da organização
- 🏆 **Rankings** de desempenho
- 💰 **Dados Comerciais** e financeiros
- ⭐ **Índices de Satisfação** (NPS/CSAT)

### **Relatórios Disponíveis:**
- Distribuição por departamentos
- Análise de produtividade
- Histórico de performance
- Métricas de engajamento
- Controle de comissões

## 🔒 **Sistema de Permissões**

Controle granular por perfil de usuário:

- **👑 ADM** - Acesso total ao sistema
- **👤 Gerente** - Gestão de equipe e relatórios
- **📊 Analista** - Visualização de dados e métricas  
- **👥 Colaborador** - Acesso limitado às próprias informações
- **🔧 Técnico** - Manutenção de sistemas específicos

## 🔄 **Atualizações e Manutenção**

### **Deploy de Atualizações:**
```bash
# Pull das mudanças
git pull origin main

# Rebuild dos containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **Backup e Restore:**
```bash
# Scripts de backup automático (incluídos)
cd scripts/maintenance
python backup_database.py
```

## 📞 **Suporte**

- **Documentação:** Veja as pastas `config/README.md` e `scripts/README.md`
- **Logs:** `docker-compose logs -f [backend|frontend]`
- **Debug:** Execute `python backend/utils/config_helper.py`

## 📄 **Changelog**

### **v2.0.0** (Março 2026) - Limpeza Completa ✨
- ✅ Removido banco local do Docker
- ✅ Desabilitado módulo de metas individuais  
- ✅ Sistema simplificado e otimizado
- ✅ Configuração centralizada
- ✅ Interface mais clean e objetiva

### **v1.0.0** - Versão Inicial
- Sistema completo com todos os módulos

---

## 🎉 **Sistema Pronto para Produção!**

**UniPortal v2.0** - Mais simples, mais rápido, mais confiável! 🚀

Para dúvidas ou suporte, consulte a documentação nas pastas `config/` e `scripts/`.