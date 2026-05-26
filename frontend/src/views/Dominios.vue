<template>
  <div class="dominios-container">
    <!-- Header Premium -->
    <div class="header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-title">
            <h1>
              <i class="fas fa-globe header-icon"></i>
              Gestão de Domínios
            </h1>
            <p class="header-subtitle">Gerencie os domínios de internet, hospedagens e datas de vencimento</p>
          </div>
        </div>
        <div class="header-right">
          <div class="controls-group">
            <div class="search-control">
              <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input 
                  v-model="searchQuery" 
                  placeholder="Buscar domínio..." 
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
                <span>Novo Domínio</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Stats Dashboard -->
      <div class="stats-dashboard">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-globe"></i>
          </div>
          <div class="stat-content">
            <span v-if="isLoading" class="skeleton-dark skeleton-text" style="width: 40px; height: 32px; margin-bottom: 4px;"></span>
            <span v-else class="stat-number">{{ dominios.length }}</span>
            <span class="stat-label">Total Cadastrados</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon inactive">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="stat-content">
            <span v-if="isLoading" class="skeleton-dark skeleton-text" style="width: 40px; height: 32px; margin-bottom: 4px;"></span>
            <span v-else class="stat-number">{{ dominiosPertoVencer }}</span>
            <span class="stat-label">Perto do Vencimento (&lt; 30 dias)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabela -->
    <div class="content-area">
      <div class="content-padding">
        <div class="table-container-premium">
          <table class="modern-table-premium">
            <thead>
              <tr>
                <th>Domínio</th>
                <th>Data de Vencimento</th>
                <th>Hospedagem</th>
                <th>Provedor</th>
                <th>Status / Dias para Expirar</th>
                <th class="actions-column">Ações</th>
              </tr>
            </thead>
            <tbody>
              <template v-if="isLoading && !dominios.length">
                <tr v-for="i in 3" :key="i">
                  <td><div class="skeleton-dark skeleton-text"></div></td>
                  <td><div class="skeleton-dark skeleton-text"></div></td>
                  <td><div class="skeleton-dark skeleton-text"></div></td>
                  <td><div class="skeleton-dark skeleton-text" style="width: 80px;"></div></td>
                  <td><div class="skeleton-dark skeleton-text" style="width: 60px;"></div></td>
                </tr>
              </template>
              <tr v-else-if="filteredDominios.length > 0" v-for="dominio in filteredDominios" :key="dominio.id">
                <td class="font-bold">
                  <a :href="'https://' + dominio.dominio" target="_blank" style="color: #3b82f6; text-decoration: none;">
                    {{ dominio.dominio }}
                  </a>
                </td>
                <td>{{ formatDate(dominio.data_vencimento) }}</td>
                <td>{{ dominio.hospedagem || '-' }}</td>
                <td>{{ dominio.provedor || '-' }}</td>
                <td>
                  <span :class="getStatusClass(dominio.data_vencimento)">
                    {{ getDiasParaExpirarText(dominio.data_vencimento) }}
                  </span>
                </td>
                <td class="actions-cell">
                  <button class="action-btn-premium edit-btn" @click="editDominio(dominio)" title="Editar"><i class="fas fa-edit"></i></button>
                  <button class="action-btn-premium delete-btn" @click="deleteDominio(dominio.id)" title="Excluir"><i class="fas fa-trash"></i></button>
                </td>
              </tr>
              <tr v-else>
                <td colspan="5" class="empty-state-premium">Nenhum domínio encontrado.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal de Cadastro / Edição -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingDominio ? 'Editar Domínio' : 'Novo Domínio' }}</h3>
          <button @click="showModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group" style="margin-bottom: 16px;">
            <label>Domínio</label>
            <input v-model="form.dominio" placeholder="Ex: meusite.com.br" />
          </div>
          <div class="form-group" style="margin-bottom: 16px;">
            <label>Data de Vencimento</label>
            <input type="date" v-model="form.data_vencimento" />
          </div>
          <div class="form-group" style="margin-bottom: 16px;">
            <label>Hospedagem</label>
            <input v-model="form.hospedagem" placeholder="Ex: HostGator, AWS..." />
          </div>
          <div class="form-group" style="margin-bottom: 16px;">
            <label>Provedor</label>
            <input v-model="form.provedor" placeholder="Ex: Registro.br, GoDaddy..." />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn-primary" @click="saveDominio">Salvar</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '@/api.js';

