<template>
  <div class="optimized-component render-optimized">
    <!-- Loading state otimizado -->
    <div v-if="isLoading('funcionarios')" class="loading-container">
      <div class="loading-spinner-optimized"></div>
      <p>Carregando funcionários...</p>
    </div>

    <!-- Lista virtual para performance -->
    <div v-else class="virtual-scroll-container" ref="containerRef" @scroll="handleScroll">
      <div class="virtual-scroll-spacer" :style="{ height: `${totalHeight}px` }">
        <div class="virtual-scroll-content" :style="{ transform: `translateY(${offsetY}px)` }">
          <div 
            v-for="item in visibleItems" 
            :key="item.id"
            class="list-item hardware-accelerated card-hover-optimized"
            :style="{ height: '50px' }"
          >
            <div class="item-content">
              <strong>{{ item.nome }}</strong>
              <span>{{ item.email }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search com debounce -->
    <div class="search-section">
      <input 
        v-model="searchTerm"
        @input="debouncedSearch"
        :class="['search-input-optimized', { 'input-debouncing': isSearching }]"
        placeholder="Buscar funcionários..."
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useAPI } from '@/composables/useAPI'
import { useLoading } from '@/composables/useLoading'
import { useVirtualScroll } from '@/composables/useVirtualScroll'
import { debounce } from '@/config/performance'
import { API_BASE_URL } from '@/api'

export default {
  name: 'OptimizedFuncionariosList',
  setup() {
    // Composables
    const { get } = useAPI(API_BASE_URL)
    const { isLoading, setLoading } = useLoading()
    
    // State
    const funcionarios = ref([])
    const searchTerm = ref('')
    const isSearching = ref(false)
    
    // Computed
    const filteredFuncionarios = computed(() => {
      if (!searchTerm.value) return funcionarios.value
      
      const term = searchTerm.value.toLowerCase()
      return funcionarios.value.filter(func => 
        func.nome?.toLowerCase().includes(term) ||
        func.email?.toLowerCase().includes(term)
      )
    })
    
    // Virtual scroll
    const {
      containerRef,
      visibleItems,
      totalHeight,
      offsetY,
      handleScroll
    } = useVirtualScroll(filteredFuncionarios, 50)
    
    // Methods
    const loadFuncionarios = async () => {
      try {
        const data = await get('/funcionarios/', {
          cache: true,
          cacheTime: 5 * 60 * 1000, // 5 minutos
          loadingKey: 'funcionarios'
        })
        funcionarios.value = data
      } catch (error) {
        console.error('Erro ao carregar funcionários:', error)
      }
    }
    
    const searchFuncionarios = () => {
      isSearching.value = true
      setTimeout(() => {
        isSearching.value = false
      }, 300)
    }
    
    // Debounced search
    const debouncedSearch = debounce(searchFuncionarios, 300)
    
    // Lifecycle
    loadFuncionarios()
    
    return {
      // State
      funcionarios,
      searchTerm,
      isSearching,
      
      // Computed
      filteredFuncionarios,
      
      // Virtual scroll
      containerRef,
      visibleItems,
      totalHeight,
      offsetY,
      handleScroll,
      
      // Methods
      loadFuncionarios,
      debouncedSearch,
      
      // Composables
      isLoading
    }
  }
}
</script>

<style scoped>
.optimized-component {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid #eee;
  background: white;
  margin-bottom: 1px;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-content strong {
  font-size: 14px;
  color: var(--cor-primaria);
}

.item-content span {
  font-size: 12px;
  color: #666;
}

.search-section {
  margin-bottom: 20px;
}

.search-section input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}
</style>
