<template>
  <div class="grupos-email-container">
    <!-- Header Premium -->
    <div class="header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-title">
            <h1>
              <i class="fas fa-envelope header-icon"></i>
              Gestão de Grupos de E-mail
            </h1>
            <p class="header-subtitle">Gerencie grupos e listas de e-mail</p>
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
            <i class="fas fa-envelope"></i>
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
      </div>
    </div>

    <!-- Tabela Premium -->
    <div class="table-container">
      <div class="table-wrapper">
        <table class="modern-table">
          <thead>
            <tr>
              <th style="text-align:left; vertical-align:middle;">
                <div class="th-content" style="justify-content:flex-start; align-items:center; height:56px; display:flex; flex-direction:row;">
                  <i class="fas fa-envelope" style="align-self:center;"></i>
                  <span style="margin-left:6px; align-self:center; font-size:1.08rem;">Nome do Grupo</span>
                </div>
              </th>
              <th style="text-align:center;">
                <div class="th-content" style="justify-content:center;">
                  <i class="fas fa-users participants-icon"></i>
                  <span style="margin-left:6px;">Participantes</span>
                </div>
              </th>
              <th class="actions-column" style="text-align:center;">
                <span style="display:inline-block;">Ações</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="grupo in gruposFiltrados" :key="grupo.id" class="table-row">
              <td class="name-cell" style="vertical-align:middle;">
                <div class="grupo-row" style="display:flex; align-items:center; gap:14px; min-height:38px;">
                  <div class="grupo-icon" style="background:#2563eb; color:#fff; border-radius:8px; width:38px; height:38px; display:flex; align-items:center; justify-content:center; font-size:1.3rem; flex-shrink:0;">
                    <i class="fas fa-envelope"></i>
                  </div>
                  <div style="display:flex; flex-direction:column; justify-content:center;">
                    <span class="grupo-nome" style="font-weight:700; color:#222; font-size:1.08rem; line-height:1.2;">{{ grupo.nome }}</span>
                    <span class="grupo-email" style="font-size:0.98rem; color:#2563eb; line-height:1.2;">{{ grupo.email }}</span>
                  </div>
                </div>
              </td>
              <td class="participants-cell" style="text-align:center; vertical-align:middle;">
                <div style="display:flex; align-items:center; justify-content:center; gap:4px;">
                  <i class="fas fa-users participants-icon small" aria-hidden="true" style="margin:0;"></i>
                  <span style="font-weight:500; color:#222;">{{ grupo.qtd_participantes }} participante(s)</span>
                </div>
              </td>
              <td class="actions-cell" style="text-align:center; vertical-align:middle;">
                <button class="action-btn edit-btn" @click="abrirEditar(grupo)" title="Editar" style="background:#2563eb; color:#fff; margin-right:6px;">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete-btn" @click="excluirGrupo(grupo.id)" title="Excluir" style="background:#ef4444; color:#fff; margin-right:6px;">
                  <i class="fas fa-trash"></i>
                </button>
                <button class="action-btn users-btn" @click="abrirModalParticipantes(grupo)" title="Participantes" style="background:#f3f4f6; color:#2563eb;">
                  <i class="fas fa-users"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal de Gerenciar Participantes (padrão premium azul) -->
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
                      <span class="participant-email">{{ participante.email }}</span>
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
                      <span class="participant-email">{{ funcionario.email }}</span>
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

    <!-- Modal -->
    <div v-if="showForm" class="modal-overlay" @click="fecharModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editando ? 'Editar Grupo de E-mail' : 'Novo Grupo de E-mail' }}</h3>
          <button class="close-button" @click="fecharModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="editando ? salvarEdicaoGrupo() : cadastrarGrupo()">
          <input v-model="form.nome" placeholder="Nome do Grupo" required />
          <div class="modal-actions">
            <button type="submit" class="btn-primary">Salvar</button>
            <button type="button" @click="fecharModal" class="btn-secondary">Cancelar</button>
          </div>
        </form>
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
        nome: ''
      },
      buscaGrupo: '',
      ordenacaoNome: 'asc',
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
        lista = lista.filter(g => {
          const nome = (g.nome || '').toLowerCase();
          return nome.includes(busca);
        });
      }
      // Ordena por nome asc/desc
      return lista.slice().sort((a, b) => {
        const nomeA = (a.nome || '').toLowerCase();
        const nomeB = (b.nome || '').toLowerCase();
        if (nomeA < nomeB) return this.ordenacaoNome === 'asc' ? -1 : 1;
        if (nomeA > nomeB) return this.ordenacaoNome === 'asc' ? 1 : -1;
        return 0;
      });
    },

    // Computed que retorna a lista de funcionários disponíveis já filtrada pela caixa de busca
    funcionariosFiltrados() {
      const funcionarios = Array.isArray(this.funcionariosDisponiveis) ? this.funcionariosDisponiveis : [];
      const participantes = Array.isArray(this.participantes) ? this.participantes : [];
      // Remove já participantes
      let disponiveis = funcionarios.filter(f => !participantes.some(p => p.id === f.id));
      if (this.filtroFuncionarios) {
        const termo = this.filtroFuncionarios.toLowerCase();
        disponiveis = disponiveis.filter(f =>
          (f.nome && f.nome.toLowerCase().includes(termo)) ||
          (f.sobrenome && f.sobrenome.toLowerCase().includes(termo)) ||
          (f.email && f.email.toLowerCase().includes(termo))
        );
      }
      // Ordena A -> Z pelo nome + sobrenome
      disponiveis = disponiveis.slice().sort((a, b) => {
        const nomeA = ((a.nome || '') + ' ' + (a.sobrenome || '')).toLowerCase();
        const nomeB = ((b.nome || '') + ' ' + (b.sobrenome || '')).toLowerCase();
        return nomeA.localeCompare(nomeB, 'pt-BR');
      });
      return disponiveis;
    }
  },
  async mounted() {
    await this.carregarGrupos();
  },
  methods: {
    async abrirModalParticipantes(grupo) {
      // Define seleção e abre modal imediatamente para melhor UX
      this.grupoSelecionado = grupo;
      this.mostrarModalParticipantes = true;
      // limpa listas enquanto carrega
      this.participantes = [];
      this.funcionariosDisponiveis = [];
      // ativa indicadores de loading
      this.loadingParticipantes = true;
      this.loadingDisponiveis = true;
      // carrega em paralelo para reduzir tempo total
      const promises = [
        this.carregarParticipantes(grupo.id),
        this.carregarFuncionariosDisponiveis(grupo.id)
      ];
      const results = await Promise.allSettled(promises);
      // garante que flags sejam desativadas mesmo se houver erro
      this.loadingParticipantes = false;
      this.loadingDisponiveis = false;
      // opcional: log de erros
      results.forEach(r => {
        if (r.status === 'rejected') console.error(r.reason);
      });
    },
    fecharModalParticipantes() {
      // sincroniza contador antes de fechar
      if (this.grupoSelecionado) {
        const idx = this.grupos.findIndex(g => g.id === this.grupoSelecionado.id);
        if (idx !== -1) this.grupos[idx].qtd_participantes = Array.isArray(this.participantes) ? this.participantes.length : 0;
      }
      this.mostrarModalParticipantes = false;
      this.grupoSelecionado = null;
      this.participantes = [];
      this.funcionariosDisponiveis = [];
      this.filtroFuncionarios = '';
    },
    async carregarParticipantes(grupoId) {
      try {
  const res = await axios.get(`${API_BASE_URL}/grupos-email/${grupoId}`);
  this.participantes = res.data.funcionarios || [];
  return this.participantes;
      } catch (error) {
        console.error('Erro ao carregar participantes:', error);
        this.participantes = [];
  throw error;
      }
    },
    async carregarFuncionariosDisponiveis(grupoId) {
      try {
        const res = await axios.get(`${API_BASE_URL}/grupos-email/${grupoId}/disponiveis`);
        this.funcionariosDisponiveis = res.data || [];
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
        const res = await axios.post(`${API_BASE_URL}/grupos-email/${this.grupoSelecionado.id}/adicionar-participante/${funcionarioId}`);
        const body = res && res.data ? res.data : null;
        if (body && Array.isArray(body.funcionarios)) {
          this.participantes = body.funcionarios;
          const idx = this.grupos.findIndex(g => g.id === this.grupoSelecionado.id);
          if (idx !== -1) this.grupos[idx].qtd_participantes = body.qtd_participantes || this.participantes.length;
          await this.carregarFuncionariosDisponiveis(this.grupoSelecionado.id);
        } else {
          await this.carregarParticipantes(this.grupoSelecionado.id);
          await this.carregarFuncionariosDisponiveis(this.grupoSelecionado.id);
        }
      } catch (error) {
        console.error('Erro ao adicionar participante:', error);
      }
    },
    async removerParticipante(funcionarioId) {
      if (!this.grupoSelecionado) return;
      try {
        const res = await axios.delete(`${API_BASE_URL}/grupos-email/${this.grupoSelecionado.id}/remover-participante/${funcionarioId}`);
        const body = res && res.data ? res.data : null;
        if (body && Array.isArray(body.funcionarios)) {
          this.participantes = body.funcionarios;
          const idx = this.grupos.findIndex(g => g.id === this.grupoSelecionado.id);
          if (idx !== -1) this.grupos[idx].qtd_participantes = body.qtd_participantes || this.participantes.length;
          await this.carregarFuncionariosDisponiveis(this.grupoSelecionado.id);
        } else {
          await this.carregarParticipantes(this.grupoSelecionado.id);
          await this.carregarFuncionariosDisponiveis(this.grupoSelecionado.id);
        }
      } catch (error) {
        console.error('Erro ao remover participante:', error);
      }
    },
    toggleOrdenacaoNome() {
      this.ordenacaoNome = this.ordenacaoNome === 'asc' ? 'desc' : 'asc';
    },
  // ...existing methods...
    async carregarGrupos() {
      const res = await axios.get(`${API_BASE_URL}/grupos-email/`);
      this.grupos = res.data;
    },
    async cadastrarGrupo() {
      await axios.post(`${API_BASE_URL}/grupos-email/`, {
        nome: this.form.nome
      });
      await this.carregarGrupos();
      this.fecharModal();
    },
    abrirEditar(grupo) {
      this.form = { nome: grupo.nome };
      this.grupoEditId = grupo.id;
      this.editando = true;
      this.showForm = true;
    },
    abrirModal() {
      this.showForm = true;
      this.editando = false;
      this.form = { nome: '' };
      this.grupoEditId = null;
    },
    async salvarEdicaoGrupo() {
      await axios.put(`${API_BASE_URL}/grupos-email/${this.grupoEditId}`, {
        nome: this.form.nome
      });
      await this.carregarGrupos();
      this.fecharModal();
    },
    async excluirGrupo(id) {
      await axios.delete(`${API_BASE_URL}/grupos-email/${id}`);
      await this.carregarGrupos();
      // Dispara evento global para atualizar dashboard
      window.dispatchEvent(new Event('atualizarDashboard'));
    },
    fecharModal() {
      this.showForm = false;
      this.editando = false;
      this.grupoEditId = null;
      this.form = { nome: '' };
    },
  }
}
</script>