export default {
  name: 'Dominios',
  data() {
    return {
      dominios: [],
      searchQuery: '',
      showModal: false,
      editingDominio: null,
      form: {
        dominio: '', data_vencimento: '', hospedagem: '', provedor: ''
      },
      isLoading: false
    };
  },
  computed: {
    filteredDominios() {
      let filtered = this.dominios;
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        filtered = filtered.filter(d => {
          const str = `${d.dominio || ''} ${d.hospedagem || ''} ${d.provedor || ''}`.toLowerCase();
          return str.includes(q);
        });
      }
      
      // Ordenar por urgência: vermelhos (dias < 0) primeiro, amarelos em seguida, verdes por último
      return filtered.sort((a, b) => {
        const diasA = this.calcularDiasRestantes(a.data_vencimento);
        const diasB = this.calcularDiasRestantes(b.data_vencimento);
        return diasA - diasB;
      });
    },
    dominiosPertoVencer() {
      return this.dominios.filter(d => {
        const dias = this.calcularDiasRestantes(d.data_vencimento);
        return dias >= 0 && dias <= 30;
      }).length;
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.isLoading = true;
      try {
        const res = await axios.get(`${API_BASE_URL}/dominios/`);
        this.dominios = res.data;
      } catch (error) {
        console.error('Erro ao buscar domínios:', error);
      } finally {
        this.isLoading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const [y, m, d] = dateString.split('-');
      if (y && m && d) return `${d}/${m}/${y}`;
      return dateString;
    },
    calcularDiasRestantes(dataVencimento) {
      if (!dataVencimento) return 0;
      const hoje = new Date();
      hoje.setHours(0, 0, 0, 0);
      const vencimento = new Date(dataVencimento + 'T00:00:00');
      const diferencaTempo = vencimento.getTime() - hoje.getTime();
      return Math.ceil(diferencaTempo / (1000 * 3600 * 24));
    },
    getDiasParaExpirarText(dataVencimento) {
      const dias = this.calcularDiasRestantes(dataVencimento);
      if (dias < 0) return `Expirado há ${Math.abs(dias)} dia(s)`;
      if (dias === 0) return "Expira HOJE";
      if (dias === 1) return "Expira amanhã";
      return `Expira em ${dias} dia(s)`;
    },
    getStatusClass(dataVencimento) {
      const dias = this.calcularDiasRestantes(dataVencimento);
      let className = "status-badge ";
      if (dias < 0) {
        return className + "status-danger";
      } else if (dias <= 30) {
        return className + "status-warning";
      } else {
        return className + "status-success";
      }
    },
    openCreateModal() {
      this.editingDominio = null;
      this.form = { dominio: '', data_vencimento: '', hospedagem: '', provedor: '' };
      this.showModal = true;
    },
    editDominio(dominio) {
      this.editingDominio = dominio;
      this.form = { ...dominio };
      this.showModal = true;
    },
    async saveDominio() {
      try {
        if (this.editingDominio) {
           await axios.put(`${API_BASE_URL}/dominios/${this.editingDominio.id}`, this.form);
        } else {
           await axios.post(`${API_BASE_URL}/dominios/`, this.form);
        }
        this.showModal = false;
        this.fetchData();
      } catch (error) {
        console.error('Erro ao salvar domínio:', error);
        const msg = error.response?.data?.detail || 'Erro ao salvar domínio. Verifique os dados.';
        alert(msg);
      }
    },
    async deleteDominio(id) {
      if (!confirm('Tem certeza que deseja excluir?')) return;
      try {
        await axios.delete(`${API_BASE_URL}/dominios/${id}`);
        this.fetchData();
      } catch (error) {
        console.error('Erro ao excluir domínio:', error);
        alert('Erro ao excluir domínio.');
      }
    }
  }
};
</script>

<style scoped>
.dominios-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 20px;
}

.header-premium {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 10px 40px rgba(59, 130, 246, 0.15), 0 4px 16px rgba(59, 130, 246, 0.1);
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

.header-title h1 {
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

.stat-icon.inactive { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }

.stat-content { display: flex; flex-direction: column; }
.stat-number { font-size: 2rem; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.stat-label { font-size: 0.9rem; opacity: 0.85; font-weight: 500; }

/* Status Badges */
.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}
.status-success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}
.status-warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}
.status-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Content */
.content-area { background: white; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }
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
.modal-content { background: white; border-radius: 20px; width: 100%; max-width: 500px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); overflow: hidden; animation: modalIn 0.3s ease; }
@keyframes modalIn { from { opacity: 0; transform: translateY(20px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-header { padding: 20px 24px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.modal-header h3 { margin: 0; font-size: 1.25rem; font-weight: 700; color: #1e293b; }
.close-btn { background: none; border: none; font-size: 24px; color: #94a3b8; cursor: pointer; transition: color 0.2s; line-height: 1; }
.close-btn:hover { color: #ef4444; }
.modal-body { padding: 24px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 14px; font-weight: 600; color: #475569; }
.form-group input { padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; color: #334155; transition: all 0.2s; }
.form-group input:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.modal-footer { padding: 16px 24px; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 12px; background: #f8fafc; }
.btn-primary, .btn-secondary { padding: 10px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn-primary { background: #3b82f6; color: white; }
.btn-primary:hover { background: #2563eb; transform: translateY(-1px); }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #475569; }
.btn-secondary:hover { background: #f1f5f9; color: #1e293b; }
</style>
