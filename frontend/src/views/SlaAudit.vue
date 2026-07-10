<template>
  <div class="sla-audit-container">
    <!-- Fundo Premium -->
    <div class="premium-bg">
      <div class="blob-1"></div>
      <div class="blob-2"></div>
    </div>

    <div class="content-wrapper">
      <!-- Header -->
      <header class="page-header">
        <div class="header-titles">
          <h1>Auditoria de <span>SLA {{ $auth && $auth.hasPermission('infra') ? 'Infraestrutura' : 'T.I.' }}</span></h1>
          <p>Monitoramento de performance e conformidade de chamados</p>
        </div>

        <!-- Botão Voltar (Opcional se precisar sair da auditoria) -->
        <div class="header-actions">
           <!-- seções de filtros etc -->
        </div>
        
        <div class="header-actions">
          <div class="date-selector glass-panel">
            <input type="date" v-model="startDate" class="date-input" />
            <span class="separator">até</span>
            <input type="date" v-model="endDate" class="date-input" />
            <button @click="handleSearch" :disabled="loading || syncing" class="btn-search">
              <i v-if="loading" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-search"></i>
              {{ loading ? 'Carregando...' : 'Pesquisar' }}
            </button>
          </div>


          <button @click="exportToExcel" class="btn-print glass-panel no-print">
            <i class="fas fa-file-excel"></i>
            Exportar Excel
          </button>
        </div>
      </header>

      <!-- Toast de notificação -->
      <Transition name="toast">
        <div v-if="toastMsg" :class="['toast-notif', toastType]">
          <i :class="toastType === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'"></i>
          {{ toastMsg }}
        </div>
      </Transition>

      <!-- Skeleton Loading -->
      <div v-if="loading" class="skeleton-grid">
        <div v-for="i in 4" :key="i" class="skeleton-card glass-panel"></div>
        <div class="skeleton-chart glass-panel"></div>
        <div class="skeleton-table glass-panel"></div>
      </div>

      <template v-else>
        <!-- KPI Cards -->
        <div class="kpi-grid">
          <div class="kpi-card glass-panel">
            <div class="kpi-icon blue"><i class="fas fa-ticket-alt"></i></div>
            <div class="kpi-info">
              <span class="label">Total de chamados</span>
              <span class="value">{{ stats.total_atendimentos }}</span>
            </div>
          </div>

          <div class="kpi-card glass-panel">
            <div class="kpi-icon green"><i class="fas fa-check-double"></i></div>
            <div class="kpi-info">
              <span class="label">SLA OK</span>
              <span class="value">{{ stats.sla_ok }}</span>
            </div>
          </div>

          <div class="kpi-card glass-panel">
            <div class="kpi-icon red"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="kpi-info">
              <span class="label">SLA NÃO OK</span>
              <span class="value">{{ stats.sla_not_ok }}</span>
            </div>
          </div>

          <div class="kpi-card glass-panel">
            <div :class="['kpi-icon', stats.percent_sla >= 90 ? 'green' : 'amber']">
              <i class="fas fa-percentage"></i>
            </div>
            <div class="kpi-info">
              <span class="label">Porcentagem SLA</span>
              <span class="value">{{ stats.percent_sla }}%</span>
              <div class="progress-bar-mini">
                <div class="progress-fill" :style="{ width: stats.percent_sla + '%', background: getSlaColor(stats.percent_sla) }"></div>
              </div>
            </div>
          </div>

          <div class="kpi-card glass-panel">
            <div class="kpi-icon purple"><i class="fas fa-clock"></i></div>
            <div class="kpi-info">
              <span class="label">Média Hora</span>
              <span class="value">{{ stats.average_hours }}h</span>
            </div>
          </div>

          <div v-if="!($auth && $auth.hasPermission('infra'))" class="kpi-card glass-panel">
            <div class="kpi-icon gold"><i class="fas fa-clipboard-check"></i></div>
            <div class="kpi-info">
              <span class="label">Etapas Auditoria</span>
              <span class="value">{{ stats.total_etapas }}</span>
            </div>
          </div>
        </div>
        
        <!-- Diretoria Summary -->
        <div class="summary-card glass-panel no-print">
          <div class="summary-content">
            <div class="summary-section">
              <i class="fas fa-chart-line"></i>
              <div class="summary-text">
                <h4>Visão Geral do Período</h4>
                <p v-if="stats.percent_sla >= 90">Alta conformidade: O SLA de <strong>{{ stats.percent_sla }}%</strong> está acima da meta institucional de 90%.</p>
                <p v-else>Atenção: O SLA de <strong>{{ stats.percent_sla }}%</strong> está abaixo da meta institucional de 90%.</p>
              </div>
            </div>
            <div v-if="!($auth && $auth.hasPermission('infra'))" class="summary-divider"></div>
            <div v-if="!($auth && $auth.hasPermission('infra'))" class="summary-section">
              <i class="fas fa-tasks"></i>
              <div class="summary-text">
                <h4>Auditoria e Governança</h4>
                <p>Foram validadas <strong>{{ stats.total_etapas }} etapas</strong> de auditoria em categorias críticas (Desligamentos, Acessos e Transferências).</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Dashboard Charts & Breakdown -->
        <div class="analysis-grid">
          <div class="breakdown-box glass-panel">
            <h3>Listagem Detalhada <small>(Por Categoria)</small></h3>
            <div class="breakdown-list">
              <div 
                v-for="cat in stats.by_category" 
                :key="cat.name" 
                class="breakdown-item clickable"
                @click="openCategoryModal(cat.name)"
              >
                <div class="item-header">
                  <span class="cat-name">{{ cat.name }}</span>
                  <span class="cat-count">{{ cat.total }} chamados</span>
                </div>
                <div class="item-stats">
                  <div class="progress-bar-large">
                    <div class="progress-fill" :style="{ width: cat.percent + '%', background: getSlaColor(cat.percent) }"></div>
                  </div>
                  <span class="cat-percent">{{ cat.percent.toFixed(1) }}% OK</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="!($auth && $auth.hasPermission('infra'))" class="breakdown-box glass-panel audit-results">
            <h3>Tabela de Auditoria</h3>
            <div class="table-responsive">
              <table class="audit-table">
                <thead>
                  <tr>
                    <th>Auditoria</th>
                    <th>Quant</th>
                    <th>Etapas</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in stats.auditoria" :key="item.name">
                    <td>{{ item.name }}</td>
                    <td>{{ item.quant }}</td>
                    <td>{{ item.etapas }}</td>
                  </tr>
                  <tr v-if="stats.auditoria && stats.auditoria.length > 0" class="total-row">
                    <td><strong>Total</strong></td>
                    <td>-</td>
                    <td><strong>{{ stats.total_etapas }}</strong></td>
                  </tr>
                  <tr v-if="!stats.auditoria || stats.auditoria.length === 0">
                    <td colspan="3" class="empty-msg">Nenhum dado de auditoria no período</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Modal de Detalhes da Categoria -->
        <Transition name="fade">
          <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
            <div class="modal-content glass-panel">
              <div class="modal-header">
                <h3>Chamados: <span>{{ selectedCategory }}</span></h3>
                <button class="btn-close" @click="closeModal"><i class="fas fa-times"></i></button>
              </div>
              
              <div class="modal-body">
                <div class="table-responsive">
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Título</th>
                        <th>SLA</th>
                        <th>Tempo</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="t in ticketsByCategory" :key="t.glpi_id">
                        <td><span class="badge-id">#{{ t.glpi_id }}</span></td>
                        <td class="td-title-modal">{{ t.titulo }}</td>
                        <td>
                          <span :class="['badge-sla', t.status_sla === 'SLA OK' ? 'ok' : 'nok']">
                            {{ t.status_sla }}
                          </span>
                        </td>
                        <td>{{ formatMinutes(t.tempo_atendimento_minutos) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </Transition>

        <!-- Data Table -->
        <div class="table-box glass-panel">
          <div class="table-header">
            <h3>Auditoria de Chamados - Detalhes</h3>
            <div class="search-box">
              <i class="fas fa-search"></i>
              <input type="text" v-model="searchQuery" placeholder="Filtrar chamados...">
            </div>
          </div>
          <div class="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>ID GLPI</th>
                  <th>Título</th>
                  <th>Categoria</th>
                  <th>Status SLA</th>
                  <th>Tempo</th>
                  <th>Auditoria</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ticket in filteredTickets" :key="ticket.glpi_id">
                  <td><span class="badge-id">#{{ ticket.glpi_id }}</span></td>
                  <td class="td-title">{{ ticket.titulo }}</td>
                  <td>{{ ticket.categoria }}</td>
                  <td>
                    <span :class="['badge-sla', ticket.status_sla === 'SLA OK' ? 'ok' : 'nok']">
                      {{ ticket.status_sla }}
                    </span>
                  </td>
                  <td>{{ formatMinutes(ticket.tempo_atendimento_minutos) }}</td>
                  <td>
                    <div class="audit-steps" v-if="ticket.etapas_total > 0">
                      <i class="fas fa-check-circle"></i> {{ ticket.etapas_total }} etapas
                    </div>
                    <span v-else class="no-audit">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, onUnmounted, watch } from 'vue'
import axios from 'axios'
import API_CONFIG from '@/config/api.js'

export default {
  name: 'SlaAudit',
  setup() {
    const today = new Date();
    // Padrão: início de 3 meses atrás (cobre histórico de INFRA desde maio/2026)
    const threeMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 2, 1);
    
    const todayStr = today.toISOString().slice(0, 10);
    const threeMonthsAgoStr = threeMonthsAgo.toISOString().slice(0, 10);
    const startDate = ref(threeMonthsAgoStr);
    const endDate = ref(todayStr);
    
    const loading = ref(false)
    const syncing = ref(false)
    const stats = ref({
      total_atendimentos: 0,
      total_solucionados: 0,
      sla_ok: 0,
      sla_not_ok: 0,
      percent_sla: 0,
      average_hours: 0,
      total_etapas: 0,
      by_category: [],
      auditoria: []
    })
    const tickets = ref([])
    const searchQuery = ref('')
    const showModal = ref(false)
    const selectedCategory = ref('')
    const toastMsg = ref('')
    const toastType = ref('success')

    const monthsList = computed(() => {
      const list = []
      const now = new Date()
      for (let i = 0; i < 12; i++) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
        const val = d.toISOString().slice(0, 7)
        list.push({
          value: val,
          label: d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' }).replace(/^\w/, c => c.toUpperCase())
        })
      }
      return list
    })

    const fetchData = async () => {
      loading.value = true
      try {
        const resStats = await axios.get(`${API_CONFIG.BASE_URL}/sla/stats`, {
          params: { start_date: startDate.value, end_date: endDate.value }
        })
        stats.value = resStats.data
        
        const resTickets = await axios.get(`${API_CONFIG.BASE_URL}/sla/tickets`, {
          params: { start_date: startDate.value, end_date: endDate.value }
        })
        tickets.value = resTickets.data
      } catch (e) {
        console.error("Erro ao carregar dados:", e)
      } finally {
        loading.value = false
      }
    }

    const handleSearch = async () => {
      await fetchData();
    }

    // Força sync do GLPI para o período selecionado
    const syncData = async () => {
      syncing.value = true
      toastMsg.value = ''
      try {
        // Timeout de 5 minutos — GLPI pode demorar para responder em períodos longos
        const res = await axios.post(`${API_CONFIG.BASE_URL}/sla/sync`, null, {
          params: { start_date: startDate.value, end_date: endDate.value },
          timeout: 300000  // 5 minutos
        })
        const r = res.data
        const tiCount    = r.ti_count    ?? '?'
        const infraCount = r.infra_count ?? '?'
        const processed  = r.processed   ?? '?'
        toastMsg.value = `✅ Sync concluído! TI: ${tiCount} | INFRA: ${infraCount} chamados importados`
        toastType.value = 'success'
        // Recarregar dados após sync
        await fetchData()
      } catch (e) {
        console.error('Erro no sync:', e)
        if (e.code === 'ECONNABORTED' || e.message?.includes('timeout')) {
          toastMsg.value = '⏱ Sync ainda em andamento (timeout). Os dados serão atualizados pelo agendador em breve.'
        } else if (e.response?.status === 500) {
          toastMsg.value = `❌ Erro no backend: ${e.response.data?.detail ?? 'Falha na conexão com GLPI'}` 
        } else {
          toastMsg.value = '❌ Erro ao sincronizar. Verifique se o backend está rodando.'
        }
        toastType.value = 'error'
      } finally {
        syncing.value = false
        // Esconde o toast após 8 segundos (maior para erros com mais texto)
        setTimeout(() => { toastMsg.value = '' }, 8000)
      }
    }

    const filteredTickets = computed(() => {
      if (!searchQuery.value) return tickets.value
      const q = searchQuery.value.toLowerCase()
      return tickets.value.filter(t => 
        t.titulo.toLowerCase().includes(q) || 
        t.categoria.toLowerCase().includes(q) ||
        t.glpi_id.toString().includes(q)
      )
    })

    const ticketsByCategory = computed(() => {
      if (!selectedCategory.value) return []
      return tickets.value.filter(t => t.categoria === selectedCategory.value)
    })

    const openCategoryModal = (catName) => {
      selectedCategory.value = catName
      showModal.value = true
      document.body.style.overflow = 'hidden'
    }

    const closeModal = () => {
      showModal.value = false
      document.body.style.overflow = 'auto'
    }

    let autoRefreshTimer = null;

    const getSlaColor = (pct) => {
      if (pct >= 90) return '#10b981'
      if (pct >= 75) return '#f59e0b'
      return '#ef4444'
    }

    const formatMinutes = (min) => {
      if (!min || min <= 0) return '0m'
      // >= 1440 min (24h): exibe em dias — usado para INFRA (VAZAMENTO 2d, PINTURA 7d, etc.)
      if (min >= 1440) {
        const d = Math.floor(min / 1440)
        const h = Math.floor((min % 1440) / 60)
        return h > 0 ? `${d}d ${h}h` : `${d}d`
      }
      // < 24h: exibe em horas e minutos — TI (8h, 4h, etc.)
      if (min < 60) return `${min}m`
      const h = Math.floor(min / 60)
      const m = min % 60
      return m > 0 ? `${h}h ${m}m` : `${h}h`
    }

    onMounted(() => {
      // Carregar dados automaticamente ao abrir o componente
      fetchData();
    });

    onUnmounted(() => {
      if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
      }
    });

    return {
      startDate, endDate, loading, syncing, stats, 
      handleSearch, syncData, getSlaColor, 
      searchQuery, formatMinutes, filteredTickets, tickets,
      showModal, selectedCategory, ticketsByCategory,
      openCategoryModal, closeModal,
      toastMsg, toastType,
      exportToExcel: () => {
        if (!tickets.value || tickets.value.length === 0) {
          alert("Não há dados para exportar.");
          return;
        }

        const headers = ['ID GLPI', 'Titulo', 'Categoria', 'Status SLA', 'Tempo Atendimento (Min)', 'Mes Referencia', 'Total Etapas Auditoria'];
        
        let csvContent = "data:text/csv;charset=utf-8,\uFEFF"; // BOM para suporte a acentos no Excel
        csvContent += headers.join(';') + '\r\n';

        filteredTickets.value.forEach(t => {
          const row = [
            t.glpi_id,
            `"${(t.titulo || '').replace(/"/g, '""')}"`,
            `"${(t.categoria || '').replace(/"/g, '""')}"`,
            t.status_sla,
            t.tempo_atendimento_minutos,
            t.mes_referencia,
            t.etapas_total
          ];
          csvContent += row.join(';') + '\r\n';
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `Relatorio_SLA_${startDate.value}_a_${endDate.value}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    }
  }
}
</script>

<style scoped>
.sla-audit-container {
  min-height: 100vh;
  padding: 2rem;
  color: white;
  position: relative;
  overflow-y: auto;
}

.premium-bg {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: -1;
  background: #050a18;
  overflow: hidden;
}

.blob-1 {
  position: absolute;
  top: -10%; right: -10%;
  width: 40vw; height: 40vw;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
}

.blob-2 {
  position: absolute;
  bottom: -10%; left: -10%;
  width: 30vw; height: 30vw;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
}

.glass-panel {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-titles h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.header-titles h1 span {
  color: #3b82f6;
}

.header-titles p {
  color: #94a3b8;
  margin: 0.25rem 0 0;
}

.last-update {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.date-selector {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  gap: 0.75rem;
}

.date-input {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 0.25rem 0.5rem;
  color: white;
  font-family: inherit;
  outline: none;
}

.date-input::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}

.separator {
  color: #94a3b8;
  font-size: 0.85rem;
  font-weight: 600;
}

.btn-search {
  background: #3b82f6;
  border: none;
  border-radius: 8px;
  color: white;
  padding: 0.5rem 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
  margin-left: 0.5rem;
}

.btn-search:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-search:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-sync-now {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 8px;
  color: #10b981;
  padding: 0.5rem 1rem;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sync-now:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.25);
  border-color: rgba(16, 185, 129, 0.6);
  transform: translateY(-1px);
}

.btn-sync-now:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Toast de notificação */
.toast-notif {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 9999;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.toast-notif.success {
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #6ee7b7;
}

.toast-notif.error {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

.toast-enter-active, .toast-leave-active { transition: all 0.4s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(1rem); }

.btn-sync-new {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #94a3b8;
  padding: 0.5rem 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sync-new:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-color: rgba(59, 130, 246, 0.5);
}

.btn-sync-new:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sync {
  padding: 0 1.5rem;
  height: 44px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: 0.3s;
}

.btn-sync:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  display: flex;
  padding: 1.5rem;
  gap: 1.5rem;
  align-items: center;
}

.kpi-icon {
  width: 54px;
  height: 54px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.kpi-icon.blue { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.kpi-icon.green { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.kpi-icon.red { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.kpi-icon.amber { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.kpi-icon.purple { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
.kpi-icon.gold { background: rgba(252, 202, 50, 0.15); color: #fcca32; }

.kpi-info .label {
  display: block;
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 0.25rem;
}

.kpi-info .value {
  font-size: 1.5rem;
  font-weight: 700;
}

.progress-bar-mini {
  width: 100px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin-top: 0.5rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: 1s ease-out;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-box, .breakdown-box {
  padding: 1.5rem;
  min-height: 400px;
}

h3 {
  font-size: 1.25rem;
  margin: 0 0 1.5rem;
  color: #f8fafc;
}

.chart-wrapper {
  height: 280px;
  position: relative;
}

.breakdown-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.breakdown-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 1.25rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.3s ease;
}

.breakdown-item.clickable {
  cursor: pointer;
}

.breakdown-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(59, 130, 246, 0.3);
}

h3 small {
  font-size: 0.8rem;
  font-weight: normal;
  color: #94a3b8;
  margin-left: 0.5rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.modal-content {
  width: 100%;
  max-width: 900px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: modalIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.modal-header h3 {
  margin: 0;
}

.modal-header h3 span {
  color: #3b82f6;
}

.btn-close {
  background: rgba(255, 255, 255, 0.05);
  border: none;
  color: #94a3b8;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.modal-body {
  overflow-y: auto;
  flex: 1;
}

.td-title-modal {
  max-width: 400px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.9rem;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.cat-name { font-weight: 600; color: #e2e8f0; }
.cat-count { font-size: 0.8rem; color: #94a3b8; }

.item-stats {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar-large {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}

.cat-percent {
  font-size: 0.85rem;
  font-weight: 700;
  width: 60px;
  text-align: right;
}

.table-box {
  padding: 1.5rem;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
}

.search-box input {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border-radius: 10px;
  color: white;
  outline: none;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 1rem;
  color: #94a3b8;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

td {
  padding: 1.25rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.02);
}

.badge-id {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-family: monospace;
  font-weight: 600;
}

.td-title {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge-sla {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.badge-sla.ok { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.badge-sla.nok { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.audit-steps {
  color: #fcca32;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.no-audit { color: #475569; }

/* Skeletons */
.skeleton-card { height: 120px; }
.skeleton-chart { height: 400px; margin-bottom: 1.5rem; }
.skeleton-table { height: 500px; }

.skeleton-dark {
  background: linear-gradient(90deg, #1e293b 25%, #334155 50%, #1e293b 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite linear;
}

.summary-card {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border-left: 4px solid #3b82f6;
}

.summary-content {
  display: flex;
  gap: 3rem;
  align-items: center;
}

.summary-section {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex: 1;
}

.summary-section i {
  font-size: 2rem;
  color: #3b82f6;
  opacity: 0.8;
}

.summary-text h4 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: #f8fafc;
}

.summary-text p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.95rem;
  line-height: 1.5;
}

.summary-divider {
  width: 1px;
  height: 60px;
  background: rgba(255, 255, 255, 0.1);
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Auditoria Table Specifics */
.audit-table {
  margin-top: 1rem;
}

.audit-table th {
  background: rgba(255, 255, 255, 0.02);
  color: #64748b;
  font-weight: 700;
  font-size: 0.75rem;
}

.audit-table td {
  padding: 1rem;
  font-size: 0.95rem;
}

.audit-table .total-row {
  background: rgba(30, 41, 59, 0.5);
  border-top: 2px solid rgba(255, 255, 255, 0.1);
}

.audit-table .total-row td {
  color: #fbbf24;
  font-weight: 700;
}

.empty-msg {
  text-align: center;
  color: #64748b;
  padding: 3rem !important;
  font-style: italic;
}

.audit-results h3 {
  color: #fbbf24;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.audit-results h3::after {
  content: '\f022';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  font-size: 0.9rem;
  opacity: 0.5;
}

@media (max-width: 1200px) {
  .analysis-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .breakdown-list {
    grid-template-columns: 1fr;
  }
  .chart-container {
     height: 250px;
  }
}

@media print {
  .no-print, .btn-sync, .page-header .header-actions, .search-box {
    display: none !important;
  }
  .sla-audit-container {
    padding: 0;
    background: white;
    color: black;
  }
  .glass-panel {
    background: white !important;
    border: 1px solid #ddd !important;
    box-shadow: none !important;
    color: black !important;
  }
  .kpi-grid, .analysis-grid {
    break-inside: avoid;
  }
  .td-title {
    max-width: none;
    white-space: normal;
  }
  .header-titles h1 span {
    color: black;
  }
  .kpi-icon {
    border: 1px solid #ddd;
  }
}

.btn-print {
  padding: 0 1.5rem;
  height: 44px;
  color: #fbbf24;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: 0.3s;
}

.btn-print:hover {
  background: rgba(251, 191, 36, 0.1);
}
</style>