<style scoped>
/* Layout Container Principal */
.grupos-email-container {
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 32px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f3f4f6;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.close-button {
  background: none;
  border: none;
  font-size: 20px;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-content form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-content input {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.modal-content input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

.modal-actions .btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-actions .btn-primary:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-secondary {
  background: #f3f4f6;
  border: none;
  color: #374151;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.premium-modal-bg {
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(5px);
}
.premium-modal {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.18);
  max-width: 700px;
  width: 95%;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}
/* Garantir que o modal não ultrapasse a viewport e permita scroll interno */
.premium-modal {
  max-height: calc(100vh - 80px);
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
.premium-list-scroll {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 0.5rem;
  margin-bottom: 1.2rem;
  max-height: 220px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #25D366 #e2e8f0;
}
.premium-list-scroll::-webkit-scrollbar {
  width: 7px;
}
.premium-list-scroll::-webkit-scrollbar-thumb {
  background: #25D366;
  border-radius: 8px;
}
.premium-list-scroll::-webkit-scrollbar-track {
  background: #e2e8f0;
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
  .grupos-email-container {
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
.premium-list-scroll-blue {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 0.5rem;
  margin-bottom: 1.2rem;
  max-height: 220px;
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
.premium-search-bar {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.premium-input-blue {
  border: 2px solid #2563eb;
  border-radius: 10px;
  padding: 0.7rem 1rem;
  font-size: 1rem;
  transition: all 0.2s ease;
  font-family: inherit;
  width: 100%;
  box-shadow: 0 1px 4px rgba(37,99,235,0.07);
}
.premium-input-blue:focus {
  outline: none;
  border-color: #1e40af;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.13);
}
</style>
