import { ref, computed, onMounted, onUnmounted } from 'vue'

export function useVirtualScroll(items, itemHeight = 50) {
  const containerRef = ref(null)
  const scrollTop = ref(0)
  const containerHeight = ref(400)
  
  const visibleRange = computed(() => {
    const start = Math.floor(scrollTop.value / itemHeight)
    const end = Math.min(
      start + Math.ceil(containerHeight.value / itemHeight) + 5, // buffer
      items.value.length
    )
    return { start, end }
  })

  const visibleItems = computed(() => {
    const { start, end } = visibleRange.value
    return items.value.slice(start, end).map((item, index) => ({
      ...item,
      index: start + index
    }))
  })

  const totalHeight = computed(() => items.value.length * itemHeight)
  const offsetY = computed(() => visibleRange.value.start * itemHeight)

  const handleScroll = (e) => {
    scrollTop.value = e.target.scrollTop
  }

  const updateContainerHeight = () => {
    if (containerRef.value) {
      containerHeight.value = containerRef.value.clientHeight
    }
  }

  onMounted(() => {
    updateContainerHeight()
    window.addEventListener('resize', updateContainerHeight)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateContainerHeight)
  })

  return {
    containerRef,
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    updateContainerHeight
  }
}
