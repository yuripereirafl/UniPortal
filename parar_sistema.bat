@echo off
echo ================================================
echo         SISTEMA TI - PARAR SERVICOS
echo ================================================
echo.

echo Parando processos do Backend (Python/Uvicorn)...
taskkill /F /IM python.exe 2>nul
if errorlevel 1 (
    echo Nenhum processo Python encontrado
) else (
    echo Processos Python finalizados
)

echo.
echo Parando processos do Frontend (Node.js)...
taskkill /F /IM node.exe 2>nul
if errorlevel 1 (
    echo Nenhum processo Node.js encontrado
) else (
    echo Processos Node.js finalizados
)

echo.
echo Limpando processos nas portas 8000 e 8080...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080"') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo ================================================
echo          TODOS OS SERVICOS PARADOS
echo ================================================
echo.
pause
