<template>
  <div class="funcionarios-container">
    <!-- Header Premium -->
    <div class="header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-title">
            <h1>
              <i class="fas fa-users-cog header-icon"></i>
              Gestão de Funcionários
            </h1>
          </div>
        </div>
        <div class="header-right">
          <div class="controls-group">
            <div class="filter-control">
              <label class="toggle-switch">
                <input type="checkbox" v-model="somenteAtivos" />
                <span class="slider"></span>
                <span class="toggle-text">Apenas Ativos</span>
              </label>
            </div>
            <div class="search-control">
              <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input 
                  v-model="buscaFuncionario" 
                  @input="debouncedBusca"
                  placeholder="Buscar funcionário..." 
                  class="search-input" 
                />
                <button v-if="buscaFuncionario" @click="buscaFuncionario = ''" class="clear-search">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            <div class="action-buttons">
              <div class="view-toggle">
                <button 
                  class="toggle-btn" 
                  :class="{ active: viewMode === 'table' }"
                  @click="viewMode = 'table'"
                >
                  <i class="fas fa-table"></i>
                </button>
                <button 
                  class="toggle-btn" 
                  :class="{ active: viewMode === 'cards' }"
                  @click="viewMode = 'cards'"
                >
                  <i class="fas fa-th-large"></i>
                </button>
              </div>
              <button class="btn-primary" @click="abrirModalAdicionar">
                <i class="fas fa-plus"></i>
                <span>Adicionar</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Stats Dashboard -->
      <div class="stats-dashboard">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ loadingStates.funcionarios ? '...' : funcionarios.length }}</span>
            <span class="stat-label">Total</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon active">
            <i class="fas fa-user-check"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ loadingStates.funcionarios ? '...' : funcionariosAtivos.length }}</span>
            <span class="stat-label">Ativos</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon inactive">
            <i class="fas fa-user-times"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ loadingStates.funcionarios ? '...' : (funcionarios.length - funcionariosAtivos.length) }}</span>
            <span class="stat-label">Inativos</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-filter"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ loadingStates.funcionarios ? '...' : funcionariosFiltrados.length }}</span>
            <span class="stat-label">Filtrados</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Conteúdo Principal -->
    <div class="content-area">
      <!-- Visualização em Tabela -->
      <div v-if="viewMode === 'table'" class="table-view">
        <div v-if="loadingStates.funcionarios && funcionarios.length === 0" class="loading-indicator">
          <div class="spinner"></div>
          <span>Carregando funcionários...</span>
        </div>
        <div v-else class="table-container">
          <!-- Loading overlay sutil se ainda carregando grupos -->
          <div v-if="loadingStates.grupos" class="loading-overlay">
            <div class="mini-spinner"></div>
          </div>
          <table class="responsive-table">
      <thead>
        <tr>
          <th class="col-nome" @click="toggleOrdenacaoNome" style="cursor:pointer">
            Nome
            <span v-if="ordenacaoNome === 'asc'">▲</span>
            <span v-else>▼</span>
          </th>
          <th class="col-sobrenome">Sobrenome</th>
          <th class="col-admissao">Data de Admissão</th>
          <th class="col-desligamento">Data de Desligamento</th>
          <th class="col-celular">Celular</th>
          <th class="col-email">E-mail</th>
          <th class="col-grupo-email">Grupo E-mail</th>
          <th class="col-grupo-whatsapp">Grupo WhatsApp</th>
          <th class="col-pastas">Pastas</th>
          <th class="col-setor">Setor</th>
          <th class="col-cargo">Cargo</th>
          <th class="col-sistemas">Sistemas</th>
          <th class="col-acoes">Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="func in funcionariosFiltrados" :key="func.id">
          <td class="col-nome" :class="['clicavel', celulasExpandidas.has('nome-' + func.id) ? 'expandida' : '']" @click="toggleCelula('nome-' + func.id)">
            {{ func.nome }}
          </td>
          <td class="col-sobrenome" :class="['clicavel', celulasExpandidas.has('sobrenome-' + func.id) ? 'expandida' : '']" @click="toggleCelula('sobrenome-' + func.id)">
            {{ func.sobrenome }}
          </td>
          <td class="col-admissao">
            {{ func.data_admissao ? func.data_admissao.split('-').reverse().join('/') : '—' }}
          </td>
          <td class="col-desligamento">
            {{ func.data_inativado ? func.data_inativado.split('-').reverse().join('/') : '—' }}
          </td>
          <td class="col-celular" :class="['clicavel', celulasExpandidas.has('celular-' + func.id) ? 'expandida' : '']" @click="toggleCelula('celular-' + func.id)">
            {{ func.celular }}
          </td>
          <td class="col-email" :class="['clicavel', celulasExpandidas.has('email-' + func.id) ? 'expandida' : '']" @click="toggleCelula('email-' + func.id)">
            {{ func.email }}
          </td>
          <td class="col-grupo-email" :class="['clicavel', celulasExpandidas.has('grupos-' + func.id) ? 'expandida' : '']" @click="toggleCelula('grupos-' + func.id)">
            <span v-if="func.grupos_email && func.grupos_email.length">
              {{ func.grupos_email.map(g => g.nome).join(', ') }}
            </span>
            <span v-else>—</span>
          </td>
          <td class="col-grupo-whatsapp" :class="['clicavel', celulasExpandidas.has('grupos-whatsapp-' + func.id) ? 'expandida' : '']" @click="toggleCelula('grupos-whatsapp-' + func.id)">
            <span v-if="func.grupos_whatsapp && func.grupos_whatsapp.length">
              {{ func.grupos_whatsapp.map(g => g.nome).join(', ') }}
            </span>
            <span v-else>—</span>
          </td>
          <td class="col-pastas" :class="['clicavel', celulasExpandidas.has('grupos-pasta-' + func.id) ? 'expandida' : '']" @click="toggleCelula('grupos-pasta-' + func.id)">
            <span v-if="func.grupos_pasta && func.grupos_pasta.length">
              {{ func.grupos_pasta.map(g => g.nome).join(', ') }}
            </span>
            <span v-else>—</span>
          </td>
          <td class="col-setor" :class="['clicavel', celulasExpandidas.has('setores-' + func.id) ? 'expandida' : '']" @click="toggleCelula('setores-' + func.id)">
            <span v-if="func.setores && func.setores.length">
              {{ func.setores.map(s => s.nome).join(', ') }}
            </span>
            <span v-else>—</span>
          </td>
          <td class="col-cargo" :class="['clicavel', celulasExpandidas.has('cargo-' + func.id) ? 'expandida' : '']" @click="toggleCelula('cargo-' + func.id)">
            {{ func.cargo && typeof func.cargo === 'object' && func.cargo.nome ? func.cargo.nome : (func.cargo || '—') }}
          </td>
          <td class="col-sistemas" :class="['clicavel', celulasExpandidas.has('sistemas-' + func.id) ? 'expandida' : '']" @click="toggleCelula('sistemas-' + func.id)">
            <span v-if="func.sistemas && func.sistemas.length">
              {{ func.sistemas.map(s => `${s.nome} (${s.status})`).join(', ') }}
            </span>
            <span v-else>Nenhum sistema vinculado</span>
          </td>
          <td class="col-acoes">
            <div class="action-buttons-table">
              <button v-if="$auth && ($auth.hasPermission('editar_colaborador') || $auth.hasPermission('adm'))" class="btn-editar" @click="abrirEditar(func)">
                <i class="fas fa-edit"></i>
              </button>
              <button v-if="$auth && ($auth.hasPermission('excluir_colaborador') || $auth.hasPermission('adm'))" class="btn-excluir" @click="excluirFuncionario(func.id)">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
        </div>
      </div>

      <!-- Visualização em Cards -->
      <div v-else class="cards-view">
        <div class="cards-grid">
          <div v-for="func in funcionariosFiltrados" :key="func.id" class="employee-card">
            <div class="card-header">
              <div class="employee-avatar">
                {{ (func.nome || 'U').charAt(0).toUpperCase() }}
              </div>
              <div class="employee-info">
                <h3 class="employee-name">{{ func.nome }} {{ func.sobrenome }}</h3>
                <p class="employee-cargo">{{ func.cargo || 'Sem cargo definido' }}</p>
              </div>
              <div class="employee-status">
                <span :class="['status-badge', func.data_inativado ? 'inactive' : 'active']">
                  {{ func.data_inativado ? 'Inativo' : 'Ativo' }}
                </span>
              </div>
            </div>
            
            <div class="card-content">
              <div class="info-row">
                <div class="info-item">
                  <i class="fas fa-envelope"></i>
                  <span>{{ func.email || '—' }}</span>
                </div>
                <div class="info-item">
                  <i class="fas fa-phone"></i>
                  <span>{{ func.celular || '—' }}</span>
                </div>
              </div>
              
              <div class="info-row">
                <div class="info-item">
                  <i class="fas fa-calendar-alt"></i>
                  <span>{{ func.data_admissao ? func.data_admissao.split('-').reverse().join('/') : '—' }}</span>
                </div>
                <div class="info-item" v-if="func.data_inativado">
                  <i class="fas fa-calendar-times"></i>
                  <span>{{ func.data_inativado.split('-').reverse().join('/') }}</span>
                </div>
              </div>
              
              <div v-if="func.setores && func.setores.length" class="tags-section">
                <label>Setores:</label>
                <div class="tags">
                  <span v-for="setor in func.setores.slice(0, 3)" :key="setor.id" class="tag">
                    {{ setor.nome }}
                  </span>
                  <span v-if="func.setores.length > 3" class="tag more">
                    +{{ func.setores.length - 3 }}
                  </span>
                </div>
              </div>
              
              <div v-if="func.sistemas && func.sistemas.length" class="tags-section">
                <label>Sistemas:</label>
                <div class="tags">
                  <span v-for="sistema in func.sistemas.slice(0, 2)" :key="sistema.id" class="tag system">
                    {{ sistema.nome }}
                  </span>
                  <span v-if="func.sistemas.length > 2" class="tag more">
                    +{{ func.sistemas.length - 2 }}
                  </span>
                </div>
              </div>
            </div>
            
              <div class="card-actions">
              <button v-if="$auth && ($auth.hasPermission('editar_colaborador') || $auth.hasPermission('adm'))" class="btn-edit" @click="abrirEditar(func)">
                <i class="fas fa-edit"></i>
                Editar
              </button>
              <button v-if="$auth && ($auth.hasPermission('excluir_colaborador') || $auth.hasPermission('adm'))" class="btn-delete" @click="excluirFuncionario(func.id)">
                <i class="fas fa-trash"></i>
                Excluir
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal usando Teleport para evitar problemas de overflow -->
    <Teleport to="body">
      <div v-if="showForm" class="modal-overlay" @click.self="fecharModal">
        <div class="form-modal">
        <h3>{{ editando ? 'Editar Funcionário' : 'Adicionar Funcionário' }}</h3>
        <form @submit.prevent="editando ? salvarEdicaoFuncionario() : cadastrarFuncionario()">
          <!-- Bloco principal do formulário -->
          <div class="form-grid">
            <div>
              <label>Nome</label>
              <input v-model="form.nome" placeholder="Nome" required />
            </div>
            <div>
              <label>Sobrenome</label>
              <input v-model="form.sobrenome" placeholder="Sobrenome" required />
            </div>
            <div v-if="!contratoEspecial">
              <label>Celular</label>
              <input v-model="form.celular" placeholder="Celular" />
            </div>
            <div v-if="!contratoEspecial">
              <label>CPF</label>
              <input v-model="form.cpf" placeholder="CPF" :required="contratoObrigatorio" />
            </div>
            <div v-if="!contratoEspecial">
              <label>ID Eyal</label>
              <input v-model="form.id_eyal" placeholder="ID Eyal" />
            </div>
            <div>
              <label>Data de Admissão</label>
              <input type="date" v-model="form.data_admissao" />
            </div>
            <div>
              <label>Tipo de Contrato</label>
              <select v-model="form.tipo_contrato" class="select-tipo-contrato">
                <option value="">Selecione...</option>
                <option value="CLT">CLT</option>
                <option value="PJ">PJ</option>
                <option value="Genérico">Genérico</option>
                <option value="Terceirizado">Terceirizado</option>
              </select>
            </div>
            <div style="grid-column: span 2;">
              <label>E-mail</label>
              <input v-model="form.email" placeholder="E-mail" required type="email" />
            </div>
            <div v-if="editando" style="grid-column: span 2;">
              <label>Data de Desligamento</label>
              <input type="date" v-model="form.data_inativado" />
              <button type="button" @click="inativarFuncionario" style="width: 220px; margin-top: 8px;">Inativar hoje</button>
            </div>
            <div v-if="editando">
              <label>Data de Afastamento</label>
              <input type="date" v-model="form.data_afastamento" />
            </div>
            <div v-if="editando">
              <label>Data de Retorno</label>
              <input type="date" v-model="form.data_retorno" />
            </div>
          </div>
          <hr class="modal-divider" />
          <div class="modal-row selects-2x2">
            <div class="modal-col">
              <div class="select-group">
                <label>Grupos de E-mail:</label>
                <div class="multi-select-container">
                  <div class="selected-items">
                    <span v-for="id in form.grupos_email_ids" :key="id" class="selected-chip" @click="removeGrupo(id)">
                      {{ getGrupoNome(id) }}
                    </span>
                  </div>
                  <select v-model="novoGrupoId" @change="addGrupo" class="multi-select">
                    <option value="">+ Adicionar grupo...</option>
                    <option v-for="grupo in gruposEmailDisponiveis" :key="grupo.id" :value="grupo.id">
                      {{ grupo.nome }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
            <div class="modal-col">
              <div class="select-group">
                <label>Grupos de Pastas:</label>
                <div class="multi-select-container">
                  <div class="selected-items">
                    <span v-for="id in form.grupos_pasta_ids" :key="id" class="selected-chip" @click="removeGrupoPasta(id)">
                      {{ getGrupoPastaNome(id) }}
                    </span>
                  </div>
                  <select v-model="novoGrupoPastaId" @change="addGrupoPasta" class="multi-select">
                    <option value="">+ Adicionar grupo de pastas...</option>
                    <option v-for="grupo in gruposPastaDisponiveis" :key="grupo.id" :value="grupo.id">
                      {{ grupo.nome }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-row selects-2x2">
            <div class="modal-col">
              <div class="select-group">
                <label>Setores:</label>
                <div class="multi-select-container">
                  <div class="selected-items">
                    <span v-for="id in form.setores_ids" :key="id" class="selected-chip" @click="removeSetor(id)">
                      {{ getSetorNome(id) }}
                    </span>
                  </div>
                  <select v-model="novoSetorId" @change="addSetor" class="multi-select">
                    <option value="">+ Adicionar setor...</option>
                    <option v-for="setor in setoresDisponiveis" :key="setor.id" :value="setor.id">
                      {{ setor.nome }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
            <div class="modal-col">
              <div class="select-group">
                <label>Sistemas:</label>
                <div class="multi-select-container">
                  <div class="selected-items">
                    <span v-for="id in form.sistemas_ids" :key="id" class="selected-chip" @click="removeSistema(id)">
                      {{ getSistemaNome(id) }}
                    </span>
                  </div>
                  <select v-model="novoSistemaId" @change="addSistema" class="multi-select">
                    <option value="">+ Adicionar sistema...</option>
                    <option v-for="sistema in sistemasDisponiveis" :key="sistema.id" :value="sistema.id">
                      {{ sistema.nome }} ({{ sistema.status }})
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-row selects-2x2">
            <div class="modal-col">
              <div class="select-group">
                <label>Cargo:</label>
                <CargoMultiSelect
                  v-model="form.cargo_id"
                  :multiple="false"
                />
              </div>
            </div>
            <div class="modal-col">
              <div class="select-group">
                <label>Grupos de WhatsApp:</label>
                <div class="multi-select-container">
                  <div class="selected-items">
                    <span v-for="id in form.grupos_whatsapp_ids" :key="id" class="selected-chip" @click="removeGrupoWhatsapp(id)">
                      {{ getGrupoWhatsappNome(id) }}
                    </span>
                  </div>
                  <select v-model="novoGrupoWhatsappId" @change="addGrupoWhatsapp" class="multi-select">
                    <option value="">+ Adicionar grupo de WhatsApp...</option>
                    <option v-for="grupo in gruposWhatsappDisponiveis" :key="grupo.id" :value="grupo.id">
                      {{ grupo.nome }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-cadastrar">Salvar</button>
            <button type="button" @click="fecharModal">Cancelar</button>
          </div>
        </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../api';
import CargoMultiSelect from '../components/CargoMultiSelect.vue';

export default {
  components: { CargoMultiSelect },
  data() {
    return {
      viewMode: 'table', // 'table' ou 'cards'
      funcionarios: [],
      setores: [],
      sistemas: [],
      showForm: false,
      editando: false,
      funcionarioEditId: null,
      
      // Cache para otimização
      _cachedFiltro: '',
      _cachedAtivos: true,
      _cachedOrdenacao: 'asc',
      _cachedResultado: [],
      
      // Debounce timer
      debounceTimer: null,
      isLoading: false,
      loadingStates: {
        funcionarios: false,
        setores: false,
        sistemas: false,
        grupos: false
      },
      
      form: {
        nome: '',
        sobrenome: '',
        celular: '',
        email: '',
        cpf: '',
        id_eyal: '',
        tipo_contrato: '',
        data_afastamento: '',
        data_retorno: '',
        grupo_email: '',
        setores_ids: [],
        sistemas_ids: [],
        grupos_email_ids: [],
        grupos_pasta_ids: [],
        grupos_whatsapp_ids: [],
        data_admissao: '',
        data_inativado: '',
        cargo_id: null
      },
      gruposEmail: [],
      gruposPasta: [],
      gruposWhatsapp: [],
      buscaFuncionario: '',
      celulasExpandidas: new Set(), 
      novoGrupoId: '',
      novoSetorId: '',
      novoSistemaId: '',
      novoGrupoPastaId: '',
      novoGrupoWhatsappId: '',
      ordenacaoNome: 'asc',
      somenteAtivos: true, // filtro padrão ativado
    }
  },
  computed: {
    funcionariosAtivos() {
      return this.funcionarios.filter(f => !f.data_inativado);
    },
    
    funcionariosFiltrados() {
      // Cache para evitar reprocessamento
      if (this._cachedFiltro === this.buscaFuncionario && 
          this._cachedAtivos === this.somenteAtivos &&
          this._cachedOrdenacao === this.ordenacaoNome) {
        return this._cachedResultado || [];
      }

      let lista = this.funcionarios;
      
      if (this.buscaFuncionario && this.buscaFuncionario.length > 2) {
        const busca = this.buscaFuncionario.toLowerCase();
        lista = lista.filter(f => {
          const nomeCompleto = `${f.nome || ''} ${f.sobrenome || ''}`.toLowerCase();
          const email = (f.email || '').toLowerCase();
          
          if (nomeCompleto.includes(busca) || email.includes(busca)) {
            return true;
          }
          
          // Busca mais detalhada só se necessário
          let cargoNome = '';
          if (typeof f.cargo === 'string') {
            cargoNome = f.cargo;
          } else if (f.cargo && typeof f.cargo === 'object') {
            cargoNome = f.cargo.nome || f.cargo.cargo_nome || f.cargo.funcao || '';
          }
          const cargo = cargoNome.toLowerCase();
          const celular = (f.celular || '').toLowerCase();
          
          return cargo.includes(busca) || celular.includes(busca);
        });
      }
      
      // Filtra ativos/inativos
      if (this.somenteAtivos) {
        lista = lista.filter(f => !f.data_inativado);
      }
      
      // Ordenação simples
      lista.sort((a, b) => {
        const nomeA = (a.nome || '').toLowerCase();
        const nomeB = (b.nome || '').toLowerCase();
        return this.ordenacaoNome === 'asc' 
          ? nomeA.localeCompare(nomeB)
          : nomeB.localeCompare(nomeA);
      });

      // Cache do resultado
      this._cachedFiltro = this.buscaFuncionario;
      this._cachedAtivos = this.somenteAtivos;
      this._cachedOrdenacao = this.ordenacaoNome;
      this._cachedResultado = lista;
      
      return lista;
    },
    
    // Computadas otimizadas para selects
    gruposEmailDisponiveis() {
      if (!this.gruposEmail.length) return [];
      return this.gruposEmail.filter(grupo => 
        !this.form.grupos_email_ids.includes(grupo.id)
      );
    },
    
    gruposPastaDisponiveis() {
      if (!this.gruposPasta.length) return [];
      const gruposPastaIds = Array.isArray(this.form.grupos_pasta_ids) ? this.form.grupos_pasta_ids : [];
      return this.gruposPasta.filter(grupo => 
        !gruposPastaIds.includes(grupo.id)
      );
    },
    
    gruposWhatsappDisponiveis() {
      console.log('Computed gruposWhatsappDisponiveis executada');
      console.log('this.gruposWhatsapp:', this.gruposWhatsapp);
      console.log('this.form.grupos_whatsapp_ids:', this.form.grupos_whatsapp_ids);
      if (!this.gruposWhatsapp.length) return [];
      const gruposWhatsappIds = Array.isArray(this.form.grupos_whatsapp_ids) ? this.form.grupos_whatsapp_ids : [];
      const result = this.gruposWhatsapp.filter(grupo => 
        !gruposWhatsappIds.includes(grupo.id)
      ).slice().sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
      console.log('Grupos disponíveis resultado:', result);
      return result;
    },
    
    setoresDisponiveis() {
      if (!this.setores.length) return [];
      return this.setores.filter(setor => 
        !this.form.setores_ids.includes(setor.id)
      );
    },
    
    sistemasDisponiveis() {
      if (!this.sistemas.length) return [];
      return this.sistemas.filter(sistema => 
        !this.form.sistemas_ids.includes(sistema.id)
      );
    }
    ,
    contratoEspecial() {
      const tipo = (this.form.tipo_contrato || '').toString().toLowerCase();
      return tipo === 'genérico' || tipo === 'generico' || tipo === 'terceirizado';
    },
    contratoObrigatorio() {
      const tipo = (this.form.tipo_contrato || '').toString().toLowerCase();
      return tipo === 'clt' || tipo === 'pj';
    }
  },
  methods: {
    checkScreenSize() {
      const w = window.innerWidth;
      // Se a tela for pequena, trocar para 'cards' automaticamente
      if (w <= 1024) {
        this.viewMode = 'cards';
      } else {
        // Mantém o modo atual se o usuário já tiver alterado manualmente
        if (!this.viewMode) this.viewMode = 'table';
      }
    },
    debouncedBusca() {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        this.invalidateCache();
      }, 300);
    },
    
    invalidateCache() {
      this._cachedFiltro = '';
      this._cachedAtivos = null;
      this._cachedOrdenacao = '';
      this._cachedResultado = [];
    },

    async carregarDados(tipo) {
      console.log('carregarDados chamado com tipo:', tipo);
      const loadingKey = tipo; // Usar o tipo diretamente como chave única
      
      if (this.loadingStates[loadingKey]) {
        console.log('Loading já em progresso para:', loadingKey);
        return;
      }
      
      this.loadingStates[loadingKey] = true;
      
      if (tipo === 'funcionarios') {
        this.isLoading = true;
      }
      
      try {
        switch(tipo) {
          case 'funcionarios':
            const res = await axios.get(`${API_BASE_URL}/funcionarios/`);
            this.funcionarios = res.data;
            break;
          case 'setores':
            const resSetores = await axios.get(`${API_BASE_URL}/setores/`);
            this.setores = resSetores.data;
            break;
          case 'sistemas':
            const resSistemas = await axios.get(`${API_BASE_URL}/sistemas/`);
            this.sistemas = resSistemas.data;
            break;
          case 'grupos-email':
            const resEmail = await axios.get(`${API_BASE_URL}/grupos-email/`);
            this.gruposEmail = resEmail.data;
            break;
          case 'grupos-whatsapp':
            console.log('Carregando grupos WhatsApp...');
            const resWhats = await axios.get(`${API_BASE_URL}/grupos_whatsapp/`);
            console.log('Dados recebidos:', resWhats.data);
            // Transformar os dados para o formato esperado pelo frontend
            this.gruposWhatsapp = resWhats.data.map(grupo => ({
              id: grupo.id,
              nome: grupo.nome,
              descricao: grupo.descricao || ''
            }));
            console.log('Grupos WhatsApp após transformação:', this.gruposWhatsapp);
            break;
          case 'grupos-pasta':
            const resPasta = await axios.get(`${API_BASE_URL}/grupos-pasta/`);
            this.gruposPasta = resPasta.data;
            break;
        }
        this.invalidateCache();
      } catch (error) {
        console.error(`Erro ao carregar ${tipo}:`, error);
      } finally {
        this.loadingStates[loadingKey] = false;
        if (tipo === 'funcionarios') {
          this.isLoading = false;
        }
      }
    },

    async carregarFuncionarios() {
      await this.carregarDados('funcionarios');
    },
    
    async carregarSetores() {
      await this.carregarDados('setores');
    },
    
    async carregarSistemas() {
      await this.carregarDados('sistemas');
    },
    
    async carregarGruposEmail() {
      await this.carregarDados('grupos-email');
    },
    
    async carregarGruposWhatsapp() {
      console.log('MÉTODO carregarGruposWhatsapp CHAMADO');
      try {
        await this.carregarDados('grupos-whatsapp');
        console.log('carregarDados completed, gruposWhatsapp:', this.gruposWhatsapp);
      } catch (error) {
        console.error('Erro em carregarGruposWhatsapp:', error);
      }
    },
    
    async carregarGruposPasta() {
      await this.carregarDados('grupos-pasta');
    },
    
    toggleOrdenacaoNome() {
      this.ordenacaoNome = this.ordenacaoNome === 'asc' ? 'desc' : 'asc';
      this.invalidateCache();
    },

    toggleCelula(key) {
      if (this.celulasExpandidas.has(key)) {
        this.celulasExpandidas.delete(key);
      } else {
        this.celulasExpandidas.add(key);
      }
      // Forçar atualização do Vue (Set não é reativo)
      this.celulasExpandidas = new Set(this.celulasExpandidas);
    },

    inativarFuncionario() {
      // Preenche com a data atual no formato yyyy-mm-dd
      this.form.data_inativado = new Date().toISOString().slice(0, 10);
    },
    // Métodos para Select Múltiplo - Grupos
    addGrupo() {
      if (this.novoGrupoId && !this.form.grupos_email_ids.includes(parseInt(this.novoGrupoId))) {
        this.form.grupos_email_ids.push(parseInt(this.novoGrupoId));
        this.novoGrupoId = '';
      }
    },
    removeGrupo(id) {
      this.form.grupos_email_ids = this.form.grupos_email_ids.filter(gId => gId !== id);
    },
    getGrupoNome(id) {
      const grupo = this.gruposEmail.find(g => g.id === id);
      return grupo ? grupo.nome : 'Grupo não encontrado';
    },
    // Métodos para Select Múltiplo - Setores
    addSetor() {
      if (this.novoSetorId && !this.form.setores_ids.includes(parseInt(this.novoSetorId))) {
        this.form.setores_ids.push(parseInt(this.novoSetorId));
        this.novoSetorId = '';
      }
    },
    removeSetor(id) {
      this.form.setores_ids = this.form.setores_ids.filter(sId => sId !== id);
    },
    getSetorNome(id) {
      const setor = this.setores.find(s => s.id === id);
      return setor ? setor.nome : 'Setor não encontrado';
    },
    // Métodos para Select Múltiplo - Sistemas
    addSistema() {
      if (this.novoSistemaId && !this.form.sistemas_ids.includes(parseInt(this.novoSistemaId))) {
        this.form.sistemas_ids.push(parseInt(this.novoSistemaId));
        this.novoSistemaId = '';
      }
    },
    removeSistema(id) {
      this.form.sistemas_ids = this.form.sistemas_ids.filter(sId => sId !== id);
    },
    getSistemaNome(id) {
      const sistema = this.sistemas.find(s => s.id === id);
      return sistema ? sistema.nome : 'Sistema não encontrado';
    },
    addGrupoPasta() {
      if (this.novoGrupoPastaId && !this.form.grupos_pasta_ids.includes(parseInt(this.novoGrupoPastaId))) {
        this.form.grupos_pasta_ids.push(parseInt(this.novoGrupoPastaId));
        this.novoGrupoPastaId = '';
      }
    },
    removeGrupoPasta(id) {
      this.form.grupos_pasta_ids = this.form.grupos_pasta_ids.filter(gId => gId !== id);
    },
    getGrupoPastaNome(id) {
      const grupo = this.gruposPasta.find(g => g.id === id);
      return grupo ? grupo.nome : 'Grupo não encontrado';
    },
    addGrupoWhatsapp() {
      if (this.novoGrupoWhatsappId && !this.form.grupos_whatsapp_ids.includes(parseInt(this.novoGrupoWhatsappId))) {
        this.form.grupos_whatsapp_ids.push(parseInt(this.novoGrupoWhatsappId));
        this.novoGrupoWhatsappId = '';
      }
    },
    removeGrupoWhatsapp(id) {
      this.form.grupos_whatsapp_ids = this.form.grupos_whatsapp_ids.filter(gId => gId !== id);
    },
    getGrupoWhatsappNome(id) {
      const grupo = this.gruposWhatsapp.find(g => g.id === id);
      return grupo ? grupo.nome : 'Grupo não encontrado';
    },
    async cadastrarFuncionario() {
      let dataAdmissaoFormatada = '';
      if (this.form.data_admissao) {
        if (typeof this.form.data_admissao === 'string') {
          dataAdmissaoFormatada = this.form.data_admissao;
        } else if (this.form.data_admissao instanceof Date) {
          const year = this.form.data_admissao.getFullYear();
          const month = String(this.form.data_admissao.getMonth() + 1).padStart(2, '0');
          const day = String(this.form.data_admissao.getDate()).padStart(2, '0');
          dataAdmissaoFormatada = `${year}-${month}-${day}`;
        }
      }
      await axios.post(`${API_BASE_URL}/funcionarios/`, {
        nome: this.form.nome,
        sobrenome: this.form.sobrenome,
        cargo_id: this.form.cargo_id,
        celular: this.form.celular,
        email: this.form.email || '',
        cpf: this.form.cpf,
        id_eyal: this.form.id_eyal,
        tipo_contrato: this.form.tipo_contrato,
        grupos_email_ids: [...this.form.grupos_email_ids],
        setores_ids: [...this.form.setores_ids],
        sistemas_ids: [...this.form.sistemas_ids],
        grupos_pasta_ids: [...this.form.grupos_pasta_ids],
        grupos_whatsapp_ids: [...this.form.grupos_whatsapp_ids],
        data_admissao: dataAdmissaoFormatada,
        data_inativado: ''
      });
      await this.carregarFuncionarios();
      this.fecharModal();
    },
    fecharModal() {
      this.showForm = false;
      this.editando = false;
      this.funcionarioEditId = null;
      this.form = {
        nome: '',
        sobrenome: '',
        cargo: '',
        celular: '',
        email: '',
        cpf: '',
        id_eyal: '',
        tipo_contrato: '',
        data_afastamento: '',
        data_retorno: '',
        grupo_email: '',
        setores_ids: [],
        sistemas_ids: [],
        grupos_email_ids: [],
        grupos_pasta_ids: [],
        grupos_whatsapp_ids: [],
        data_admissao: '',
        data_inativado: ''
      };
      this.novoGrupoId = '';
      this.novoSetorId = '';
      this.novoSistemaId = '';
      this.novoGrupoPastaId = '';
      this.novoGrupoWhatsappId = '';
    },
    abrirModalAdicionar() {
      this.editando = false;
      this.showForm = true;

    },
    abrirEditar(func) {
      let dataInativado = '';
      if (func.data_inativado && func.data_inativado.length >= 10) {
        dataInativado = func.data_inativado.slice(0, 10);
      }
      this.form = {
        nome: func.nome,
        sobrenome: func.sobrenome,
        cargo_id: func.cargo_id || null,
        celular: func.celular,
        email: func.email,
        grupo_email: (func.grupo_email || ''),
        setores_ids: func.setores ? func.setores.map(s => s.id) : [],
        sistemas_ids: func.sistemas ? func.sistemas.map(s => s.id) : [],
        grupos_email_ids: func.grupos_email ? func.grupos_email.map(g => g.id) : [],
        grupos_pasta_ids: func.grupos_pasta ? func.grupos_pasta.map(g => g.id) : [],
        grupos_whatsapp_ids: func.grupos_whatsapp ? func.grupos_whatsapp.map(g => g.id) : [],
        data_admissao: func.data_admissao || '',
        data_inativado: dataInativado || '',
        cpf: func.cpf || '',
        id_eyal: func.id_eyal || '',
        tipo_contrato: func.tipo_contrato || '',
        data_afastamento: func.data_afastamento || '',
        data_retorno: func.data_retorno || ''
      };
      this.funcionarioEditId = func.id;
      this.editando = true;
      this.showForm = true;
      // Adiciona classe que permite sombra visível - Não mais necessário com Teleport
      // document.body.classList.add('modal-open');
      axios.get(`${API_BASE_URL}/funcionarios/${func.id}/sistemas`).then(res => {
        this.form.sistemas_ids = res.data.map(s => s.id);
      });
    },
    async salvarEdicaoFuncionario() {
      // Garante tipos corretos antes do envio
      let dataInativadoFormatada = '';
      if (this.form.data_inativado) {
        if (typeof this.form.data_inativado === 'string') {
          dataInativadoFormatada = this.form.data_inativado;
        } else if (this.form.data_inativado instanceof Date) {
          const year = this.form.data_inativado.getFullYear();
          const month = String(this.form.data_inativado.getMonth() + 1).padStart(2, '0');
          const day = String(this.form.data_inativado.getDate()).padStart(2, '0');
          dataInativadoFormatada = `${year}-${month}-${day}`;
        }
      }
      // Arrays nunca undefined ou string
      const grupos_email_ids = Array.isArray(this.form.grupos_email_ids) ? this.form.grupos_email_ids : [];
      const setores_ids = Array.isArray(this.form.setores_ids) ? this.form.setores_ids : [];
      const sistemas_ids = Array.isArray(this.form.sistemas_ids) ? this.form.sistemas_ids : [];
      const grupos_pasta_ids = Array.isArray(this.form.grupos_pasta_ids) ? this.form.grupos_pasta_ids : [];
      const grupos_whatsapp_ids = Array.isArray(this.form.grupos_whatsapp_ids) ? this.form.grupos_whatsapp_ids : [];
      // cargo_id nunca string vazia
      let cargo_id = this.form.cargo_id;
      if (cargo_id === '' || cargo_id === undefined) cargo_id = null;
      // Garante formato correto para data_admissao
      let dataAdmissaoFormatada = '';
      if (this.form.data_admissao) {
        if (typeof this.form.data_admissao === 'string') {
          dataAdmissaoFormatada = this.form.data_admissao;
        } else if (this.form.data_admissao instanceof Date) {
          const year = this.form.data_admissao.getFullYear();
          const month = String(this.form.data_admissao.getMonth() + 1).padStart(2, '0');
          const day = String(this.form.data_admissao.getDate()).padStart(2, '0');
          dataAdmissaoFormatada = `${year}-${month}-${day}`;
        }
      }
      await axios.put(`${API_BASE_URL}/funcionarios/${this.funcionarioEditId}`, {
        nome: this.form.nome,
        sobrenome: this.form.sobrenome,
        cargo_id: this.form.cargo_id,
        celular: this.form.celular,
        email: this.form.email || '',
        cpf: this.form.cpf,
        id_eyal: this.form.id_eyal,
        tipo_contrato: this.form.tipo_contrato,
        data_afastamento: this.form.data_afastamento,
        data_retorno: this.form.data_retorno,
        grupos_email_ids,
        setores_ids,
        sistemas_ids,
        grupos_pasta_ids,
        grupos_whatsapp_ids,
        data_admissao: dataAdmissaoFormatada,
        data_inativado: dataInativadoFormatada
      });
      await this.carregarFuncionarios();
      this.fecharModal();
    },
    async excluirFuncionario(id) {
      if (confirm('Tem certeza que deseja excluir este funcionário?')) {
        try {
          await axios.delete(`${API_BASE_URL}/funcionarios/${id}`);
          await this.carregarFuncionarios();
        } catch (error) {
          alert('Erro ao excluir funcionário. Verifique se o funcionário existe ou se há dependências.');
        }
      }
    },
    
    // Inicialização otimizada
    async inicializarComponente() {
      try {
        // Carregar dados essenciais em paralelo para reduzir piscar
        await Promise.all([
          this.carregarFuncionarios(),
          this.carregarSetores(),
          this.carregarSistemas()
        ]);
        
        // Dados secundários sem delay visível
        setTimeout(async () => {
          await Promise.all([
            this.carregarGruposEmail(),
            this.carregarGruposWhatsapp(),
            this.carregarGruposPasta()
          ]);
        }, 50); // Delay muito menor
        
      } catch (error) {
        console.error('Erro ao inicializar componente:', error);
      }
    }
  },
  
  mounted() {
    // Carregamento otimizado - dados principais primeiro
    this.inicializarComponente();
    // checar e reagir a mudanças de tamanho para responsividade
    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize);
  }

  ,
  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize);
  }
}
</script>


