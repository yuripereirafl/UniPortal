<template>
  <div class="dashboard-colaboradores">
    <div class="header-section">
      <h2><i class="fas fa-users"></i> Quadro de Colaboradores</h2>
      <div class="stats">
        <span class="stat-item">
          <i class="fas fa-chart-bar"></i> 
          Total: {{ colaboradores.length }}
        </span>
      </div>
    </div>
    
    <!-- Loading com animação -->
    <div v-if="carregando" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Carregando colaboradores...</p>
    </div>
    
    <!-- Erro estilizado -->
    <div v-else-if="erro" class="error-container">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ erro }}</p>
      <button @click="carregarColaboradores" class="btn-retry">Tentar Novamente</button>
    </div>
    
    <!-- Tabela moderna -->
    <div v-else class="table-container">
      <table class="modern-table">
        <thead>
          <tr>
            <th @click="ordenarPor('nome')" style="cursor:pointer">
              Nome <i class="fas fa-sort"></i>
            </th>
            <th>Sobrenome</th>
            <th @click="ordenarPor('unidade')" style="cursor:pointer">
              Unidade <i class="fas fa-sort"></i>
            </th>
            <th>Cargo</th>
            <th>Função</th>
            <th>Equipe</th>
            <th>Nível</th>
            <th>Status</th>
            <th>Meta</th>
            <th>Tipo Pgto</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="colaboradoresOrdenados.length === 0" class="empty-row">
            <td colspan="11">
              <div class="empty-state">
                <i class="fas fa-inbox empty-icon"></i>
                <p>Nenhum colaborador encontrado</p>
                <small>Verifique os dados ou tente recarregar</small>
              </div>
            </td>
          </tr>
          <tr v-for="(colab, index) in colaboradoresOrdenados" :key="colab.id" class="data-row" :class="{ 'row-even': index % 2 === 0 }">
            <td class="name-cell">
              <div class="user-info">
                <div class="avatar">{{ (colab.nome || 'U').charAt(0).toUpperCase() }}</div>
                <span>{{ colab.nome || '-' }}</span>
              </div>
            </td>
            <td>{{ colab.sobrenome || '-' }}</td>
            <td>
              <div class="tag-container">
                <span v-if="colab.setores && colab.setores.length" 
                      v-for="setor in colab.setores.slice(0, 2)" 
                      :key="setor.id" 
                      class="tag tag-setor">
                  {{ setor.nome }}
                </span>
                <span v-if="colab.setores && colab.setores.length > 2" class="tag tag-more">
                  +{{ colab.setores.length - 2 }}
                </span>
                <span v-else-if="!colab.setores || colab.setores.length === 0" class="no-data">—</span>
              </div>
            </td>
            <td>
              <span class="badge badge-cargo">{{ colab.cargo && colab.cargo.nome ? colab.cargo.nome : '-' }}</span>
            </td>
            <td>{{ colab.cargo && colab.cargo.funcao ? colab.cargo.funcao : '-' }}</td>
            <td>
              <span class="badge badge-equipe">{{ colab.cargo && colab.cargo.equipe ? colab.cargo.equipe : '-' }}</span>
            </td>
            <td>
              <span class="level-indicator" :class="'level-' + (colab.cargo?.nivel || 'none')">
                {{ colab.cargo && colab.cargo.nivel ? colab.cargo.nivel : '-' }}
              </span>
            </td>
            <td>
              <span
                :class="[
                  'status-indicator',
                  colab.data_inativado
                    ? 'status-inativo'
                    : (colab.status === 'Ativo' ? 'status-active' : 'status-afastado')
                ]"
              >
                {{ colab.data_inativado ? 'Inativo' : (colab.status || 'Ativo') }}
              </span>
            </td>
            <td>
              <span class="meta-value">{{ colab.meta && colab.meta.calc_meta !== undefined ? colab.meta.calc_meta : '-' }}</span>
            </td>
            <td>{{ colab.meta && colab.meta.tipo_pgto ? colab.meta.tipo_pgto : '-' }}</td>
            <td>
              <button @click="editarColaborador(colab)" class="btn-action">
                <i class="fas fa-edit"></i>
                <span>Editar</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Modal de Edição -->
    <div v-if="showModal" class="modal-overlay" @click="fecharModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3><i class="fas fa-user-edit"></i> Editar Colaborador</h3>
          <button @click="fecharModal" class="btn-close">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="salvarEdicao">
            <div class="form-row">
              <div class="form-group">
                <label><i class="fas fa-user"></i> Nome *</label>
                <input v-model="colaboradorEditando.nome" type="text" disabled placeholder="(não editável)" />
              </div>
              <div class="form-group">
                <label><i class="fas fa-user-tag"></i> Sobrenome *</label>
                <input v-model="colaboradorEditando.sobrenome" type="text" disabled placeholder="(não editável)" />
              </div>
            </div>
            <div class="form-group">
              <label><i class="fas fa-envelope"></i> Email</label>
              <input v-model="colaboradorEditando.email" type="email" disabled placeholder="(não editável)" />
            </div>
            <div class="form-group">
              <label><i class="fas fa-id-card"></i> CPF</label>
              <input v-model="colaboradorEditando.cpf" type="text" disabled placeholder="(não editável)" />
            </div>
            <!-- Campos separados do cargo -->
            <div class="form-group">
              <label><i class="fas fa-briefcase"></i> Nome do Cargo</label>
              <div class="select-wrapper">
                <select v-model="colaboradorEditando.cargo_nome">
                  <option value="">Selecione o nome do cargo</option>
                  <option v-for="nome in opcoesCargoSeparadas.nomes" :key="nome" :value="nome">
                    {{ nome }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label><i class="fas fa-user-tag"></i> Função</label>
              <div class="select-wrapper">
                <select v-model="colaboradorEditando.cargo_funcao">
                  <option value="">Selecione a função</option>
                  <option v-for="funcao in opcoesCargoSeparadas.funcoes" :key="funcao" :value="funcao">
                    {{ funcao }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label><i class="fas fa-users"></i> Equipe</label>
              <div class="select-wrapper">
                <select v-model="colaboradorEditando.cargo_equipe">
                  <option value="">Selecione a equipe</option>
                  <option v-for="equipe in opcoesCargoSeparadas.equipes" :key="equipe" :value="equipe">
                    {{ equipe }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label><i class="fas fa-layer-group"></i> Nível</label>
              <div class="select-wrapper">
                <select v-model="colaboradorEditando.cargo_nivel">
                  <option value="">Selecione o nível</option>
                  <option v-for="nivel in opcoesCargoSeparadas.niveis" :key="nivel" :value="nivel">
                    {{ nivel }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label><i class="fas fa-building"></i> Unidade</label>
              <div class="select-wrapper">
                <select v-model="colaboradorEditando.setor_id">
                  <option v-for="setor in setores" :key="setor.id" :value="setor.id">
                    {{ setor.nome }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label><i class="fas fa-money-bill-wave"></i> Tipo de Pagamento</label>
              <div class="select-wrapper">
                <select v-model="colaboradorEditando.tipo_pgto" class="custom-select-tipo-pgto">
                  <option v-for="opcao in opcoesTipoPgto" :key="opcao" :value="opcao">
                    <span v-if="opcao === 'Pela unidade'">🔢 Pela unidade</span>
                    <span v-else-if="opcao === 'Pelo que realizou'">✅ Pelo que realizou</span>
                    <span v-else>{{ opcao }}</span>
                  </option>
                </select>
              </div>
            </div>
            <div v-if="colaboradorEditando.tipo_pgto" class="form-group">
              <label><i class="fas fa-bullseye"></i> Meta</label>
              <div class="select-wrapper">
                <select v-model="colaboradorEditando.meta" class="custom-select-tipo-pgto">
                  <option v-for="valor in colaboradorEditando.tipo_pgto === 'Pela unidade' ? opcoesValoresUnidade : opcoesValoresRealizados" :key="valor" :value="valor">
                    {{ valor }}
                  </option>
                </select>
              </div>
            </div>
            <!-- Seção de Afastamento -->
            <div class="form-group">
              <label><i class="fas fa-clipboard-list"></i> Motivo do Afastamento</label>
              <select v-model="colaboradorEditando.motivo_afastamento">
                <option value="">Selecione o motivo</option>
                <option value="Férias">Férias</option>
                <option value="Licença Médica">Licença Médica</option>
                <option value="Licença Maternidade">Licença Maternidade</option>
                <option value="Licença Paternidade">Licença Paternidade</option>
                <option value="Licença sem Vencimentos">Licença sem Vencimentos</option>
                <option value="Afastamento INSS">Afastamento INSS</option>
                <option value="Suspensão">Suspensão</option>
                <option value="Capacitação/Treinamento">Capacitação/Treinamento</option>
                <option value="Outros">Outros</option>
              </select>
            </div>
            
            <!-- Campo adicional quando selecionar "Outros" -->
            <div class="form-group" v-if="colaboradorEditando.motivo_afastamento === 'Outros'">
              <label><i class="fas fa-edit"></i> Especifique o motivo</label>
              <textarea v-model="colaboradorEditando.motivo_outros" 
                        placeholder="Descreva o motivo específico"
                        rows="3"></textarea>
            </div>
            
            <div class="form-group">
              <label><i class="fas fa-calendar-times"></i> Data de Afastamento</label>
              <input v-model="colaboradorEditando.data_afastamento" type="date" placeholder="Data do afastamento" />
            </div>
            <div class="form-group">
              <label><i class="fas fa-calendar-check"></i> Data de Retorno</label>
              <input v-model="colaboradorEditando.data_retorno" type="date" placeholder="Data de retorno" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label><i class="fas fa-calendar-plus"></i> Data de Admissão</label>
                <input v-model="colaboradorEditando.data_admissao" type="date" disabled placeholder="(não editável)" />
              </div>
              <div class="form-group">
                <label><i class="fas fa-calendar-minus"></i> Data de Desligamento</label>
                <input v-model="colaboradorEditando.data_inativado" type="date" disabled placeholder="(não editável)" />
              </div>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button type="button" @click="fecharModal" class="btn-secondary">
            <i class="fas fa-times"></i> Cancelar
          </button>
          <button type="submit" @click="salvarEdicao" class="btn-primary" :disabled="salvando">
            <i class="fas fa-save" v-if="!salvando"></i>
            <i class="fas fa-spinner fa-spin" v-if="salvando"></i>
            {{ salvando ? 'Salvando...' : 'Salvar Alterações' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuadroColaboradores',
  data() {
    return {
      colaboradores: [],
      carregando: false,
      erro: null,
      showModal: false,
      colaboradorEditando: {
        id: null,
        nome: '',
        sobrenome: '',
        cargo_id: null,
        // Campos separados do cargo
        cargo_nome: '',
        cargo_funcao: '',
        cargo_equipe: '',
        cargo_nivel: '',
        setor_id: '',
        setores_ids: [],
        // Campos de afastamento
        data_afastamento: '',
        data_retorno: '',
        motivo_afastamento: '',
        motivo_outros: ''
      },
      salvando: false,
      // Listas para os selects
      cargos: [],
      setores: [],
      // Opções separadas do cargo para os selects
      opcoesCargoSeparadas: {
        nomes: [],
        funcoes: [],
        equipes: [],
        niveis: []
      },
      opcoesTipoPgto: [
        'Pela unidade',
        'Pelo que realizou'
      ],
      opcoesValoresRealizados: [
        0, 0.5, 1
      ],
      opcoesValoresUnidade: [
        0, 0.5, 1
      ],
      ordenacao: {
        coluna: '',
        asc: true
      }
    }
  },
  mounted() {
    this.ordenacao.coluna = 'nome'; // Ordena por nome ao abrir
    this.ordenacao.asc = true;
    this.carregarColaboradores();
    this.carregarCargos();
    this.carregarSetores();
    this.carregarOpcoesCargoSeparadas();
  },
  computed: {
    colaboradoresOrdenados() {
      let lista = [...this.colaboradores];
      if (this.ordenacao.coluna === 'nome') {
        lista.sort((a, b) => {
          const nomeA = (a.nome || '').toLowerCase();
          const nomeB = (b.nome || '').toLowerCase();
          if (nomeA < nomeB) return this.ordenacao.asc ? -1 : 1;
          if (nomeA > nomeB) return this.ordenacao.asc ? 1 : -1;
          return 0;
        });
      }
      if (this.ordenacao.coluna === 'unidade') {
        lista.sort((a, b) => {
          const unidadeA = (a.setores?.[0]?.nome || '').toLowerCase();
          const unidadeB = (b.setores?.[0]?.nome || '').toLowerCase();
          if (unidadeA < unidadeB) return this.ordenacao.asc ? -1 : 1;
          if (unidadeA > unidadeB) return this.ordenacao.asc ? 1 : -1;
          return 0;
        });
      }
      return lista;
    }
  },
  methods: {
    async carregarColaboradores() {
      this.carregando = true;
      this.erro = null;
      try {
        console.log('Buscando dados do backend...');
    const response = await fetch('/quadro_colaboradores/');
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Dados recebidos:', data);
        this.colaboradores = data;
        
        if (data.length === 0) {
          console.log('Nenhum colaborador encontrado');
        }
      } catch (e) {
        console.error('Erro ao carregar colaboradores:', e);
        this.erro = 'Erro ao carregar colaboradores: ' + e.message;
        this.colaboradores = [];
      }
      this.carregando = false;
    },
    editarColaborador(colaborador) {
      console.log('Editando colaborador:', colaborador);
      console.log('Setores disponíveis:', this.setores);
      console.log('Setores do colaborador:', colaborador.setores);
      console.log('Data afastamento original:', colaborador.data_afastamento);
      console.log('Data retorno original:', colaborador.data_retorno);
      console.log('Motivo afastamento original:', colaborador.motivo_afastamento);
      
      // Preenche setor_id - agora os setores vêm como objetos {id, nome}
      let setorId = '';
      if (colaborador.setores && colaborador.setores.length > 0) {
        // Agora os setores vêm como objetos com id e nome
        setorId = colaborador.setores[0].id;
      }
      
      console.log('Setor ID selecionado para o modal:', setorId);
      
      this.colaboradorEditando = {
        id: colaborador.id,
        nome: colaborador.nome || '',
        sobrenome: colaborador.sobrenome || '',
        cargo_id: colaborador.cargo?.id || null,
        // Campos separados do cargo
        cargo_nome: colaborador.cargo?.nome || '',
        cargo_funcao: colaborador.cargo?.funcao || '',
        cargo_equipe: colaborador.cargo?.equipe || '',
        cargo_nivel: colaborador.cargo?.nivel || '',
        // Preenche setor_id como id do setor, para select único
        setor_id: setorId,
        sistemas_ids: colaborador.sistemas?.map(s => s.id) || [],
        grupos_email_ids: colaborador.grupos_email?.map(g => g.id) || [],
        grupos_pasta_ids: colaborador.grupos_pasta?.map(g => g.id) || [],
        celular: colaborador.celular || '',
        email: colaborador.email ? colaborador.email : '',
        data_admissao: colaborador.data_admissao || '',
        data_inativado: colaborador.data_inativado || '',
        cpf: colaborador.cpf ? colaborador.cpf : '',
        data_afastamento: colaborador.data_afastamento || '',
        tipo_contrato: colaborador.tipo_contrato || '',
        data_retorno: colaborador.data_retorno || '',
        // Tratar motivo_afastamento - se começar com "Outros:", separar
        motivo_afastamento: colaborador.motivo_afastamento && colaborador.motivo_afastamento.startsWith('Outros:') 
          ? 'Outros' 
          : colaborador.motivo_afastamento || '',
        motivo_outros: colaborador.motivo_afastamento && colaborador.motivo_afastamento.startsWith('Outros:')
          ? colaborador.motivo_afastamento.replace('Outros:', '').trim()
          : '',
        meta: colaborador.meta?.calc_meta ?? '',
        tipo_pgto: colaborador.meta?.tipo_pgto ?? ''
      };
      
      console.log('Objeto colaboradorEditando criado:', this.colaboradorEditando);
      console.log('Data afastamento formatada:', this.colaboradorEditando.data_afastamento);
      console.log('Data retorno formatada:', this.colaboradorEditando.data_retorno);
      console.log('Motivo processado:', this.colaboradorEditando.motivo_afastamento);
      console.log('Motivo outros:', this.colaboradorEditando.motivo_outros);
      
      this.showModal = true;
    },
    
    fecharModal() {
      this.showModal = false;
      this.colaboradorEditando = {
        id: null,
        nome: '',
        sobrenome: '',
        cargo_id: null,
        // Campos separados do cargo
        cargo_nome: '',
        cargo_funcao: '',
        cargo_equipe: '',
        cargo_nivel: '',
        setor_id: '',
        setores_ids: []
      };
    },
    
    async salvarEdicao() {
      this.salvando = true;
      try {
        // Validações básicas
        if (!this.colaboradorEditando.nome || this.colaboradorEditando.nome.trim() === '') {
          alert('O campo nome é obrigatório!');
          this.salvando = false;
          return;
        }
        if (!this.colaboradorEditando.sobrenome || this.colaboradorEditando.sobrenome.trim() === '') {
          alert('O campo sobrenome é obrigatório!');
          this.salvando = false;
          return;
        }

        // Validação da meta se fornecida
        if (this.colaboradorEditando.meta !== null && this.colaboradorEditando.meta !== '' && this.colaboradorEditando.meta !== undefined) {
          const metaValor = parseFloat(this.colaboradorEditando.meta);
          if (isNaN(metaValor) || ![0, 0.5, 1].includes(metaValor)) {
            alert('Meta deve ser um dos valores: 0, 0.5 ou 1');
            this.salvando = false;
            return;
          }
        }

        // Validação do tipo de pagamento se meta for fornecida
        if (this.colaboradorEditando.meta && !this.colaboradorEditando.tipo_pgto) {
          alert('Tipo de pagamento é obrigatório quando uma meta é definida!');
          this.salvando = false;
          return;
        }

        const payload = {
          nome: this.colaboradorEditando.nome.trim(),
          sobrenome: this.colaboradorEditando.sobrenome.trim(),
          cargo_nome: this.colaboradorEditando.cargo_nome || null,
          cargo_funcao: this.colaboradorEditando.cargo_funcao || null,
          cargo_equipe: this.colaboradorEditando.cargo_equipe || null,
          cargo_nivel: this.colaboradorEditando.cargo_nivel || null,
          // Backend espera setores_ids como array
          setores_ids: this.colaboradorEditando.setor_id ? [parseInt(this.colaboradorEditando.setor_id)] : [],
          sistemas_ids: this.colaboradorEditando.sistemas_ids || [],
          grupos_email_ids: this.colaboradorEditando.grupos_email_ids || [],
          grupos_pasta_ids: this.colaboradorEditando.grupos_pasta_ids || [],
          celular: this.colaboradorEditando.celular || '',
          email: this.colaboradorEditando.email || '',
          cpf: this.colaboradorEditando.cpf || '',
          data_admissao: this.colaboradorEditando.data_admissao || '',
          data_inativado: this.colaboradorEditando.data_inativado || '',
          data_afastamento: this.colaboradorEditando.data_afastamento || '',
          tipo_contrato: this.colaboradorEditando.tipo_contrato || '',
          data_retorno: this.colaboradorEditando.data_retorno || '',
          // Combinar motivo padrão com especificação quando for "Outros"
          motivo_afastamento: this.colaboradorEditando.motivo_afastamento === 'Outros' 
            ? `Outros: ${this.colaboradorEditando.motivo_outros || ''}`.trim()
            : this.colaboradorEditando.motivo_afastamento || '',
          // Garantir que meta seja enviada como número (float) e tipo_pgto como string
          meta: this.colaboradorEditando.meta ? parseFloat(this.colaboradorEditando.meta) : null,
          tipo_pgto: this.colaboradorEditando.tipo_pgto || null
        };

        console.log('Payload sendo enviado:', payload);
        console.log('Dados do colaborador sendo editado:', this.colaboradorEditando);
        console.log('=== PAYLOAD DEBUG ===');
        console.log('Payload completo enviado no PUT:', JSON.stringify(payload, null, 2));
        console.log('Tipo da meta:', typeof payload.meta, 'Valor:', payload.meta);
        console.log('Tipo do tipo_pgto:', typeof payload.tipo_pgto, 'Valor:', payload.tipo_pgto);
        console.log('setores_ids:', payload.setores_ids);
        console.log('=====================');
        
        const response = await fetch(`/funcionarios/${this.colaboradorEditando.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
          // Tenta ler detalhes do erro do backend (FastAPI retorna JSON com detalhes)
          let errorDetails = '';
          try {
            const errorData = await response.json();
            errorDetails = JSON.stringify(errorData, null, 2);
          } catch (e) {
            errorDetails = await response.text();
          }
          throw new Error(`Erro ${response.status}: ${errorDetails}`);
        }
        
        // Recarregar a tabela
        await this.carregarColaboradores();
        
        // Fechar modal
        this.fecharModal();
        
        console.log('Colaborador atualizado com sucesso');
        
      } catch (error) {
        console.error('Erro ao salvar colaborador:', error);
        alert('Erro ao salvar colaborador: ' + error.message);
      }
      this.salvando = false;
    },
    
    // Métodos para carregar listas de opções
    async carregarCargos() {
      try {
    const response = await fetch('/cargos/');
        this.cargos = await response.json();
      } catch (e) {
        console.error('Erro ao carregar cargos:', e);
      }
    },
    
    async carregarSetores() {
      try {
    const response = await fetch('/setores/');
        this.setores = await response.json();
      } catch (e) {
        console.error('Erro ao carregar setores:', e);
      }
    },
    
    async carregarOpcoesCargoSeparadas() {
      try {
        // Carrega opções distintas de cada campo
        const [nomes, funcoes, equipes, niveis] = await Promise.all([
          fetch('/cargos/nomes').then(r => r.json()),
          fetch('/cargos/funcoes').then(r => r.json()),
          fetch('/cargos/equipes').then(r => r.json()),
          fetch('/cargos/niveis').then(r => r.json())
        ]);
        
        // Popula o objeto opcoesCargoSeparadas
        this.opcoesCargoSeparadas = {
          nomes,
          funcoes,
          equipes,
          niveis
        };
        
        console.log('Opções de cargo carregadas:', this.opcoesCargoSeparadas);
      } catch (e) {
        console.error('Erro ao carregar opções de cargo:', e);
      }
    },
    ordenarPor(coluna) {
      if (this.ordenacao.coluna === coluna) {
        this.ordenacao.asc = !this.ordenacao.asc;
      } else {
        this.ordenacao.coluna = coluna;
        this.ordenacao.asc = true;
      }
    }
  }
}
</script>

<style scoped>
/* Import Font Awesome se não estiver já incluído */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

.dashboard-colaboradores {
  padding: 24px;
  background: #f8fafc;
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 24px;
  background: #fff; /* Removido gradiente */
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border: 1px solid #e2e8f0;
}

.header-section h2 {
  color: #1e293b;
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-section h2 i {
  color: #3b82f6;
  font-size: 24px;
}

.stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  background: #2563eb; /* Azul sólido */
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.loading-container {
  text-align: center;
  padding: 80px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  text-align: center;
  padding: 48px;
  background: #fecaca; /* Sólido */
  border: 2px solid #f87171;
  border-radius: 16px;
  color: #dc2626;
}

.error-container i {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.btn-retry {
  background: #dc2626; /* Sólido */
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  margin-top: 20px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25);
}

.btn-retry:hover {
  background: #b91c1c; /* Sólido */
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(220, 38, 38, 0.35);
}

.table-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
}

.modern-table th {
  background: #1e293b; /* Sólido */
  color: white;
  padding: 20px 16px;
  text-align: left;
  font-weight: 700;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.modern-table th i {
  margin-right: 8px;
  opacity: 0.9;
}

.modern-table td {
  padding: 18px 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
  vertical-align: middle;
  transition: all 0.2s ease;
}

.data-row:hover {
  background: #e2e8f0; /* Sólido */
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.row-even {
  background: #fafbfc;
}

.name-cell {
  min-width: 200px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  background: #2563eb; /* Sólido */
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tag-setor {
  background: #dbeafe; /* Sólido */
  color: #1e40af;
  border: 1px solid #93c5fd;
}

.tag-more {
  background: #e5e7eb; /* Sólido */
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-cargo {
  background: #dbeafe; /* Sólido */
  color: #0369a1;
  border: 1px solid #7dd3fc;
}

.badge-equipe {
  background: #dcfce7; /* Sólido */
  color: #15803d;
  border: 1px solid #86efac;
}

.level-indicator {
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.level-1, .level-junior {
  background: #fde68a; /* Sólido */
  color: #92400e;
  border: 1px solid #f59e0b;
}

.level-2, .level-pleno {
  background: #c7d2fe; /* Sólido */
  color: #4338ca;
  border: 1px solid #818cf8;
}

.level-3, .level-senior {
  background: #fbcfe8; /* Sólido */
  color: #be185d;
  border: 1px solid #f472b6;
}

.level-none {
  background: #e5e7eb; /* Sólido */
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.status-indicator {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-active {
  background: #bbf7d0; /* Sólido */
  color: #166534;
  border: 1px solid #4ade80;
}

.status-afastado {
  background: #fde68a; /* Sólido */
  color: #92400e;
  border: 1px solid #f59e0b;
}

.status-inativo {
  background: #fca5a5; /* Sólido */
  color: #991b1b;
  border: 1px solid #f87171;
}

.meta-value {
  font-weight: 700;
  color: #059669;
  font-size: 15px;
}

.no-data {
  color: #9ca3af;
  font-style: italic;
  font-size: 13px;
}

.btn-action {
  background: #2563eb; /* Sólido */
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  min-width: 100px;
  justify-content: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
}

.btn-action:hover {
  background: #1e40af; /* Sólido */
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.35);
}

.empty-row td {
  padding: 80px 20px;
  text-align: center;
}

.empty-state {
  color: #6b7280;
}

.empty-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #374151;
}

.empty-state small {
  font-size: 14px;
  color: #9ca3af;
}

/* Modal Styles Modernos e Profissionais */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(15, 23, 42, 0.25);
  animation: slideUp 0.4s ease;
  border: 1px solid #e2e8f0;
}

@keyframes slideUp {
  from { 
    transform: translateY(60px) scale(0.9);
    opacity: 0;
  }
  to { 
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px 36px;
  border-bottom: 2px solid #e2e8f0;
  background: #f8fafc; /* Sólido */
  border-radius: 20px 20px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-header h3 i {
  color: #3b82f6;
  font-size: 20px;
}

.btn-close {
  background: #ef4444; /* Sólido */
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}

.btn-close:hover {
  background: #b91c1c; /* Sólido */
  transform: scale(1.1) rotate(90deg);
}

.modal-body {
  padding: 36px;
  background: #fafbfc;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 700;
  color: #1e293b;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group label i {
  color: #3b82f6;
  font-size: 14px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background: white;
  font-weight: 500;
}

.form-group textarea {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background: white;
  font-weight: 500;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background: #fafbfc;
  transform: translateY(-1px);
}

.select-wrapper {
  position: relative;
}

.select-wrapper::after {
  content: '\f107';
  font-family: 'Font Awesome 6 Free';
  font-weight: 900;
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  pointer-events: none;
}

.select-wrapper.multi::after {
  display: none;
}

.select-wrapper select {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  box-sizing: border-box;
  background: white;
  appearance: none;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.select-wrapper select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background: #fafbfc;
  transform: translateY(-1px);
}

.select-wrapper.multi select {
  height: 140px;
  padding: 12px;
}

.select-wrapper.multi select option {
  padding: 10px;
  margin: 2px 0;
  border-radius: 6px;
  font-weight: 500;
}

.select-wrapper.multi select option:checked {
  background: #2563eb; /* Sólido */
  color: white;
}

.form-group small {
  display: block;
  margin-top: 8px;
  color: #64748b;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.form-group small i {
  color: #3b82f6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 28px 36px;
  border-top: 2px solid #e2e8f0;
  background: #f8fafc; /* Sólido */
  border-radius: 0 0 20px 20px;
}

.btn-secondary {
  background: #64748b; /* Sólido */
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(100, 116, 139, 0.25);
}

.btn-secondary:hover {
  background: #334155; /* Sólido */
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(100, 116, 139, 0.35);
}

.btn-primary {
  background: #059669; /* Sólido */
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  min-width: 180px;
  justify-content: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
}

.btn-primary:hover:not(:disabled) {
  background: #065f46; /* Sólido */
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(5, 150, 105, 0.35);
}

.btn-primary:disabled {
  background: #9ca3af; /* Sólido */
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.fa-spin {
  animation: fa-spin 1s infinite linear;
}

@keyframes fa-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Estilos personalizados para o select de tipo de pagamento */
.custom-select-tipo-pgto {
  position: relative;
  padding-left: 40px;
  padding-right: 40px;
  height: 48px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: #dbeafe; /* Sólido */
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  appearance: none;
  transition: all 0.3s ease;
}

.custom-select-tipo-pgto:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background: #fafbfc;
}

.custom-select-tipo-pgto option {
  padding: 10px;
  margin: 2px 0;
  border-radius: 6px;
  font-weight: 500;
  background: #dbeafe;
  color: #0369a1;
}
</style>
