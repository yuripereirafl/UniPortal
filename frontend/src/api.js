
// Usar variável de ambiente ou fallback
// Prioriza variável de ambiente (deployed ou em container). Fallback para a VM destino.
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://192.168.1.37:8000';
