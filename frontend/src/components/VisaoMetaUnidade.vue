<template>
  <div class="visao-meta-unidade">
    <!-- Header premium da unidade -->
    <div class="header-unidade">
      <div class="header-background-pattern"></div>
      <div class="header-content">
        <div class="header-left">
          <button class="btn-voltar-premium" @click="$emit('voltar')">
            <i class="fas fa-arrow-left"></i>
            <span>Voltar</span>
          </button>
          <div class="header-title">
            <h1>
              <i class="fas fa-building header-icon"></i>
              Dashboard da Unidade
            </h1>
            <p>Visão consolidada de performance e resultados</p>
          </div>
        </div>
        <div class="header-right">
          <div class="controls-group">
            <div class="filter-control">
              <label>
                <i class="fas fa-building"></i>
                Unidade
              </label>
              <select v-model="unidadeSelecionada" @change="atualizarDados" class="select-premium">
                <option value="">Todas as Unidades</option>
                <option v-for="unidade in unidades" :key="unidade.id" :value="unidade.id">
                  {{ unidade.nome }}
                </option>
              </select>
            </div>
            <div class="date-control">
              <label>
                <i class="fas fa-calendar-alt"></i>
                Período
              </label>
              <input type="month" v-model="dataFiltro" @change="atualizarDados" class="date-input-premium" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="carregando" class="loading-modern">
      <div class="loading-animation">
        <div class="pulse-ring"></div>
        <div class="pulse-ring"></div>
        <div class="pulse-ring"></div>
      </div>
      <p>Carregando dados da unidade...</p>
    </div>

    <!-- Dashboard da Unidade -->
    <div v-else class="dashboard-container">
      <!-- KPIs Principais da Unidade -->
      <div class="kpis-unidade">
        <h3 class="section-title">
          <i class="fas fa-chart-bar"></i>
          Indicadores Principais
        </h3>
        <div class="kpis-grid">
          <div class="kpi-card colaboradores">
            <div class="kpi-header">
              <div class="kpi-icon">
                <i class="fas fa-users"></i>
              </div>
              <span class="kpi-label">Total Colaboradores</span>
            </div>
            <div class="kpi-value">{{ dadosUnidade.totalColaboradores || 0 }}</div>
            <div class="kpi-trend positive">
              <i class="fas fa-arrow-up"></i>
              +5% este mês
            </div>
          </div>

          <div class="kpi-card meta-total">
            <div class="kpi-header">
              <div class="kpi-icon">
                <i class="fas fa-bullseye"></i>
              </div>
              <span class="kpi-label">Meta Total</span>
            </div>
            <div class="kpi-value">{{ dadosUnidade.metaTotal || 0 }}</div>
            <div class="kpi-progress">
              <div class="progress-bar">
                <div class="progress-fill meta-progress" :style="{ width: '100%' }"></div>
              </div>
            </div>
          </div>

          <div class="kpi-card realizado-total">
            <div class="kpi-header">
              <div class="kpi-icon">
                <i class="fas fa-chart-line"></i>
              </div>
              <span class="kpi-label">Total Realizado</span>
            </div>
            <div class="kpi-value">{{ dadosUnidade.totalRealizado || 0 }}</div>
            <div class="kpi-progress">
              <div class="progress-bar">
                <div class="progress-fill realizado-progress" :style="{ width: percentualTotalRealizado + '%' }"></div>
              </div>
              <span class="progress-text">{{ percentualTotalRealizado.toFixed(1) }}% da meta</span>
            </div>
          </div>

          <div class="kpi-card performance-media">
            <div class="kpi-header">
              <div class="kpi-icon">
                <i class="fas fa-trophy"></i>
              </div>
              <span class="kpi-label">Performance Média</span>
            </div>
            <div class="kpi-value">{{ performanceMedia }}%</div>
            <div class="kpi-trend" :class="performanceMedia >= 80 ? 'positive' : 'neutral'">
              <i :class="performanceMedia >= 80 ? 'fas fa-arrow-up' : 'fas fa-minus'"></i>
              {{ performanceStatus }}
            </div>
          </div>
        </div>
      </div>

      <!-- Rankings por Categoria -->
      <div class="rankings-section">
        <h3 class="section-title">
          <i class="fas fa-medal"></i>
          Rankings por Categoria
        </h3>
        <div class="rankings-grid">
          <!-- Ranking Odonto -->
          <div class="ranking-card odonto">
            <div class="ranking-header">
              <div class="ranking-icon">
                <i class="fas fa-tooth"></i>
              </div>
              <h4>Odonto</h4>
              <span class="total-categoria">Total: {{ totaisPorCategoria.odonto || 0 }}</span>
            </div>
            <div class="ranking-list">
              <div v-for="(item, index) in rankingOdonto" :key="index" class="ranking-item">
                <span class="posicao">{{ index + 1 }}º</span>
                <span class="nome">{{ item.nome }}</span>
                <span class="valor">{{ item.valor }}</span>
              </div>
            </div>
          </div>

          <!-- Ranking Check-Up -->
          <div class="ranking-card checkup">
            <div class="ranking-header">
              <div class="ranking-icon">
                <i class="fas fa-stethoscope"></i>
              </div>
              <h4>Check-Up</h4>
              <span class="total-categoria">Total: {{ totaisPorCategoria.checkup || 0 }}</span>
            </div>
            <div class="ranking-list">
              <div v-for="(item, index) in rankingCheckup" :key="index" class="ranking-item">
                <span class="posicao">{{ index + 1 }}º</span>
                <span class="nome">{{ item.nome }}</span>
                <span class="valor">{{ item.valor }}</span>
              </div>
            </div>
          </div>

          <!-- Ranking Dr. Central -->
          <div class="ranking-card drcentral">
            <div class="ranking-header">
              <div class="ranking-icon">
                <i class="fas fa-user-md"></i>
              </div>
              <h4>Dr. Central</h4>
              <span class="total-categoria">Total: {{ totaisPorCategoria.drCentral || 0 }}</span>
            </div>
            <div class="ranking-list">
              <div v-for="(item, index) in rankingDrCentral" :key="index" class="ranking-item">
                <span class="posicao">{{ index + 1 }}º</span>
                <span class="nome">{{ item.nome }}</span>
                <span class="valor">{{ item.valor }}</span>
              </div>
            </div>
          </div>

          <!-- Ranking BabyClick -->
          <div class="ranking-card babyclick">
            <div class="ranking-header">
              <div class="ranking-icon">
                <i class="fas fa-baby"></i>
              </div>
              <h4>BabyClick</h4>
              <span class="total-categoria">Total: {{ totaisPorCategoria.babyclick || 0 }}</span>
            </div>
            <div class="ranking-list">
              <div v-for="(item, index) in rankingBabyclick" :key="index" class="ranking-item">
                <span class="posicao">{{ index + 1 }}º</span>
                <span class="nome">{{ item.nome }}</span>
                <span class="valor">{{ item.valor }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Resumo Executivo -->
      <div class="resumo-executivo">
        <h3 class="section-title">
          <i class="fas fa-clipboard-list"></i>
          Resumo Executivo
        </h3>
        <div class="resumo-grid">
          <div class="resumo-card insights">
            <h4>Principais Insights</h4>
            <div class="insight-list">
              <div class="insight-item positive">
                <i class="fas fa-check-circle"></i>
                <span>{{ insightsPositivos }} colaboradores acima da meta</span>
              </div>
              <div class="insight-item warning">
                <i class="fas fa-exclamation-triangle"></i>
                <span>{{ insightsAlerta }} colaboradores precisam de atenção</span>
              </div>
              <div class="insight-item info">
                <i class="fas fa-info-circle"></i>
                <span>Performance geral da unidade: {{ performanceGeral }}%</span>
              </div>
            </div>
          </div>

          <div class="resumo-card acoes">
            <h4>Ações Recomendadas</h4>
            <div class="acao-list">
              <div class="acao-item">
                <i class="fas fa-bullhorn"></i>
                <span>Implementar programa de incentivos para equipes com baixa performance</span>
              </div>
              <div class="acao-item">
                <i class="fas fa-graduation-cap"></i>
                <span>Oferecer treinamento adicional em vendas consultivas</span>
              </div>
              <div class="acao-item">
                <i class="fas fa-handshake"></i>
                <span>Fortalecer relacionamento com clientes estratégicos</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VisaoMetaUnidade',
  data() {
    return {
      carregando: false,
      unidadeSelecionada: '',
      dataFiltro: new Date().toISOString().slice(0, 7), // Formato YYYY-MM
      
      // Dados da unidade
      dadosUnidade: {
        totalColaboradores: 0,
        metaTotal: 0,
        totalRealizado: 0
      },
      
      // Unidades disponíveis
      unidades: [
        { id: 1, nome: 'Unidade Assis Brasil' },
        { id: 2, nome: 'Unidade DF 47' },
        { id: 3, nome: 'Unidade Azenha' },
        { id: 4, nome: 'Unidade Assis 32224' }
      ],
      
      // Rankings
      rankingOdonto: [],
      rankingCheckup: [],
      rankingDrCentral: [],
      rankingBabyclick: [],
      
      // Totais por categoria
      totaisPorCategoria: {
        odonto: 0,
        checkup: 0,
        drCentral: 0,
        babyclick: 0
      }
    };
  },
  computed: {
    percentualTotalRealizado() {
      return this.dadosUnidade.metaTotal > 0 
        ? (this.dadosUnidade.totalRealizado / this.dadosUnidade.metaTotal) * 100 
        : 0;
    },
    performanceMedia() {
      return this.percentualTotalRealizado.toFixed(1);
    },
    performanceStatus() {
      const perf = this.percentualTotalRealizado;
      if (perf >= 100) return 'Excelente';
      if (perf >= 80) return 'Bom';
      if (perf >= 60) return 'Regular';
      return 'Crítico';
    },
    insightsPositivos() {
      return Math.floor(this.dadosUnidade.totalColaboradores * 0.6); 
    },
    insightsAlerta() {
      return Math.floor(this.dadosUnidade.totalColaboradores * 0.25); 
    },
    performanceGeral() {
      return this.percentualTotalRealizado.toFixed(1);
    },
    mesAtual() {
      if (!this.dataFiltro) return '';
      const [ano, mes] = this.dataFiltro.split('-');
      const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
      ];
      return `${meses[parseInt(mes) - 1]} ${ano}`;
    }
  },
  mounted() {
    this.carregarDadosUnidade();
  },
  methods: {
    async carregarDadosUnidade() {
      this.carregando = true;
      try {
        // Simular carregamento - aqui você faria a chamada real para a API
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Dados simulados - substitua pela chamada real da API
        this.dadosUnidade = {
          totalColaboradores: 45,
          metaTotal: 2250,
          totalRealizado: 1890
        };
        
        // Rankings simulados
        this.rankingOdonto = [
          { nome: 'Maria Silva', valor: 85 },
          { nome: 'João Santos', valor: 78 },
          { nome: 'Ana Costa', valor: 72 },
          { nome: 'Pedro Lima', valor: 68 },
          { nome: 'Carla Rocha', valor: 65 }
        ];
        
        this.rankingCheckup = [
          { nome: 'Roberto Alves', valor: 92 },
          { nome: 'Lucia Mendes', valor: 88 },
          { nome: 'Carlos Dias', valor: 82 },
          { nome: 'Isabel Moura', valor: 79 },
          { nome: 'Fernando Cruz', valor: 76 }
        ];
        
        this.rankingDrCentral = [
          { nome: 'Dr. André Silva', valor: 95 },
          { nome: 'Dra. Beatriz Costa', valor: 89 },
          { nome: 'Dr. Carlos Mendes', valor: 84 },
          { nome: 'Dra. Diana Rocha', valor: 80 },
          { nome: 'Dr. Eduardo Lima', valor: 77 }
        ];
        
        this.rankingBabyclick = [
          { nome: 'Juliana Oliveira', valor: 88 },
          { nome: 'Marcos Pereira', valor: 82 },
          { nome: 'Leticia Santos', valor: 78 },
          { nome: 'Gabriel Costa', valor: 74 },
          { nome: 'Camila Silva', valor: 71 }
        ];
        
        // Totais por categoria
        this.totaisPorCategoria = {
          odonto: 368,
          checkup: 415,
          drCentral: 421,
          babyclick: 393
        };
        
      } catch (error) {
        console.error('Erro ao carregar dados da unidade:', error);
      } finally {
        this.carregando = false;
      }
    },
    
    atualizarDados() {
      console.log('Atualizando dados para unidade:', this.unidadeSelecionada, 'período:', this.dataFiltro);
      this.carregarDadosUnidade();
    }
  }
};
</script>

