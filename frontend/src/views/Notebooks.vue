<template>
  <div class="notebooks-container">
    <!-- Header Premium -->
    <div class="header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-title">
            <h1>
              <i class="fas fa-laptop header-icon"></i>
              Gestão de Notebooks
            </h1>
            <p class="header-subtitle">Gerencie os notebooks, patrimônios e atribuições</p>
          </div>
        </div>
        <div class="header-right">
          <div class="controls-group">
            <div class="search-control">
              <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input 
                  v-model="searchQuery" 
                  placeholder="Buscar notebooks (Patrimônio, Colaborador...)" 
                  class="search-input" 
                />
                <button v-if="searchQuery" @click="searchQuery = ''" class="clear-search">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            <div class="action-buttons">
              <button class="btn-action-premium" @click="openCreateModal">
                <i class="fas fa-plus"></i>
                <span>Novo Notebook</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Stats Dashboard -->
      <div class="stats-dashboard">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-laptop"></i>
          </div>
          <div class="stat-content">
            <span v-if="isLoading" class="skeleton-dark skeleton-text" style="width: 40px; height: 32px; margin-bottom: 4px;"></span>
            <span v-else class="stat-number">{{ notebooks.length }}</span>
            <span class="stat-label">Total Cadastrados</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon active">
            <i class="fas fa-user-check"></i>
          </div>
          <div class="stat-content">
            <span v-if="isLoading" class="skeleton-dark skeleton-text" style="width: 40px; height: 32px; margin-bottom: 4px;"></span>
            <span v-else class="stat-number">{{ notebooksAtribuidos }}</span>
            <span class="stat-label">Atribuídos</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon inactive">
            <i class="fas fa-box-open"></i>
          </div>
          <div class="stat-content">
            <span v-if="isLoading" class="skeleton-dark skeleton-text" style="width: 40px; height: 32px; margin-bottom: 4px;"></span>
            <span v-else class="stat-number">{{ notebooksDisponiveis }}</span>
            <span class="stat-label">Em Estoque</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs e Conteúdo -->
    <div class="content-area">
      <div class="tabs-premium">
        <button 
          class="tab-btn-premium" 
          :class="{ active: activeTab === 'atribuidos' }" 
          @click="activeTab = 'atribuidos'"
        >
          <i class="fas fa-user-check"></i> Notebooks Atribuídos
        </button>
        <button 
          class="tab-btn-premium" 
          :class="{ active: activeTab === 'estoque' }" 
          @click="activeTab = 'estoque'"
        >
          <i class="fas fa-box-open"></i> Estoque TI
        </button>
      </div>

      <div class="content-padding">
        <!-- Tabela de Notebooks Atribuídos -->
        <div v-if="activeTab === 'atribuidos'" class="tab-content-premium">
          <div class="table-container-premium">
            <table class="modern-table-premium">
              <thead>
                <tr>
                  <th>Patrimônio</th>
                  <th>Modelo/Note</th>
                  <th>Data Entrega</th>
                  <th>Colaborador</th>
                  <th>Setor</th>
                  <th class="actions-column">Ações</th>
                </tr>
              </thead>
              <tbody>
                <template v-if="isLoading && !notebooks.length">
                  <tr v-for="i in 5" :key="i">
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text" style="width: 60px;"></div></td>
                  </tr>
                </template>
                <tr v-else-if="filteredAtribuidos.length > 0" v-for="note in filteredAtribuidos" :key="note.id">
                  <td class="font-bold">{{ note.patrimonio || '-' }}</td>
                  <td>{{ note.modelo || '-' }}</td>
                  <td>{{ formatDate(note.data_entrega) || '-' }}</td>
                  <td>{{ getFuncionarioNome(note.funcionario_id) }}</td>
                  <td>{{ getSetorNome(note.setor_id) }}</td>
                  <td class="actions-cell">
                    <button class="action-btn-premium edit-btn" @click="editNotebook(note)" title="Editar"><i class="fas fa-edit"></i></button>
                    <button class="action-btn-premium delete-btn" @click="deleteNotebook(note.id)" title="Excluir"><i class="fas fa-trash"></i></button>
                  </td>
                </tr>
                <tr v-else>
                  <td colspan="6" class="empty-state-premium">Nenhum notebook atribuído encontrado.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Tab Estoque TI -->
        <div v-else class="tab-content-premium">
          <div class="table-container-premium">
            <table class="modern-table-premium">
              <thead>
                <tr>
                  <th>Patrimônio</th>
                  <th>Modelo/Note</th>
                  <th>Status</th>
                  <th class="actions-column">Ações</th>
                </tr>
              </thead>
              <tbody>
                <template v-if="isLoading && !notebooks.length">
                  <tr v-for="i in 3" :key="i">
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text" style="width: 80px;"></div></td>
                    <td><div class="skeleton-dark skeleton-text" style="width: 60px;"></div></td>
                  </tr>
                </template>
                <tr v-else-if="filteredEstoque.length > 0" v-for="note in filteredEstoque" :key="note.id">
                  <td class="font-bold">{{ note.patrimonio || '-' }}</td>
                  <td>{{ note.modelo || '-' }}</td>
                  <td>
                    <span style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                      Disponível em Estoque
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button class="action-btn-premium edit-btn" @click="editNotebook(note)" title="Atribuir a Colaborador"><i class="fas fa-user-plus"></i></button>
                    <button class="action-btn-premium delete-btn" @click="deleteNotebook(note.id)" title="Excluir"><i class="fas fa-trash"></i></button>
                  </td>
                </tr>
                <tr v-else>
                  <td colspan="4" class="empty-state-premium">Estoque vazio ou não encontrado.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Cadastro / Edição -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingNote ? 'Editar Notebook' : 'Novo Notebook' }}</h3>
          <button @click="showModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label>Patrimônio</label>
              <input v-model="form.patrimonio" placeholder="Ex: NTB-001">
            </div>
            <div class="form-group">
              <label>Note / Modelo</label>
              <input v-model="form.modelo" placeholder="Ex: Dell Latitude">
            </div>
            <div class="form-group">
              <label>Data de Entrega</label>
              <input type="date" v-model="form.data_entrega">
            </div>
            <div class="form-group">
              <label>Setor</label>
              <select v-model="form.setor_id">
                <option :value="null">Nenhum</option>
                <option v-for="s in setores" :key="s.id" :value="s.id">{{ s.nome }}</option>
              </select>
            </div>
            <div class="form-group" style="grid-column: 1 / -1;">
              <label>Colaborador</label>
              <select v-model="form.funcionario_id">
                <option :value="null">Estoque / Nenhum</option>
                <option v-for="f in sortedFuncionarios" :key="f.id" :value="f.id">
                  {{ f.nome }} {{ f.sobrenome }}
                </option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn-primary" @click="saveNotebook">Salvar</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '@/api.js';

