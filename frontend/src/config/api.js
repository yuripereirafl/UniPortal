// Configuração da API
// Para desenvolvimento: use localhost
// Para produção: altere para sua URL real

export const API_CONFIG = {
  // BASE_URL agora usa variável de ambiente ou cai para o IP desejado
  BASE_URL: process.env.VUE_APP_API_URL || 'http://192.168.1.37:8080',
  ENDPOINTS: {
    DASHBOARD_TOTAIS: '/dashboard/totais',
    FUNCIONARIOS_POR_SETOR: '/dashboard/funcionarios-por-setor',
    FUNCIONARIOS_POR_SISTEMA: '/dashboard/funcionarios-por-sistema'
  }
}

export default API_CONFIG
