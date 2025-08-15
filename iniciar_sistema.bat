@echo off
echo ================================================
echo        SISTEMA TI - INICIALIZAR PROJETO
echo ================================================
echo.

:: Verificar se estamos na pasta correta
if not exist "backend" (
    echo ERRO: Pasta 'backend' nao encontrada!
    echo Certifique-se de estar na pasta raiz do projeto System_ti
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERRO: Pasta 'frontend' nao encontrada!
    echo Certifique-se de estar na pasta raiz do projeto System_ti
    pause
    exit /b 1
)

echo [1/4] Verificando dependencias...
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao esta instalado ou nao esta no PATH
    echo Instale Python 3.8+ e tente novamente
    pause
    exit /b 1
)

:: Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Node.js nao esta instalado ou nao esta no PATH
    echo Instale Node.js 14+ e tente novamente
    pause
    exit /b 1
)

echo [2/4] Obtendo IP da rede local...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set LOCAL_IP=%%b
        goto :found_ip
    )
)
:found_ip

if "%LOCAL_IP%"=="" (
    echo AVISO: Nao foi possivel detectar o IP automaticamente
    set LOCAL_IP=192.168.1.151
    echo Usando IP padrao: %LOCAL_IP%
) else (
    echo IP detectado: %LOCAL_IP%
)

echo.
echo [3/4] Iniciando Backend (FastAPI)...
echo.
echo Abrindo novo terminal para o Backend...
start "Backend - Sistema TI" cmd /k "cd /d %cd%\backend && echo Iniciando Backend FastAPI... && python -m uvicorn app.main:app --reload --host %LOCAL_IP% --port 8000"

:: Aguardar um pouco para o backend iniciar
timeout /t 3 /nobreak >nul

echo.
echo [4/4] Iniciando Frontend (Vue.js)...
echo.
echo Abrindo novo terminal para o Frontend...
start "Frontend - Sistema TI" cmd /k "cd /d %cd%\frontend && echo Iniciando Frontend Vue.js... && npm run serve"

echo.
echo ================================================
echo            SISTEMA INICIADO COM SUCESSO!
echo ================================================
echo.
echo URLs de acesso:
echo.
echo Frontend:  http://localhost:8080
echo           http://%LOCAL_IP%:8080
echo.
echo Backend:   http://%LOCAL_IP%:8000
echo API Docs:  http://%LOCAL_IP%:8000/docs
echo.
echo ================================================
echo.
echo Os servicos foram iniciados em terminais separados.
echo Para parar, feche as janelas ou pressione Ctrl+C em cada terminal.
echo.
pause
