@echo off
title UniPortal - Sistema Local
echo =================================
echo    UniPortal - Iniciando Sistema
echo =================================
echo.
echo IP da Maquina: 127.0.0.1
echo Frontend: http://127.0.0.1:8080
echo Backend:  http://127.0.0.1:8000
echo.

REM Configurar variáveis de ambiente
set VUE_APP_API_URL=http://127.0.0.1:8000
set BACKEND_HOST=127.0.0.1
set BACKEND_PORT=8000

echo [1/3] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo [2/3] Iniciando Backend (uvicorn)...
start "UniPortal Backend" cmd /c "cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [3/3] Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo [4/4] Iniciando Frontend (Vite)...
start "UniPortal Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ========================================
echo Sistema iniciado com sucesso!
echo.
echo Acesse o sistema em:
echo Frontend: http://127.0.0.1:8080
echo Backend API: http://127.0.0.1:8000
echo Documentação: http://127.0.0.1:8000/docs
echo ========================================
echo.
echo Pressione qualquer tecla para sair...
pause >nul
