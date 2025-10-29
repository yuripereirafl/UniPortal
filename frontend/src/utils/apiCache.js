class APICache {
  constructor() {
    this.cache = new Map()
    this.expireTime = 5 * 60 * 1000 // 5 minutos
  }

  set(key, data, customExpireTime = null) {
    const expireAt = Date.now() + (customExpireTime || this.expireTime)
    this.cache.set(key, { data, expireAt })
  }

  get(key) {
    const cached = this.cache.get(key)
    if (!cached) return null
    
    if (Date.now() > cached.expireAt) {
      this.cache.delete(key)
      return null
    }
    
    return cached.data
  }

  invalidate(key) {
    this.cache.delete(key)
  }

  invalidatePattern(pattern) {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key)
      }
    }
  }

  clear() {
    this.cache.clear()
  }

  size() {
    return this.cache.size
  }
}

// Instância global do cache
const apiCache = new APICache()

export default apiCache