export default {
  name: 'Notebooks',
  data() {
    return {
      activeTab: 'atribuidos',
      notebooks: [],
      funcionarios: [],
      setores: [],
      
      searchQuery: '',
      
      showModal: false,
      editingNote: null,
      form: {
        patrimonio: '', modelo: '', data_entrega: '', funcionario_id: null, setor_id: null
      },
      
      isLoading: false
    };
  },
  computed: {
    sortedFuncionarios() {
      return [...this.funcionarios].sort((a,b) => a.nome.localeCompare(b.nome));
    },
    notebooksAtribuidos() {
      return this.notebooks.filter(n => n.funcionario_id).length;
    },
    notebooksDisponiveis() {
      return this.notebooks.filter(n => !n.funcionario_id).length;
    },
    filteredAtribuidos() {
      let result = this.notebooks.filter(n => n.funcionario_id);
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        result = result.filter(n => {
          const str = `${n.patrimonio || ''} ${n.modelo || ''} ${this.getFuncionarioNome(n.funcionario_id)} ${this.getSetorNome(n.setor_id)}`.toLowerCase();
          return str.includes(q);
        });
      }
      return result;
    },
    filteredEstoque() {
      let result = this.notebooks.filter(n => !n.funcionario_id);
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        result = result.filter(n => {
          const str = `${n.patrimonio || ''} ${n.modelo || ''}`.toLowerCase();
          return str.includes(q);
        });
      }
      return result;
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.isLoading = true;
      try {
        const [noteRes, funcRes, setorRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/notebooks/`),
          axios.get(`${API_BASE_URL}/funcionarios/dropdown`),
          axios.get(`${API_BASE_URL}/setores/`)
        ]);
        this.notebooks = noteRes.data;
        this.funcionarios = funcRes.data;
        this.setores = setorRes.data;
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        this.isLoading = false;
      }
    },
    getFuncionarioNome(id) {
      if (!id) return 'Estoque';
      const f = this.funcionarios.find(f => f.id === id);
      return f ? `${f.nome} ${f.sobrenome}` : 'Desconhecido';
    },
    getSetorNome(id) {
      if (!id) return '-';
      const s = this.setores.find(s => s.id === id);
      return s ? s.nome : '-';
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const [y, m, d] = dateString.split('-');
      if (y && m && d) return `${d}/${m}/${y}`;
      return dateString;
    },
    
    openCreateModal() {
      this.editingNote = null;
      this.form = { patrimonio: '', modelo: '', data_entrega: '', funcionario_id: null, setor_id: null };
      this.showModal = true;
    },
    editNotebook(note) {
      this.editingNote = note;
      this.form = { ...note };
      this.showModal = true;
    },
    async saveNotebook() {
      try {
        if (this.editingNote) {
           await axios.put(`${API_BASE_URL}/notebooks/${this.editingNote.id}`, this.form);
        } else {
           await axios.post(`${API_BASE_URL}/notebooks/`, this.form);
        }
        this.showModal = false;
        this.fetchData();
      } catch (error) {
        console.error('Erro ao salvar notebook:', error);
        alert('Erro ao salvar notebook. Verifique os dados.');
      }
    },
    async deleteNotebook(id) {
      if (!confirm('Tem certeza que deseja excluir?')) return;
      try {
        await axios.delete(`${API_BASE_URL}/notebooks/${id}`);
        this.fetchData();
      } catch (error) {
        console.error('Erro ao excluir notebook:', error);
        alert('Erro ao excluir notebook.');
      }
    }
  }
};
</script>

<style scoped>
/* Usando as mesmas classes do Celulares.vue para manter a consistência do tema */
.notebooks-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 20px;
}

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
  width: 350px;
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
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-action-premium {
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
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.btn-action-premium:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
  transform: translateY(-2px);
}

/* Stats */
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
}

.stat-icon.active { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.stat-icon.inactive { background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); }

.stat-content { display: flex; flex-direction: column; }
.stat-number { font-size: 2rem; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.stat-label { font-size: 0.9rem; opacity: 0.85; font-weight: 500; }

/* Tabs */
.content-area { background: white; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }
.tabs-premium { display: flex; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.tab-btn-premium { flex: 1; padding: 16px; border: none; background: transparent; font-weight: 600; color: #64748b; font-size: 15px; cursor: pointer; transition: all 0.3s ease; border-bottom: 3px solid transparent; display: flex; align-items: center; justify-content: center; gap: 8px; }
.tab-btn-premium:hover { color: #3b82f6; background: rgba(59, 130, 246, 0.05); }
.tab-btn-premium.active { color: #3b82f6; border-bottom-color: #3b82f6; background: white; }

.content-padding { padding: 24px; }

/* Tables */
.modern-table-premium { width: 100%; border-collapse: separate; border-spacing: 0; }
.modern-table-premium th { padding: 16px; text-align: left; background: #f8fafc; color: #475569; font-weight: 600; font-size: 14px; border-bottom: 2px solid #e2e8f0; }
.modern-table-premium td { padding: 16px; border-bottom: 1px solid #f1f5f9; color: #334155; font-size: 14px; vertical-align: middle; }
.modern-table-premium tr:hover td { background-color: #f8fafc; }

.actions-cell { display: flex; gap: 8px; }
.action-btn-premium { width: 36px; height: 36px; border-radius: 8px; border: none; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s ease; }
.edit-btn { background: #eff6ff; color: #3b82f6; }
.edit-btn:hover { background: #3b82f6; color: white; }
.delete-btn { background: #fef2f2; color: #ef4444; }
.delete-btn:hover { background: #ef4444; color: white; }

/* Modals */
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 9999; }
.modal-content { background: white; border-radius: 20px; width: 100%; max-width: 600px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); overflow: hidden; animation: modalIn 0.3s ease; }
@keyframes modalIn { from { opacity: 0; transform: translateY(20px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-header { padding: 20px 24px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.modal-header h3 { margin: 0; font-size: 1.25rem; font-weight: 700; color: #1e293b; }
.close-btn { background: none; border: none; font-size: 24px; color: #94a3b8; cursor: pointer; transition: color 0.2s; line-height: 1; }
.close-btn:hover { color: #ef4444; }
.modal-body { padding: 24px; max-height: calc(100vh - 200px); overflow-y: auto; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 14px; font-weight: 600; color: #475569; }
.form-group input, .form-group select { padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; color: #334155; transition: all 0.2s; background: white; }
.form-group input:focus, .form-group select:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.modal-footer { padding: 16px 24px; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 12px; background: #f8fafc; }
.btn-primary, .btn-secondary { padding: 10px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn-primary { background: #3b82f6; color: white; }
.btn-primary:hover { background: #2563eb; transform: translateY(-1px); }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #475569; }
.btn-secondary:hover { background: #f1f5f9; color: #1e293b; }
</style>
