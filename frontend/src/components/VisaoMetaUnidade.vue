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
            <div class="kpi-value">{{ formatarMoeda(dadosUnidade.metaTotal) }}</div>
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
            <div class="kpi-value">{{ formatarMoeda(dadosUnidade.totalRealizado) }}</div>
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
<!--
       Rankings por Categoria
      <div class="rankings-section">
        <h3 class="section-title">
          <i class="fas fa-medal"></i>
          Rankings por Categoria
        </h3>
        <div class="rankings-grid">
           Ranking Odonto
          <div class="ranking-card odonto">
            <div class="ranking-header">
              <div class="ranking-icon">
                <i class="fas fa-tooth"></i>
              </div>
              <h4>Top Odonto</h4>
              <div class="categoria-stats">
                <span class="quantidade">{{ rankingOdonto.length }} procedimentos</span>
                <span class="total-categoria">Total: {{ formatarMoeda(totaisPorCategoria.odonto) }}</span>
              </div>
            </div>
            <div class="ranking-list">
              <div v-for="(item, index) in rankingOdonto" :key="index" class="ranking-item">
                <span class="posicao">{{ item.posicao || (index + 1) }}º</span>
                <div class="vendedor-info">
                  <span class="nome-vendedor">{{ item.nome }}</span>
                  <span class="unidade-vendedor">{{ item.unidade }}</span>
                  <div class="stats-vendedor">
                    <span class="quantidade">{{ item.quantidade || 0 }} procedimentos</span>
                    <span class="valor">{{ item.valor_formatado || formatarMoeda(item.valor) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

           Ranking Exames
          <div class="ranking-card exames">
            <div class="ranking-header">
              <div class="ranking-icon">
                <i class="fas fa-vials"></i>
              </div>
              <h4>Top Exames</h4>
              <div class="categoria-stats">
                <span class="quantidade">{{ rankingExames.length }} procedimentos</span>
                <span class="total-categoria">Total: {{ formatarMoeda(totaisPorCategoria.exames) }}</span>
              </div>
            </div>
            <div class="ranking-list">
              <div v-for="(item, index) in rankingExames" :key="index" class="ranking-item">
                <span class="posicao">{{ item.posicao || (index + 1) }}º</span>
                <div class="vendedor-info">
                  <span class="nome-vendedor">{{ item.nome }}</span>
                  <span class="unidade-vendedor">{{ item.unidade }}</span>
                  <div class="stats-vendedor">
                    <span class="quantidade">{{ item.quantidade || 0 }} exames</span>
                    <span class="valor">{{ item.valor_formatado || formatarMoeda(item.valor) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

           Ranking Consultas
          <div class="ranking-card consultas">
            <div class="ranking-header">
              <div class="ranking-icon">
                <i class="fas fa-stethoscope"></i>
              </div>
              <h4>Top Consultas</h4>
              <div class="categoria-stats">
                <span class="quantidade">{{ rankingConsultas.length }} procedimentos</span>
                <span class="total-categoria">Total: {{ formatarMoeda(totaisPorCategoria.consultas) }}</span>
              </div>
            </div>
            <div class="ranking-list">
              <div v-for="(item, index) in rankingConsultas" :key="index" class="ranking-item">
                <span class="posicao">{{ item.posicao || (index + 1) }}º</span>
                <div class="vendedor-info">
                  <span class="nome-vendedor">{{ item.nome }}</span>
                  <span class="unidade-vendedor">{{ item.unidade }}</span>
                  <div class="stats-vendedor">
                    <span class="quantidade">{{ item.quantidade || 0 }} consultas</span>
                    <span class="valor">{{ item.valor_formatado || formatarMoeda(item.valor) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

           Ranking Checkups
          <div class="ranking-card checkups">
            <div class="ranking-header">
              <div class="ranking-icon">
                <i class="fas fa-heart-pulse"></i>
              </div>
              <h4>Top Checkups</h4>
              <div class="categoria-stats">
                <span class="quantidade">{{ rankingCheckup.length }} procedimentos</span>
                <span class="total-categoria">Total: {{ formatarMoeda(totaisPorCategoria.checkup) }}</span>
              </div>
            </div>
            <div class="ranking-list">
              <div v-for="(item, index) in rankingCheckup" :key="index" class="ranking-item">
                <span class="posicao">{{ item.posicao || (index + 1) }}º</span>
                <div class="vendedor-info">
                  <span class="nome-vendedor">{{ item.nome }}</span>
                  <span class="unidade-vendedor">{{ item.unidade }}</span>
                  <div class="stats-vendedor">
                    <span class="quantidade">{{ item.quantidade || 0 }} checkups</span>
                    <span class="valor">{{ item.valor_formatado || formatarMoeda(item.valor) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

           Ranking BabyClick
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
    -->
      <!-- Tabela Detalhada de Colaboradores -->
      <div class="colaboradores-detalhados-section">
        <h3 class="section-title">
          <i class="fas fa-users-cog"></i>
          Colaboradores da Unidade - Visão Detalhada
        </h3>

        <!-- Loading -->
        <div v-if="carregandoColaboradores" class="loading-colaboradores">
          <div class="spinner"></div>
          <p>Carregando colaboradores...</p>
        </div>

        <!-- Tabela de Colaboradores -->
        <div v-else-if="colaboradoresDetalhados.length > 0" class="tabela-colaboradores-container">
          <div class="tabela-colaboradores-wrapper">
            <table class="tabela-colaboradores">
              <thead>
                <tr>
                  <th class="col-nome">
                    <i class="fas fa-user"></i>
                    Nome
                  </th>
                  <th class="col-cargo">
                    <i class="fas fa-briefcase"></i>
                    Cargo
                  </th>
                  <th class="col-meta">
                    <i class="fas fa-bullseye"></i>
                    Meta Total
                  </th>
                  <th class="col-realizado">
                    <i class="fas fa-chart-line"></i>
                    Realizado
                  </th>
                  <th class="col-saldo">
                    <i class="fas fa-balance-scale"></i>
                    Saldo
                  </th>
                  <th class="col-percentual">
                    <i class="fas fa-percent"></i>
                    % Atual
                  </th>
                  <th class="col-projecao">
                    <i class="fas fa-chart-area"></i>
                    Projeção
                  </th>
                  <th class="col-nps">
                    <i class="fas fa-star"></i>
                    NPS
                  </th>
                  <th class="col-vendas">
                    <i class="fas fa-shopping-cart"></i>
                    Vendas
                  </th>
                  <th class="col-comissao">
                    <i class="fas fa-dollar-sign"></i>
                    Comissão
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(colab, index) in colaboradoresDetalhados" :key="colab.id_eyal"
                    :class="{ 'linha-destaque': index < 3 }">
                  <td class="col-nome">
                    <div class="colaborador-nome">
                      <span class="nome-principal">{{ colab.nome }}</span>
                      <span class="id-eyal">ID: {{ colab.id_eyal }}</span>
                    </div>
                  </td>
                  <td class="col-cargo">
                    <span class="badge-cargo">{{ colab.cargo }}</span>
                  </td>
                  <td class="col-meta">
                    <span class="valor-destaque">{{ formatarMoeda(colab.meta_total) }}</span>
                    <span class="valor-secundario">Diária: {{ formatarMoeda(colab.meta_diaria) }}</span>
                  </td>
                  <td class="col-realizado">
                    <span class="valor-destaque positivo">{{ formatarMoeda(colab.realizado) }}</span>
                  </td>
                  <td class="col-saldo">
                    <span :class="['valor-destaque', colab.saldo >= 0 ? 'positivo' : 'negativo']">
                      {{ formatarMoeda(colab.saldo) }}
                    </span>
                  </td>
                  <td class="col-percentual">
                    <div class="percentual-wrapper">
                      <span :class="['percentual-valor', getClassePercentual(colab.percentual_atual)]">
                        {{ colab.percentual_atual.toFixed(1) }}%
                      </span>
                      <div class="mini-progress-bar">
                        <div class="mini-progress-fill"
                             :style="{ width: Math.min(colab.percentual_atual, 100) + '%' }"
                             :class="getClassePercentual(colab.percentual_atual)"></div>
                      </div>
                    </div>
                  </td>
                  <td class="col-projecao">
                    <span class="valor-destaque">{{ formatarMoeda(colab.previsao_atingimento) }}</span>
                    <span class="valor-secundario">{{ (colab.percentual_projetado || 0).toFixed(1) }}%</span>
                  </td>
                  <td class="col-nps">
                    <span :class="['nps-valor', getClasseNPS(Number(colab.nps))]">
                      {{ Number(colab.nps || 0).toFixed(0) }}
                    </span>
                  </td>
                  <td class="col-vendas">
                    <div class="vendas-detalhes">
                      <span class="venda-item">O: {{ colab.vendas.odonto }}</span>
                      <span class="venda-item">ORC: {{ colab.vendas.marcuz }}</span>
                      <span class="venda-item">C: {{ colab.vendas.checkup }}</span>
                      <span class="venda-total">Total: {{ colab.vendas.total }}</span>
                    </div>
                  </td>
                  <td class="col-comissao">
                    <span class="valor-destaque comissao">{{ formatarMoeda(colab.comissao.total) }}</span>
                    <span class="valor-secundario">Prod: {{ formatarMoeda(colab.comissao.valor_pago_producao) }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Resumo da Tabela -->
          <div class="tabela-resumo">
            <div class="resumo-item">
              <i class="fas fa-users"></i>
              <span>{{ colaboradoresDetalhados.length }} colaboradores</span>
            </div>
            <div class="resumo-item">
              <i class="fas fa-bullseye"></i>
              <span>Meta Total: {{ formatarMoeda(totalMetaColaboradores) }}</span>
            </div>
            <div class="resumo-item">
              <i class="fas fa-chart-line"></i>
              <span>Realizado Total: {{ formatarMoeda(totalRealizadoColaboradores) }}</span>
            </div>
            <div class="resumo-item">
              <i class="fas fa-percent"></i>
              <span>Média: {{ mediaPercentualColaboradores.toFixed(1) }}%</span>
            </div>
          </div>
        </div>

        <!-- Estado vazio -->
        <div v-else class="colaboradores-vazio">
          <i class="fas fa-users-slash"></i>
          <p>Nenhum colaborador encontrado para esta unidade no período selecionado.</p>
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
    // Calcular mês atual no formato YYYY-MM
    const dataAtual = new Date();
    const mesAtual = `${dataAtual.getFullYear()}-${String(dataAtual.getMonth() + 1).padStart(2, '0')}`;
    
    return {
      carregando: false,
      unidadeSelecionada: '',
      dataFiltro: mesAtual, // Formato YYYY-MM - mês atual automaticamente
      
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
      rankingExames: [],
      rankingConsultas: [],
      rankingCheckup: [],
      rankingDrCentral: [],
      rankingBabyclick: [],
      
      // Totais por categoria
      totaisPorCategoria: {
        odonto: 0,
        exames: 0,
        consultas: 0,
        checkup: 0,
        drCentral: 0,
        babyclick: 0
      },

      // Colaboradores detalhados
      colaboradoresDetalhados: [],
      carregandoColaboradores: false
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
    },

    // Computed properties para a tabela de colaboradores
    totalMetaColaboradores() {
      return this.colaboradoresDetalhados.reduce((sum, c) => sum + (c.meta_total || 0), 0);
    },
    totalRealizadoColaboradores() {
      return this.colaboradoresDetalhados.reduce((sum, c) => sum + (c.realizado || 0), 0);
    },
    mediaPercentualColaboradores() {
      if (this.colaboradoresDetalhados.length === 0) return 0;
      const soma = this.colaboradoresDetalhados.reduce((sum, c) => sum + (c.percentual_atual || 0), 0);
      return soma / this.colaboradoresDetalhados.length;
    }
  },
  mounted() {
    this.carregarDadosUnidade();
    this.carregarColaboradoresDetalhados();
  },
  methods: {
    async carregarDadosUnidade() {
      this.carregando = true;
      try {
        // Buscar dados reais da API usando o mês atual (dataFiltro)
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/metas-unidades-real/dashboard?mes_ref=${this.dataFiltro}`);
        
        if (!response.ok) {
          throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Dados reais recebidos da API:', data);
        
        // Atualizar dados da unidade com dados reais
        if (data.resumo) {
          this.dadosUnidade = {
            totalColaboradores: data.resumo.total_colaboradores || 0,
            metaTotal: data.resumo.meta_total || 0,
            totalRealizado: data.resumo.realizado_total || 0
          };
          
          // Atualizar totais por categoria com dados reais da API
          if (data.resumo.totais_por_categoria) {
            this.totaisPorCategoria = {
              odonto: data.resumo.totais_por_categoria.odonto.valor,
              exames: data.resumo.totais_por_categoria.exames.valor,
              consultas: data.resumo.totais_por_categoria.consultas.valor
            };
          }
        }
        
        // Buscar unidades disponíveis da API real
        if (data.unidades && data.unidades.length > 0) {
          const unidadesUnicas = [...new Set(data.unidades.map(u => u.unidade))];
          this.unidades = unidadesUnicas.map((nome, index) => ({
            id: index + 1,
            nome: nome
          }));
        }
        
        // Carregar rankings reais
        await this.carregarRankings();
        
      } catch (error) {
        console.error('Erro ao carregar dados da unidade:', error);
        
        // Em caso de erro, usar dados padrão
        this.dadosUnidade = {
          totalColaboradores: 0,
          metaTotal: 0,
          totalRealizado: 0
        };
      } finally {
        this.carregando = false;
      }
    },
    
    async atualizarDados() {
      console.log('Atualizando dados para unidade:', this.unidadeSelecionada, 'período:', this.dataFiltro);
      this.carregando = true;

      // Limpa o estado dos dados antes de atualizar
      this.dadosUnidade = { totalColaboradores: 0, metaTotal: 0, totalRealizado: 0 };
      this.colaboradoresDetalhados = [];

      try {
        // Sempre usa o mês de referência atual do filtro
        const mesRef = this.dataFiltro;
        let url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/metas-unidades-real/dashboard?mes_ref=${mesRef}`;

        const response = await fetch(url);

        if (response.ok) {
          const data = await response.json();
          console.log('Dados atualizados da API real:', data);

          // Atualizar dados da unidade
          if (data.resumo) {
            this.dadosUnidade = {
              totalColaboradores: data.resumo.total_unidades || 0,
              metaTotal: data.resumo.meta_total || 0,
              totalRealizado: data.resumo.realizado_total || 0
            };
          }

          // Se uma unidade específica foi selecionada, filtrar os dados
          if (this.unidadeSelecionada && data.unidades) {
            const unidadeNome = this.unidades.find(u => u.id == this.unidadeSelecionada)?.nome;
            const unidadeData = data.unidades.find(u => u.unidade === unidadeNome);

            if (unidadeData) {
              this.dadosUnidade = {
                totalColaboradores: 1, // Uma unidade específica
                metaTotal: unidadeData.meta || 0,
                totalRealizado: unidadeData.realizado || 0
              };
            }
          }

          // Atualizar unidades disponíveis
          if (data.unidades && data.unidades.length > 0) {
            const unidadesUnicas = [...new Set(data.unidades.map(u => u.unidade))];
            this.unidades = unidadesUnicas.map((nome, index) => ({
              id: index + 1,
              nome: nome
            }));
          }

          // Carregar rankings e colaboradores detalhados usando o mesmo mês de referência
          await this.carregarRankings();
          await this.carregarColaboradoresDetalhados();

        } else {
          console.error('Erro na resposta da API:', response.status, response.statusText);
          await this.carregarDadosUnidade(); // Fallback para dados gerais
        }

      } catch (error) {
        console.error('Erro ao atualizar dados:', error);
        await this.carregarDadosUnidade(); // Fallback para dados gerais
      } finally {
        this.carregando = false;
      }
    },
    
    async carregarRankings() {
      try {
        // Construir URL com filtros para o novo endpoint
        let url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/metas-unidades-real/rankings-top10?mes_ref=${this.dataFiltro}`;
        
        // Adicionar filtro de unidade se selecionada
        if (this.unidadeSelecionada && this.unidadeSelecionada !== 'Todas') {
          const unidadeNome = this.unidades.find(u => u.id == this.unidadeSelecionada)?.nome;
          if (unidadeNome) {
            url += `&unidade=${encodeURIComponent(unidadeNome)}`;
          }
        }
        
        console.log('🏆 Carregando rankings reais da URL:', url);
        const response = await fetch(url);
        
        if (response.ok) {
          const data = await response.json();
          console.log('🏆 Rankings reais recebidos:', data);
          
          // Limpar rankings existentes
          this.rankingOdonto = [];
          this.rankingExames = [];
          this.rankingConsultas = [];
          this.rankingCheckup = [];
          
          // Processar rankings por categoria
          if (data.rankings && Array.isArray(data.rankings)) {
            data.rankings.forEach(categoria => {
              console.log(`🏆 Processando categoria: ${categoria.categoria} (${categoria.vendedores?.length || 0} vendedores)`);
              
              switch (categoria.categoria?.toUpperCase()) {
                case 'ODONTO':
                  this.rankingOdonto = categoria.vendedores || [];
                  break;
                case 'EXAMES':
                  this.rankingExames = categoria.vendedores || [];
                  break;
                case 'CONSULTAS':
                  this.rankingConsultas = categoria.vendedores || [];
                  break;
                case 'CHECKUPS':
                  this.rankingCheckup = categoria.vendedores || [];
                  break;
                default:
                  console.warn(`🏆 Categoria não reconhecida: ${categoria.categoria}`);
              }
            });
            
            console.log('🏆 Rankings carregados com dados reais:', {
              odonto: this.rankingOdonto.length,
              exames: this.rankingExames.length,
              consultas: this.rankingConsultas.length,
              checkups: this.rankingCheckup.length
            });
          } else {
            console.warn('🏆 Nenhum ranking encontrado na resposta');
          }
        } else {
          console.error('🏆 Erro na resposta da API de rankings:', response.status, response.statusText);
          // Manter rankings vazios em caso de erro
        }
        
      } catch (error) {
        console.error('🏆 Erro ao carregar rankings:', error);
        // Manter rankings vazios em caso de erro
      }
    },
    
    carregarRankingsSimulados() {
      this.rankingOdonto = [
        { nome: 'VANESSA SOUZA GUIMARAES', quantidade: 47, valor: 30683.70, unidade: 'DR. FLORES 47' },
        { nome: 'Maria Silva', quantidade: 35, valor: 25000, unidade: 'CANOAS' },
        { nome: 'João Santos', quantidade: 28, valor: 22000, unidade: 'CENTRAL DE MARCAÇÕES' },
        { nome: 'Ana Costa', quantidade: 22, valor: 18500, unidade: 'ASSIS BRASIL 3044' }
      ];
      this.rankingExames = [
        { nome: 'Fernanda Oliveira', quantidade: 52, valor: 35200, unidade: 'ASSIS BRASIL 3044' },
        { nome: 'Ricardo Pereira', quantidade: 48, valor: 32800, unidade: 'GRAVATAI' },
        { nome: 'Lucia Santos', quantidade: 41, valor: 28600, unidade: 'CANOAS' },
        { nome: 'Pedro Lima', quantidade: 38, valor: 26400, unidade: 'DR. FLORES 47' }
      ];
      this.rankingConsultas = [
        { nome: 'Carla Mendes', quantidade: 65, valor: 19500, unidade: 'DR. FLORES 47' },
        { nome: 'Roberto Silva', quantidade: 58, valor: 17400, unidade: 'CANOAS' },
        { nome: 'Marina Costa', quantidade: 52, valor: 15600, unidade: 'ASSIS BRASIL 3044' },
        { nome: 'Antonio Pereira', quantidade: 47, valor: 14100, unidade: 'GRAVATAI' }
      ];
        this.rankingCheckup = [
          { nome: 'Ana Silva', quantidade: 8, valor: 15000, unidade: 'CENTRO DE CURITIBA' },
          { nome: 'Carlos Santos', quantidade: 6, valor: 12000, unidade: 'GRAVATAI' },
          { nome: 'Mariana Costa', quantidade: 4, valor: 8000, unidade: 'ASSIS BRASIL 3044' },
          { nome: 'Felipe Nunes', quantidade: 10, valor: 25000, unidade: 'GRAVATAI' }
        ];      // Atualizar totais por categoria
      this.totaisPorCategoria = {
        odonto: this.rankingOdonto.reduce((sum, item) => sum + item.valor, 0),
        exames: this.rankingExames.reduce((sum, item) => sum + item.valor, 0),
        consultas: this.rankingConsultas.reduce((sum, item) => sum + item.valor, 0),
        checkup: this.rankingCheckup.reduce((sum, item) => sum + item.valor, 0),
        drCentral: 0,
        babyclick: 0
      };
    },

    async carregarColaboradoresDetalhados() {
      this.carregandoColaboradores = true;
      try {
        const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

        // Buscar colaboradores com metas
        console.log('📋 Carregando colaboradores com metas...');
        const response = await fetch(`${API_BASE_URL}/metas/colaboradores-com-metas`);

        if (!response.ok) {
          console.error('❌ Erro ao buscar colaboradores:', response.status);
          this.colaboradoresDetalhados = [];
          return;
        }

        let colaboradores = await response.json();
        console.log('📋 Total de colaboradores com metas:', colaboradores.length);

        // Filtrar por unidade se selecionada
        if (this.unidadeSelecionada) {
          const unidadeNome = this.unidades.find(u => u.id == this.unidadeSelecionada)?.nome;
          if (unidadeNome) {
            colaboradores = colaboradores.filter(c => c.unidade === unidadeNome);
            console.log(`📋 Colaboradores filtrados para unidade "${unidadeNome}":`, colaboradores.length);
          }
        }

        // Para cada colaborador, buscar dados detalhados e aproveitar todos os campos do endpoint
        const colaboradoresDetalhados = [];

        for (const colab of colaboradores) {
          try {
            const idEyal = colab.id_eyal;
            if (!idEyal) continue;

            let mesRef = this.dataFiltro || '';
            if (mesRef && mesRef.length === 7) {
              mesRef = `${mesRef}-01`;
            }

            // Realizado
            const urlRealizado = `${API_BASE_URL}/realizado/painel/${idEyal}${mesRef ? `?mes_ref=${mesRef}` : ''}`;
            const respRealizado = await fetch(urlRealizado);
            let data = respRealizado.ok ? await respRealizado.json() : {};


            // Buscar meta individual do colaborador para o mes_ref atual
            let metaTotal = 0;
            let metaDiaria = 0;
            const urlMeta = `${API_BASE_URL}/metas/colaborador/${idEyal}?mes_ref=${mesRef}`;
            const respMeta = await fetch(urlMeta);
            if (respMeta.ok) {
              const metaData = await respMeta.json();
              if (Array.isArray(metaData) && metaData.length > 0) {
                metaTotal = metaData[0].meta_final || 0;
                metaDiaria = metaData[0].meta_diaria || 0;
              }
            }

            // Projeção (usa realizado_final e percentual, ou calcula se necessário)
            let projecao = 0;
            if (data.realizado?.realizado_final && data.realizado?.percentual_atingido) {
              projecao = data.realizado.realizado_final / (data.realizado.percentual_atingido / 100);
            }

            // NPS
            let nps = 0;
            const urlNPS = `${API_BASE_URL}/nps/colaborador/${idEyal}?mes_ref=${mesRef.substring(0,7)}`;
            const respNPS = await fetch(urlNPS);
            if (respNPS.ok) {
              const npsData = await respNPS.json();
              if (npsData.success && npsData.nps_data && npsData.nps_data.nps !== null) {
                nps = Number(npsData.nps_data.nps).toFixed(2);
              } else {
                nps = 0;
              }
            }

            // Vendas
            let vendas = { odonto: 0, marcuz: 0, checkup: 0, total: 0 };
            const urlVendas = `${API_BASE_URL}/vendas/colaborador/${idEyal}?mes_ref=${mesRef.substring(0,7)}`;
            const respVendas = await fetch(urlVendas);
            if (respVendas.ok) {
              const vendasData = await respVendas.json();
              if (vendasData.success && vendasData.resumo) {
                vendas = {
                  odonto: vendasData.resumo.odonto || 0,
                  marcuz: vendasData.resumo.marcuz || 0,
                  checkup: vendasData.resumo.checkup || 0,
                  total: vendasData.resumo.total_vendas || 0
                };
              }
            }

            // Comissão
            let comissao = { total: 0, valor_pago_producao: 0 };
            const urlComissao = `${API_BASE_URL}/comissao/resumo/${idEyal}?mes_ref=${mesRef}`;
            const respComissao = await fetch(urlComissao);
            if (respComissao.ok) {
              const comissaoData = await respComissao.json();
              comissao = {
                total: comissaoData.total_comissao || 0,
                valor_pago_producao: comissaoData.projecao_meta || 0
              };
            }

            colaboradoresDetalhados.push({
              id_eyal: data.colaborador?.id_eyal || idEyal,
              nome: data.colaborador?.nome || colab.nome,
              cargo: data.colaborador?.cargo || colab.cargo || 'Não informado',
              unidade: data.colaborador?.unidade || colab.unidade || '',
              meta_total: metaTotal,
              meta_diaria: metaDiaria,
              realizado: data.realizado?.realizado_final || 0,
              realizado_individual: data.realizado?.realizado_individual || 0,
              saldo: (data.realizado?.realizado_final || 0) - metaTotal,
              percentual_atual: data.realizado?.percentual_atingido || 0,
              projecao: projecao,
              nps: nps,
              vendas: vendas,
              comissao: comissao,
              nivel: data.colaborador?.nivel || '',
              lider_direto: data.colaborador?.lider_direto || ''
            });
          } catch (error) {
            console.error(`❌ Erro ao processar colaborador ${colab.nome}:`, error);
          }
        }

        this.colaboradoresDetalhados = colaboradoresDetalhados;
        console.log(`✅ ${this.colaboradoresDetalhados.length} colaboradores carregados com dados detalhados`);

          // Pós-processamento: calcular previsao_atingimento e percentual_projetado para cada colaborador
          this.colaboradoresDetalhados = this.colaboradoresDetalhados.map(colab => {
            // Previsao Atingimento: se não veio do backend, calcula
            let previsao_atingimento = 0;
            if (colab.realizado && colab.percentual_atual) {
              // Mesma lógica do MetaColaborador.vue
              previsao_atingimento = colab.percentual_atual > 0
                ? (colab.realizado / (colab.percentual_atual / 100))
                : colab.realizado;
            }
            // Se já veio do backend, prioriza
            if (colab.projecao && colab.projecao > 0) {
              previsao_atingimento = colab.projecao;
            }

            // Percentual Projetado: (previsao_atingimento / meta_total) * 100
            let percentual_projetado = 0;
            if (colab.meta_total && colab.meta_total > 0) {
              percentual_projetado = (previsao_atingimento / colab.meta_total) * 100;
            }

            return {
              ...colab,
              previsao_atingimento,
              percentual_projetado
            };
          });

      } catch (error) {
        console.error('❌ Erro ao carregar colaboradores detalhados:', error);
        this.colaboradoresDetalhados = [];
      } finally {
        this.carregandoColaboradores = false;
      }
    },

    getClassePercentual(percentual) {
      if (percentual >= 100) return 'excelente';
      if (percentual >= 80) return 'bom';
      if (percentual >= 60) return 'regular';
      return 'critico';
    },

    getClasseNPS(nps) {
      if (nps >= 75) return 'excelente';
      if (nps >= 50) return 'bom';
      if (nps >= 0) return 'regular';
      return 'critico';
    },

    formatarMoeda(valor) {
      if (typeof valor !== 'number') return 'R$ 0,00';
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(valor);
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
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.ranking-header > div:first-child {
  display: flex;
  align-items: center;
  gap: 15px;
}

.ranking-header h4 {
  flex: 1;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #2c3e50;
}

.categoria-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.quantidade {
  color: #667eea;
  font-weight: 600;
  background: rgba(102, 126, 234, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
}

.total-categoria {
  color: #28a745;
  font-weight: 700;
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

.ranking-card.exames .ranking-icon {
  background: linear-gradient(135deg, #17a2b8, #138496);
}

.ranking-card.consultas .ranking-icon {
  background: linear-gradient(135deg, #28a745, #1e7e34);
}

.ranking-card.checkups .ranking-icon {
  background: linear-gradient(135deg, #dc3545, #c82333);
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
  flex-shrink: 0;
}

.colaborador-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nome {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.unidade {
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 500;
}

.valor {
  font-weight: 700;
  color: #667eea;
  font-size: 1.1rem;
}

/* Estilos para vendedores */
.vendedor-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nome-vendedor {
  font-weight: 600;
  font-size: 14px;
  color: #212529;
  line-height: 1.2;
}

.unidade-vendedor {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

.stats-vendedor {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.stats-vendedor .quantidade {
  font-size: 12px;
  color: #28a745;
  font-weight: 600;
  background: rgba(40, 167, 69, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.stats-vendedor .valor {
  font-weight: 700;
  font-size: 14px;
  color: #007bff;
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

/* Tabela de Colaboradores Detalhados */
.colaboradores-detalhados-section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
}

.loading-colaboradores {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #667eea;
}

.loading-colaboradores .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e9ecef;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.colaboradores-vazio {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6c757d;
}

.colaboradores-vazio i {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.3;
}

.tabela-colaboradores-container {
  margin-top: 20px;
}

.tabela-colaboradores-wrapper {
  overflow-x: auto;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.tabela-colaboradores {
  width: 100%;
  border-collapse: collapse;
  background: white;
  font-size: 0.9rem;
}

.tabela-colaboradores thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.tabela-colaboradores thead th {
  padding: 15px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.tabela-colaboradores thead th i {
  margin-right: 6px;
  font-size: 0.9rem;
}

.tabela-colaboradores tbody tr {
  border-bottom: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.tabela-colaboradores tbody tr:hover {
  background: #f8f9fa;
  transform: translateX(2px);
}

.tabela-colaboradores tbody tr.linha-destaque {
  background: rgba(102, 126, 234, 0.05);
}

.tabela-colaboradores tbody tr.linha-destaque:hover {
  background: rgba(102, 126, 234, 0.1);
}

.tabela-colaboradores tbody td {
  padding: 15px 12px;
  vertical-align: middle;
}

/* Colunas específicas */
.col-nome {
  min-width: 200px;
  max-width: 250px;
}

.colaborador-nome {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nome-principal {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.id-eyal {
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 500;
}

.col-cargo {
  min-width: 150px;
}

.badge-cargo {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block;
}

.col-meta,
.col-realizado,
.col-saldo,
.col-projecao,
.col-comissao {
  min-width: 130px;
}

.valor-destaque {
  display: block;
  font-weight: 700;
  font-size: 1rem;
  color: #2c3e50;
  margin-bottom: 2px;
}

.valor-destaque.positivo {
  color: #28a745;
}

.valor-destaque.negativo {
  color: #dc3545;
}

.valor-destaque.comissao {
  color: #667eea;
}

.valor-secundario {
  display: block;
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 500;
}

.col-percentual {
  min-width: 140px;
}

.percentual-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.percentual-valor {
  font-weight: 700;
  font-size: 1.1rem;
}

.percentual-valor.excelente {
  color: #28a745;
}

.percentual-valor.bom {
  color: #17a2b8;
}

.percentual-valor.regular {
  color: #ffc107;
}

.percentual-valor.critico {
  color: #dc3545;
}

.mini-progress-bar {
  height: 6px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.6s ease;
}

.mini-progress-fill.excelente {
  background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
}

.mini-progress-fill.bom {
  background: linear-gradient(90deg, #17a2b8 0%, #138496 100%);
}

.mini-progress-fill.regular {
  background: linear-gradient(90deg, #ffc107 0%, #ffb300 100%);
}

.mini-progress-fill.critico {
  background: linear-gradient(90deg, #dc3545 0%, #c82333 100%);
}

.col-nps {
  min-width: 80px;
  text-align: center;
}

.nps-valor {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 1.1rem;
}

.nps-valor.excelente {
  background: rgba(40, 167, 69, 0.15);
  color: #28a745;
}

.nps-valor.bom {
  background: rgba(23, 162, 184, 0.15);
  color: #17a2b8;
}

.nps-valor.regular {
  background: rgba(255, 193, 7, 0.15);
  color: #ffc107;
}

.nps-valor.critico {
  background: rgba(220, 53, 69, 0.15);
  color: #dc3545;
}

.col-vendas {
  min-width: 180px;
}

.vendas-detalhes {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.venda-item {
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 500;
}

.venda-total {
  font-weight: 700;
  color: #2c3e50;
  font-size: 0.85rem;
  margin-top: 4px;
  padding-top: 4px;
  border-top: 1px solid #e9ecef;
}

/* Resumo da Tabela */
.tabela-resumo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 25px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
}

.resumo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2c3e50;
  font-weight: 600;
}

.resumo-item i {
  font-size: 1.2rem;
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
