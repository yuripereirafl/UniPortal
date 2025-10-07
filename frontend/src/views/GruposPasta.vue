<template>
  <div class="grupos-pasta-container">
    <!-- Header Premium -->
    <div class="header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-title">
            <h1>
              <i class="fas fa-folder-open header-icon"></i>
              Gestão de Grupos de Pastas
            </h1>
            <p class="header-subtitle">Gerencie grupos e permissões de pastas</p>
          </div>
        </div>
        <div class="header-right">
          <div class="controls-group">
            <div class="search-control">
              <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input 
                  v-model="buscaGrupo" 
                  placeholder="Buscar grupo..." 
                  class="search-input" 
                />
                <button v-if="buscaGrupo" @click="buscaGrupo = ''" class="clear-search">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            <div class="action-buttons">
              <button class="btn-primary" @click="abrirModal">
                <i class="fas fa-plus"></i>
                <span>Adicionar Grupo</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Stats Dashboard -->
      <div class="stats-dashboard">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-folder-open"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ grupos.length }}</span>
            <span class="stat-label">Total</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon active">
            <i class="fas fa-filter"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ gruposFiltrados.length }}</span>
            <span class="stat-label">Filtrados</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ gruposComDescricao }}</span>
            <span class="stat-label">Com Descrição</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabela Premium -->
    <div class="table-container">
      <div class="table-wrapper">
        <table class="modern-table">
          <thead>
            <tr>
              <th @click="toggleOrdenacaoNome" class="sortable">
                <div class="th-content">
                  <span>Nome do Grupo</span>
                  <i class="fas fa-sort sort-icon" :class="{ 
                    'fa-sort-up': ordenacaoNome === 'asc',
                    'fa-sort-down': ordenacaoNome === 'desc'
                  }"></i>
                </div>
              </th>
              <th>Descrição</th>
              <th style="text-align:center;"><i class="fas fa-users participants-icon"></i> Participantes</th>
              <th class="actions-column">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="grupo in gruposFiltrados" :key="grupo.id" class="table-row">
              <td class="name-cell">
                <div class="name-content">
                  <div class="grupo-icon">
                    <i class="fas fa-folder-open"></i>
                  </div>
                  <span class="grupo-name">{{ grupo.nome }}</span>
                </div>
              </td>
              <td class="description-cell">
                <span v-if="grupo.descricao" class="description-text">{{ grupo.descricao }}</span>
                <span v-else class="no-description">Sem descrição</span>
              </td>
              <td class="participants-cell" style="text-align:center; vertical-align:middle;">
                <div style="display:flex; align-items:center; justify-content:center; gap:4px;">
                  <i class="fas fa-users participants-icon small" aria-hidden="true" style="margin:0;"></i>
                  <span style="font-weight:500;">{{ grupo.qtd_participantes }} participante(s)</span>
                </div>
              </td>
              <td class="actions-cell">
                <button class="action-btn edit-btn" @click="abrirEditar(grupo)" title="Editar">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete-btn" @click="excluirGrupo(grupo.id)" title="Excluir">
                  <i class="fas fa-trash-alt"></i>
                </button>
                <button class="action-btn users-btn" @click="abrirModalParticipantes(grupo)" title="Participantes">
                  <i class="fas fa-users"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal de Gerenciar Participantes -->
    <div v-if="mostrarModalParticipantes" class="modal-overlay premium-modal-bg" @click="fecharModalParticipantes">
      <div class="modal-container large-modal premium-modal" @click.stop>
        <div class="modal-header premium-modal-header-blue">
          <h3>
            <i class="fas fa-users-cog"></i>
            Gerenciar Participantes - {{ grupoSelecionado?.nome }}
          </h3>
          <button @click="fecharModalParticipantes" class="modal-close premium-close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body premium-modal-body">
          <div class="participants-section">
            <h4 style="display:flex; align-items:center; gap:10px;">
              <i class="fas fa-users participants-icon small" aria-hidden="true"></i>
              <span>Participantes Atuais ({{ participantes.length }})</span>
            </h4>
            <div class="participants-list premium-list-scroll-blue">
              <div v-if="loadingParticipantes" class="list-loading">Carregando participantes...</div>
              <div v-else>
                <div v-for="participante in participantes.slice().sort((a, b) => ((a.nome + ' ' + a.sobrenome).localeCompare(b.nome + ' ' + b.sobrenome)))" :key="participante.id" class="participant-item premium-item-compact">
                  <div class="participant-info">
                    <div class="participant-avatar premium-avatar-blue">
                      <i class="fas fa-user"></i>
                    </div>
                    <div class="participant-details">
                      <span class="participant-name">{{ participante.nome }} {{ participante.sobrenome }}</span>
                      <span class="participant-pasta">{{ participante.pasta }}</span>
                    </div>
                  </div>
                  <button @click="removerParticipante(participante.id)" class="btn-remove premium-btn-blue">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="add-participants-section">
            <h4>
              <i class="fas fa-user-plus"></i>
              Adicionar Participantes
            </h4>
            <div class="search-participants premium-search-bar">
              <input 
                v-model="filtroFuncionarios" 
                class="form-input premium-input-blue"
                placeholder="Buscar funcionários..." 
              />
            </div>
            <div class="available-participants premium-list-scroll-blue">
              <div v-if="loadingDisponiveis" class="list-loading">Carregando funcionários...</div>
              <div v-else>
                <div v-for="funcionario in funcionariosFiltrados" :key="funcionario.id" class="participant-item premium-item-compact">
                  <div class="participant-info">
                    <div class="participant-avatar premium-avatar-blue">
                      <i class="fas fa-user"></i>
                    </div>
                    <div class="participant-details">
                      <span class="participant-name">{{ funcionario.nome }} {{ funcionario.sobrenome }}</span>
                      <span class="participant-pasta">{{ funcionario.pasta }}</span>
                    </div>
                  </div>
                  <button @click="adicionarParticipante(funcionario.id)" class="btn-add premium-btn-blue">
                    <i class="fas fa-plus"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer premium-modal-footer">
          <button type="button" @click="fecharModalParticipantes" class="btn-primary btn-primary-blue">
            <i class="fas fa-check"></i>
            CONCLUÍDO
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Criar/Editar Grupo (Premium) -->
    <div v-if="showForm" class="modal-overlay premium-modal-bg" @click="fecharModal">
      <div class="modal-container large-modal premium-modal" @click.stop>
        <div class="modal-header premium-modal-header-blue">
          <h3>{{ editando ? 'Editar Grupo de Pastas' : 'Novo Grupo de Pastas' }}</h3>
          <button class="modal-close premium-close-btn" @click="fecharModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body premium-modal-body">
          <form @submit.prevent="editando ? salvarEdicaoGrupo() : cadastrarGrupo()">
            <div style="display:flex; gap:12px; align-items:flex-start; margin-bottom:12px;">
              <input v-model="form.nome" placeholder="Nome do Grupo" required class="form-input" />
              <textarea v-model="form.descricao" placeholder="Descrição (opcional)" rows="3" class="form-input" style="min-width:260px;"></textarea>
            </div>
            <div style="display:flex; gap:12px; justify-content:flex-end;">
              <button type="button" @click="fecharModal" class="btn-secondary">Cancelar</button>
              <button type="submit" class="btn-primary btn-primary-blue">Salvar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../api';
