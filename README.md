<<<<<<< HEAD
# Sistema TI - Controle de Gestão da TI

Sistema de gestão para controle de funcionários, sistemas, setores e grupos de email da área de TI.

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- **Python 3.8+** (recomendado Python 3.9 ou superior)
- **Node.js 14+** e **npm**
- **Git** (opcional, para controle de versão)

## 🚀 Como executar o projeto

### 1. Preparação inicial

1. Abra o **PowerShell** como administrador
2. Navegue até a pasta do projeto:
   ```powershell
   cd c:\Users\yuri.flores\Desktop\System_ti
   ```

### 2. Configuração do Backend (FastAPI)

1. **Navegue para a pasta do backend:**
   ```powershell
   cd backend
   ```

2. **Instale as dependências Python** (se ainda não instalou):
   ```powershell
   pip install fastapi uvicorn sqlalchemy sqlite3
   ```

3. **Inicie o servidor backend:**
   ```powershell
   python -m uvicorn app.main:app --reload --host 192.168.1.151 --port 8000
   ```

   > ⚠️ **Importante**: Use o IP da sua rede local. Para descobrir seu IP:
   > ```powershell
   > ipconfig
   > ```
   > Procure por "Endereço IPv4" na seção do seu adaptador de rede.

4. **Verifique se está funcionando:**
   - Acesse: `http://192.168.1.151:8000/docs` (documentação da API)
   - Deve mostrar a interface do Swagger com todas as rotas disponíveis

### 3. Configuração do Frontend (Vue.js)

1. **Abra um NOVO terminal PowerShell** (mantenha o backend rodando no primeiro)
2. **Navegue para a pasta do frontend:**
   ```powershell
   cd c:\Users\yuri.flores\Desktop\System_ti\frontend
   ```

3. **Instale as dependências do Node.js** (se ainda não instalou):
   ```powershell
   npm install
   ```

4. **Inicie o servidor de desenvolvimento:**
   ```powershell
   npm run serve
   ```

5. **Aguarde a compilação** e acesse:
   - Local: `http://localhost:8080`
   - Rede: `http://192.168.1.151:8080`

## 🔧 Estrutura do Projeto

```
System_ti/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── main.py         # Arquivo principal da API
│   │   ├── models/         # Modelos do banco de dados
│   │   ├── routes/         # Rotas da API
│   │   └── database.py     # Configuração do banco
│   └── requirements.txt    # Dependências Python
├── frontend/               # Interface Vue.js
│   ├── src/
│   │   ├── views/          # Páginas da aplicação
│   │   ├── components/     # Componentes reutilizáveis
│   │   └── assets/         # Imagens e recursos
│   ├── package.json        # Dependências Node.js
│   └── public/             # Arquivos públicos
└── README.md              # Este arquivo
```

## 🌐 URLs importantes

- **Frontend**: http://localhost:8080 ou http://192.168.1.151:8080
- **Backend API**: http://192.168.1.151:8000
- **Documentação da API**: http://192.168.1.151:8000/docs
- **Banco de dados**: SQLite (arquivo local)

## 💡 Funcionalidades

- ✅ **Dashboard Analítico**: Visão geral com métricas e indicadores
- ✅ **Gestão de Funcionários**: CRUD completo com filtros de busca
- ✅ **Gestão de Sistemas**: Controle de sistemas de TI com analytics
- ✅ **Gestão de Setores**: Organização departamental
- ✅ **Grupos de Email**: Controle de listas de distribuição
- ✅ **Filtros de Busca**: Em todas as tabelas do sistema
- ✅ **Interface Responsiva**: Design profissional e moderno

## 🔍 Solução de Problemas

### Erro "Falha ao carregar dados"
- Verifique se o backend está rodando em `192.168.1.151:8000`
- Confirme se não há firewall bloqueando as portas 8000 e 8080
- Verifique se o IP configurado está correto

### Erro de CORS
- O backend já está configurado para aceitar requisições de qualquer origem
- Se persistir, verifique a configuração em `backend/app/main.py`

### Porta em uso
- Se a porta 8000 ou 8080 já estiver em uso, mude para outra porta:
  ```powershell
  # Backend em porta diferente
  python -m uvicorn app.main:app --reload --host 192.168.1.151 --port 8001
  
  # Frontend em porta diferente
  npm run serve -- --port 8081
  ```

## 📦 Scripts úteis

### Para parar os serviços:
```powershell
# No terminal onde está rodando, pressione Ctrl+C
# Ou force o término:
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

### Para rebuild completo:
```powershell
# Frontend
cd frontend
npm install
npm run build

# Backend
cd backend
pip install -r requirements.txt
```

## 🛠️ Desenvolvimento

### Banco de Dados
- O sistema usa SQLite, banco local criado automaticamente
- Arquivo do banco: `backend/database.db`
- Para reset completo: delete o arquivo `database.db` e reinicie o backend

### Estrutura da API
- **Funcionários**: `/funcionarios/`
- **Sistemas**: `/sistemas/`
- **Setores**: `/setores/`
- **Grupos Email**: `/grupos-email/`
- **Analytics**: `/sistemas/analytics/`

### Hot Reload
- **Backend**: Salve qualquer arquivo Python e a API recarrega automaticamente
- **Frontend**: Salve qualquer arquivo Vue e a página atualiza automaticamente

## 📝 Comandos de Início Rápido

**Terminal 1 (Backend):**
```powershell
cd c:\Users\yuri.flores\Desktop\System_ti\backend
python -m uvicorn app.main:app --reload --host 192.168.1.151 --port 8000
```

**Terminal 2 (Frontend):**
```powershell
cd c:\Users\yuri.flores\Desktop\System_ti\frontend
npm run serve
```

---

## 👥 Suporte

Em caso de dúvidas ou problemas:
1. Verifique se todos os pré-requisitos estão instalados
2. Confirme se as portas 8000 e 8080 estão livres
3. Verifique se o IP da rede está correto
4. Consulte os logs nos terminais para identificar erros específicos

**Desenvolvido para o Controle de Gestão da TI** 🚀
=======
# System_ti
>>>>>>> e36849d2b4f20f10c3d8316a6a3784d1a9b7c634
