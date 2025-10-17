<template>
  <div class="detalhamento-comissao">
    <!-- Botão para expandir detalhes -->
    <button @click="mostrarDetalhes = !mostrarDetalhes" class="btn-toggle-detalhes">
      <i :class="mostrarDetalhes ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      {{ mostrarDetalhes ? 'Ocultar Detalhes' : 'Ver Detalhes' }}
    </button>

    <!-- Painel expansível com detalhes -->
    <transition name="slide-fade">
      <div v-if="mostrarDetalhes" class="detalhes-panel">
        <div class="loading" v-if="carregando">
          <i class="fas fa-spinner fa-spin"></i> Carregando detalhes...
        </div>

        <div v-else-if="erro" class="erro-message">
          <i class="fas fa-exclamation-triangle"></i>
          {{ erro }}
        </div>

        <div v-else-if="dadosComissao" class="detalhes-content">
          <!-- Resumo Geral -->
          <div class="resumo-geral">
            <div class="stat-item">
              <span class="label">Total de Vendas:</span>
              <span class="value">{{ dadosComissao.total_procedimentos }}</span>
            </div>
            <div class="stat-item">
              <span class="label">Valor em Vendas:</span>
              <span class="value">{{ formatarMoeda(dadosComissao.total_vendas) }}</span>
            </div>
            <div class="stat-item">
              <span class="label">Comissão Total:</span>
              <span class="value destaque">{{ formatarMoeda(dadosComissao.total_comissao) }}</span>
            </div>
          </div>

          <!-- Breakdown por Categoria -->
          <div class="categorias-breakdown">
            <h4><i class="fas fa-chart-pie"></i> Comissão por Categoria</h4>
            
            <div
              v-for="categoria in dadosComissao.por_categoria"
              :key="categoria.categoria"
              class="categoria-card"
            >
              <div class="categoria-header">
                <div class="categoria-nome">
                  <i :class="getIconeCategoria(categoria.categoria)"></i>
                  {{ categoria.categoria }}
                </div>
                <div class="categoria-valores">
                  <span class="quantidade">{{ categoria.quantidade_vendas }} vendas</span>
                  <span class="comissao">{{ formatarMoeda(categoria.valor_total_comissao) }}</span>
                </div>
              </div>

              <!-- Barra de progresso -->
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: getPercentual(categoria.valor_total_comissao) + '%' }"
                ></div>
              </div>

              <div class="categoria-detalhes">
                <span>Valor vendas: {{ formatarMoeda(categoria.valor_total_vendas) }}</span>
              </div>
            </div>
          </div>

          <!-- Lista de Vendas (se disponível) -->
          <div v-if="mostrarListaVendas && vendasDetalhadas.length > 0" class="lista-vendas">
            <h4>
              <i class="fas fa-list"></i> Vendas Individuais
              <span class="contador">({{ vendasDetalhadas.length }})</span>
            </h4>
            
            <div class="tabela-vendas">
              <table>
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Procedimento</th>
                    <th>Grupo</th>
                    <th>Valor</th>
                    <th>Comissão</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(venda, index) in vendasLimitadas" :key="index">
                    <td>{{ formatarData(venda.data_agenda) }}</td>
                    <td class="descricao">{{ venda.descricao }}</td>
                    <td><span class="badge">{{ venda.grupo }}</span></td>
                    <td class="valor">{{ formatarMoeda(venda.valor_procedimento) }}</td>
                    <td class="comissao-valor">{{ formatarMoeda(venda.valor_comissao) }}</td>
                  </tr>
                </tbody>
              </table>

              <button
                v-if="vendasDetalhadas.length > limitVendas"
                @click="expandirVendas"
                class="btn-ver-mais"
              >
                Ver mais {{ vendasDetalhadas.length - limitVendas }} vendas
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
const API_BASE_URL = 'http://192.168.1.202:8000';

