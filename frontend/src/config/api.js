// Configuração da API
// Para desenvolvimento: use localhost
// Para produção: altere para sua URL real

export const API_CONFIG = {
  // Usar variável de ambiente - flexível para qualquer ambiente
  BASE_URL: process.env.VUE_APP_API_URL || 'http://192.168.1.37:8000',
  
  // Exemplos de configuração:
  // Desenvolvimento local: http://localhost:8000
  // Servidor específico: http://192.168.1.37:8000
  // Produção: https://sua-api-producao.com
  
  // Endpoints
  ENDPOINTS: {
    DASHBOARD_TOTAIS: '/dashboard/totais',
    FUNCIONARIOS_POR_SETOR: '/dashboard/funcionarios-por-setor',
    FUNCIONARIOS_POR_SISTEMA: '/dashboard/funcionarios-por-sistema'
  }
}

export default API_CONFIG
