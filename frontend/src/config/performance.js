// Configuração de Performance do Sistema
import apiCache from '@/utils/apiCache'

// Configurações de performance
const PERFORMANCE_CONFIG = {
  // Cache
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutos
  CACHE_MAX_SIZE: 100, // máximo de entradas no cache
  
  // Debounce
  SEARCH_DEBOUNCE_DELAY: 300, // ms
  RESIZE_DEBOUNCE_DELAY: 150, // ms
  
  // Virtual Scroll
  VIRTUAL_ITEM_HEIGHT: 50, // px
  VIRTUAL_BUFFER_SIZE: 5, // items extras para buffer
  
  // Paginação
  ITEMS_PER_PAGE: 50,
  LAZY_LOAD_THRESHOLD: 10, // carregar mais quando restam X items
  
  // Animações
  ANIMATION_DURATION: 200, // ms
  TRANSITION_EASING: 'ease-in-out',
  
  // Timeouts
  API_TIMEOUT: 30000, // 30 segundos
  TOAST_DURATION: 3000, // 3 segundos
}

// Função para limpar cache quando necessário
export function cleanupCache() {
  if (apiCache.size() > PERFORMANCE_CONFIG.CACHE_MAX_SIZE) {
    apiCache.clear()
  }
}

// Debounce utility
export function debounce(func, delay) {
  let timeoutId
  return function (...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func.apply(this, args), delay)
  }
}

// Throttle utility
export function throttle(func, delay) {
  let inThrottle
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, delay)
    }
  }
}

// Lazy loading utility
export function createIntersectionObserver(callback, options = {}) {
  const defaultOptions = {
    rootMargin: '50px',
    threshold: 0.1,
    ...options
  }
  
  return new IntersectionObserver(callback, defaultOptions)
}

// Memory cleanup
export function setupMemoryCleanup() {
  // Limpar cache a cada 10 minutos
  setInterval(() => {
    cleanupCache()
  }, 10 * 60 * 1000)
  
  // Limpar cache quando a página é escondida
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      cleanupCache()
    }
  })
}

export default PERFORMANCE_CONFIG
