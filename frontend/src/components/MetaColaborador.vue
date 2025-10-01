<template>
  <div class="meta-colaborador">
  <div v-if="error" class="erro-meta" style="color: red; margin: 16px 0; text-align: center;">{{ error }}</div>
    <!-- Modal de Ranking dos Vendedores -->
    <div v-if="mostrarRanking" class="ranking-modal-overlay">
      <div class="ranking-modal">
        <div class="ranking-header">
          <div class="ranking-title">
            <h1>
              <i class="fas fa-trophy"></i>
              Ranking dos Principais Vendedores
            </h1>
            <p>Conheça nossos campeões e inspire-se para alcançar o topo!</p>
          </div>
          <button @click="fecharRanking" class="btn-close-ranking">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="ranking-content">
          <!-- Importância das Vendas -->
          <div class="importancia-vendas">
            <div class="importancia-card">
              <div class="importancia-icon">
                <i class="fas fa-star"></i>
              </div>
              <h3>Por que as vendas são importantes?</h3>
              <ul>
                <li><i class="fas fa-check"></i> Crescimento da empresa e oportunidades de carreira</li>
                <li><i class="fas fa-check"></i> Melhores comissões e bonificações para você</li>
                <li><i class="fas fa-check"></i> Satisfação dos clientes com nossos serviços</li>
                <li><i class="fas fa-check"></i> Fortalecimento da marca no mercado</li>
              </ul>
            </div>
          </div>

          <!-- Ranking dos Top Vendedores -->
          <div class="top-vendedores">
            <h3>
              <i class="fas fa-medal"></i>
              Top 5 Vendedores do Mês
            </h3>
            <div class="ranking-lista">
              <div class="vendedor-item podium primeiro" style="animation-delay: 0.1s">
                <div class="posicao-badge">1º</div>
                <div class="vendedor-info">
                  <div class="vendedor-avatar primeiro">
                    <i class="fas fa-crown"></i>
                  </div>
                  <div class="vendedor-dados">
                    <h4>Maria Silva Santos</h4>
                    <p>Vendedora Sênior</p>
                    <div class="vendedor-stats">
                      <span class="vendas">156 vendas</span>
                      <span class="meta">125% da meta</span>
                    </div>
                  </div>
                </div>
                <div class="premio-badge primeiro">
                  <i class="fas fa-trophy"></i>
                  Campeã
                </div>
              </div>

              <div class="vendedor-item podium segundo" style="animation-delay: 0.2s">
                <div class="posicao-badge">2º</div>
                <div class="vendedor-info">
                  <div class="vendedor-avatar segundo">
                    <i class="fas fa-medal"></i>
                  </div>
                  <div class="vendedor-dados">
                    <h4>João Carlos Pereira</h4>
                    <p>Consultor de Vendas</p>
                    <div class="vendedor-stats">
                      <span class="vendas">142 vendas</span>
                      <span class="meta">118% da meta</span>
                    </div>
                  </div>
                </div>
                <div class="premio-badge segundo">
                  <i class="fas fa-medal"></i>
                  Vice
                </div>
              </div>

              <div class="vendedor-item podium terceiro" style="animation-delay: 0.3s">
                <div class="posicao-badge">3º</div>
                <div class="vendedor-info">
                  <div class="vendedor-avatar terceiro">
                    <i class="fas fa-award"></i>
                  </div>
                  <div class="vendedor-dados">
                    <h4>Ana Beatriz Costa</h4>
                    <p>Supervisora de Vendas</p>
                    <div class="vendedor-stats">
                      <span class="vendas">128 vendas</span>
                      <span class="meta">107% da meta</span>
                    </div>
                  </div>
                </div>
                <div class="premio-badge terceiro">
                  <i class="fas fa-award"></i>
                  Bronze
                </div>
              </div>

              <div class="vendedor-item" style="animation-delay: 0.4s">
                <div class="posicao-badge">4º</div>
                <div class="vendedor-info">
                  <div class="vendedor-avatar">PL</div>
                  <div class="vendedor-dados">
                    <h4>Pedro Henrique Lima</h4>
                    <p>Vendedor Pleno</p>
                    <div class="vendedor-stats">
                      <span class="vendas">98 vendas</span>
                      <span class="meta">98% da meta</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="vendedor-item" style="animation-delay: 0.5s">
                <div class="posicao-badge">5º</div>
                <div class="vendedor-info">
                  <div class="vendedor-avatar">CR</div>
                  <div class="vendedor-dados">
                    <h4>Carla Fernanda Rocha</h4>
                    <p>Consultora Especializada</p>
                    <div class="vendedor-stats">
                      <span class="vendas">87 vendas</span>
                      <span class="meta">92% da meta</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Motivação -->
          <div class="motivacao-section">
            <div class="motivacao-card">
              <div class="motivacao-icon">
                <i class="fas fa-rocket"></i>
              </div>
              <h3>Você também pode estar aqui!</h3>
              <p>Cada venda conta para o sucesso da equipe. Vamos juntos alcançar novos patamares!</p>
              <div class="stats-gerais">
                <div class="stat-item">
                  <span class="numero">2.847</span>
                  <span class="label">Vendas este mês</span>
                </div>
                <div class="stat-item">
                  <span class="numero">98.5%</span>
                  <span class="label">Meta da equipe</span>
                </div>
                <div class="stat-item">
                  <span class="numero">R$ 847k</span>
                  <span class="label">Faturamento</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="ranking-footer">
          <button @click="fecharRanking" class="btn-continuar">
            <i class="fas fa-chart-line"></i>
            Ver Minha Meta Individual
          </button>
        </div>
      </div>
    </div>

    <!-- Conteúdo Principal (aparece após fechar o ranking) -->
    <div v-if="!mostrarRanking">
      <!-- Header premium -->
    <div class="header-meta-colaborador">
      <div class="header-background-pattern"></div>
      <div class="header-content">
        <div class="header-left">
          <div class="header-title">
            <h1>
              <i class="fas fa-user-chart header-icon"></i>
              Meta Individual dos Colaboradores
            </h1>
          </div>
        </div>
        <div class="header-right">
          <div class="controls-group">
            <div class="filter-control">
              <label>
                <i class="fas fa-user"></i>
                Colaborador
              </label>
              <select 
                v-model="colaboradorSelecionado" 
                @change="carregarMetaColaborador" 
                class="select-premium"
                :disabled="carregandoColaboradores"
              >
                <option value="" v-if="carregandoColaboradores">Carregando colaboradores...</option>
                <option value="" v-else>Selecione um colaborador...</option>
                <option v-for="colaborador in colaboradoresProcessados" :key="colaborador.id" :value="colaborador.id">
                  {{ colaborador.nome }} - {{ colaborador.cargo }}
                </option>
              </select>
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
      <p>Carregando meta do colaborador...</p>
    </div>

    <!-- Seleção de Colaborador -->
    <div v-else-if="!colaboradorSelecionado" class="selecao-colaborador">
      <div class="instrucao-card">
        <div class="instrucao-icon">
          <i class="fas fa-hand-point-up"></i>
        </div>
        <h3>Selecione um Colaborador</h3>
        <p>Escolha um colaborador no menu acima para visualizar sua meta individual detalhada</p>
      </div>
    </div>

    <!-- Meta Individual do Colaborador -->
    <div v-else class="meta-individual-container">
      <!-- Cabeçalho do Colaborador -->
      <div class="colaborador-header">
        <div class="colaborador-profile">
          <div class="avatar-grande">
            {{ (dadosColaborador.nome || 'U').charAt(0).toUpperCase() }}
          </div>
          <div class="colaborador-dados">
            <h2>{{ dadosColaborador.nome }}</h2>
            <p class="cargo">{{ dadosColaborador.cargo || 'Cargo não definido' }}</p>
            <span class="unidade-badge">{{ dadosColaborador.unidade || 'Sem unidade' }}</span>
          </div>
        </div>
        <div class="performance-resumo">
          <div class="meta-badge" :class="getPerformanceClass(dadosColaborador.percentualMeta || 0)">
            {{ (dadosColaborador.percentualMeta || 0).toFixed(1) }}% da Meta
          </div>
        </div>
      </div>

      <!-- KPIs Principais -->
      <div class="kpis-principais">
        <div class="kpi-card meta-total">
          <div class="kpi-header">
            <div class="kpi-icon">
              <i class="fas fa-target"></i>
            </div>
            <span class="kpi-titulo">Meta Total</span>
          </div>
          <div class="kpi-valor">{{ formatarMoeda(dadosColaborador.metaTotal || 0) }}</div>
          <div class="kpi-sublabel">Objetivo do mês</div>
        </div>

        <div class="kpi-card realizado">
          <div class="kpi-header">
            <div class="kpi-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <span class="kpi-titulo">Realizado</span>
          </div>
          <div class="kpi-valor">{{ formatarMoeda(dadosColaborador.totalRealizado || 0) }}</div>
          <div class="kpi-sublabel">Até o momento</div>
        </div>

        <div class="kpi-card faltante">
          <div class="kpi-header">
            <div class="kpi-icon">
              <i class="fas fa-flag-checkered"></i>
            </div>
            <span class="kpi-titulo">Faltante</span>
          </div>
          <div class="kpi-valor">{{ formatarMoeda((dadosColaborador.metaTotal || 0) - (dadosColaborador.totalRealizado || 0)) }}</div>
          <div class="kpi-sublabel">Para atingir meta</div>
        </div>

        <div class="kpi-card media-diaria">
          <div class="kpi-header">
            <div class="kpi-icon">
              <i class="fas fa-calendar-day"></i>
            </div>
            <span class="kpi-titulo">Média Diária</span>
          </div>
          <div class="kpi-valor">{{ mediaDiaria }}</div>
          <div class="kpi-sublabel">Necessária</div>
        </div>
      </div>

      <!-- Barra de Progresso Geral -->
      <div class="progress-geral">
        <div class="progress-header">
          <h3>Progresso da Meta Geral</h3>
          <span class="progress-percentage">{{ (dadosColaborador.percentualMeta || 0).toFixed(1) }}%</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar-bg">
            <div 
              class="progress-bar-fill" 
              :style="{ width: Math.min(dadosColaborador.percentualMeta || 0, 100) + '%' }"
              :class="getProgressClass(dadosColaborador.percentualMeta || 0)"
            ></div>
          </div>
        </div>
      </div>

      <!-- Performance por Categoria -->
      <div class="categorias-performance">
        <h3 class="section-title">
          <i class="fas fa-chart-pie"></i>
          Performance por Categoria
        </h3>
        <div class="categorias-grid">
          <div 
            v-for="categoria in dadosColaborador.categorias" 
            :key="categoria.nome"
            class="categoria-card"
          >
            <div class="categoria-header">
              <div class="categoria-icon">
                <i :class="categoria.icon"></i>
              </div>
              <h4>{{ categoria.nome }}</h4>
            </div>
            
            <div class="categoria-metricas">
              <div class="metrica-item">
                <span class="metrica-label">Meta</span>
                <span class="metrica-valor">{{ categoria.meta || 0 }}</span>
              </div>
              <div class="metrica-item">
                <span class="metrica-label">Realizado</span>
                <span class="metrica-valor realizado">{{ categoria.realizado || 0 }}</span>
              </div>
              <div class="metrica-item">
                <span class="metrica-label">Percentual</span>
                <span class="metrica-valor percentual">{{ categoria.meta ? ((categoria.realizado / categoria.meta) * 100).toFixed(1) : 0 }}%</span>
              </div>
            </div>

            <div class="categoria-progress">
              <div class="categoria-progress-bg">
                <div 
                  class="categoria-progress-fill"
                  :style="{ width: Math.min(categoria.meta ? (categoria.realizado / categoria.meta) * 100 : 0, 100) + '%' }"
                ></div>
              </div>
            </div>

            <div class="categoria-status" :class="getCategoriaStatus(categoria.realizado || 0, categoria.meta || 1)">
              {{ getCategoriaStatusText(categoria.realizado || 0, categoria.meta || 1) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Histórico e Tendências -->
      <div class="historico-tendencias">
        <h3 class="section-title">
          <i class="fas fa-chart-area"></i>
          Histórico e Tendências
        </h3>
        <div class="historico-grid">
          <div class="historico-card">
            <h4>Últimos 7 Dias</h4>
            <div class="historico-valor">{{ dadosColaborador.ultimos7Dias || 0 }}</div>
            <div class="historico-meta">Meta: {{ Math.round((dadosColaborador.metaTotal || 0) / 30 * 7) }}</div>
          </div>
          
          <div class="historico-card">
            <h4>Mês Anterior</h4>
            <div class="historico-valor">{{ dadosColaborador.mesAnterior || 0 }}</div>
            <div class="historico-comparacao" :class="(dadosColaborador.totalRealizado || 0) > (dadosColaborador.mesAnterior || 0) ? 'positivo' : 'negativo'">
              {{ (dadosColaborador.totalRealizado || 0) > (dadosColaborador.mesAnterior || 0) ? '+' : '' }}{{ dadosColaborador.mesAnterior ? (((dadosColaborador.totalRealizado || 0) - (dadosColaborador.mesAnterior || 0)) / dadosColaborador.mesAnterior * 100).toFixed(1) : 0 }}%
            </div>
          </div>
          
          <div class="historico-card">
            <h4>Melhor Categoria</h4>
            <div class="historico-valor">{{ melhorCategoria.nome }}</div>
            <div class="historico-meta">{{ melhorCategoria.percentual }}% da meta</div>
          </div>
          
        </div>
      </div>
    </div>
    </div> <!-- Fecha div do conteúdo principal -->
  </div> <!-- Fecha div meta-colaborador -->
</template>

<script>
import { API_BASE_URL } from '@/api.js'

export default {
  name: 'MetaColaborador',
  props: {
    colaboradores: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      carregando: false,
      carregandoColaboradores: false,
      colaboradorSelecionado: '',
      colaboradoresProcessados: [],
      dadosColaborador: {},
      mostrarRanking: true, // Modal de ranking aparece primeiro
      error: null
    };
  },
  computed: {
    mediaDiaria() {
      console.log('Calculando mediaDiaria...');
      console.log('dadosColaborador.metaDiaria:', this.dadosColaborador.metaDiaria);
      console.log('dadosColaborador.metaTotal:', this.dadosColaborador.metaTotal);
      
      // Usa a meta diária que vem da API, ou calcula se não houver
      if (this.dadosColaborador.metaDiaria && this.dadosColaborador.metaDiaria > 0) {
        const valorFormatado = this.formatarMoeda(this.dadosColaborador.metaDiaria);
        console.log('Usando meta diária da API:', valorFormatado);
        return valorFormatado;
      }
      
      if (!this.dadosColaborador.metaTotal) {
        console.log('Sem meta total, retornando 0');
        return this.formatarMoeda(0);
      }
      
      const diasRestantes = 30 - new Date().getDate();
      const faltante = (this.dadosColaborador.metaTotal || 0) - (this.dadosColaborador.totalRealizado || 0);
      const valorCalculado = diasRestantes > 0 ? Math.ceil(faltante / diasRestantes) : 0;
      
      console.log('Calculando meta diária:', {
        diasRestantes,
        faltante,
        valorCalculado
      });
      
      return this.formatarMoeda(valorCalculado);
    },
    
    melhorCategoria() {
      if (!this.dadosColaborador.categorias || this.dadosColaborador.categorias.length === 0) {
        return { nome: '-', percentual: 0 };
      }
      
      const melhor = this.dadosColaborador.categorias.reduce((prev, current) => {
        const prevPerc = prev.meta ? (prev.realizado / prev.meta) * 100 : 0;
        const currentPerc = current.meta ? (current.realizado / current.meta) * 100 : 0;
        return currentPerc > prevPerc ? current : prev;
      });
      
      return {
        nome: melhor.nome || '-',
        percentual: melhor.meta ? ((melhor.realizado / melhor.meta) * 100).toFixed(1) : 0
      };
    },
    
    piorCategoria() {
      if (!this.dadosColaborador.categorias || this.dadosColaborador.categorias.length === 0) {
        return { nome: '-', percentual: 0 };
      }
      
      const pior = this.dadosColaborador.categorias.reduce((prev, current) => {
        const prevPerc = prev.meta ? (prev.realizado / prev.meta) * 100 : 0;
        const currentPerc = current.meta ? (current.realizado / current.meta) * 100 : 0;
        return currentPerc < prevPerc ? current : prev;
      });
      
      return {
        nome: pior.nome || '-',
        percentual: pior.meta ? ((pior.realizado / pior.meta) * 100).toFixed(1) : 0
      };
    }
  },
  watch: {
    colaboradores: {
      immediate: true,
      handler(newColaboradores) {
        this.processarColaboradores(newColaboradores);
      }
    }
  },
  mounted() {
    // Carrega colaboradores com metas diretamente da API ao invés de depender das props
    this.carregarColaboradoresComMetas();
  },
  methods: {
    async carregarColaboradoresComMetas() {
      this.carregandoColaboradores = true;
      try {
        // Primeiro, tenta buscar colaboradores que têm metas cadastradas
        const response = await fetch(`${API_BASE_URL}/metas/colaboradores-com-metas`);
        
        if (response.ok) {
          const colaboradores = await response.json();
          console.log('Colaboradores com metas carregados da API:', colaboradores);
          this.processarColaboradores(colaboradores);
        } else {
          console.log('API de colaboradores-com-metas não disponível, usando filtro local');
          // Fallback: filtrar colaboradores das props que têm metas
          await this.filtrarColaboradoresComMetas();
        }
      } catch (error) {
        console.error('Erro ao carregar colaboradores com metas:', error);
        // Fallback: filtrar colaboradores das props que têm metas
        await this.filtrarColaboradoresComMetas();
      } finally {
        this.carregandoColaboradores = false;
      }
    },

    async filtrarColaboradoresComMetas() {
      // Método fallback que verifica quais colaboradores das props têm metas
      const colaboradoresComMetas = [];
      
      for (const colaborador of this.colaboradores) {
        try {
          // Verifica se o colaborador tem meta cadastrada
          const responseVerificacao = await fetch(`${API_BASE_URL}/metas/colaborador/${colaborador.cpf || colaborador.id}`);
          
          if (responseVerificacao.ok) {
            const metas = await responseVerificacao.json();
            if (metas && metas.length > 0) {
              // Adiciona dados da meta ao colaborador
              const metaAtual = metas[0];
              colaboradoresComMetas.push({
                ...colaborador,
                meta_total: metaAtual.meta_final,
                meta_diaria: metaAtual.meta_diaria,
                id_eyal: metaAtual.id_eyal,
                cargo: metaAtual.cargo || colaborador.cargo
              });
            }
          }
        } catch (error) {
          console.log(`Erro ao verificar meta para colaborador ${colaborador.nome}:`, error);
        }
      }
      
      console.log('Colaboradores filtrados com metas:', colaboradoresComMetas);
      this.processarColaboradores(colaboradoresComMetas);
    },

    fecharRanking() {
      this.mostrarRanking = false;
    },
    
    processarColaboradores(colaboradores) {
      console.log('Processando colaboradores:', colaboradores);
      
      if (!colaboradores || colaboradores.length === 0) {
        this.colaboradoresProcessados = [];
        return;
      }

      // Processar dados dos colaboradores
      this.colaboradoresProcessados = colaboradores.map(colab => {
        console.log('Processando colaborador:', colab);
        
        // Extrair informações do cargo
        let cargoInfo = 'Cargo não definido';
        if (colab.cargo) {
          if (typeof colab.cargo === 'string') {
            cargoInfo = colab.cargo;
          } else if (typeof colab.cargo === 'object') {
            cargoInfo = colab.cargo.nome || colab.cargo.cargo_nome || colab.cargo.funcao || 'Cargo não definido';
          }
        }
        
        // Se não tem cargo, tenta usar a função
        if (cargoInfo === 'Cargo não definido' && colab.funcao) {
          cargoInfo = colab.funcao;
        }

        // Extrair nome completo
        let nomeCompleto = '';
        if (colab.nome && colab.sobrenome) {
          nomeCompleto = `${colab.nome} ${colab.sobrenome}`;
        } else if (colab.nome) {
          nomeCompleto = colab.nome;
        } else {
          nomeCompleto = 'Nome não definido';
        }

        return {
          id: colab.id || colab.id_funcionario,
          nome: nomeCompleto,
          cpf: colab.cpf,
          cargo: cargoInfo,
          setores: colab.setores || [],
          unidade: colab.unidade || this.getUnidadeFromSetores(colab.setores || []) || 'Sem unidade',
          // Campos adicionais que podem vir da API de metas
          meta_total: colab.meta_final || colab.meta_total || 0,
          meta_diaria: colab.meta_diaria || 0,
          id_eyal: colab.id_eyal
        };
      });

      console.log('Colaboradores processados:', this.colaboradoresProcessados);
    },

    getUnidadeFromSetores(setores) {
      if (!setores || setores.length === 0) return 'Sem unidade';
      
      // Mapear setores para unidades (você pode ajustar essa lógica)
      const setor = setores[0];
      const mapeamentoUnidades = {
        'TI': 'Filial Centro',
        'Vendas': 'Filial Norte', 
        'Administrativo': 'Filial Sul',
        'RH': 'Filial Centro',
        'Financeiro': 'Filial Norte'
      };
      
      return mapeamentoUnidades[setor.nome] || 'Filial Centro';
    },
    
    async carregarMetaColaborador() {
      if (!this.colaboradorSelecionado) {
        this.dadosColaborador = {};
        this.error = null;
        return;
      }
      try {
        this.carregando = true;
        this.error = null;
        
        const colaborador = this.colaboradoresProcessados.find(c => c.id == this.colaboradorSelecionado);
        if (!colaborador) {
          this.error = 'Colaborador não encontrado.';
          this.dadosColaborador = {};
          return;
        }

        console.log('Colaborador selecionado:', colaborador);

        // Se já temos dados de meta do colaborador (vindos da nova API), usa eles
        if (colaborador.meta_total && colaborador.id_eyal) {
          console.log('Usando dados de meta já carregados:', colaborador);
          
          this.dadosColaborador = {
            ...colaborador,
            nome: colaborador.nome,
            sobrenome: '', // Limpa sobrenome para evitar duplicação
            unidade: colaborador.unidade || 'Sem unidade',
            equipe: colaborador.equipe || '',
            cargo: colaborador.cargo || colaborador.funcao || 'Cargo não definido',
            nivel: colaborador.nivel || '',
            lider_direto: colaborador.lider_direto || '',
            metaTotal: colaborador.meta_total || 0,
            metaDiaria: colaborador.meta_diaria || 0,
            diasTrabalhados: colaborador.dias_trabalhados || 0,
            diasFalta: colaborador.dias_de_falta || 0,
            totalRealizado: 0, // Será preenchido quando tivermos dados de realizado
            percentualMeta: 0, // Será calculado quando tivermos dados de realizado
            categorias: [], // Será preenchido quando tivermos dados de realizado
            ultimos7Dias: 0,
            mesAnterior: 0,
            mesRef: colaborador.mes_ref || new Date().toISOString().slice(0, 7),
            id_eyal: colaborador.id_eyal
          };
          
          console.log('Dados do colaborador montados:', this.dadosColaborador);
          
          // Busca os dados de realizado
          if (colaborador.id_eyal) {
            await this.carregarDadosRealizado(colaborador.id_eyal);
          }
          
          return;
        }

        // Fallback: busca dados da API tradicional se não temos dados completos
        if (!colaborador.cpf) {
          this.error = 'Colaborador sem CPF cadastrado.';
          this.dadosColaborador = {};
          return;
        }

        const response = await fetch(`${API_BASE_URL}/metas/colaborador/${colaborador.cpf}`);
        if (!response.ok) {
          if (response.status === 404) {
            console.log(`Info: Funcionário ${colaborador.nome} (CPF: ${colaborador.cpf}) não possui metas cadastradas`);
          }
          this.error = 'Colaborador não encontrado ou sem meta cadastrada.';
          this.dadosColaborador = {};
          return;
        }
        
        const dadosApi = await response.json();
        console.log('Dados recebidos da API de metas (fallback):', dadosApi);
        
        // A API retorna um array de metas, vamos pegar a primeira (mais recente)
        const metaAtual = Array.isArray(dadosApi) && dadosApi.length > 0 ? dadosApi[0] : null;
        console.log('Meta atual selecionada:', metaAtual);
        console.log('Meta diária recebida:', metaAtual?.meta_diaria);
        
        if (!metaAtual) {
          this.error = 'Nenhuma meta encontrada para este colaborador.';
          this.dadosColaborador = {};
          return;
        }
        
        // Adapta os dados recebidos para o formato esperado pelo frontend
        this.dadosColaborador = {
          ...colaborador,
          nome: metaAtual.nome || colaborador.nome,
          sobrenome: '', // Limpa sobrenome para evitar duplicação 
          unidade: metaAtual.unidade || colaborador.unidade || 'Sem unidade',
          equipe: metaAtual.equipe || '',
          cargo: metaAtual.cargo || metaAtual.funcao || colaborador.cargo || 'Cargo não definido',
          nivel: metaAtual.nivel || '',
          lider_direto: metaAtual.lider_direto || '',
          metaTotal: metaAtual.meta_final || 0,
          metaDiaria: metaAtual.meta_diaria || 0,
          diasTrabalhados: metaAtual.dias_trabalhados || 0,
          diasFalta: metaAtual.dias_de_falta || 0,
          totalRealizado: 0, // Será preenchido quando tivermos dados de realizado
          percentualMeta: 0, // Será calculado quando tivermos dados de realizado
          categorias: [], // Será preenchido quando tivermos dados de realizado
          ultimos7Dias: 0,
          mesAnterior: 0,
          mesRef: metaAtual.mes_ref,
          id_eyal: metaAtual.id_eyal
        };
        
        console.log('Dados do colaborador montados:', this.dadosColaborador);
        
        // Agora busca os dados de realizado se tiver id_eyal
        if (metaAtual.id_eyal) {
          await this.carregarDadosRealizado(metaAtual.id_eyal);
        }
      } catch (error) {
        this.error = 'Erro ao carregar meta do colaborador.';
        this.dadosColaborador = {};
      } finally {
        this.carregando = false;
      }
    },
    
    async carregarDadosRealizado(idEyal) {
      try {
        const response = await fetch(`${API_BASE_URL}/realizado/colaborador/${idEyal}/resumo`);
        
        if (response.ok) {
          const dadosRealizado = await response.json();
          console.log('Dados de realizado:', dadosRealizado);
          
          // Calcula o total realizado (remove o TOTAL_GERAL do cálculo)
          const totalRealizado = dadosRealizado.TOTAL_GERAL || 0;
          
          // Atualiza os dados do colaborador
          this.dadosColaborador.totalRealizado = totalRealizado;
          this.dadosColaborador.percentualMeta = this.dadosColaborador.metaTotal > 0 
            ? (totalRealizado / this.dadosColaborador.metaTotal) * 100 
            : 0;
          
          // Cria categorias baseadas nos dados de realizado
          this.dadosColaborador.categorias = Object.entries(dadosRealizado)
            .filter(([key]) => key !== 'TOTAL_GERAL')
            .map(([tipo, realizado]) => ({
              nome: tipo || 'Outros',
              meta: Math.round(this.dadosColaborador.metaTotal * 0.25), // Distribui meta proporcionalmente
              realizado: realizado,
              icon: 'fas fa-chart-bar'
            }));
        } else {
          console.log(`Info: Funcionário ID Eyal ${idEyal} não possui dados de realizado`);
          // Mantém os valores zerados que já foram definidos
        }
      } catch (error) {
        console.error('Erro ao carregar dados de realizado:', error);
        // Mantém os valores zerados que já foram definidos
      }
    },
    
    gerarDadosSimulados(colaborador) {
      // Gerar dados simulados únicos para cada colaborador real
      const baseMultiplier = colaborador.id * 8.5;
      
      const metaTotal = Math.round(40 + baseMultiplier);
      const totalRealizado = Math.round(metaTotal * (0.6 + (colaborador.id * 0.08)));
      const percentualMeta = (totalRealizado / metaTotal) * 100;
      
      return {
        metaTotal,
        totalRealizado,
        percentualMeta,
        ultimos7Dias: Math.round(totalRealizado * 0.3),
        mesAnterior: Math.round(totalRealizado * 0.85),
        categorias: [
          {
            nome: 'Odonto',
            icon: 'fas fa-tooth',
            meta: Math.round(metaTotal * 0.3),
            realizado: Math.round(totalRealizado * 0.28)
          },
          {
            nome: 'Check-up',
            icon: 'fas fa-stethoscope',
            meta: Math.round(metaTotal * 0.35),
            realizado: Math.round(totalRealizado * 0.38)
          },
          {
            nome: 'Dr. Central',
            icon: 'fas fa-user-md',
            meta: Math.round(metaTotal * 0.25),
            realizado: Math.round(totalRealizado * 0.24)
          },
          {
            nome: 'BabyClick',
            icon: 'fas fa-baby',
            meta: Math.round(metaTotal * 0.1),
            realizado: Math.round(totalRealizado * 0.1)
          }
        ]
      };
    },
    
    getPerformanceClass(percentual) {
      if (percentual >= 100) return 'excelente';
      if (percentual >= 80) return 'bom';
      if (percentual >= 60) return 'regular';
      return 'baixo';
    },
    
    getProgressClass(percentual) {
      if (percentual >= 100) return 'excellent';
      if (percentual >= 80) return 'good';
      if (percentual >= 60) return 'regular';
      return 'low';
    },
    
    getCategoriaStatus(realizado, meta) {
      const percentual = (realizado / meta) * 100;
      if (percentual >= 100) return 'atingida';
      if (percentual >= 80) return 'quase-atingida';
      return 'em-andamento';
    },
    
    getCategoriaStatusText(realizado, meta) {
      const percentual = (realizado / meta) * 100;
      if (percentual >= 100) return 'Meta Atingida';
      if (percentual >= 80) return 'Quase Lá';
      return 'Em Andamento';
    },
    
    formatarMoeda(valor) {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2
      }).format(valor || 0);
    }
  }
};
</script>

