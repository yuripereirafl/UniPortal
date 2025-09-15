<template>
  <div class="sistemas-container">
    <!-- Header Premium -->
    <div class="header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-title">
            <h1>
              <i class="fas fa-desktop header-icon"></i>
              Gestão de Sistemas
            </h1>
            <p class="header-subtitle">Gerencie sistemas e configurações</p>
          </div>
        </div>
        <div class="header-right">
          <div class="controls-group">
            <div class="search-control">
              <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input 
                  v-model="buscaSistema" 
                  placeholder="Buscar sistema..." 
                  class="search-input" 
                />
                <button v-if="buscaSistema" @click="buscaSistema = ''" class="clear-search">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            <div class="action-buttons">
              <button class="btn-primary" @click="showForm = !showForm">
                <i class="fas fa-plus"></i>
                <span>Adicionar Sistema</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Stats Dashboard -->
      <div class="stats-dashboard">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-desktop"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ sistemas.length }}</span>
            <span class="stat-label">Total</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon active">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ sistemasAtivos.length }}</span>
            <span class="stat-label">Ativos</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon inactive">
            <i class="fas fa-times-circle"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ sistemas.length - sistemasAtivos.length }}</span>
            <span class="stat-label">Inativos</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-filter"></i>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ sistemasFiltrados.length }}</span>
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
              <th @click="toggleOrdenacaoNome" class="sortable">
                <div class="th-content">
                  <span>Nome</span>
                  <i class="fas fa-sort sort-icon" :class="{ 
                    'fa-sort-up': ordenacaoNome === 'asc',
                    'fa-sort-down': ordenacaoNome === 'desc'
                  }"></i>
                </div>
              </th>
              <th>Descrição</th>
              <th>Status</th>
              <th class="actions-column">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sistema in sistemasFiltrados" :key="sistema.id" class="table-row">
              <td class="name-cell">
                <div class="name-content">
                  <div class="sistema-icon">
                    <i class="fas fa-desktop"></i>
                  </div>
                  <span class="sistema-name">{{ sistema.nome }}</span>
                </div>
              </td>
              <td class="description-cell">{{ sistema.descricao }}</td>
              <td class="status-cell">
                <span class="status-badge" :class="getStatusClass(sistema.status)">
                  {{ sistema.status }}
                </span>
              </td>
              <td class="actions-cell">
                <button class="action-btn edit-btn" @click="abrirEditar(sistema)" title="Editar">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete-btn" @click="excluirSistema(sistema.id)" title="Excluir">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showForm" class="modal-overlay" @click="fecharModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editando ? 'Editar Sistema' : 'Adicionar Sistema' }}</h3>
          <button class="close-button" @click="fecharModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="editando ? salvarEdicao() : cadastrarSistema()">
          <input v-model="form.nome" placeholder="Nome do Sistema" required />
          <input v-model="form.descricao" placeholder="Descrição" />
          <input v-model="form.status" placeholder="Status" required />
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
  name: 'Sistemas',
  data() {
    return {
      sistemas: [],
      buscaSistema: '',
      ordenacaoNome: 'asc',
      showForm: false,
      editando: false,
      sistemaEditId: null,
      form: {
        nome: '',
        descricao: '',
        status: ''
      }
    }
  },
  computed: {
    sistemasFiltrados() {
      let lista = this.sistemas;
      if (this.buscaSistema) {
        const busca = this.buscaSistema.toLowerCase();
        lista = lista.filter(s => {
          const nome = (s.nome || '').toLowerCase();
          const descricao = (s.descricao || '').toLowerCase();
          const status = (s.status || '').toLowerCase();
          return (
            nome.includes(busca) ||
            descricao.includes(busca) ||
            status.includes(busca)
          );
        });
      }
      return lista.slice().sort((a, b) => {
        const nomeA = (a.nome || '').toLowerCase();
        const nomeB = (b.nome || '').toLowerCase();
        if (nomeA < nomeB) return this.ordenacaoNome === 'asc' ? -1 : 1;
        if (nomeA > nomeB) return this.ordenacaoNome === 'asc' ? 1 : -1;
        return 0;
      });
    },
    sistemasAtivos() {
      return this.sistemas.filter(sistema => 
        sistema.status && sistema.status.toLowerCase() === 'ativo'
      );
    }
  },
  mounted() {
    this.carregarSistemas();
  },
  methods: {
    toggleOrdenacaoNome() {
      this.ordenacaoNome = this.ordenacaoNome === 'asc' ? 'desc' : 'asc';
    },
    async carregarSistemas() {
      try {
        const response = await axios.get(`${API_BASE_URL}/sistemas`);
        this.sistemas = response.data;
      } catch (error) {
        console.error('Erro ao carregar sistemas:', error);
      }
    },
    async cadastrarSistema() {
      try {
        await axios.post(`${API_BASE_URL}/sistemas`, this.form);
        this.carregarSistemas();
        this.fecharModal();
      } catch (error) {
        console.error('Erro ao cadastrar sistema:', error);
      }
    },
    abrirEditar(sistema) {
      this.editando = true;
      this.sistemaEditId = sistema.id;
      this.form = {
        nome: sistema.nome,
        descricao: sistema.descricao,
        status: sistema.status
      };
      this.showForm = true;
    },
    async salvarEdicao() {
      try {
        await axios.put(`${API_BASE_URL}/sistemas/${this.sistemaEditId}`, this.form);
        this.carregarSistemas();
        this.fecharModal();
      } catch (error) {
        console.error('Erro ao salvar edição:', error);
      }
    },
    fecharModal() {
      this.showForm = false;
      this.editando = false;
      this.sistemaEditId = null;
      this.form = { nome: '', descricao: '', status: '' };
    },
    async excluirSistema(id) {
      if (confirm('Tem certeza que deseja excluir este sistema?')) {
        try {
          await axios.delete(`${API_BASE_URL}/sistemas/${id}`);
          this.carregarSistemas();
        } catch (error) {
          console.error('Erro ao excluir sistema:', error);
        }
      }
    },
    getStatusClass(status) {
      if (!status) return 'status-undefined';
      const statusLower = status.toLowerCase();
      if (statusLower === 'ativo') return 'status-active';
      if (statusLower === 'inativo') return 'status-inactive';
      return 'status-default';
    }
  }
}
</script>

<style scoped>
/* Layout Container Principal */
.sistemas-container {
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

.stat-icon.inactive {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
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

.sistema-icon {
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

.sistema-name {
  font-weight: 600;
  color: #1f2937;
}

.description-cell {
  color: #6b7280;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-cell {
  text-align: center;
}

.status-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.status-active {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
  border: 1px solid #10b981;
}

.status-badge.status-inactive {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
  border: 1px solid #ef4444;
}

.status-badge.status-default {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #374151;
  border: 1px solid #9ca3af;
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

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
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
  .sistemas-container {
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
</style>