export default {
  name: 'DetalhamentoComissao',
  
  props: {
    idEyal: {
      type: String,
      required: true
    },
    mesRef: {
      type: String,
      default: null
    },
    mostrarListaVendas: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      mostrarDetalhes: false,
      carregando: false,
      erro: null,
      dadosComissao: null,
      limitVendas: 10
    };
  },

  computed: {
    vendasDetalhadas() {
      if (!this.dadosComissao || !this.dadosComissao.por_categoria) return [];
      
      // Juntar todas as vendas de todas categorias
      const todasVendas = [];
      this.dadosComissao.por_categoria.forEach(cat => {
        if (cat.vendas && cat.vendas.length > 0) {
          todasVendas.push(...cat.vendas);
        }
      });
      
      // Ordenar por data (mais recente primeiro)
      return todasVendas.sort((a, b) => {
        if (!a.data_agenda) return 1;
        if (!b.data_agenda) return -1;
        return new Date(b.data_agenda) - new Date(a.data_agenda);
      });
    },

    vendasLimitadas() {
      return this.vendasDetalhadas.slice(0, this.limitVendas);
    }
  },

  watch: {
    mostrarDetalhes(novoValor) {
      if (novoValor && !this.dadosComissao) {
        this.carregarDetalhes();
      }
    },

    mesRef() {
      // Recarregar se o mês mudar
      if (this.mostrarDetalhes) {
        this.carregarDetalhes();
      }
    }
  },

  methods: {
    async carregarDetalhes() {
      this.carregando = true;
      this.erro = null;

      try {
        const mesRef = this.mesRef || new Date().toISOString().slice(0, 7);
        const incluirDetalhes = this.mostrarListaVendas ? 'true' : 'false';
        const url = `${API_BASE_URL}/comissao/colaborador/${this.idEyal}?mes_ref=${mesRef}&incluir_detalhes=${incluirDetalhes}`;
        
        console.log('🔍 Carregando detalhes de comissão:', url);
        
        const response = await fetch(url);

        if (!response.ok) {
          throw new Error(`Erro ${response.status}: ${await response.text()}`);
        }

        this.dadosComissao = await response.json();
        console.log('✅ Detalhes carregados:', this.dadosComissao);

      } catch (error) {
        console.error('❌ Erro ao carregar detalhes:', error);
        this.erro = 'Não foi possível carregar os detalhes da comissão';
      } finally {
        this.carregando = false;
      }
    },

    expandirVendas() {
      this.limitVendas += 20;
    },

    getPercentual(valor) {
      if (!this.dadosComissao || this.dadosComissao.total_comissao === 0) return 0;
      return (valor / this.dadosComissao.total_comissao) * 100;
    },

    getIconeCategoria(categoria) {
      const categoriaLower = categoria.toLowerCase();
      if (categoriaLower.includes('odonto')) return 'fas fa-tooth';
      if (categoriaLower.includes('check')) return 'fas fa-notes-medical';
      if (categoriaLower.includes('baby')) return 'fas fa-baby';
      if (categoriaLower.includes('central')) return 'fas fa-hospital';
      return 'fas fa-file-medical';
    },

    formatarMoeda(valor) {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(valor || 0);
    },

    formatarData(data) {
      if (!data) return '-';
      return new Date(data).toLocaleDateString('pt-BR');
    }
  }
};
</script>

<style scoped>
.detalhamento-comissao {
  margin-top: 15px;
}

.btn-toggle-detalhes {
  width: 100%;
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.btn-toggle-detalhes:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.detalhes-panel {
  margin-top: 15px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
}

.erro-message {
  text-align: center;
  padding: 20px;
  color: #e74c3c;
  background: #ffe8e6;
  border-radius: 8px;
}

/* Resumo Geral */
.resumo-geral {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-item .label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.stat-item .value {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.stat-item .value.destaque {
  color: #27ae60;
  font-size: 24px;
}

/* Categorias */
.categorias-breakdown h4 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 15px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.categoria-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 12px;
}

.categoria-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.categoria-nome {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.categoria-valores {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.categoria-valores .quantidade {
  font-size: 12px;
  color: #666;
}

.categoria-valores .comissao {
  font-size: 16px;
  font-weight: 700;
  color: #27ae60;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.6s ease;
}

.categoria-detalhes {
  font-size: 12px;
  color: #666;
}

/* Lista de Vendas */
.lista-vendas {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
}

.lista-vendas h4 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 15px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.contador {
  font-size: 14px;
  color: #666;
  font-weight: 400;
}

.tabela-vendas {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

thead {
  background: #f8f9fa;
}

thead th {
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #dee2e6;
}

tbody tr {
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s ease;
}

tbody tr:hover {
  background: #f8f9fa;
}

tbody td {
  padding: 12px 10px;
  color: #333;
}

.descricao {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.valor {
  text-align: right;
  font-weight: 600;
}

.comissao-valor {
  text-align: right;
  font-weight: 700;
  color: #27ae60;
}

.btn-ver-mais {
  margin-top: 15px;
  padding: 10px 20px;
  background: white;
  border: 2px solid #667eea;
  border-radius: 6px;
  color: #667eea;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-ver-mais:hover {
  background: #667eea;
  color: white;
}

/* Animações */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
