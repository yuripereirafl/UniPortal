// =============================================================================
// CONFIGURAÇÃO DA API - CENTRALIZADA
// =============================================================================
// Este arquivo usa as configurações centralizadas do projeto
// Todas as URLs são configuradas automaticamente por ambiente

/**
 * Detecta o ambiente atual baseado na URL ou variáveis
 * SISTEMA CONFIGURADO PARA USAR APENAS SERVIDOR EXTERNO
 * @returns {string} environment
 */
function detectEnvironment() {
  // Se há variável de ambiente definida, use ela
  if (process.env.VUE_APP_ENVIRONMENT) {
    return process.env.VUE_APP_ENVIRONMENT;
  }
  
  // Auto-detect baseado na URL - sem localhost
  const hostname = window.location.hostname;
  
  if (hostname.includes('192.168.1')) {
    return 'production';
  } else {
    return 'production'; // default - sempre servidor externo
  }
}

/**
 * Configurações por ambiente - SEM LOCALHOST
 * Todo o sistema usa apenas o servidor externo
 */
const CONFIG_BY_ENVIRONMENT = {
  development: {
    BASE_URL: 'http://192.168.1.11:8000',
    WS_URL: 'ws://192.168.1.11:8000'
  },
  production: {
    BASE_URL: 'http://192.168.1.11:8000',
    WS_URL: 'ws://192.168.1.11:8000'
  },
  testing: {
    BASE_URL: 'http://192.168.1.11:8000',
    WS_URL: 'ws://192.168.1.11:8000'
  }
};

// Detectar ambiente atual
const CURRENT_ENVIRONMENT = detectEnvironment();
const ENV_CONFIG = CONFIG_BY_ENVIRONMENT[CURRENT_ENVIRONMENT];

export const API_CONFIG = {
  // URL Base da API (com fallback para compatibilidade)
  BASE_URL: process.env.VUE_APP_API_URL || ENV_CONFIG.BASE_URL,
  
  // URL para WebSockets (se necessário futuramente)
  WS_URL: ENV_CONFIG.WS_URL,
  
  // Informações do ambiente
  ENVIRONMENT: CURRENT_ENVIRONMENT,
  
  // Timeout padrão para requisições (ms)
  TIMEOUT: 30000,
  
  // Endpoints da API (centralizados)
  ENDPOINTS: {
    // Dashboard
    DASHBOARD_TOTAIS: '/dashboard/totais',
    FUNCIONARIOS_POR_SETOR: '/dashboard/funcionarios-por-setor',
    FUNCIONARIOS_POR_SISTEMA: '/dashboard/funcionarios-por-sistema',
    
    // Autenticação
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH_TOKEN: '/auth/refresh',
    
    // Funcionários
    FUNCIONARIOS: '/funcionarios',
    FUNCIONARIO_BY_ID: '/funcionarios/{id}',
    
    // Sistemas
    SISTEMAS: '/sistemas',
    SISTEMA_BY_ID: '/sistemas/{id}',
    
    // Setores
    SETORES: '/setores',
    SETOR_BY_ID: '/setores/{id}',
    
    // Grupos
    GRUPOS_EMAIL: '/grupos-email',
    GRUPOS_PASTA: '/grupos-pasta', 
    GRUPOS_WHATSAPP: '/grupos-whatsapp',
    
    // Relatórios
    RELATORIOS: '/relatorios',
    
    // Usuários
    USUARIOS: '/usuarios',
    USUARIO_BY_ID: '/usuarios/{id}',
  },
  
  // Headers padrão
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
}

/**
 * Helper para construir URLs de endpoints com parâmetros
 * @param {string} endpoint - Nome do endpoint
 * @param {Object} params - Parâmetros para substituir na URL
 * @returns {string} URL completa
 */
export function buildEndpointUrl(endpoint, params = {}) {
  let url = API_CONFIG.ENDPOINTS[endpoint] || endpoint;
  
  // Substituir parâmetros na URL (ex: {id} -> 123)
  Object.entries(params).forEach(([key, value]) => {
    url = url.replace(`{${key}}`, value);
  });
  
  return `${API_CONFIG.BASE_URL}${url}`;
}

/**
 * Informações de debug (útil para desenvolvimento)
 */
export function getConfigInfo() {
  return {
    environment: API_CONFIG.ENVIRONMENT,
    baseUrl: API_CONFIG.BASE_URL,
    wsUrl: API_CONFIG.WS_URL,
    endpointsCount: Object.keys(API_CONFIG.ENDPOINTS).length
  };
}

// Log de configuração em desenvolvimento
if (CURRENT_ENVIRONMENT === 'development') {
  console.log('🔧 API Config:', getConfigInfo());
}

export default API_CONFIG