export default {
  data() {
    return {
      grupos: [],
      showForm: false,
      editando: false,
      grupoEditId: null,
      form: {
        nome: '',
        descricao: ''
      },
      buscaGrupo: '',
      ordenacaoNome: 'asc',
  // participantes modal state
  mostrarModalParticipantes: false,
  grupoSelecionado: null,
  participantes: [],
  funcionariosDisponiveis: [],
  loadingParticipantes: false,
  loadingDisponiveis: false,
  filtroFuncionarios: ''
    }
  },
  computed: {
    gruposFiltrados() {
      let lista = this.grupos;
      if (this.buscaGrupo) {
        const busca = this.buscaGrupo.toLowerCase();
        lista = lista.filter(g => (g.nome || '').toLowerCase().includes(busca));
      }
      return lista.slice().sort((a, b) => {
        const nomeA = (a.nome || '').toLowerCase();
        const nomeB = (b.nome || '').toLowerCase();
        if (nomeA < nomeB) return this.ordenacaoNome === 'asc' ? -1 : 1;
        if (nomeA > nomeB) return this.ordenacaoNome === 'asc' ? 1 : -1;
        return 0;
      });
    },
    gruposComDescricao() {
      return this.grupos.filter(g => g.descricao && g.descricao.trim() !== '').length;
    }
    ,
    funcionariosFiltrados() {
      const funcionarios = Array.isArray(this.funcionariosDisponiveis) ? this.funcionariosDisponiveis : [];
      const participantes = Array.isArray(this.participantes) ? this.participantes : [];
      let disponiveis = funcionarios.filter(f => !participantes.some(p => p.id === f.id));
      if (this.filtroFuncionarios) {
        const termo = this.filtroFuncionarios.toLowerCase();
        disponiveis = disponiveis.filter(f =>
          (f.nome && f.nome.toLowerCase().includes(termo)) ||
          (f.sobrenome && f.sobrenome.toLowerCase().includes(termo)) ||
          (f.email && f.email.toLowerCase().includes(termo))
        );
      }
      return disponiveis.slice().sort((a, b) => {
        const nomeA = ((a.nome || '') + ' ' + (a.sobrenome || '')).toLowerCase();
        const nomeB = ((b.nome || '') + ' ' + (b.sobrenome || '')).toLowerCase();
        return nomeA.localeCompare(nomeB, 'pt-BR');
      });
    }
  },
  methods: {
    toggleOrdenacaoNome() {
      this.ordenacaoNome = this.ordenacaoNome === 'asc' ? 'desc' : 'asc';
    },
    async cadastrarGrupo() {
      await axios.post(`${API_BASE_URL}/grupos-pasta/`, {
        nome: this.form.nome,
        descricao: this.form.descricao
      });
      await this.carregarGrupos();
      this.fecharModal();
    },
    async salvarEdicaoGrupo() {
      await axios.put(`${API_BASE_URL}/grupos-pasta/${this.grupoEditId}`, {
        nome: this.form.nome,
        descricao: this.form.descricao
      });
      await this.carregarGrupos();
      this.fecharModal();
    },
    async excluirGrupo(id) {
      if (confirm('Tem certeza que deseja excluir este grupo?')) {
        await axios.delete(`${API_BASE_URL}/grupos-pasta/${id}`);
        await this.carregarGrupos();
      }
    },
    abrirEditar(grupo) {
      this.form = {
        nome: grupo.nome,
        descricao: grupo.descricao || ''
      };
      this.grupoEditId = grupo.id;
      this.editando = true;
      this.showForm = true;
    },
    async abrirModalParticipantes(grupo) {
      this.grupoSelecionado = grupo;
      this.mostrarModalParticipantes = true;
      this.participantes = [];
      this.funcionariosDisponiveis = [];
      this.loadingParticipantes = true;
      this.loadingDisponiveis = true;
      const promises = [
        this.carregarParticipantes(grupo.id),
        this.carregarFuncionariosDisponiveis(grupo.id)
      ];
      const results = await Promise.allSettled(promises);
      this.loadingParticipantes = false;
      this.loadingDisponiveis = false;
      results.forEach(r => { if (r.status === 'rejected') console.error(r.reason); });
    },
    fecharModalParticipantes() {
      // atualiza contador no grupo pai antes de fechar
      if (this.grupoSelecionado) {
        const idx = this.grupos.findIndex(g => g.id === this.grupoSelecionado.id);
        if (idx !== -1) {
          this.grupos[idx].qtd_participantes = Array.isArray(this.participantes) ? this.participantes.length : 0;
        }
      }
      this.mostrarModalParticipantes = false;
      this.grupoSelecionado = null;
      this.participantes = [];
      this.funcionariosDisponiveis = [];
      this.filtroFuncionarios = '';
    },
    async carregarParticipantes(grupoId) {
      try {
        const res = await axios.get(`${API_BASE_URL}/grupos-pasta/${grupoId}`);
        // Aceita vários formatos de resposta: {funcionarios: [...]}, {value: [...]}, ou array direto
        const body = res && res.data ? res.data : [];
        if (Array.isArray(body)) {
          this.participantes = body;
        } else if (Array.isArray(body.funcionarios)) {
          this.participantes = body.funcionarios;
        } else if (Array.isArray(body.value)) {
          this.participantes = body.value;
        } else {
          this.participantes = [];
        }
        return this.participantes;
      } catch (error) {
        console.error('Erro ao carregar participantes:', error);
        this.participantes = [];
        throw error;
      }
    },
    async carregarFuncionariosDisponiveis(grupoId) {
      try {
        const res = await axios.get(`${API_BASE_URL}/grupos-pasta/${grupoId}/disponiveis`);
        const body = res && res.data ? res.data : [];
        if (Array.isArray(body)) {
          this.funcionariosDisponiveis = body;
        } else if (Array.isArray(body.value)) {
          this.funcionariosDisponiveis = body.value;
        } else {
          this.funcionariosDisponiveis = [];
        }
        return this.funcionariosDisponiveis;
      } catch (error) {
        console.error('Erro ao carregar funcionários disponíveis:', error);
        this.funcionariosDisponiveis = [];
        throw error;
      }
    },
    async adicionarParticipante(funcionarioId) {
      if (!this.grupoSelecionado) return;
      try {
  await axios.post(`${API_BASE_URL}/grupos-pasta/${this.grupoSelecionado.id}/adicionar-participante/${funcionarioId}`);
  await this.carregarParticipantes(this.grupoSelecionado.id);
  // atualiza contador no grupo principal
  const idxAdd = this.grupos.findIndex(g => g.id === this.grupoSelecionado.id);
  if (idxAdd !== -1) this.grupos[idxAdd].qtd_participantes = Array.isArray(this.participantes) ? this.participantes.length : 0;
  await this.carregarFuncionariosDisponiveis(this.grupoSelecionado.id);
      } catch (error) {
        console.error('Erro ao adicionar participante:', error);
      }
    },
    async removerParticipante(funcionarioId) {
      if (!this.grupoSelecionado) return;
      try {
  await axios.delete(`${API_BASE_URL}/grupos-pasta/${this.grupoSelecionado.id}/remover-participante/${funcionarioId}`);
  await this.carregarParticipantes(this.grupoSelecionado.id);
  // atualiza contador no grupo principal
  const idxRem = this.grupos.findIndex(g => g.id === this.grupoSelecionado.id);
  if (idxRem !== -1) this.grupos[idxRem].qtd_participantes = Array.isArray(this.participantes) ? this.participantes.length : 0;
  await this.carregarFuncionariosDisponiveis(this.grupoSelecionado.id);
      } catch (error) {
        console.error('Erro ao remover participante:', error);
      }
    },
    abrirModal() {
      this.showForm = true;
      this.editando = false;
      this.form = { nome: '', descricao: '' };
      this.grupoEditId = null;
    },
    fecharModal() {
      this.showForm = false;
      this.editando = false;
      this.grupoEditId = null;
      this.form = { nome: '', descricao: '' };
    },
    async carregarGrupos() {
      const res = await axios.get(`${API_BASE_URL}/grupos-pasta/`);
      const data = res.data || [];
      // Normaliza para garantir qtd_participantes mesmo que backend não retorne
      this.grupos = data.map(g => ({
        ...g,
        qtd_participantes: typeof g.qtd_participantes === 'number' ? g.qtd_participantes : (Array.isArray(g.funcionarios) ? g.funcionarios.length : 0)
      }));
    }
  },
  mounted() {
    this.carregarGrupos();
  }
}
</script>

