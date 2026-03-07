<template>
  <div class="dashboard-analytics">
    <!-- Fundo tecnológico animado (Mesma estética do login) -->
    <div class="tech-bg">
      <div class="glow-circle glow-1"></div>
      <div class="glow-circle glow-2"></div>
      <div class="grid-overlay"></div>
    </div>

    <div class="dashboard-content-wrapper">
      <!-- Header Premium (Glassmorphism) -->
      <div class="dashboard-header">
        <div class="header-content" v-if="!loading">
          <h1>
            <i class="fas fa-chart-line"></i>
            Dashboard <span>Analytics</span>
          </h1>
          <p class="dashboard-subtitle">Visão geral da plataforma UniPortal</p>
        </div>
        <div class="header-content-skeleton" v-else>
          <div class="skeleton-dark skeleton-title"></div>
          <div class="skeleton-dark skeleton-text" style="width: 30%"></div>
        </div>
      </div>

      <!-- Cards Premium (Glassmorphism) -->
      <div class="dashboard-cards">
        <template v-if="!loading">
          <div 
            v-for="card in cardsData" 
            :key="card.label"
            :class="['premium-card', card.class]"
          >
            <div class="card-glass-body">
              <div class="card-icon">
                <i :class="card.icon"></i>
              </div>
              <div class="card-info">
                <div class="card-label">{{ card.label }}</div>
                <div class="card-value">{{ card.value }}</div>
                <div class="card-trend">
                  <i :class="card.trend.icon"></i>
                  {{ card.trend.text }}
                </div>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div v-for="i in 4" :key="i" class="premium-card">
            <div class="card-glass-body">
              <div class="skeleton-dark skeleton-circle" style="width: 52px; height: 52px; flex-shrink: 0;"></div>
              <div style="flex: 1">
                <div class="skeleton-dark skeleton-text" style="width: 60%"></div>
                <div class="skeleton-dark skeleton-title" style="width: 40%; margin-bottom: 0;"></div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Charts Premium (Glassmorphism) -->
      <div class="dashboard-charts">
        <div class="chart-container-glass">
          <div class="chart-header">
            <h3>Funcionários por Setor</h3>
          </div>
          <div class="chart-content">
            <canvas ref="chartSetores"></canvas>
          </div>
        </div>

        <div class="chart-container-glass">
          <div class="chart-header">
            <h3>Funcionários por Sistema</h3>
          </div>
          <div class="chart-content">
            <canvas ref="chartSistemas"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Chart, registerables } from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'
import axios from 'axios'
import API_CONFIG from '@/config/api.js'

Chart.register(...registerables, ChartDataLabels)

export default {
  name: 'DashboardPanel',
  setup() {
    // Configuração da API centralizada
    const { BASE_URL, ENDPOINTS } = API_CONFIG
    
    const totalFuncionarios = ref(0)
    const totalSetores = ref(0)
    const totalSistemas = ref(0)
    const totalEmails = ref(0)
    const cardsData = ref([])
    const loading = ref(true)

    const chartSetores = ref(null)
    const chartSistemas = ref(null)

    // Cores profissionais para gráficos
    const coresProfissionais = [
      '#3b82f6', '#f59e0b', '#10b981', '#ef4444', 
      '#8b5cf6', '#f97316', '#06b6d4', '#84cc16',
      '#ec4899', '#6366f1', '#14b8a6', '#f43f5e'
    ]

    const montarCards = () => {
      cardsData.value = [
        {
          label: 'Total Funcionários',
          value: totalFuncionarios.value,
          icon: 'fas fa-users',
          class: 'card-funcionarios',
          trend: {
            icon: 'fas fa-arrow-up',
            text: '+12% este mês'
          }
        },
        {
          label: 'Total Setores',
          value: totalSetores.value,
          icon: 'fas fa-building',
          class: 'card-setores',
          trend: {
            icon: 'fas fa-arrow-up',
            text: '+5% este mês'
          }
        },
        {
          label: 'Sistemas Ativos',
          value: totalSistemas.value,
          icon: 'fas fa-server',
          class: 'card-sistemas',
          trend: {
            icon: 'fas fa-minus',
            text: 'Estável'
          }
        },
        {
          label: 'Grupos de Email',
          value: totalEmails.value,
          icon: 'fas fa-envelope',
          class: 'card-emails',
          trend: {
            icon: 'fas fa-arrow-up',
            text: '+8% este mês'
          }
        }
      ]
    }

    const carregarDados = async () => {
      loading.value = true
      try {
        // Cache simples para evitar múltiplas requisições
        if (window.dashboardCache && (Date.now() - window.dashboardCache.timestamp) < 60000) {
          const cached = window.dashboardCache.data;
          totalFuncionarios.value = cached.funcionarios;
          totalSetores.value = cached.setores;
          totalSistemas.value = cached.sistemas;
          totalEmails.value = cached.emails;
          montarCards();
          carregarGraficos();
          loading.value = false
          return;
        }

        // Carrega todos os totais de uma vez
        const response = await axios.get(`${BASE_URL}${ENDPOINTS.DASHBOARD_TOTAIS}`)
        const totais = response.data

        // Salvar no cache
        window.dashboardCache = {
          data: totais,
          timestamp: Date.now()
        };

        totalFuncionarios.value = totais.funcionarios
        totalSetores.value = totais.setores
        totalSistemas.value = totais.sistemas
        totalEmails.value = totais.emails

        montarCards()
        carregarGraficos()
      } catch (error) {
        console.error('Erro ao carregar dados:', error)
        // Dados fallback para demonstração
        totalFuncionarios.value = 45
        totalSetores.value = 8
        totalSistemas.value = 12
        totalEmails.value = 6
        montarCards()
        carregarGraficos()
      } finally {
        setTimeout(() => {
          loading.value = false
        }, 800) // Pequeno delay para evitar flickering
      }
    }

    const carregarGraficos = async () => {
      try {
        // Dados para gráfico de setores
        const dadosSetores = await axios.get(`${BASE_URL}${ENDPOINTS.FUNCIONARIOS_POR_SETOR}`)
        criarGraficoSetores(dadosSetores.data)

        // Dados para gráfico de sistemas
        const dadosSistemas = await axios.get(`${BASE_URL}${ENDPOINTS.FUNCIONARIOS_POR_SISTEMA}`)
        criarGraficoSistemas(dadosSistemas.data)
      } catch (error) {
        console.error('Erro ao carregar gráficos:', error)
      }
    }

    const criarGraficoSetores = (dados) => {
      const ctx = chartSetores.value?.getContext('2d')
      if (!ctx) return

      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: dados.map(item => item.nome),
          datasets: [{
            data: dados.map(item => item.total),
            backgroundColor: coresProfissionais.slice(0, dados.length),
            borderWidth: 0,
            cutout: '60%'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 20,
                usePointStyle: true,
                font: {
                  size: 12,
                  weight: '500'
                }
              }
            },
            datalabels: {
              color: 'white',
              font: {
                weight: 'bold',
                size: 14
              },
              formatter: (value) => value
            }
          }
        },
        plugins: [ChartDataLabels]
      })
    }

    const criarGraficoSistemas = (dados) => {
      const ctx = chartSistemas.value?.getContext('2d')
      if (!ctx) return

      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: dados.map(item => item.nome),
          datasets: [{
            label: 'Funcionários',
            data: dados.map(item => item.total),
            backgroundColor: coresProfissionais[0],
            borderRadius: 8,
            borderSkipped: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            datalabels: {
              anchor: 'end',
              align: 'top',
              color: '#374151',
              font: {
                weight: 'bold',
                size: 12
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                font: {
                  size: 12
                }
              },
              grid: {
                color: '#f3f4f6'
              }
            },
            x: {
              ticks: {
                font: {
                  size: 12
                }
              },
              grid: {
                display: false
              }
            }
          }
        },
        plugins: [ChartDataLabels]
      })
    }

    onMounted(() => {
      carregarDados()
    })

    return {
      totalFuncionarios,
      totalSetores,
      totalSistemas,
      totalEmails,
      cardsData,
      loading,
      chartSetores,
      chartSistemas
    }
  }
}
</script>