<style scoped>
/* Estilos de seleção otimizados */
* {
  -webkit-user-select: text !important;
  -moz-user-select: text !important;
  user-select: text !important;
  -webkit-tap-highlight-color: transparent !important;
  -webkit-touch-callout: none !important;
  outline: none !important;
}

*::selection {
  background: #dbeafe !important;
  color: #1e40af !important;
  text-shadow: none !important;
}

*::-moz-selection {
  background: #dbeafe !important;
  color: #1e40af !important;
  text-shadow: none !important;
}

/* Container principal otimizado */
.funcionarios-container {
  padding: 1.2rem 1.2rem 2rem 1.2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: 100vh;
  width: 100%;
  max-width: 100vw;
  overflow-x: auto; /* permitir rolagem horizontal quando necessário para evitar corte */
  box-sizing: border-box;
}

/* Tabela responsiva: permite rolagem horizontal em telas pequenas/zoom alto */
.table-container {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.responsive-table {
  min-width: 900px; /* reduzido de 1200 para 900 para evitar corte em 100% zoom */
  width: 100%;
  border-collapse: collapse;
}

.table-view table th,
.table-view table td {
  white-space: nowrap;
}

/* Ajustes para caber melhor em 1366x768 */
@media (max-width: 1366px) {
  .funcionarios-container {
    padding: 0.6rem;
  }

  .header-premium {
    padding: 0.8rem;
    margin-bottom: 0.8rem;
    border-radius: 10px;
  }

  .header-title h1 {
    font-size: 1.15rem;
  }

  .header-icon {
    font-size: 1.15rem;
  }

  .header-right {
    max-width: 520px;
  }

  .controls-group {
    gap: 0.6rem;
  }

  .stats-dashboard {
    gap: 0.5rem;
  }

  .stat-card {
    padding: 0.4rem 0.6rem;
    min-width: 120px;
    border-radius: 8px;
  }

  .stat-number {
    font-size: 1.05rem;
  }

  .stat-label {
    font-size: 0.75rem;
  }

  .table-container {
    margin-top: 0.4rem;
  }

  .responsive-table th,
  .responsive-table td {
    padding: 8px 6px;
    font-size: 12px;
  }

  /* Esconder colunas menos importantes para reduzir largura total (por classe) */
  .col-grupo-email,
  .col-grupo-whatsapp,
  .col-pastas,
  .col-sistemas,
  .col-setor,
  .col-cargo {
    display: none;
  }

  /* Reduz altura das linhas */
  .responsive-table tbody tr td {
    line-height: 1.2;
    padding-top: 8px;
    padding-bottom: 8px;
  }

  /* Tornar botões de ação menores */
  .action-buttons-table .btn-editar,
  .action-buttons-table .btn-excluir {
    width: 34px;
    height: 34px;
    padding: 6px;
    font-size: 12px;
  }

  /* reduzir min-width para acomodar mais colunas sem scroll */
  .responsive-table {
    min-width: 760px;
  }
}

/* Transições e elementos de loading */
.table-container,
.stats-dashboard,
.stat-number {
  transition: opacity 0.2s ease-in-out;
}

.stat-number {
  min-width: 30px;
  display: inline-block;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  padding: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.mini-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.header-premium {
  background: #3b82f6;
  border-radius: 18px;
  padding: 1.2rem 1.4rem;
  margin-bottom: 1.2rem;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 1px 2px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 2rem;
}

.header-left {
  flex: 1;
}

.header-title h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.header-icon {
  color: #ffffff;
  font-size: 2rem;
}

.header-subtitle {
  margin: 0;
  color: #e0f2fe;
  font-size: 1.1rem;
  font-weight: 400;
}

.header-right {
  flex: 2;
  max-width: 800px;
}

.controls-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
  justify-content: flex-end;
}

.toggle-switch {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  user-select: none;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: relative;
  width: 48px;
  height: 24px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.slider::before {
  content: '';
  position: absolute;
  height: 18px;
  width: 18px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-switch input:checked + .slider {
  background: rgba(255, 255, 255, 0.9);
}

.toggle-switch input:checked + .slider::before {
  transform: translateX(24px);
}

.toggle-text {
  font-weight: 600;
  color: #ffffff;
  font-size: 0.9rem;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: #94a3b8;
  z-index: 1;
}

.search-input {
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
  width: 280px;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.clear-search {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.clear-search:hover {
  color: #ef4444;
  background: #fef2f2;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.view-toggle {
  display: flex;
  background: #f1f5f9;
  border-radius: 10px;
  padding: 4px;
  gap: 2px;
}

.toggle-btn {
  background: transparent;
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.toggle-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toggle-btn:hover:not(.active) {
  color: #475569;
}

.content-area {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* Container da tabela otimizado */
.table-container {
  overflow-x: auto !important;
  width: 100%;
  max-width: 100vw;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
  padding-bottom: 2px;
}

.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.cards-view {
  padding: 2rem;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.employee-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.employee-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.employee-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
}

.employee-info {
  flex: 1;
}

.employee-name {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.employee-cargo {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.employee-status {
  align-self: flex-start;
}

.status-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background: #10b981;
  color: white;
}

.status-badge.inactive {
  background: #ef4444;
  color: white;
}

.card-content {
  padding: 1.5rem;
}

.info-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #475569;
}

.info-item i {
  color: #667eea;
  width: 16px;
  text-align: center;
}

.tags-section {
  margin-bottom: 1rem;
}

.tags-section label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: #e2e8f0;
  color: #475569;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.tag.system {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
}

.tag.more {
  background: #667eea;
  color: white;
}

.card-actions {
  padding: 1rem 1.5rem;
  background: #f8fafc;
  display: flex;
  gap: 0.75rem;
  border-top: 1px solid #e2e8f0;
}

.btn-edit, .btn-delete {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-edit {
  background: #3b82f6;
  color: white;
}

.btn-edit:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-delete {
  background: #ef4444;
  color: white;
}

.btn-delete:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

/* Responsividade dos Cards */
@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .employee-card {
    margin: 0 1rem;
  }
  
  .info-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .card-actions {
    flex-direction: column;
  }
}

.btn-primary, .btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: #ffffff;
  color: #3b82f6;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-primary:hover {
  background: #f1f5f9;
  color: #2563eb;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
}

/* Stats Dashboard */
.stats-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  background: #e5e7eb;
  color: #6b7280;
}

.stat-icon.active {
  background: #10b981;
  color: white;
}

.stat-icon.inactive {
  background: #ef4444;
  color: white;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

/* Responsividade do Header */
@media (max-width: 1024px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1.5rem;
  }
  
  .controls-group {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 240px;
  }
}

@media (max-width: 768px) {
  .funcionarios-container {
    padding: 1rem;
  }
  
  .header-premium {
    padding: 1.5rem;
  }
  
  .header-title h1 {
    font-size: 1.8rem;
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .controls-group {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-input {
    width: 100%;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .stats-dashboard {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 1.2rem;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
  
  /* Esconder toggle de visualização em mobile */
  .view-toggle {
    display: none;
  }
  
  /* Forçar visualização em cards em mobile */
  .table-view {
    display: none !important;
  }
  
  .cards-view {
    display: block !important;
  }
}

/* Manter estilos existentes da tabela */
.tabela-funcionarios {
  background: var(--cor-branco);
  border-radius: 12px;
  padding: 24px 20px;
  margin: 20px 0 0 0;
  box-shadow: 0 2px 8px rgba(20,65,121,0.08);
  overflow-x: auto;
}

/* Dica de expansão */
.dica-expansao {
  text-align: center;
  margin-bottom: 16px;
  color: var(--cor-sec1);
  font-family: var(--font-corpo);
  opacity: 0.8;
}

/* Header melhorado */
.header-funcionarios {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
  gap: 20px;
}
.busca-adicionar {
  display: flex;
  gap: 16px;
  align-items: center;
}
.input-busca {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1.5px solid var(--cor-sec2);
  min-width: 220px;
  font-size: 15px;
  font-family: var(--font-corpo);
  background: #f8fafc;
  transition: border 0.2s;
}
.input-busca:focus {
  border: 2px solid var(--cor-destaque);
  outline: none;
}
.header h2 {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
}
.btn-cadastrar {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  border: none;
  border-radius: 4px;
  padding: 10px 18px;
  font-size: 15px;
  font-family: var(--font-titulo);
  cursor: pointer;
  transition: background 0.2s;
}
.btn-cadastrar:hover {
  background: var(--cor-sec3);
}
/* Estilos de tabela otimizados */
table {
  width: 100%;
  min-width: 1200px;
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 16px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  table-layout: fixed;
}

thead th {
  position: sticky;
  top: 0;
  background: #3b82f6;
  color: #ffffff;
  font-family: var(--font-titulo);
  font-size: 14px;
  font-weight: 600;
  padding: 16px 12px;
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  z-index: 2;
}

/* Larguras das colunas otimizadas */
thead th:nth-child(1), td:nth-child(1) { width: 90px; }
thead th:nth-child(2), td:nth-child(2) { width: 120px; }
thead th:nth-child(3), td:nth-child(3) { width: 95px; }
thead th:nth-child(4), td:nth-child(4) { width: 105px; }
thead th:nth-child(5), td:nth-child(5) { width: 90px; }
thead th:nth-child(6), td:nth-child(6) { width: 180px; }
thead th:nth-child(7), td:nth-child(7) { width: 100px; }
thead th:nth-child(8), td:nth-child(8) { width: 110px; }
thead th:nth-child(9), td:nth-child(9) { width: 80px; }
thead th:nth-child(10), td:nth-child(10) { width: 70px; }
thead th:nth-child(11), td:nth-child(11) { width: 70px; }
thead th:nth-child(12), td:nth-child(12) { width: 85px; }
thead th:nth-child(13), td:nth-child(13) { width: 75px; }

thead th:hover {
  background: #2563eb;
  cursor: pointer;
}

tbody tr {
  transition: background-color 0.2s ease;
  background: #ffffff;
}

tbody tr:nth-child(even) {
  background: #f8fafc;
}

tbody tr:hover {
  background: #dbeafe;
}

td {
  padding: 14px 12px;
  border-bottom: 1px solid #e5e7eb;
  font-family: var(--font-corpo);
  font-size: 14px;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
  position: relative;
}

tbody tr:last-child td {
  border-bottom: none;
}
/* Células clicáveis e expandidas */
.clicavel {
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
}

.clicavel:hover {
  background: #dbeafe;
  color: #1d4ed8;
  font-weight: 500;
}

.clicavel.expandida,
.expandida {
  background: #dbeafe !important;
  color: #1d4ed8 !important;
  font-weight: 600;
  white-space: normal !important;
  word-break: break-word !important;
  overflow: visible !important;
  text-overflow: clip !important;
  max-width: none !important;
  z-index: 10;
  position: relative;
}

.clicavel::after {
  content: '👆';
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  opacity: 0;
  transition: opacity 0.2s;
}

.clicavel:hover::after {
  opacity: 0.6;
}

/* Estilos de células específicas */
.sistemas-celula {
  font-size: 13px;
  line-height: 1.3;
}

.sistemas-celula.expandida {
  font-size: 14px;
  line-height: 1.4;
  padding: 12px 8px;
}

.data-importante {
  font-weight: 600;
  color: #1d4ed8;
  background: #dbeafe;
  border-radius: 6px;
  padding: 6px 10px;
  margin: 2px;
  display: inline-block;
}

/* Botões de ação otimizados */
.btn-editar,
.btn-excluir {
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid;
}

.btn-editar {
  background: #3b82f6;
  color: #ffffff;
  border-color: #2563eb;
  margin-right: 8px;
}

.btn-editar:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-excluir {
  background: #ef4444;
  color: #ffffff;
  border-color: #dc2626;
}

.btn-excluir:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.action-buttons-table {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.action-buttons-table .btn-editar,
.action-buttons-table .btn-excluir {
  padding: 8px 12px;
  margin: 0;
  min-width: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-buttons-table .btn-editar i,
.action-buttons-table .btn-excluir i {
  font-size: 14px;
}
/* Modal otimizado */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(20,65,121,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 40px;
  box-sizing: border-box;
}

.form-modal {
  background: var(--cor-branco);
  border-radius: 16px;
  padding: 40px 32px;
  max-width: 580px;
  width: calc(100% - 80px);
  max-height: calc(100vh - 80px);
  overflow-y: auto;
  box-shadow: 
    0 25px 50px -12px rgba(20,65,121,0.25),
    0 10px 25px rgba(20,65,121,0.1),
    0 0 0 1px rgba(20,65,121,0.05);
  font-family: var(--font-corpo);
}

.form-modal h3 {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
  margin-bottom: 24px;
  text-align: center;
}

.form-modal input {
  width: 100%;
  padding: 10px;
  margin-bottom: 16px;
  border: 1px solid var(--cor-sec2);
  border-radius: 4px;
  font-size: 15px;
  font-family: var(--font-corpo);
}

.form-modal input:focus {
  outline: 2px solid var(--cor-destaque);
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.form-modal button {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  border: none;
  border-radius: 4px;
  padding: 10px 18px;
  font-size: 15px;
  font-family: var(--font-titulo);
  cursor: pointer;
  margin-right: 8px;
  transition: background 0.2s;
  flex: 1;
}

.form-modal button:last-child {
  background: var(--cor-sec1);
  color: var(--cor-branco);
  margin-right: 0;
}

.form-modal button:hover {
  background: var(--cor-sec3);
}

/* Estilos para Select Múltiplo */
.select-group {
  margin-bottom: 20px;
}

.select-group label {
  font-weight: bold;
  margin-bottom: 8px;
  display: block;
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
}

.multi-select-container {
  border: 1px solid var(--cor-sec2);
  border-radius: 6px;
  padding: 8px;
  background: #f8fafc;
  min-height: 80px;
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
  min-height: 32px;
  max-height: 80px;
  overflow-y: auto;
  padding-right: 8px;
}

.selected-chip {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  padding: 4px 28px 4px 8px; /* padding extra à direita para o x */
  border-radius: 16px;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-corpo);
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  position: relative;
  word-break: break-all;
  cursor: pointer;
}



/* Tooltip para chips grandes */
.selected-chip:hover::after {
  content: attr(title);
  position: absolute;
  left: 0;
  top: 100%;
  background: #fffbe6;
  color: #333;
  border: 1px solid #e0c97f;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  white-space: normal;
  box-shadow: 0 2px 8px rgba(20,65,121,0.08);
  z-index: 10;
  min-width: 120px;
  max-width: 350px;
  pointer-events: none;
}
.multi-select {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--cor-sec2);
  border-radius: 4px;
  background: white;
  font-family: var(--font-corpo);
  font-size: 14px;
  color: var(--cor-primaria);
}

.multi-select:focus {
  outline: 2px solid var(--cor-destaque);
}

.multi-select option {
  padding: 8px;
}

.selects-2x2 {
  display: flex;
  gap: 24px;
  margin-bottom: 0;
}
.selects-2x2 .modal-col {
  min-width: 180px;
  flex: 1 1 0;
}
@media (max-width: 768px) {
  .selects-2x2 {
    flex-direction: column;
    gap: 10px;
  }
  .selects-2x2 .modal-col {
    min-width: 100%;
  }
}
/* Modal styling consolidado acima */

/* Responsividade para modal */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 20px;
    align-items: flex-start;
    padding-top: 40px;
  }
  
  .form-modal {
    width: calc(100% - 40px);
    padding: 32px 24px;
    max-height: calc(100vh - 80px);
    border-radius: 12px;
    max-width: 99%;
    padding: 16px;
  }
  
  .modal-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-col {
    min-width: 100%;
    gap: 8px;
  }
  
  .selected-chip:hover {
    background: #ffe082;
  }
}

@media (max-width: 480px) {
  .modal-overlay {
    padding: 15px;
    padding-top: 30px;
  }
  
  .form-modal {
    width: calc(100% - 30px);
    padding: 24px 20px;
    border-radius: 8px;
  }
}

/* Elementos de modal que estavam faltando */
.modal-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.modal-col {
  flex: 1;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-divider {
  border: none;
  border-top: 1.5px solid var(--cor-sec2);
  margin: 18px 0;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}
.form-grid > div {
  width: 100%;
}
@media (max-width: 700px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

/* Responsividade específica para tabela */
@media (max-width: 1400px) {
  table {
    min-width: 1150px;
  }
  
  thead th:nth-child(1), td:nth-child(1) { width: 85px; } /* Nome */
  thead th:nth-child(2), td:nth-child(2) { width: 115px; } /* Sobrenome */
  thead th:nth-child(3), td:nth-child(3) { width: 90px; } /* Data Admissão */
  thead th:nth-child(4), td:nth-child(4) { width: 100px; } /* Data Desligamento */
  thead th:nth-child(5), td:nth-child(5) { width: 85px; } /* Celular */
  thead th:nth-child(6), td:nth-child(6) { width: 170px; } /* E-mail */
  thead th:nth-child(7), td:nth-child(7) { width: 95px; } /* Grupo E-mail */
  thead th:nth-child(8), td:nth-child(8) { width: 105px; } /* Grupo WhatsApp */
  thead th:nth-child(9), td:nth-child(9) { width: 75px; } /* Pastas */
  thead th:nth-child(10), td:nth-child(10) { width: 65px; } /* Setor */
  thead th:nth-child(11), td:nth-child(11) { width: 65px; } /* Cargo */
  thead th:nth-child(12), td:nth-child(12) { width: 80px; } /* Sistemas */
  thead th:nth-child(13), td:nth-child(13) { width: 70px; } /* Ações */
}

@media (max-width: 1200px) {
  table {
    min-width: 900px;
  }
  thead th, td {
    padding: 12px 6px;
    font-size: 13px;
    max-width: 160px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

@media (max-width: 1000px) {
  table {
    min-width: 800px;
  }
  
  thead th, td {
    padding: 10px 6px;
    font-size: 12px;
  }
}

/* Otimização específica para zoom 100% em resoluções padrão */
@media (min-width: 1366px) and (max-width: 1920px) {
  .table-container {
    margin: 0 -0.5rem;
    padding: 0 0.5rem;
    overflow-x: auto;
  }
  
  table {
    min-width: 1200px;
    max-width: 100%;
  }
  
  .funcionarios-container {
    padding: 1.5rem;
  }
}
</style>

<style scoped>
.select-tipo-contrato {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #3b82f6;
  border-radius: 8px;
  background: #f0f9ff;
  color: #1e3a8a;
  font-weight: 600;
}
.select-tipo-contrato:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(59,130,246,0.12);
}
</style>