<style scoped>
.meta-colaborador {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
}

/* Header Premium */
.header-meta-colaborador {
  position: relative;
  background: linear-gradient(135deg, #2c3e50, #3498db);
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
  overflow: hidden;
}

.header-background-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
}

.header-content {
  position: relative;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.header-title h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  font-size: 2rem;
  opacity: 0.9;
}

.header-title p {
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.controls-group {
  display: flex;
  gap: 1.5rem;
  align-items: end;
}

.filter-control {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-control label {
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.select-premium {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  background: rgba(255,255,255,0.95);
  color: #2c3e50;
  font-weight: 500;
  min-width: 300px;
  backdrop-filter: blur(10px);
}

/* Loading */
.loading-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: white;
}

.loading-animation {
  position: relative;
  width: 80px;
  height: 80px;
  margin-bottom: 1.5rem;
}

.pulse-ring {
  position: absolute;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.pulse-ring:nth-child(1) {
  width: 80px;
  height: 80px;
  animation-delay: 0s;
}

.pulse-ring:nth-child(2) {
  width: 60px;
  height: 60px;
  top: 10px;
  left: 10px;
  animation-delay: 0.5s;
}

.pulse-ring:nth-child(3) {
  width: 40px;
  height: 40px;
  top: 20px;
  left: 20px;
  animation-delay: 1s;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.7;
  }
  100% {
    transform: scale(0.95);
    opacity: 1;
  }
}

/* Seleção de Colaborador */
.selecao-colaborador {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.instrucao-card {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  max-width: 500px;
}

.instrucao-icon {
  font-size: 4rem;
  color: #667eea;
  margin-bottom: 1.5rem;
}

.instrucao-card h3 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.instrucao-card p {
  color: #6c757d;
  font-size: 1.1rem;
  line-height: 1.6;
}

/* Meta Individual Container */
.meta-individual-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

/* Cabeçalho do Colaborador */
.colaborador-header {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.colaborador-profile {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.avatar-grande {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  font-weight: 700;
}

.colaborador-dados h2 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
}

.colaborador-dados .cargo {
  margin: 0.5rem 0;
  color: #6c757d;
  font-size: 1.1rem;
}

.unidade-badge {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  color: #1976d2;
  padding: 0.5rem 1rem;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 600;
}

.meta-badge {
  padding: 1rem 1.5rem;
  border-radius: 25px;
  font-size: 1.2rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-badge.excelente {
  background: linear-gradient(135deg, #4caf50, #388e3c);
  color: white;
}

.meta-badge.bom {
  background: linear-gradient(135deg, #2196f3, #1976d2);
  color: white;
}

.meta-badge.regular {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
}

.meta-badge.baixo {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
}

/* KPIs Principais */
.kpis-principais {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.kpi-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.3rem;
}

.kpi-card.meta-total .kpi-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.kpi-card.realizado .kpi-icon {
  background: linear-gradient(135deg, #4caf50, #388e3c);
}

.kpi-card.faltante .kpi-icon {
  background: linear-gradient(135deg, #ff9800, #f57c00);
}

.kpi-card.media-diaria .kpi-icon {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
}

.kpi-titulo {
  font-size: 1rem;
  font-weight: 600;
  color: #6c757d;
}

.kpi-valor {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.kpi-sublabel {
  font-size: 0.9rem;
  color: #6c757d;
}

/* Progresso Geral */
.progress-geral {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c3e50;
}

.progress-percentage {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}

.progress-bar-container {
  height: 20px;
  background: #e9ecef;
  border-radius: 15px;
  overflow: hidden;
  position: relative;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 15px;
  transition: all 1s ease;
  position: relative;
}

.progress-bar-fill.excellent {
  background: linear-gradient(90deg, #4caf50, #66bb6a);
}

.progress-bar-fill.good {
  background: linear-gradient(90deg, #2196f3, #42a5f5);
}

.progress-bar-fill.regular {
  background: linear-gradient(90deg, #ff9800, #ffb74d);
}

.progress-bar-fill.low {
  background: linear-gradient(90deg, #f44336, #ef5350);
}

/* Section Title */
.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
}

/* Categorias Performance */
.categorias-performance {
  margin-bottom: 2rem;
}

.categorias-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.categoria-card {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.categoria-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.categoria-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.categoria-icon {
  width: 45px;
  height: 45px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.categoria-header h4 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #2c3e50;
}

.categoria-metricas {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.metrica-item {
  text-align: center;
}

.metrica-label {
  display: block;
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.metrica-valor {
  display: block;
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c3e50;
}

.metrica-valor.realizado {
  color: #4caf50;
}

.metrica-valor.percentual {
  color: #667eea;
}

.categoria-progress {
  margin-bottom: 1rem;
}

.categoria-progress-bg {
  height: 8px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
}

.categoria-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 10px;
  transition: width 0.8s ease;
}

.categoria-status {
  text-align: center;
  padding: 0.5rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
}

.categoria-status.atingida {
  background: #e8f5e8;
  color: #4caf50;
}

.categoria-status.quase-atingida {
  background: #e3f2fd;
  color: #2196f3;
}

.categoria-status.em-andamento {
  background: #fff3e0;
  color: #ff9800;
}

/* Histórico e Tendências */
.historico-tendencias {
  margin-bottom: 2rem;
}

.historico-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.historico-card {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.historico-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.historico-card h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #6c757d;
}

.historico-valor {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.historico-meta {
  font-size: 0.9rem;
  color: #6c757d;
}

.historico-comparacao {
  font-size: 1rem;
  font-weight: 600;
}

.historico-comparacao.positivo {
  color: #4caf50;
}

.historico-comparacao.negativo {
  color: #f44336;
}

/* Responsividade */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .controls-group {
    flex-direction: column;
    width: 100%;
  }
  
  .select-premium {
    min-width: 100%;
  }
  
  .colaborador-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  
  .kpis-principais {
    grid-template-columns: 1fr;
  }
  
  .categorias-grid {
    grid-template-columns: 1fr;
  }
  
  .historico-grid {
    grid-template-columns: 1fr;
  }
  
  .categoria-metricas {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
}

/* Modal de Ranking dos Vendedores - Otimizado */
.ranking-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(30, 30, 60, 0.9));
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from { 
    opacity: 0;
    backdrop-filter: blur(0px);
  }
  to { 
    opacity: 1;
    backdrop-filter: blur(10px);
  }
}

.ranking-modal {
  background: linear-gradient(135deg, #ffffff, #f8f9ff);
  border-radius: 20px;
  max-width: 1000px;
  width: 100%;
  max-height: 95vh;
  overflow: hidden;
  box-shadow: 
    0 25px 50px rgba(0,0,0,0.25),
    0 0 0 1px rgba(255,255,255,0.1),
    inset 0 1px 0 rgba(255,255,255,0.9);
  animation: slideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  flex-direction: column;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(40px) scale(0.9);
    filter: blur(5px);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0px);
  }
}

.ranking-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #8b5fbf 100%);
  color: white;
  padding: 2rem 2.5rem;
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  overflow: hidden;
}

.ranking-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
  pointer-events: none;
}

.ranking-title {
  position: relative;
  z-index: 1;
}

.ranking-title h1 {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 1rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
  letter-spacing: -0.5px;
}

.ranking-title h1 i {
  font-size: 2.5rem;
  color: #ffd700;
  text-shadow: 0 0 20px rgba(255,215,0,0.5);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.ranking-title p {
  margin: 0.75rem 0 0 0;
  opacity: 0.95;
  font-size: 1.1rem;
  font-weight: 400;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.btn-close-ranking {
  background: rgba(255,255,255,0.15);
  border: 2px solid rgba(255,255,255,0.2);
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  font-size: 1.3rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
  backdrop-filter: blur(10px);
}

.btn-close-ranking:hover {
  background: rgba(255,255,255,0.25);
  border-color: rgba(255,255,255,0.4);
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.ranking-content {
  padding: 2.5rem;
  overflow-y: auto;
  flex: 1;
  background: linear-gradient(180deg, #ffffff 0%, #f8f9ff 100%);
}

/* Importância das Vendas - Otimizada */
.importancia-vendas {
  margin-bottom: 2.5rem;
}

.importancia-card {
  background: linear-gradient(135deg, #e8f8f5 0%, #f0f9ff 50%, #f3e5f5 100%);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(76, 175, 80, 0.2);
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(76, 175, 80, 0.1);
}

.importancia-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(76, 175, 80, 0.05) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
  pointer-events: none;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.importancia-icon {
  color: #4caf50;
  font-size: 2.5rem;
  margin-bottom: 1.25rem;
  position: relative;
  z-index: 1;
  text-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
}

.importancia-card h3 {
  margin: 0 0 1.25rem 0;
  color: #2c3e50;
  font-size: 1.4rem;
  font-weight: 800;
  position: relative;
  z-index: 1;
}

.importancia-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  position: relative;
  z-index: 1;
}

.importancia-card li {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-weight: 600;
  font-size: 1.05rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.importancia-card li:hover {
  transform: translateX(5px);
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
}

.importancia-card li i {
  color: #4caf50;
  width: 20px;
  font-size: 1.1rem;
  text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
}

/* Top Vendedores - Otimizado */
.top-vendedores h3 {
  margin: 0 0 2rem 0;
  color: #2c3e50;
  font-size: 1.5rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 1rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.top-vendedores h3 i {
  color: #667eea;
  text-shadow: 0 0 15px rgba(102, 126, 234, 0.4);
}

.ranking-lista {
  display: grid;
  gap: 1.5rem;
}

.vendedor-item {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 20px;
  padding: 1.5rem;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 1.5rem;
  box-shadow: 
    0 4px 20px rgba(0,0,0,0.08),
    0 1px 3px rgba(0,0,0,0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
  opacity: 0;
  transform: translateY(30px);
  animation: slideInUp 0.6s ease forwards;
}

@keyframes slideInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.vendedor-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
  transition: left 0.5s ease;
}

.vendedor-item:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 
    0 12px 40px rgba(0,0,0,0.12),
    0 4px 20px rgba(102, 126, 234, 0.15);
}

.vendedor-item:hover::before {
  left: 100%;
}

.vendedor-item.podium {
  border: 3px solid;
  box-shadow: 
    0 8px 32px rgba(0,0,0,0.15),
    0 0 0 1px rgba(255,255,255,0.1);
}

.vendedor-item.primeiro {
  background: linear-gradient(135deg, #fff9c4 0%, #fffbeb 50%, #fff8dc 100%);
  border-image: linear-gradient(135deg, #ffd700, #ffed4e) 1;
  box-shadow: 
    0 12px 40px rgba(255, 215, 0, 0.25),
    0 0 30px rgba(255, 215, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.vendedor-item.segundo {
  background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 50%, #f0f0f0 100%);
  border-image: linear-gradient(135deg, #c0c0c0, #e0e0e0) 1;
  box-shadow: 
    0 10px 35px rgba(192, 192, 192, 0.2),
    0 0 25px rgba(192, 192, 192, 0.1);
}

.vendedor-item.terceiro {
  background: linear-gradient(135deg, #fff4e6 0%, #fff8f1 50%, #ffeee6 100%);
  border-image: linear-gradient(135deg, #cd7f32, #daa520) 1;
  box-shadow: 
    0 10px 35px rgba(205, 127, 50, 0.2),
    0 0 25px rgba(205, 127, 50, 0.1);
}

.posicao-badge {
  font-size: 1.8rem;
  font-weight: 900;
  color: #667eea;
  min-width: 50px;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
  z-index: 1;
}

.vendedor-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  position: relative;
  z-index: 1;
}

.vendedor-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.4rem;
  font-weight: 700;
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.vendedor-avatar::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%);
  animation: shine 3s infinite;
}

@keyframes shine {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.vendedor-avatar.primeiro {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 50%, #fff200 100%);
  color: #2c3e50;
  box-shadow: 
    0 8px 25px rgba(255, 215, 0, 0.4),
    0 0 30px rgba(255, 215, 0, 0.3),
    inset 0 2px 0 rgba(255, 255, 255, 0.3);
}

.vendedor-avatar.segundo {
  background: linear-gradient(135deg, #c0c0c0 0%, #e0e0e0 50%, #d3d3d3 100%);
  color: #2c3e50;
  box-shadow: 
    0 8px 25px rgba(192, 192, 192, 0.4),
    inset 0 2px 0 rgba(255, 255, 255, 0.4);
}

.vendedor-avatar.terceiro {
  background: linear-gradient(135deg, #cd7f32 0%, #daa520 50%, #b8860b 100%);
  color: white;
  box-shadow: 
    0 8px 25px rgba(205, 127, 50, 0.4),
    inset 0 2px 0 rgba(255, 255, 255, 0.2);
}

.vendedor-dados h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #2c3e50;
}

.vendedor-dados p {
  margin: 0.25rem 0 0.5rem 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.vendedor-stats {
  display: flex;
  gap: 1rem;
}

.vendedor-stats span {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 10px;
}

.vendas {
  background: #e3f2fd;
  color: #1976d2;
}

.meta {
  background: #e8f5e8;
  color: #388e3c;
}

.premio-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.premio-badge.primeiro {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #2c3e50;
}

.premio-badge.segundo {
  background: linear-gradient(135deg, #c0c0c0, #e0e0e0);
  color: #2c3e50;
}

.premio-badge.terceiro {
  background: linear-gradient(135deg, #cd7f32, #daa520);
  color: white;
}

/* Motivação */
.motivacao-section {
  margin-top: 2rem;
}

.motivacao-card {
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  border: 2px solid #667eea;
}

.motivacao-icon {
  color: #667eea;
  font-size: 3rem;
  margin-bottom: 1rem;
}

.motivacao-card h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.5rem;
  font-weight: 700;
}

.motivacao-card p {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
  line-height: 1.6;
}

.stats-gerais {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
}

.stat-item .numero {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.stat-item .label {
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 600;
}

/* Footer do Modal - Otimizado */
.ranking-footer {
  padding: 2rem 2.5rem;
  background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
  text-align: center;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
  position: relative;
}

.ranking-footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 20%;
  right: 20%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
}

.btn-continuar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #8b5fbf 100%);
  color: white;
  border: none;
  padding: 1.25rem 2.5rem;
  border-radius: 25px;
  font-size: 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.3),
    0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-continuar::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s ease;
}

.btn-continuar:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 50%, #5a67d8 100%);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 
    0 12px 35px rgba(102, 126, 234, 0.4),
    0 8px 20px rgba(0, 0, 0, 0.15);
}

.btn-continuar:hover::before {
  left: 100%;
}

.btn-continuar:active {
  transform: translateY(-1px) scale(1.02);
}

/* Responsividade do Modal - Otimizada */
@media (max-width: 768px) {
  .ranking-modal {
    margin: 0.5rem;
    max-height: 98vh;
    border-radius: 15px;
  }
  
  .ranking-header {
    padding: 1.5rem;
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .ranking-title h1 {
    font-size: 1.6rem;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .ranking-title h1 i {
    font-size: 2rem;
  }
  
  .ranking-content {
    padding: 1.5rem;
  }
  
  .importancia-card {
    padding: 1.5rem;
  }
  
  .importancia-card li {
    padding: 0.5rem;
    font-size: 1rem;
  }
  
  .vendedor-item {
    grid-template-columns: auto 1fr;
    grid-template-rows: auto auto;
    gap: 1rem;
    padding: 1.25rem;
    text-align: center;
  }
  
  .posicao-badge {
    grid-column: 1 / -1;
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }
  
  .vendedor-info {
    grid-column: 1 / -1;
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .vendedor-avatar {
    width: 60px;
    height: 60px;
    font-size: 1.2rem;
  }
  
  .vendedor-stats {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .stats-gerais {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .premio-badge {
    grid-column: 1 / -1;
    align-self: center;
    justify-self: center;
    margin-top: 0.5rem;
  }
  
  .ranking-footer {
    padding: 1.5rem;
  }
  
  .btn-continuar {
    padding: 1rem 2rem;
    font-size: 1rem;
    width: 100%;
    max-width: 300px;
  }
}
</style>