<style scoped>
/* Dashboard Tech Premium Styling */
.dashboard-analytics {
  min-height: 100vh;
  background-color: #050a18;
  color: #f8fafc;
  overflow-x: hidden;
  position: relative;
}

/* Background Tech Effects */
.tech-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: radial-gradient(circle at center, black, transparent 90%);
}

.glow-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.1;
  z-index: 1;
}

.glow-1 {
  width: 500px;
  height: 500px;
  background: #3b82f6;
  top: -100px;
  right: -100px;
}

.glow-2 {
  width: 400px;
  height: 400px;
  background: #1e3a8a;
  bottom: -100px;
  left: 0;
}

.dashboard-content-wrapper {
  position: relative;
  z-index: 10;
  padding: 24px;
}

/* Header Premium */
.dashboard-header {
  margin-bottom: 24px;
  padding: 24px 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
}

.header-content h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 800;
  color: #f8fafc;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content h1 span {
  color: #3b82f6;
}

.dashboard-subtitle {
  margin: 4px 0 0 0;
  font-size: 1rem;
  color: #94a3b8;
}

/* Cards Premium */
.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.premium-card {
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  overflow: hidden;
}

.premium-card:hover {
  transform: translateY(-5px);
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
}

.card-glass-body {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  min-height: 110px;
}

.card-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.card-funcionarios .card-icon { color: #3b82f6; background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.2); }
.card-setores .card-icon { color: #f59e0b; background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); }
.card-sistemas .card-icon { color: #ec4899; background: rgba(236, 72, 153, 0.1); border-color: rgba(236, 72, 153, 0.2); }
.card-emails .card-icon { color: #8b5cf6; background: rgba(139, 92, 246, 0.1); border-color: rgba(139, 92, 246, 0.2); }

.card-label {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 4px;
}

.card-value {
  font-size: 1.8rem;
  font-weight: 800;
  color: #f8fafc;
  line-height: 1;
  margin-bottom: 4px;
}

.card-trend {
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-trend i { font-size: 0.7rem; }
.card-funcionarios .card-trend { color: #10b981; }
.card-setores .card-trend { color: #10b981; }
.card-sistemas .card-trend { color: #94a3b8; }
.card-emails .card-trend { color: #10b981; }

/* Charts Premium */
.dashboard-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-container-glass {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  overflow: hidden;
}

.chart-header {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(255, 255, 255, 0.02);
}

.chart-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #cbd5e1;
}

.chart-content {
  padding: 20px;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Responsividade Gráficos */
@media (max-width: 1024px) {
  .dashboard-charts {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-content-wrapper {
    padding: 16px;
  }
  .card-value {
    font-size: 1.5rem;
  }
}
</style>
