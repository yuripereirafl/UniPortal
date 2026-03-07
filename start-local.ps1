# UniPortal - Script de Inicialização Local
# PowerShell Script para usar IP da máquina local

# Configurações
$LocalIP = "192.168.1.11"
$BackendPort = 8000
$FrontendPort = 8080

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "    UniPortal - Sistema Local" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IP da Máquina: ${LocalIP}" -ForegroundColor Green
Write-Host "Frontend: http://${LocalIP}:${FrontendPort}" -ForegroundColor Green
Write-Host "Backend:  http://${LocalIP}:${BackendPort}" -ForegroundColor Green
Write-Host ""

# Configurar variáveis de ambiente
$env:VUE_APP_API_URL = "http://${LocalIP}:${BackendPort}"
$env:BACKEND_HOST = $LocalIP
$env:BACKEND_PORT = $BackendPort

Write-Host "[1/4] Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

Write-Host "[2/4] Iniciando Backend (uvicorn)..." -ForegroundColor Yellow
$BackendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --host ${LocalIP} --port ${BackendPort} --reload" -WindowStyle Normal -PassThru

Write-Host "[3/4] Aguardando backend inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "[4/4] Iniciando Frontend (Vite)..." -ForegroundColor Yellow
$FrontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal -PassThru

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Sistema iniciado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Acesse o sistema em:" -ForegroundColor Cyan
Write-Host "Frontend: http://${LocalIP}:${FrontendPort}" -ForegroundColor White
Write-Host "Backend API: http://${LocalIP}:${BackendPort}" -ForegroundColor White
Write-Host "Documentação: http://${LocalIP}:${BackendPort}/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione Ctrl+C para parar os serviços..." -ForegroundColor Yellow

# Aguardar os processos
try {
    Wait-Process -InputObject $BackendJob, $FrontendJob
} catch {
    Write-Host "Processos interrompidos pelo usuário." -ForegroundColor Red
}