<style scoped>
/* Layout Container Principal */
.grupos-pasta-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 20px;
}

/* Header Premium - Replicado de Funcionários */
.header-premium {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 10px 40px rgba(59, 130, 246, 0.15), 
              0 4px 16px rgba(59, 130, 246, 0.1);
  color: white;
  position: relative;
  overflow: hidden;
}

.header-premium::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 200%;
  background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%);
  transform: rotate(45deg);
  pointer-events: none;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.header-left .header-title h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 16px;
  line-height: 1.2;
}

.header-icon {
  font-size: 2.2rem;
  opacity: 0.9;
}

.header-subtitle {
  margin: 8px 0 0 0;
  font-size: 1.1rem;
  opacity: 0.85;
  font-weight: 400;
}

/* Controls Section */
.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
}

.controls-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-end;
}

/* Search Premium */
.search-control {
  position: relative;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  background: rgba(255, 255, 255, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  padding: 12px 20px 12px 48px;
  color: white;
  font-size: 14px;
  width: 300px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.search-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.search-icon {
  position: absolute;
  left: 16px;
  color: rgba(255, 255, 255, 0.7);
  z-index: 1;
}

.clear-search {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.clear-search:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 12px 24px;
  border-radius: 50px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  font-size: 14px;
}

.btn-primary:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Stats Dashboard */
.stats-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  position: relative;
  z-index: 1;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.3);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  flex-shrink: 0;
}

