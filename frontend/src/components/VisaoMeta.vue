<template>
  <div class="visao-meta">
    <div class="header-modern-enhanced">
      <div class="header-background-pattern"></div>
      <div class="header-content">
        <div class="header-left">
          <button class="btn-voltar-premium" @click="$emit('voltar')">
            <i class="fas fa-arrow-left"></i>
            <span>Voltar</span>
          </button>
          <div class="header-title">
            <h1>
              <i class="fas fa-chart-line header-icon"></i>
              Painel de Performance
            </h1>
            <p>Dashboard completo de resultados e indicadores</p>
          </div>
        </div>
        <div class="header-right">
          <div class="date-control-enhanced">
            <label>
              <i class="fas fa-calendar-alt"></i>
              Período de Análise
            </label>
            <input type="month" v-model="dataFiltro" @change="atualizarDados" class="date-input-premium" />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading moderno -->
    <div v-if="carregando" class="loading-modern">
      <div class="loading-animation">
        <div class="pulse-ring"></div>
        <div class="pulse-ring"></div>
        <div class="pulse-ring"></div>
      </div>
      <p>Carregando dados...</p>
    </div>

    <div v-else class="dashboard-container">
      <div class="colaborador-card-premium">
        <div class="colaborador-background">
          <div class="background-shape"></div>
        </div>
        <div class="colaborador-content">
          <div class="colaborador-avatar-enhanced">
            <div class="avatar-image">
              {{ (colaboradorSelecionado.nome || 'U').charAt(0).toUpperCase() }}
            </div>
            <div class="status-badge">
              <i class="fas fa-check-circle"></i>
            </div>
          </div>
          <div class="colaborador-info-enhanced">
            <h2 class="colaborador-name">{{ colaboradorSelecionado.nome || 'Colaborador' }}</h2>
            <span class="colaborador-title">{{ colaboradorSelecionado.cargo?.nome || 'Cargo não definido' }}</span>
            <div class="colaborador-details-grid">
              <div class="detail-card">
                <div class="detail-icon departamento">
                  <i class="fas fa-building"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Departamento</span>
                  <span class="detail-value">{{ colaboradorSelecionado.setores?.[0]?.nome || 'Setor não definido' }}</span>
                </div>
              </div>
              <div class="detail-card">
                <div class="detail-icon periodo">
                  <i class="fas fa-calendar-alt"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Período Análise</span>
                  <span class="detail-value">{{ mesAtual }}</span>
                </div>
              </div>
              <div class="detail-card">
                <div class="detail-icon status">
                  <i class="fas fa-user-check"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Status</span>
                  <span class="detail-value status-active">
                    <i class="fas fa-circle"></i>
                    Ativo
                  </span>
                </div>
              </div>
              <div class="detail-card">
                <div class="detail-icon performance">
                  <i class="fas fa-chart-line"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Performance</span>
                  <span class="detail-value performance-good">
                    <i class="fas fa-arrow-up"></i>
                    Acima da Meta
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="metrics-container">
        <h3 class="section-title">
          <i class="fas fa-chart-line"></i>
          Métricas Principais
        </h3>
        <div class="metrics-grid">
          <div class="metric-card meta">
            <div class="metric-header">
              <div class="metric-icon">
                <i class="fas fa-bullseye"></i>
              </div>
              <span class="metric-label">Meta</span>
            </div>
            <div class="metric-value">{{ dadosMeta.meta || 0 }}</div>
            <div class="metric-progress">
              <div class="progress-bar">
                <div class="progress-fill meta-progress" :style="{ width: '100%' }"></div>
              </div>
            </div>
          </div>

          <div class="metric-card realizado">
            <div class="metric-header">
              <div class="metric-icon">
                <i class="fas fa-chart-line"></i>
              </div>
              <span class="metric-label">Realizado</span>
            </div>
            <div class="metric-value">{{ dadosMeta.realizado || 0 }}</div>
            <div class="metric-progress">
              <div class="progress-bar">
                <div class="progress-fill realizado-progress" :style="{ width: percentualRealizado + '%' }"></div>
              </div>
              <span class="progress-text">{{ percentualRealizado.toFixed(1) }}% da meta</span>
            </div>
          </div>

          <div class="metric-card restante">
            <div class="metric-header">
              <div class="metric-icon">
                <i class="fas fa-clock"></i>
              </div>
              <span class="metric-label">Meta Restante</span>
            </div>
            <div class="metric-value">{{ metaRestante }}</div>
            <div class="metric-progress">
              <div class="progress-bar">
                <div class="progress-fill restante-progress" :style="{ width: percentualRestante + '%' }"></div>
              </div>
              <span class="progress-text">{{ percentualRestante.toFixed(1) }}% restante</span>
            </div>
          </div>

          <div class="metric-card nps">
            <div class="metric-header">
              <div class="metric-icon">
                <i class="fas fa-star"></i>
              </div>
              <span class="metric-label">NPS/CSAT</span>
            </div>
            <div class="metric-value">{{ dadosMeta.nps || '-' }}</div>
            <div class="metric-progress">
              <div class="nps-rating">
                <div class="stars">
                  <i v-for="n in 5" :key="n" 
                     :class="['fas fa-star', { 'star-filled': n <= Math.floor(dadosMeta.nps/2) }]">
                  </i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Grid de médias diárias -->
      <div class="daily-metrics">
        <h3><i class="fas fa-calendar-day"></i> Médias Diárias</h3>
        <div class="daily-grid">
          <div class="daily-item">
            <span class="daily-label">Meta/Dia</span>
            <span class="daily-value">{{ metaPorDia }}</span>
          </div>
          <div class="daily-item">
            <span class="daily-label">Realizado/Dia</span>
            <span class="daily-value">{{ realizadoPorDia }}</span>
          </div>
          <div class="daily-item">
            <span class="daily-label">Restante/Dia</span>
            <span class="daily-value">{{ metaRestantePorDia }}</span>
          </div>
        </div>
      </div>

      <!-- Seção de Vendas Expandida -->
      <div class="section-card vendas-section">
        <div class="section-header">
          <i class="fas fa-chart-bar"></i>
          <h3>Vendas por Categoria</h3>
          <div class="period-info">
            <span class="period-label">Período: {{ mesAtual }}</span>
          </div>
        </div>
        <div class="vendas-expanded-grid">
          <div class="venda-item-expanded odonto">
            <div class="venda-header">
              <div class="venda-icon">
                <i class="fas fa-tooth"></i>
              </div>
              <div class="venda-info">
                <h4>Odonto</h4>
                <span class="categoria-desc">Consultas Odontológicas</span>
              </div>
            </div>
            <div class="venda-metrics">
              <div class="venda-value-main">{{ dadosVendas.odonto || 0 }}</div>
              <div class="venda-details">
                <div class="detail-item">
                  <span class="detail-label">Meta:</span>
                  <span class="detail-value">150</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">% Meta:</span>
                  <span class="detail-value success">{{ ((dadosVendas.odonto / 150) * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="venda-item-expanded checkup">
            <div class="venda-header">
              <div class="venda-icon">
                <i class="fas fa-stethoscope"></i>
              </div>
              <div class="venda-info">
                <h4>Check-Up</h4>
                <span class="categoria-desc">Exames Preventivos</span>
              </div>
            </div>
            <div class="venda-metrics">
              <div class="venda-value-main">{{ dadosVendas.checkup || 0 }}</div>
              <div class="venda-details">
                <div class="detail-item">
                  <span class="detail-label">Meta:</span>
                  <span class="detail-value">100</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">% Meta:</span>
                  <span class="detail-value success">{{ ((dadosVendas.checkup / 100) * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="venda-item-expanded drcentral">
            <div class="venda-header">
              <div class="venda-icon">
                <i class="fas fa-user-md"></i>
              </div>
              <div class="venda-info">
                <h4>Dr. Central</h4>
                <span class="categoria-desc">Consultas Médicas</span>
              </div>
            </div>
            <div class="venda-metrics">
              <div class="venda-value-main">{{ dadosVendas.drCentral || 0 }}</div>
              <div class="venda-details">
                <div class="detail-item">
                  <span class="detail-label">Meta:</span>
                  <span class="detail-value">120</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">% Meta:</span>
                  <span class="detail-value success">{{ ((dadosVendas.drCentral / 120) * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Resumo de vendas -->
        <div class="vendas-summary">
          <div class="summary-card">
            <h4>Total de Vendas</h4>
            <div class="summary-value">{{ totalVendas }}</div>
            <div class="summary-trend positive">
              <i class="fas fa-arrow-up"></i>
              +15% vs mês anterior
            </div>
          </div>
          <div class="summary-card">
            <h4>Ticket Médio</h4>
            <div class="summary-value">R$ {{ ticketMedio }}</div>
            <div class="summary-trend positive">
              <i class="fas fa-arrow-up"></i>
              +8% vs mês anterior
            </div>
          </div>
        </div>
      </div>

      <!-- Seção de Comissão -->
      <div class="section-card comissao">
        <div class="section-header">
          <i class="fas fa-dollar-sign"></i>
          <h3>Comissão</h3>
        </div>
        <div class="comissao-grid">
          <div class="comissao-item">
            <label>Meta Realizado</label>
            <div class="comissao-value">{{ dadosComissao.metaRealizado || 0 }}</div>
          </div>
          <div class="comissao-item">
            <label>Campanha</label>
            <div class="comissao-value">{{ dadosComissao.campanha || 0 }}</div>
          </div>
          <div class="comissao-item">
            <label>Dr. Central</label>
            <div class="comissao-value">{{ dadosComissao.drCentral || 0 }}</div>
          </div>
          <div class="comissao-total">
            <label>Total</label>
            <div class="total-value">R$ {{ totalComissao.toFixed(2) }}</div>
          </div>
        </div>
      </div>

      <!-- Seção de Projeções -->
      <div class="section-card projecoes">
        <div class="section-header">
          <i class="fas fa-chart-pie"></i>
          <h3>Projeções</h3>
        </div>
        <div class="projecoes-grid">
          <div class="projecao-item">
            <label>Atingimento Projetado</label>
            <div class="projecao-value">{{ projecoes.atingimentoProjetado }}%</div>
          </div>
          <div class="projecao-item">
            <label>Realizado Projetado</label>
            <div class="projecao-value">{{ projecoes.realizadoProjetado }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VisaoMeta',
  props: {
    colaborador: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      carregando: false,
      dataFiltro: new Date().toISOString().slice(0, 7), // Formato YYYY-MM
      colaboradorSelecionado: { ...this.colaborador },
      dadosMeta: {
        meta: 0,
        realizado: 0,
        nps: ''
      },
      dadosVendas: {
        odonto: 0,
        checkup: 0,
        drCentral: 0
      },
      dadosComissao: {
        metaRealizado: 0,
        campanha: 0,
        drCentral: 0
      },
      projecoes: {
        atingimentoProjetado: 0,
        realizadoProjetado: 0
      }
    }
  },
  computed: {
    metaRestante() {
      return Math.max(0, this.dadosMeta.meta - this.dadosMeta.realizado);
    },
    metaPorDia() {
      const diasNoMes = new Date(
        parseInt(this.dataFiltro.split('-')[0]),
        parseInt(this.dataFiltro.split('-')[1]),
        0
      ).getDate();
      return (this.dadosMeta.meta / diasNoMes).toFixed(2);
    },
    realizadoPorDia() {
      const hoje = new Date();
      const diasPassados = hoje.getDate();
      return (this.dadosMeta.realizado / diasPassados).toFixed(2);
    },
    metaRestantePorDia() {
      const hoje = new Date();
      const diasRestantes = new Date(
        parseInt(this.dataFiltro.split('-')[0]),
        parseInt(this.dataFiltro.split('-')[1]),
        0
      ).getDate() - hoje.getDate();
      return diasRestantes > 0 ? (this.metaRestante / diasRestantes).toFixed(2) : 0;
    },
    totalComissao() {
      return this.dadosComissao.metaRealizado + 
             this.dadosComissao.campanha + 
             this.dadosComissao.drCentral;
    },
    totalVendas() {
      return (this.dadosVendas.odonto || 0) + (this.dadosVendas.checkup || 0) + (this.dadosVendas.drCentral || 0);
    },
    ticketMedio() {
      const total = this.totalVendas;
      return total > 0 ? (total * 350 / total).toFixed(0) : 0; // Simulando ticket médio
    },
    percentualRealizado() {
      return this.dadosMeta.meta > 0 ? (this.dadosMeta.realizado / this.dadosMeta.meta) * 100 : 0;
    },
    percentualRestante() {
      return 100 - this.percentualRealizado;
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
    this.carregarDadosMeta();
  },
  methods: {
    async carregarDadosMeta() {
      this.carregando = true;
      try {
        // Aqui você fará a chamada real para a API
        // const response = await fetch(`/api/metas/${this.colaborador.id}?data=${this.dataFiltro}`);
        // const dados = await response.json();
        
        // Por enquanto, dados de exemplo - substitua pela chamada real da API
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        this.dadosMeta = {
          meta: 150,
          realizado: 75,
          nps: '8.5'
        };
        
        this.dadosVendas = {
          odonto: 10,
          checkup: 8,
          drCentral: 5
        };
        
        this.dadosComissao = {
          metaRealizado: 500,
          campanha: 200,
          drCentral: 100
        };
        
        this.calcularProjecoes();
      } catch (error) {
        console.error('Erro ao carregar dados de meta:', error);
      } finally {
        this.carregando = false;
      }
    },
    
    atualizarDados() {
      this.carregarDadosMeta();
    },
    
    calcularProjecoes() {
      const percentualRealizado = this.dadosMeta.realizado / this.dadosMeta.meta * 100;
      this.projecoes.atingimentoProjetado = Math.min(100, percentualRealizado * 1.2).toFixed(2);
      this.projecoes.realizadoProjetado = (this.dadosMeta.meta * (this.projecoes.atingimentoProjetado / 100)).toFixed(2);
    }
  },
  watch: {
    'dataFiltro'() {
      this.carregarDadosMeta();
    }
  }
}
</script>

<style scoped>
/* Variáveis CSS para cores dinâmicas */
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  --danger-gradient: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  --info-gradient: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  --dark-gradient: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  
  --shadow-light: 0 2px 10px rgba(0,0,0,0.1);
  --shadow-medium: 0 4px 20px rgba(0,0,0,0.15);
  --shadow-heavy: 0 8px 30px rgba(0,0,0,0.2);
  
  --border-radius: 16px;
  --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.visao-meta {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header moderno */
.header-modern {
  background: var(--primary-gradient);
  color: white;
  padding: 2rem 0;
  box-shadow: var(--shadow-heavy);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.btn-voltar-modern {
  background: rgba(255,255,255,0.2);
  border: 2px solid rgba(255,255,255,0.3);
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
  backdrop-filter: blur(10px);
}

.btn-voltar-modern:hover {
  background: rgba(255,255,255,0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.header-title h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(45deg, #fff, #f0f9ff);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-title p {
  margin: 0.25rem 0 0 0;
  opacity: 0.9;
  font-size: 0.9rem;
}

/* Header moderno aprimorado */
.header-modern-enhanced {
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

.header-modern-enhanced .header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
}

.header-modern-enhanced .header-left {
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

.header-modern-enhanced .header-title h1 {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
}

.header-modern-enhanced .header-title p {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 5px 0 0 0;
  font-weight: 400;
}

.date-control-enhanced {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.date-control-enhanced label {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.date-input-premium {
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  min-width: 200px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.date-input-premium:focus {
  outline: none;
  border-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

/* Card do colaborador premium */
.colaborador-card-premium {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
  position: relative;
  overflow: hidden;
}

.colaborador-background {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  opacity: 0.05;
}

.background-shape {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-radius: 50%;
  transform: translate(30%, -30%);
}

.colaborador-content {
  position: relative;
  z-index: 2;
}

.colaborador-avatar-enhanced {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.avatar-image {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.status-badge {
  position: absolute;
  bottom: -5px;
  right: -5px;
  background: #2ecc71;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  box-shadow: 0 2px 8px rgba(46, 204, 113, 0.3);
}

.colaborador-name {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.colaborador-title {
  font-size: 1.1rem;
  color: #667eea;
  font-weight: 600;
  display: block;
  margin-bottom: 25px;
}

.colaborador-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.detail-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #e9ecef;
  border-radius: 15px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s ease;
}

.detail-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.detail-icon {
  width: 45px;
  height: 45px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
}

.detail-icon.departamento {
  background: linear-gradient(135deg, #3498db, #2980b9);
}

.detail-icon.periodo {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.detail-icon.status {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
}

.detail-icon.performance {
  background: linear-gradient(135deg, #f39c12, #e67e22);
}

.detail-content {
  flex: 1;
}

.detail-label {
  display: block;
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 1rem;
  font-weight: 700;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-active {
  color: #2ecc71 !important;
}

.performance-good {
  color: #f39c12 !important;
}

.date-control {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.date-control label {
  font-size: 0.875rem;
  font-weight: 500;
  opacity: 0.9;
}

.date-control input {
  padding: 0.75rem 1rem;
  border: 2px solid rgba(255,255,255,0.2);
  border-radius: var(--border-radius);
  background: rgba(255,255,255,0.1);
  color: white;
  backdrop-filter: blur(10px);
  transition: var(--transition);
}

.date-control input:focus {
  outline: none;
  border-color: rgba(255,255,255,0.5);
  background: rgba(255,255,255,0.2);
}

/* Loading moderno */
.loading-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #64748b;
}

.loading-animation {
  position: relative;
  width: 60px;
  height: 60px;
}

.pulse-ring {
  position: absolute;
  border: 3px solid #667eea;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.pulse-ring:nth-child(1) { animation-delay: 0s; }
.pulse-ring:nth-child(2) { animation-delay: 0.7s; }
.pulse-ring:nth-child(3) { animation-delay: 1.4s; }

@keyframes pulse {
  0% {
    width: 20px;
    height: 20px;
    opacity: 1;
    transform: translate(-50%, -50%);
  }
  100% {
    width: 60px;
    height: 60px;
    opacity: 0;
    transform: translate(-50%, -50%);
  }
}

/* Container principal */
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  display: grid;
  gap: 2rem;
  grid-template-columns: 1fr;
}

/* Card do colaborador */
.colaborador-card {
  background: white;
  border-radius: var(--border-radius);
  padding: 2rem;
  box-shadow: var(--shadow-light);
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: var(--transition);
}

.colaborador-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
}

.colaborador-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  box-shadow: var(--shadow-light);
}

.colaborador-info h2 {
  margin: 0;
  color: #1e293b;
  font-size: 1.5rem;
}

.colaborador-role {
  color: #64748b;
  font-size: 0.9rem;
}

/* Grid de métricas principais */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.metric-card {
  background: white;
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
  border-left: 4px solid;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
}

.metric-card.meta { border-left-color: #10b981; }
.metric-card.realizado { border-left-color: #3b82f6; }
.metric-card.restante { border-left-color: #f59e0b; }
.metric-card.nps { border-left-color: #8b5cf6; }

.metric-card {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.metric-card.meta .metric-icon { background: linear-gradient(135deg, #10b981, #059669); }
.metric-card.realizado .metric-icon { background: linear-gradient(135deg, #3b82f6, #1e40af); }
.metric-card.restante .metric-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }
.metric-card.nps .metric-icon { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }

.metric-content {
  flex: 1;
}

/* Container das métricas principais melhorado */
.metrics-container {
  margin-bottom: 30px;
}

.metrics-container .section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e74c3c;
}

/* Grid principal das métricas expandido */
.metrics-container .metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

/* Cards das métricas ampliados */
.metrics-container .metric-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
  padding: 25px;
  transition: all 0.3s ease;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-left: none;
}

.metrics-container .metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
}

/* Header do card métrica */
.metric-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.metrics-container .metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
}

.metrics-container .metric-card.meta .metric-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.metrics-container .metric-card.realizado .metric-icon {
  background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
}

.metrics-container .metric-card.restante .metric-icon {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
}

.metrics-container .metric-card.nps .metric-icon {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
}

.metric-label {
  font-size: 1rem;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
}

/* Valor da métrica ampliado */
.metric-value {
  font-size: 2.8rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 15px 0;
  line-height: 1;
}

/* Barra de progresso melhorada */
.metric-progress {
  margin-top: 15px;
}

.progress-bar {
  height: 10px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
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

.restante-progress {
  background: linear-gradient(90deg, #f39c12 0%, #e67e22 100%);
}

.progress-text {
  font-size: 0.9rem;
  font-weight: 600;
  color: #6c757d;
}

/* Rating NPS melhorado */
.nps-rating {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stars {
  display: flex;
  gap: 4px;
}

.stars .fas.fa-star {
  font-size: 20px;
  color: #ddd;
  transition: color 0.2s ease;
}

.stars .fas.fa-star.star-filled {
  color: #f1c40f;
}

/* Seção de Vendas Expandida */
.vendas-section {
  margin-bottom: 35px;
}

.vendas-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.period-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.period-label {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.vendas-expanded-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.venda-item-expanded {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.venda-item-expanded:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
}

.venda-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.venda-item-expanded .venda-icon {
  width: 55px;
  height: 55px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.venda-item-expanded.odonto .venda-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.venda-item-expanded.checkup .venda-icon {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
}

.venda-item-expanded.drcentral .venda-icon {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.venda-info h4 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 5px 0;
}

.categoria-desc {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.venda-metrics {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.venda-value-main {
  font-size: 3rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
}

.venda-details {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-label {
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 600;
  text-transform: uppercase;
}

.detail-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2c3e50;
}

.detail-value.success {
  color: #2ecc71;
}

/* Resumo de vendas */
.vendas-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 25px;
}

.summary-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 15px;
  padding: 25px;
  text-align: center;
}

.summary-card h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 15px 0;
  opacity: 0.9;
}

.summary-value {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.summary-trend {
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.summary-trend.positive {
  color: #a8ff9a;
}

.summary-trend i {
  font-size: 0.8rem;
}

/* Input de data melhorado */
.date-input {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  min-width: 180px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.date-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.date-input::-webkit-calendar-picker-indicator {
  background-color: #667eea;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  padding: 4px;
  margin-left: 8px;
}

/* Responsividade melhorada */
@media (max-width: 1200px) {
  .metrics-container .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
  }
  
  .vendas-expanded-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
  
  .colaborador-details-grid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
}

@media (max-width: 768px) {
  .header-modern-enhanced .header-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .header-modern-enhanced .header-left {
    flex-direction: column;
    gap: 15px;
  }
  
  .btn-voltar-premium {
    order: 2;
  }
  
  .header-title {
    order: 1;
  }
  
  .date-control-enhanced {
    align-items: center;
  }
  
  .colaborador-card-premium {
    padding: 20px;
  }
  
  .colaborador-details-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .metrics-container .metrics-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .vendas-expanded-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .metric-value {
    font-size: 2.2rem;
  }
  
  .venda-value-main {
    font-size: 2.5rem;
  }
  
  .date-input-premium {
    min-width: 180px;
    font-size: 0.9rem;
    padding: 10px 14px;
  }
}

@media (max-width: 480px) {
  .visao-meta {
    padding: 15px;
  }
  
  .header-modern-enhanced {
    padding: 20px 15px;
  }
  
  .colaborador-name {
    font-size: 1.6rem;
  }
  
  .detail-card {
    padding: 15px;
  }
  
  .metrics-container .metric-card {
    padding: 20px;
    min-height: 160px;
  }
  
  .venda-item-expanded {
    padding: 20px;
  }
  
  .metric-value {
    font-size: 2rem;
  }
  
  .venda-value-main {
    font-size: 2.2rem;
  }
  
  .venda-details {
    flex-direction: column;
    gap: 15px;
  }
  
  .summary-card {
    padding: 20px;
  }
}

.metric-content label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.metric-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1.25rem;
  font-weight: 600;
  transition: var(--transition);
  background: #f8fafc;
}

.metric-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.metric-display {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1e293b;
  background: white;
  padding: 0.875rem;
  border-radius: 10px;
  text-align: center;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
  border: 2px solid rgba(0,0,0,0.05);
}

/* Métricas diárias */
.daily-metrics {
  background: white;
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-light);
}

.daily-metrics h3 {
  margin: 0 0 1rem 0;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.daily-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.daily-item {
  text-align: center;
  padding: 1rem;
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border-radius: 12px;
  transition: var(--transition);
}

.daily-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-light);
}

.daily-label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.daily-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

/* Seções de conteúdo */
.section-card {
  background: white;
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
}

.section-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e2e8f0;
}

.section-header i {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.1rem;
}

.section-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

/* Seção Vendas */
.vendas .section-header i {
  background: var(--warning-gradient);
}

.vendas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.venda-item {
  background: linear-gradient(135deg, #fef3c7, #fbbf24);
  border-radius: 12px;
  padding: 1.25rem;
  transition: var(--transition);
  color: #92400e;
}

.venda-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-light);
}

.venda-item.odonto {
  background: linear-gradient(135deg, #ede9fe, #c4b5fd);
  color: #3730a3;
}

.venda-item.checkup {
  background: linear-gradient(135deg, #dbeafe, #93c5fd);
  color: #1e3a8a;
}

.venda-item.drcentral {
  background: linear-gradient(135deg, #d1fae5, #86efac);
  color: #14532d;
}

.venda-icon {
  width: 35px;
  height: 35px;
  border-radius: 8px;
  background: rgba(255,255,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
  color: inherit;
}

.venda-content label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  opacity: 0.9;
}

.venda-content input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 8px;
  background: rgba(255,255,255,0.8);
  font-size: 1.1rem;
  font-weight: 600;
  transition: var(--transition);
}

.venda-content input:focus {
  outline: none;
  border-color: rgba(255,255,255,0.6);
  background: white;
  box-shadow: 0 0 0 3px rgba(255,255,255,0.2);
}

.venda-value {
  background: white;
  padding: 0.875rem;
  border-radius: 8px;
  font-size: 1.25rem;
  font-weight: 700;
  text-align: center;
  color: inherit;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
  border: 2px solid rgba(255,255,255,0.5);
}

/* Seção Comissão */
.comissao .section-header i {
  background: var(--danger-gradient);
}

.comissao-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.comissao-item {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem;
  transition: var(--transition);
}

.comissao-item:hover {
  border-color: #cbd5e1;
  box-shadow: var(--shadow-light);
}

.comissao-item label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.comissao-item input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: var(--transition);
}

.comissao-item input:focus {
  outline: none;
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.comissao-value {
  background: white;
  padding: 0.875rem;
  border-radius: 8px;
  font-size: 1.125rem;
  font-weight: 600;
  text-align: center;
  color: #1e293b;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
  border: 2px solid #e2e8f0;
}

.comissao-total {
  grid-column: 1 / -1;
  background: linear-gradient(135deg, #fef3c7, #f59e0b);
  border: none;
  text-align: center;
  padding: 1.5rem;
}

.comissao-total label {
  color: #92400e !important;
  font-size: 1rem !important;
}

.total-value {
  font-size: 2rem;
  font-weight: 800;
  color: #92400e;
  margin-top: 0.5rem;
  background: white;
  padding: 0.75rem;
  border-radius: 8px;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
  border: 2px solid rgba(255,255,255,0.5);
}

/* Seção Projeções */
.projecoes .section-header i {
  background: var(--info-gradient);
}

.projecoes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.projecao-item {
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border: 2px solid #0ea5e9;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: var(--transition);
}

.projecao-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-light);
  background: linear-gradient(135deg, #e0f2fe, #bae6fd);
}

.projecao-item label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #0c4a6e;
  margin-bottom: 0.75rem;
}

.projecao-value {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0c4a6e;
  background: rgba(255,255,255,0.7);
  padding: 0.75rem;
  border-radius: 8px;
}

/* Responsividade */
@media (max-width: 1024px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .header-left {
    flex-direction: column;
    gap: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .vendas-grid,
  .comissao-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .dashboard-container {
    padding: 0.5rem;
  }
  
  .colaborador-card {
    flex-direction: column;
    text-align: center;
  }
  
  .daily-grid {
    grid-template-columns: 1fr;
  }
}
</style>
