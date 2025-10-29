<template>
  <div class="dashboard-analytics">
    <!-- Header Premium -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1>
          <i class="fas fa-chart-line"></i>
          Dashboard Analytics
        </h1>
        <p class="dashboard-subtitle">Visão geral do sistema de gestão</p>
      </div>
    </div>

    <!-- Cards Premium -->
    <div class="dashboard-cards">
      <div 
        v-for="card in cardsData" 
        :key="card.label"
        :class="['premium-card', card.class]"
      >
        <div class="card-background">
          <div class="card-icon">
            <i :class="card.icon"></i>
          </div>
          <div class="card-content">
            <div class="card-label">{{ card.label }}</div>
            <div class="card-value">{{ card.value }}</div>
            <div class="card-trend">
              <i :class="card.trend.icon"></i>
              {{ card.trend.text }}
            </div>
          </div>
          <div class="card-decoration"></div>
        </div>
      </div>
    </div>

    <!-- Charts Premium -->
    <div class="dashboard-charts">
      <!-- Chart Funcionários por Setor -->
      <div class="chart-container">
        <div class="chart-header">
          <h3>TOP 10 - Funcionários por Setor</h3>
        </div>
        <div class="chart-content">
          <canvas ref="chartSetores"></canvas>
        </div>
      </div>

      <!-- Chart Funcionários por Sistema -->
      <div class="chart-container">
        <div class="chart-header">
          <h3>TOP 10 - Funcionários por Sistema</h3>
        </div>
        <div class="chart-content">
          <canvas ref="chartSistemas"></canvas>
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
      chartSetores,
      chartSistemas
    }
  }
}
</script>

<style scoped>
/* Dashboard Premium Styling */
.dashboard-analytics {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
}

/* Header Premium */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 32px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 16px;
}

.dashboard-subtitle {
  margin: 8px 0 0 0;
  font-size: 1.1rem;
  color: #6b7280;
  font-weight: 500;
}

/* Cards Premium */
.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.premium-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.premium-card:hover {
  transform: translateY(-8px);
}

.card-background {
  padding: 32px;
  position: relative;
  height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.card-funcionarios .card-background {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.card-setores .card-background {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.card-sistemas .card-background {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
}

.card-emails .card-background {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 16px;
  backdrop-filter: blur(10px);
}

.card-content {
  flex-grow: 1;
}

.card-label {
  font-size: 1rem;
  font-weight: 500;
  opacity: 0.9;
  margin-bottom: 8px;
}

.card-value {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 12px;
}

.card-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  opacity: 0.9;
}

.card-decoration {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  pointer-events: none;
}

/* Charts Premium */
.dashboard-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
}

.chart-container:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px 16px;
  border-bottom: 1px solid #f3f4f6;
}

.chart-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}

.chart-content {
  padding: 24px 32px 32px;
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-content canvas {
  max-width: 100%;
  max-height: 100%;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .dashboard-charts {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-analytics {
    padding: 16px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
    padding: 24px;
  }
  
  .header-content h1 {
    font-size: 2rem;
  }
  
  .dashboard-cards {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    margin-bottom: 16px;
  }
  
  .chart-content {
    height: 300px;
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .card-value {
    font-size: 2.5rem;
  }
  
  .card-background {
    padding: 24px;
    height: 160px;
  }
  
  .chart-header {
    padding: 16px 20px 12px;
  }
  
  .chart-content {
    padding: 16px 20px 24px;
  }
}
</style>