.stat-icon.active {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.85;
  font-weight: 500;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.modern-table thead {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.modern-table th {
  padding: 20px 24px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  border-bottom: 2px solid #e5e7eb;
  position: relative;
}

.modern-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
}

.modern-table th.sortable:hover {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
}

.th-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.sort-icon {
  color: #9ca3af;
  font-size: 12px;
  transition: all 0.2s ease;
}

.sort-icon.fa-sort-up,
.sort-icon.fa-sort-down {
  color: #3b82f6;
}

.modern-table tbody tr {
  transition: all 0.2s ease;
  border-bottom: 1px solid #f3f4f6;
}

.modern-table tbody tr:hover {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.modern-table td {
  padding: 20px 24px;
  vertical-align: middle;
  color: #374151;
}

/* Cell Styles */
.name-cell {
  font-weight: 500;
}

.name-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.grupo-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  flex-shrink: 0;
}

.grupo-name {
  font-weight: 600;
  color: #1f2937;
}

.description-cell {
  max-width: 300px;
}

.description-text {
  color: #6b7280;
  line-height: 1.5;
}

.no-description {
  color: #9ca3af;
  font-style: italic;
  font-size: 0.9rem;
}

/* Actions */
.actions-cell {
  text-align: center;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0 4px;
  transition: all 0.2s ease;
  font-size: 14px;
}

.edit-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.edit-btn:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.delete-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.delete-btn:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* Modal Styles (premium) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.premium-modal-bg {
  /* compatibility class used in template */
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(5px);
}

.modal-container,
.premium-modal {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.18);
  max-width: 700px; /* padronizado para 700px */
  width: 95%;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

/* Garantia extra de sobreposição e tamanho para modal grande */
.modal-container.large-modal {
  z-index: 1100;
  max-width: 900px;
  width: 92%;
}

/* Garantir que o modal não ultrapasse a viewport e permita scroll interno */
.premium-modal {
  max-height: calc(100vh - 80px);
  overflow-y: auto;
}

.large-modal {
  max-width: 900px;
  max-height: 80vh;
  overflow-y: auto;
}

.premium-modal-header {
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  color: white;
  padding: 1.2rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.premium-modal-header-blue {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  color: white;
  padding: 1.2rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.premium-modal-body {
  padding: 1.5rem;
  background: #f8fafc;
}
.premium-modal-footer {
  background: #f7fafc;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e2e8f0;
}

.premium-list-scroll-blue {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 0.5rem;
  margin-bottom: 1.2rem;
  max-height: 260px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #2563eb #e0e7ff;
}
.premium-list-scroll-blue::-webkit-scrollbar {
  width: 7px;
}
.premium-list-scroll-blue::-webkit-scrollbar-thumb {
  background: #2563eb;
  border-radius: 8px;
}
.premium-list-scroll-blue::-webkit-scrollbar-track {
  background: #e0e7ff;
  border-radius: 8px;
}

.premium-item-compact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  margin-bottom: 0.3rem;
  background: white;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  transition: background 0.2s ease;
}
.premium-item-compact:hover {
  background: #f7fafc;
}

.premium-close-btn {
  background: #e0e7ff;
  color: #1e40af;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  cursor: pointer;
  transition: background 0.2s;
}
.premium-close-btn:hover {
  background: #2563eb;
  color: #fff;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .header-right {
    width: 100%;
    align-items: center;
  }
  
  .controls-group {
    width: 100%;
    align-items: center;
  }
  
  .search-input {
    width: 100%;
    max-width: 300px;
  }
  
  .stats-dashboard {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .header-left .header-title h1 {
    font-size: 2rem;
  }
  
  .modern-table {
    font-size: 14px;
  }
  
  .modern-table th,
  .modern-table td {
    padding: 16px 12px;
  }
}

@media (max-width: 480px) {
  .grupos-pasta-container {
    padding: 16px;
  }
  
  .header-premium {
    padding: 24px;
  }
  
  .header-left .header-title h1 {
    font-size: 1.75rem;
  }
  
  .stats-dashboard {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    margin: 20px;
    padding: 24px;
  }
}

/* Regras de estilo adicionais para itens de participantes e botões (mesmas do GruposEmail) */
.premium-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
  margin-right: 0.7rem;
}
.premium-avatar-blue {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
  margin-right: 0.7rem;
}
.participant-details {
  display: flex;
  flex-direction: column;
}
.participant-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Ícone de participantes destacado usado no cabeçalho e nas células */
.participants-icon {
  background: linear-gradient(135deg, #e6f2ff 0%, #dbeafe 100%);
  color: #1e40af;
  padding: 8px;
  border-radius: 10px;
  font-size: 1.15rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 18px rgba(37,99,235,0.12);
}
.participants-icon.small {
  padding: 6px;
  font-size: 0.95rem;
  border-radius: 8px;
}
.participant-name {
  font-weight: 700;
  color: #1a202c;
  font-size: 0.95rem;
  letter-spacing: 0.2px;
}
.participant-email {
  font-size: 0.85rem;
  color: #718096;
  font-weight: 500;
}
/* Estilos para o campo de busca dentro do modal (buscar funcionários) */
.premium-search-bar .form-input,
.premium-search-bar .premium-input-blue {
  width: 100%;
  max-width: 420px;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  background: #ffffff;
  color: #374151;
  box-shadow: 0 6px 18px rgba(16,24,40,0.04);
  transition: all 0.18s ease;
}
.premium-search-bar .form-input::placeholder,
.premium-search-bar .premium-input-blue::placeholder {
  color: #9ca3af;
}
.premium-search-bar .form-input:focus,
.premium-search-bar .premium-input-blue:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 6px rgba(37,99,235,0.06);
  transform: none;
}

/* Estilos gerais para inputs/textarea usados no modal de criação/edição */
.form-input {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #374151;
  font-size: 14px;
  box-shadow: 0 6px 18px rgba(16,24,40,0.04);
  transition: all 0.18s ease;
  min-height: 40px;
}
.form-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 6px rgba(37,99,235,0.06);
}
textarea.form-input {
  min-height: 64px;
  resize: vertical;
}

