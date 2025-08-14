# 🚀 GUIA RÁPIDO - Sistema TI

## Para INICIAR o sistema:

### Opção 1: Automático (Recomendado)
1. Vá para a pasta: `c:\Users\yuri.flores\Desktop\System_ti`
2. **Duplo clique** no arquivo: `iniciar_sistema.bat`
3. Aguarde os dois terminais abrirem
4. Acesse: http://localhost:8080

### Opção 2: Manual
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

## Para PARAR o sistema:

### Opção 1: Automático
- **Duplo clique** no arquivo: `parar_sistema.bat`

### Opção 2: Manual
- Pressione `Ctrl + C` em cada terminal
- Ou feche as janelas dos terminais

## 🌐 URLs de Acesso:

- **Sistema**: http://localhost:8080
- **API**: http://192.168.1.151:8000/docs

## 📁 Arquivos importantes:

- `iniciar_sistema.bat` - Inicia tudo automaticamente
- `parar_sistema.bat` - Para todos os serviços  
- `README.md` - Documentação completa

---
**Desenvolvido para Controle de Gestão da TI**
