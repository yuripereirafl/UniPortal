import { ref, computed } from 'vue'
import axios from 'axios'
import apiCache from '@/utils/apiCache'
import { useLoading } from '@/composables/useLoading'

export function useAPI(baseURL = '') {
  const { setLoading } = useLoading()

  const createCacheKey = (url, params = {}) => {
    const paramStr = JSON.stringify(params)
    return `${url}${paramStr}`
  }

  const get = async (url, options = {}) => {
    const { 
      cache = true, 
      cacheTime = null, 
      loadingKey = null,
      params = {}
    } = options

    const cacheKey = createCacheKey(url, params)
    
    // Verificar cache
    if (cache) {
      const cached = apiCache.get(cacheKey)
      if (cached) {
        return cached
      }
    }

    // Mostrar loading
    if (loadingKey) {
      setLoading(loadingKey, true)
    }

    try {
      const response = await axios.get(`${baseURL}${url}`, { params })
      const data = response.data

      // Salvar no cache
      if (cache) {
        apiCache.set(cacheKey, data, cacheTime)
      }

      return data
    } catch (error) {
      console.error(`Erro na requisição GET ${url}:`, error)
      throw error
    } finally {
      if (loadingKey) {
        setLoading(loadingKey, false)
      }
    }
  }

  const post = async (url, data, options = {}) => {
    const { loadingKey = null, invalidateCache = [] } = options

    if (loadingKey) {
      setLoading(loadingKey, true)
    }

    try {
      const response = await axios.post(`${baseURL}${url}`, data)
      
      // Invalidar cache relacionado
      invalidateCache.forEach(pattern => {
        apiCache.invalidatePattern(pattern)
      })

      return response.data
    } catch (error) {
      console.error(`Erro na requisição POST ${url}:`, error)
      throw error
    } finally {
      if (loadingKey) {
        setLoading(loadingKey, false)
      }
    }
  }

  const put = async (url, data, options = {}) => {
    const { loadingKey = null, invalidateCache = [] } = options

    if (loadingKey) {
      setLoading(loadingKey, true)
    }

    try {
      const response = await axios.put(`${baseURL}${url}`, data)
      
      // Invalidar cache relacionado
      invalidateCache.forEach(pattern => {
        apiCache.invalidatePattern(pattern)
      })

      return response.data
    } catch (error) {
      console.error(`Erro na requisição PUT ${url}:`, error)
      throw error
    } finally {
      if (loadingKey) {
        setLoading(loadingKey, false)
      }
    }
  }

  const del = async (url, options = {}) => {
    const { loadingKey = null, invalidateCache = [] } = options

    if (loadingKey) {
      setLoading(loadingKey, true)
    }

    try {
      const response = await axios.delete(`${baseURL}${url}`)
      
      // Invalidar cache relacionado
      invalidateCache.forEach(pattern => {
        apiCache.invalidatePattern(pattern)
      })

      return response.data
    } catch (error) {
      console.error(`Erro na requisição DELETE ${url}:`, error)
      throw error
    } finally {
      if (loadingKey) {
        setLoading(loadingKey, false)
      }
    }
  }

  return {
    get,
    post,
    put,
    delete: del,
    cache: apiCache
  }
}