/* Botão secundário (Cancelar) no modal */
.btn-secondary {
  background: #ffffff;
  color: #374151;
  border: 1px solid #e5e7eb;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}
.btn-secondary:hover {
  background: #f3f4f6;
}

/* Layout do formulário dentro do modal */
.premium-modal-body form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.premium-modal-body form .form-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.premium-modal-body form .form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 6px;
}
.premium-btn {
  background: #f8d7da;
  color: #c82333;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.premium-btn.btn-add {
  background: #dbeafe;
  color: #2563eb;
}
.premium-btn-blue {
  background: #e0e7ff;
  color: #1e40af;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.premium-btn-blue.btn-add {
  background: #dbeafe;
  color: #2563eb;
}
.premium-btn:hover {
  filter: brightness(0.95);
}
.premium-btn-blue:hover {
  filter: brightness(0.95);
}
.btn-primary-blue {
  background: linear-gradient(45deg, #2563eb, #1e40af);
  color: white;
  font-weight: 700;
  border: none;
  border-radius: 25px;
  padding: 0.9rem 1.8rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.18);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.btn-primary-blue:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
/* Corrige hover do botão combinado com .btn-primary para manter o azul */
.btn-primary.btn-primary-blue:hover,
.premium-modal-footer .btn-primary.btn-primary-blue:hover {
  background: linear-gradient(45deg, #1f5fe8, #17378f);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(37,99,235,0.22);
}
/* Garantir avatar pequeno e alinhado no modal */
.participant-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.6rem;
}
.participant-pasta {
  font-size: 0.85rem;
  color: #6b7280;
}
</style>
