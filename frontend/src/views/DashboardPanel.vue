<template>
  <div class="dashboard-analytics">
    <div class="dashboard-cards">
      <div class="card" v-for="card in cards" :key="card.label" :style="{background: card.bg}">
        <div class="card-title">{{ card.label }} <span v-if="card.icon">{{ card.icon }}</span></div>
        <div class="card-value">{{ card.value }}</div>
        <div class="card-sub" v-if="card.sub">{{ card.sub }}</div>
      </div>
    </div>
    <div class="dashboard-charts">
      <div class="chart-box">
        <h4>Funcionários por Setor</h4>
        <canvas id="setorChart"></canvas>
      </div>
      <div class="chart-box">
        <h4>Funcionários por Cargo</h4>
        <canvas id="cargoChart"></canvas>
      </div>
      <div class="chart-box">
        <h4>Funcionários por Sistema</h4>
        <canvas id="sistemaChart"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import axios from 'axios';
import { API_BASE_URL } from '../api';
import ColaboradorCard from '../components/ColaboradorCard.vue';

export default {
  name: 'DashboardPanel',
  components: { ColaboradorCard },
  data() {
    return {
      cards: [],
      funcionarios: [],
      setores: [],
      grupoEmails: [],
      sistemas: [],
      filtroSelecionado: 'todos',
      valorFiltro: null,
      mostrarQuadro: false
    }
  },
  async mounted() {
    await this.carregarDados();
    this.montarCards();
    this.montarGraficos();
    // Ouvinte para atualização dos cards quando grupos de e-mail mudarem
    window.addEventListener('atualizarDashboard', this.atualizarDashboard);
  },
  beforeUnmount() {
    window.removeEventListener('atualizarDashboard', this.atualizarDashboard);
  },
    async atualizarDashboard() {
      await this.carregarDados();
      this.montarCards();
    },
  methods: {
    async carregarDados() {
      const [funcs, sets, sist, grupos] = await Promise.all([
        axios.get(`${API_BASE_URL}/funcionarios/`),
        axios.get(`${API_BASE_URL}/setores/`),
        axios.get(`${API_BASE_URL}/sistemas/`),
        axios.get(`${API_BASE_URL}/grupos-email/`),
      ]);
      this.funcionarios = funcs.data;
      this.setores = sets.data;
      this.sistemas = sist.data;
      this.grupoEmails = grupos.data;
    },
    montarCards() {
      this.cards = [
        { label: 'Funcionários', value: this.funcionarios.length, icon: '🧑‍💼', bg: '#64b5f6' },
        { label: 'Setores', value: this.setores.length, icon: '🏢', bg: '#ffd54f' },
        { label: 'Sistemas', value: this.sistemas.length, icon: '💻', bg: '#1976d2' },
        { label: 'Grupos de E-mail', value: this.grupoEmails.length, icon: '📧', bg: '#ba68c8' }
      ];
    },
    // Computed para filtrar funcionários
    funcionariosFiltrados() {
      if (this.filtroSelecionado === 'todos' || !this.valorFiltro) return this.funcionarios;
      if (this.filtroSelecionado === 'setor') {
        return this.funcionarios.filter(f => f.setores && f.setores.some(s => s.id === this.valorFiltro));
      }
      if (this.filtroSelecionado === 'sistema') {
        return this.funcionarios.filter(f => f.sistemas && f.sistemas.some(s => s.id === this.valorFiltro));
      }
      if (this.filtroSelecionado === 'grupo_email') {
        return this.funcionarios.filter(f => f.grupos_email && f.grupos_email.some(g => g.id === this.valorFiltro));
      }
      return this.funcionarios;
    },
    // Computed para opções do filtro
    opcoesFiltro() {
      if (this.filtroSelecionado === 'setor') return this.setores;
      if (this.filtroSelecionado === 'sistema') return this.sistemas;
      if (this.filtroSelecionado === 'grupo_email') return this.grupoEmails;
      return [];
    },
    montarGraficos() {
      const funcionarios = this.funcionariosFiltrados();
      // Funcionários por Setor
      const setoresLabels = this.setores.map(s => s.nome);
      const setoresData = this.setores.map(setor =>
        funcionarios.filter(f => f.setores && f.setores.some(s => s.id === setor.id)).length
      );
      const setorCanvas = document.getElementById('setorChart');
      if (setorCanvas) {
        new Chart(setorCanvas, {
          type: 'pie',
          data: {
            labels: setoresLabels,
            datasets: [{ data: setoresData, backgroundColor: ['#1976d2','#222','#fff','#174a7c','#64b5f6','#000'] }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' },
              datalabels: {
                color: '#222',
                font: { weight: 'bold', size: 16 },
                formatter: (value, ctx) => value,
              }
            }
          },
          plugins: [ChartDataLabels]
        });
      }

      // Funcionários por Cargo
      const cargosLabels = [...new Set(funcionarios.map(f => f.cargo))].filter(Boolean);
      const cargosData = cargosLabels.map(cargo =>
        funcionarios.filter(f => f.cargo === cargo).length
      );
      const cargoCanvas = document.getElementById('cargoChart');
      if (cargoCanvas) {
        new Chart(cargoCanvas, {
          type: 'bar',
          data: {
            labels: cargosLabels,
            datasets: [{ label: 'Funcionários', data: cargosData, backgroundColor: '#1976d2' }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { display: false },
              datalabels: {
                anchor: 'end',
                align: 'top',
                color: '#222',
                font: { weight: 'bold', size: 14 },
                formatter: (value, ctx) => value,
              }
            }
          },
          plugins: [ChartDataLabels]
        });
      }

      // Funcionários por Sistema
      const sistemasLabels = this.sistemas.map(s => s.nome);
      const sistemasData = this.sistemas.map(sistema =>
        funcionarios.filter(f => f.sistemas && f.sistemas.some(s => s.id === sistema.id)).length
      );
      const sistemaCanvas = document.getElementById('sistemaChart');
      if (sistemaCanvas) {
        new Chart(sistemaCanvas, {
          type: 'doughnut',
          data: {
            labels: sistemasLabels,
            datasets: [{ data: sistemasData, backgroundColor: ['#1976d2','#222','#fff','#174a7c','#64b5f6','#000'] }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' },
              datalabels: {
                color: '#222',
                font: { weight: 'bold', size: 16 },
                formatter: (value, ctx) => value,
              }
            }
          },
          plugins: [ChartDataLabels]
        });
      }

      // Funcionários por Grupo de E-mail
      if (this.grupoEmails && this.grupoEmails.length) {
        const grupoLabels = this.grupoEmails.map(g => g.nome);
        const grupoData = this.grupoEmails.map(grupo =>
          funcionarios.filter(f => f.grupos_email && f.grupos_email.some(gf => gf.id === grupo.id)).length
        );
        const grupoCanvas = document.getElementById('grupoEmailChart');
        if (grupoCanvas) {
          new Chart(grupoCanvas, {
            type: 'pie',
            data: {
              labels: grupoLabels,
              datasets: [{ data: grupoData, backgroundColor: ['#1976d2','#222','#fff','#174a7c','#64b5f6','#000'] }]
            },
            options: {
              responsive: true,
              plugins: {
                legend: { position: 'bottom' },
                datalabels: {
                  color: '#222',
                  font: { weight: 'bold', size: 16 },
                  formatter: (value, ctx) => value,
                }
              }
            },
            plugins: [ChartDataLabels]
          });
        }
      }
    }
  }
}
</script>

