import { ref } from 'vue'

// Estado global de loading
const globalLoading = ref(false)
const loadingStates = ref(new Map())

export function useLoading() {
  const setGlobalLoading = (isLoading) => {
    globalLoading.value = isLoading
  }

  const setLoading = (key, isLoading) => {
    if (isLoading) {
      loadingStates.value.set(key, true)
    } else {
      loadingStates.value.delete(key)
    }
    // Força reatividade
    loadingStates.value = new Map(loadingStates.value)
  }

  const isLoading = (key) => {
    return loadingStates.value.has(key)
  }

  const hasAnyLoading = () => {
    return loadingStates.value.size > 0 || globalLoading.value
  }

  return {
    globalLoading,
    loadingStates,
    setGlobalLoading,
    setLoading,
    isLoading,
    hasAnyLoading
  }
}