<style scoped>
/* Container principal */
.visao-meta-unidade {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 0;
}

/* Header da unidade */
.header-unidade {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 25px 30px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.header-background-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.3;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.btn-voltar-premium {
  background: rgba(255, 255, 255, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  cursor: pointer;
}

.btn-voltar-premium:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.header-icon {
  font-size: 1.2rem;
  margin-right: 10px;
  color: #ffffff;
}

.header-title h1 {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
}

.header-title p {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 5px 0 0 0;
  font-weight: 400;
}

.controls-group {
  display: flex;
  gap: 20px;
  align-items: flex-end;
}

.filter-control, .date-control {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-control label, .date-control label {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.select-premium, .date-input-premium {
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  min-width: 180px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.select-premium:focus, .date-input-premium:focus {
  outline: none;
  border-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

/* Loading */
.loading-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #667eea;
}

.loading-animation {
  position: relative;
  width: 60px;
  height: 60px;
  margin-bottom: 20px;
}

.pulse-ring {
  position: absolute;
  border: 3px solid #667eea;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: pulse 2s infinite;
}

.pulse-ring:nth-child(1) { animation-delay: 0s; }
.pulse-ring:nth-child(2) { animation-delay: 0.5s; }
.pulse-ring:nth-child(3) { animation-delay: 1s; }

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.4); opacity: 0; }
}

/* Dashboard container */
.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 35px;
}

/* Section titles */
.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 25px;
  padding-bottom: 10px;
  border-bottom: 2px solid #667eea;
}