<style scoped>



.dashboard-analytics {
  display: flex;
  flex-direction: column;
  gap: 32px;
  min-height: 100vh;
  padding: 32px 0;
  background: linear-gradient(120deg, #fff 0%, #1976d2 100%);
}



.dashboard-cards {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
}

.card {
  flex: 1;
  background: #fff;
  border-radius: 14px;
  padding: 32px 22px;
  box-shadow: 0 1px 4px rgba(20,65,121,0.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--font-titulo);
  color: #1976d2;
  min-width: 180px;
  max-width: 240px;
  border: 1px solid #1976d2;
}
.card-title {
  font-size: 1.2em;
  margin-bottom: 8px;
  font-weight: bold;
  letter-spacing: 0.5px;
  color: #222;
}
.card-value {
  font-size: 2.6em;
  font-weight: bold;
  margin-bottom: 6px;
  color: #fff;
}
.card-sub {
  font-size: 1em;
  color: #222;
}

.dashboard-charts {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}


.chart-box {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 1px 4px rgba(20,65,121,0.06);
  padding: 24px 16px;
  min-width: 320px;
  max-width: 420px;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid #1976d2;
}
.chart-box h4 {
  font-family: var(--font-titulo);
  color: #1976d2;
  margin-bottom: 12px;
  font-weight: bold;
  letter-spacing: 0.5px;
}
canvas {
  max-width: 340px;
  max-height: 220px;
  background: #fff;
  border-radius: 10px;
}

.dashboard-colaboradores {
  margin-top: 32px;
}
.colaboradores-list {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.novo-cargo-btn {
  background: #fbc02d;
  color: #1a3760;
  border: none;
  border-radius: 6px;
  padding: 8px 18px;
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
  margin-left: 18px;
}
.novo-cargo-btn:hover {
  background: #ffd54f;
}
.quadro-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}
.quadro-table th, .quadro-table td {
  border-bottom: 2px solid #fbc02d;
  padding: 10px 8px;
  text-align: left;
}
.quadro-table th {
  color: #1a3760;
  font-weight: bold;
}
.quadro-table td {
  color: #222;
}

@media (max-width: 900px) {
  .dashboard-cards, .dashboard-charts {
    flex-direction: column;
    gap: 18px;
  }
  .chart-box {
    min-width: 220px;
    max-width: 100%;
  }
}
</style>