/* KPIs da Unidade */
.kpis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.kpi-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.kpi-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
}

.kpi-card.colaboradores .kpi-icon {
  background: linear-gradient(135deg, #3498db, #2980b9);
}

.kpi-card.meta-total .kpi-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.kpi-card.realizado-total .kpi-icon {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
}

.kpi-card.performance-media .kpi-icon {
  background: linear-gradient(135deg, #f39c12, #e67e22);
}

.kpi-label {
  font-size: 1rem;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
}

.kpi-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 15px 0;
  line-height: 1;
}

.kpi-trend {
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.kpi-trend.positive {
  color: #2ecc71;
}

.kpi-trend.neutral {
  color: #f39c12;
}

.kpi-progress {
  margin-top: 15px;
}

.progress-bar {
  height: 8px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.6s ease;
}

.meta-progress {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.realizado-progress {
  background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
}

.progress-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6c757d;
}

/* Rankings */
.rankings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}

.ranking-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
}

.ranking-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.ranking-icon {
  width: 45px;
  height: 45px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.ranking-card.odonto .ranking-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.ranking-card.checkup .ranking-icon {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
}

.ranking-card.drcentral .ranking-icon {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.ranking-card.babyclick .ranking-icon {
  background: linear-gradient(135deg, #ff6b9d, #ff8a80);
}

.ranking-header h4 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
  flex: 1;
}

.total-categoria {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.ranking-item:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.posicao {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
}

.nome {
  flex: 1;
  font-weight: 600;
  color: #2c3e50;
}

.valor {
  font-weight: 700;
  color: #667eea;
  font-size: 1.1rem;
}

/* Resumo Executivo */
.resumo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
}

.resumo-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
}

.resumo-card h4 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #667eea;
}

.insight-list, .acao-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.insight-item, .acao-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 10px;
}

.insight-item.positive i {
  color: #2ecc71;
}

.insight-item.warning i {
  color: #f39c12;
}

.insight-item.info i {
  color: #667eea;
}

.acao-item i {
  color: #667eea;
}

/* Responsividade */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .header-left {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .controls-group {
    flex-direction: column;
    gap: 15px;
    width: 100%;
  }
  
  .dashboard-container {
    padding: 20px 15px;
  }
  
  .kpis-grid, .rankings-grid {
    grid-template-columns: 1fr;
  }
  
  .kpi-value {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .header-unidade {
    padding: 20px 15px;
  }
  
  .header-title h1 {
    font-size: 1.6rem;
  }
  
  .kpi-card, .ranking-card, .setor-card, .resumo-card {
    padding: 20px;
  }
  
  .kpi-value {
    font-size: 1.8rem;
  }
  
  .resumo-grid {
    grid-template-columns: 1fr;
  }
}
</style>
