<template>
  <div class="celulares-container">
    <!-- Header Premium -->
    <div class="header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-title">
            <h1>
              <i class="fas fa-mobile-alt header-icon"></i>
              Gestão de Celulares
            </h1>
            <p class="header-subtitle">Gerencie linhas móveis, aparelhos e contas associadas</p>
          </div>
        </div>
        <div class="header-right">
          <div class="controls-group">
            <div class="search-control">
              <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input 
                  v-if="activeTab === 'linhas'"
                  v-model="searchQueryLinha" 
                  placeholder="Buscar celulares (Marca, IMEI, Colaborador...)" 
                  class="search-input" 
                />
                <input 
                  v-else
                  v-model="searchQueryConta" 
                  placeholder="Buscar contas (Gmail, Colaborador...)" 
                  class="search-input" 
                />
                <button v-if="activeTab === 'linhas' ? searchQueryLinha : searchQueryConta" @click="activeTab === 'linhas' ? searchQueryLinha = '' : searchQueryConta = ''" class="clear-search">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            <div class="action-buttons">
              <button class="btn-action-premium" @click="openCreateModal">
                <i class="fas fa-plus"></i>
                <span>{{ activeTab === 'linhas' ? 'Nova Linha' : 'Nova Conta' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Stats Dashboard -->
      <div class="stats-dashboard">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-sim-card"></i>
          </div>
          <div class="stat-content">
            <span v-if="isLoading" class="skeleton-dark skeleton-text" style="width: 40px; height: 32px; margin-bottom: 4px;"></span>
            <span v-else class="stat-number">{{ linhas.length }}</span>
            <span class="stat-label">Total Linhas</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon active">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <span v-if="isLoading" class="skeleton-dark skeleton-text" style="width: 40px; height: 32px; margin-bottom: 4px;"></span>
            <span v-else class="stat-number">{{ linhasAtivasCount }}</span>
            <span class="stat-label">Ativas</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon inactive">
            <i class="fas fa-ban"></i>
          </div>
          <div class="stat-content">
            <span v-if="isLoading" class="skeleton-dark skeleton-text" style="width: 40px; height: 32px; margin-bottom: 4px;"></span>
            <span v-else class="stat-number">{{ linhasBloqueadasCount }}</span>
            <span class="stat-label">Bloqueadas</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fab fa-google"></i>
          </div>
          <div class="stat-content">
            <span v-if="isLoading" class="skeleton-dark skeleton-text" style="width: 40px; height: 32px; margin-bottom: 4px;"></span>
            <span v-else class="stat-number">{{ contas.length }}</span>
            <span class="stat-label">Contas Gmail</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs e Conteúdo -->
    <div class="content-area">
      <div class="tabs-premium">
        <button 
          class="tab-btn-premium" 
          :class="{ active: activeTab === 'linhas' }" 
          @click="activeTab = 'linhas'"
        >
          <i class="fas fa-sim-card"></i> Linhas de Celular
        </button>
        <button 
          class="tab-btn-premium" 
          :class="{ active: activeTab === 'contas' }" 
          @click="activeTab = 'contas'"
        >
          <i class="fab fa-google"></i> Contas Gmail
        </button>
      </div>

      <div class="content-padding">
        <!-- Tabela de Linhas -->
        <div v-if="activeTab === 'linhas'" class="tab-content-premium">
          <div class="table-container-premium">
            <table class="modern-table-premium">
              <thead>
                <tr>
                  <th>Marca/Modelo</th>
                  <th>IMEI</th>
                  <th>Número/Chip</th>
                  <th>Plano</th>
                  <th>Colaborador</th>
                  <th>Setor</th>
                  <th>Status</th>
                  <th class="actions-column">Ações</th>
                </tr>
              </thead>
              <tbody>
                <template v-if="isLoading && !linhas.length">
                  <tr v-for="i in 5" :key="i">
                    <td>
                      <div class="skeleton-dark skeleton-text" style="width: 80%"></div>
                      <div class="skeleton-dark skeleton-text" style="width: 50%; height: 10px;"></div>
                    </td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text"></div></td>
                    <td><div class="skeleton-dark skeleton-text" style="width: 70px; height: 24px; border-radius: 20px;"></div></td>
                    <td><div class="skeleton-dark skeleton-text" style="width: 60px;"></div></td>
                  </tr>
                </template>
                <tr v-else-if="filteredLinhas.length > 0" v-for="linha in filteredLinhas" :key="linha.id">
                  <td class="name-cell">
                    <div class="device-info">
                      <span class="device-brand">{{ linha.marca || '-' }}</span>
                      <span class="device-model">{{ linha.modelo || '-' }}</span>
                    </div>
                  </td>
                  <td>{{ linha.imei || '-' }}</td>
                  <td>{{ linha.numero_chip || '-' }}</td>
                  <td>{{ linha.plano || '-' }}</td>
                  <td>{{ getFuncionarioNome(linha.funcionario_id) }}</td>
                  <td>{{ getSetorNome(linha.setor_id) }}</td>
                  <td>
                    <span :class="['status-badge-premium', (linha.bloqueio && linha.bloqueio !== 'Ativo') ? 'status-inactive' : 'status-active']">
                      {{ linha.bloqueio || 'Ativo' }}
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button class="action-btn-premium edit-btn" @click="editLinha(linha)" title="Editar"><i class="fas fa-edit"></i></button>
                    <button class="action-btn-premium delete-btn" @click="deleteLinha(linha.id)" title="Excluir"><i class="fas fa-trash"></i></button>
                  </td>
                </tr>
                <tr v-else>
                  <td colspan="8" class="empty-state-premium">Nenhuma linha encontrada.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tabela de Contas -->
        <div v-else class="tab-content-premium">
          <div class="table-container-premium">
            <table class="modern-table-premium">
              <thead>
                <tr>
                  <th>Gmail</th>
                  <th>Senha</th>
                  <th>Aparelho Associado</th>
                  <th>Colaborador</th>
                  <th class="actions-column">Ações</th>
                </tr>
              </thead>
              <tbody>
                <template v-if="isLoading && !contas.length">
                  <tr v-for="i in 5" :key="i">
                    <td><div class="skeleton-dark skeleton-text" style="width: 90%"></div></td>
                    <td><div class="skeleton-dark skeleton-text" style="width: 100px;"></div></td>
                    <td><div class="skeleton-dark skeleton-text" style="width: 120px;"></div></td>
                    <td><div class="skeleton-dark skeleton-text" style="width: 150px;"></div></td>
                    <td><div class="skeleton-dark skeleton-text" style="width: 60px;"></div></td>
                  </tr>
                </template>
                <tr v-else-if="filteredContas.length > 0" v-for="conta in filteredContas" :key="conta.id">
                  <td class="email-cell">{{ conta.gmail }}</td>
                  <td>
                    <div class="password-wrapper">
                      <span class="password-text">{{ visiblePasswords[conta.id] ? conta.senha : '••••••••' }}</span>
                      <button class="view-pass-btn" @click="togglePassword(conta.id)">
                        <i :class="['fas', visiblePasswords[conta.id] ? 'fa-eye-slash' : 'fa-eye']"></i>
                      </button>
                    </div>
                  </td>
                  <td>{{ getDeviceDisplay(conta.celular_id) }}</td>
                  <td>{{ getFuncionarioNome(conta.funcionario_id) }}</td>
                  <td class="actions-cell">
                    <button class="action-btn-premium edit-btn" @click="editConta(conta)" title="Editar"><i class="fas fa-edit"></i></button>
                    <button class="action-btn-premium delete-btn" @click="deleteConta(conta.id)" title="Excluir"><i class="fas fa-trash"></i></button>
                  </td>
                </tr>
                <tr v-else>
                  <td colspan="5" class="empty-state-premium">Nenhuma conta encontrada.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modais -->
    
    <!-- Modal de Importação -->
    <div v-if="showImportModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Importar Planilha de Celulares</h3>
          <button @click="showImportModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <p>Selecione o arquivo Excel (.xlsx) ou CSV para importar os dados.</p>
          <div class="file-upload-area">
            <input type="file" ref="fileInput" @change="handleFileChange" accept=".xlsx, .xls, .csv" />
            <div class="upload-icon"><i class="fas fa-cloud-upload-alt"></i></div>
            <span v-if="!selectedFile">Clique ou arraste o arquivo aqui</span>
            <span v-else>{{ selectedFile.name }}</span>
          </div>
          <div v-if="isImporting" class="importing-overlay">
             <div class="spinner"></div>
             <span>Processando planilha...</span>
          </div>
          <div v-if="importResult" class="import-result" :class="importResult.status">
            {{ importResult.message }}
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showImportModal = false">Cancelar</button>
          <button class="btn-primary" @click="uploadFile" :disabled="!selectedFile || isImporting">
            Iniciar Importação
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Cadastro / Edição de LINHA -->
    <div v-if="showLinhaModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingLinha ? 'Editar Linha' : 'Nova Linha' }}</h3>
          <button @click="showLinhaModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label>Marca</label>
              <input v-model="formLinha.marca" placeholder="Ex: Samsung">
            </div>
            <div class="form-group">
              <label>Modelo</label>
              <input v-model="formLinha.modelo" placeholder="Ex: A54">
            </div>
            <div class="form-group">
              <label>IMEI</label>
              <input v-model="formLinha.imei">
            </div>
            <div class="form-group">
              <label>Número/Chip</label>
              <input v-model="formLinha.numero_chip">
            </div>
            <div class="form-group">
              <label>Plano</label>
              <input v-model="formLinha.plano">
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="formLinha.bloqueio">
                <option value="">Não informado</option>
                <option value="Ativo">Ativo</option>
                <option value="Inativo">Inativo</option>
                <!-- Opção temporária caso haja dados antigos do legado -->
                <option v-if="formLinha.bloqueio && !['Ativo', 'Inativo', ''].includes(formLinha.bloqueio)" :value="formLinha.bloqueio">
                  {{ formLinha.bloqueio }} (Legado)
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Colaborador</label>
              <select v-model="formLinha.funcionario_id">
                <option :value="null">Nenhum</option>
                <option v-for="f in sortedFuncionarios" :key="f.id" :value="f.id">
                  {{ f.nome }} {{ f.sobrenome }}
                </option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showLinhaModal = false">Cancelar</button>
          <button class="btn-primary" @click="saveLinha">Salvar</button>
        </div>
      </div>
    </div>

    <!-- Modal de Cadastro / Edição de CONTA -->
    <div v-if="showContaModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingConta ? 'Editar Conta' : 'Nova Conta' }}</h3>
          <button @click="showContaModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Gmail</label>
            <input v-model="formConta.gmail" type="email" placeholder="usuario@gmail.com">
          </div>
          <div class="form-group">
            <label>Senha</label>
            <input v-model="formConta.senha" type="text">
          </div>
          <div class="form-group">
            <label>Associar ao Celular</label>
            <select v-model="formConta.celular_id">
              <option :value="null">Nenhum</option>
              <option v-for="l in linhas" :key="l.id" :value="l.id">
                {{ l.marca }} {{ l.modelo }} ({{ l.numero_chip }})
              </option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showContaModal = false">Cancelar</button>
          <button class="btn-primary" @click="saveConta">Salvar</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Celulares',
  data() {
    return {
      activeTab: 'linhas',
      linhas: [],
      contas: [],
      funcionarios: [],
      setores: [],
      visiblePasswords: {},
      
      searchQueryLinha: '',
      searchQueryConta: '',
      
      // Modais
      showImportModal: false,
      showLinhaModal: false,
      showContaModal: false,
      
      // Form Linha
      editingLinha: null,
      formLinha: {
        marca: '', modelo: '', imei: '', numero_chip: '', plano: '', bloqueio: '', funcionario_id: null
      },
      
      // Form Conta
      editingConta: null,
      formConta: {
        gmail: '', senha: '', celular_id: null, funcionario_id: null
      },
      
      // Import
      selectedFile: null,
      isImporting: false,
      importResult: null,
      isLoading: false
    };
  },
  computed: {
    sortedFuncionarios() {
      return [...this.funcionarios].sort((a,b) => a.nome.localeCompare(b.nome));
    },
    linhasAtivasCount() {
      return this.linhas.filter(l => l.bloqueio === 'Ativo').length;
    },
    linhasBloqueadasCount() {
      return this.linhas.filter(l => l.bloqueio && l.bloqueio !== 'Ativo' && l.bloqueio !== '').length;
    },
    filteredLinhas() {
      if (!this.searchQueryLinha) return this.linhas;
      const q = this.searchQueryLinha.toLowerCase();
      return this.linhas.filter(l => {
        const funcStr = this.getFuncionarioNome(l.funcionario_id).toLowerCase();
        const str = `${l.marca || ''} ${l.modelo || ''} ${l.imei || ''} ${l.numero_chip || ''} ${l.plano || ''} ${funcStr} ${this.getSetorNome(l.setor_id)} ${l.bloqueio || 'ativo'}`.toLowerCase();
        return str.includes(q);
      });
    },
    filteredContas() {
      if (!this.searchQueryConta) return this.contas;
      const q = this.searchQueryConta.toLowerCase();
      return this.contas.filter(c => {
        const str = `${c.gmail || ''} ${this.getDeviceDisplay(c.celular_id)} ${this.getFuncionarioNome(c.funcionario_id)}`.toLowerCase();
        return str.includes(q);
      });
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.isLoading = true;
      try {
        const [linhasRes, contasRes, funcRes, setorRes] = await Promise.all([
          axios.get('/celulares/linhas'),
          axios.get('/celulares/contas'),
          axios.get('/funcionarios/dropdown'),
          axios.get('/setores/')
        ]);
        this.linhas = linhasRes.data;
        this.contas = contasRes.data;
        this.funcionarios = funcRes.data;
        this.setores = setorRes.data;
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        this.isLoading = false;
      }
    },
    getFuncionarioNome(id) {
      if (!id) return '-';
      const f = this.funcionarios.find(f => f.id === id);
      return f ? `${f.nome} ${f.sobrenome}` : '-';
    },
    getSetorNome(id) {
      if (!id) return '-';
      const s = this.setores.find(s => s.id === id);
      return s ? s.nome : '-';
    },
    getDeviceDisplay(id) {
      if (!id) return '-';
      const l = this.linhas.find(l => l.id === id);
      return l ? `${l.marca} ${l.modelo} (${l.numero_chip || 'Sem Número'})` : '-';
    },
    togglePassword(id) {
      this.visiblePasswords[id] = !this.visiblePasswords[id];
      this.visiblePasswords = { ...this.visiblePasswords };
    },
    
    // Actions Linha
    openCreateModal() {
      if (this.activeTab === 'linhas') {
        this.editingLinha = null;
        this.formLinha = { marca: '', modelo: '', imei: '', numero_chip: '', plano: '', bloqueio: 'Ativo', funcionario_id: null };
        this.showLinhaModal = true;
      } else {
        this.editingConta = null;
        this.formConta = { gmail: '', senha: '', celular_id: null, funcionario_id: null };
        this.showContaModal = true;
      }
    },
    editLinha(linha) {
      this.editingLinha = linha;
      this.formLinha = { 
        ...linha,
        bloqueio: linha.bloqueio || 'Ativo'
      };
      this.showLinhaModal = true;
    },
    async saveLinha() {
      try {
        if (this.editingLinha) {
          await axios.put(`/celulares/linhas/${this.editingLinha.id}`, this.formLinha);
        } else {
          await axios.post('/celulares/linhas', this.formLinha);
        }
        this.showLinhaModal = false;
        this.fetchData();
      } catch (error) {
        alert('Erro ao salvar linha. Verifique os dados.');
      }
    },
    async deleteLinha(id) {
      if (!confirm('Tem certeza que deseja excluir esta linha?')) return;
      await axios.delete(`/celulares/linhas/${id}`);
      this.fetchData();
    },

    // Actions Conta
    editConta(conta) {
      this.editingConta = conta;
      this.formConta = { ...conta };
      this.showContaModal = true;
    },
    async saveConta() {
      try {
        if (this.editingConta) {
          await axios.put(`/celulares/contas/${this.editingConta.id}`, this.formConta);
        } else {
          await axios.post('/celulares/contas', this.formConta);
        }
        this.showContaModal = false;
        this.fetchData();
      } catch (error) {
        alert('Erro ao salvar conta.');
      }
    },
    async deleteConta(id) {
      if (!confirm('Tem certeza que deseja excluir esta conta?')) return;
      try {
        await axios.delete(`/celulares/contas/${id}`);
        this.fetchData();
      } catch (error) {
        alert('Erro ao excluir conta.');
      }
    },

    // Import
    handleFileChange(e) {
      this.selectedFile = e.target.files[0];
      this.importResult = null;
    },
    async uploadFile() {
      if (!this.selectedFile) return;
      this.isImporting = true;
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await axios.post('/celulares/importar', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        this.importResult = {
          status: 'success',
          message: `Sucesso! ${response.data.imported} carregados. ${response.data.errors.length} avisos.`
        };
        setTimeout(() => {
          this.showImportModal = false;
          this.fetchData();
        }, 2500);
      } catch (error) {
        this.importResult = { status: 'error', message: 'Erro crítico na importação.' };
      } finally {
        this.isImporting = false;
      }
    }
  }
};
</script>

<style scoped>
.celulares-container {
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

.action-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
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
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  font-size: 14px;
}

.btn-action-premium:hover {
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

/* Content Area */
.content-area {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* Tabs Premium */
.tabs-premium {
  display: flex;
  background: #f1f5f9;
  padding: 8px;
  gap: 8px;
}

.tab-btn-premium {
  flex: 1;
  padding: 14px 24px;
  border: none;
  background: transparent;
  color: #64748b;
  font-weight: 600;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.tab-btn-premium i {
  font-size: 1.1rem;
}

.tab-btn-premium.active {
  background: white;
  color: #2563eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.tab-btn-premium:hover:not(.active) {
  background: rgba(255, 255, 255, 0.5);
  color: #1e293b;
}

.content-padding {
  padding: 24px;
}

/* Modern Table */
.table-container-premium {
  overflow-x: auto;
}

.modern-table-premium {
  width: 100%;
  border-collapse: collapse;
}

.modern-table-premium th {
  text-align: left;
  padding: 16px;
  background: #f8fafc;
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #f1f5f9;
}

.modern-table-premium td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
  font-size: 0.9rem;
}

.modern-table-premium tr:hover {
  background: #f8fafc;
}

.device-info {
  display: flex;
  flex-direction: column;
}

.device-brand {
  font-weight: 700;
  color: #1a202c;
}

.device-model {
  font-size: 0.75rem;
  color: #64748b;
}

/* Status Badge */
.status-badge-premium {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  display: inline-block;
  text-transform: uppercase;
}

.status-active {
  background: #dcfce7;
  color: #166534;
}

.status-inactive {
  background: #fee2e2;
  color: #991b1b;
}

/* Password Field */
.password-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.password-text {
  font-family: monospace;
  font-size: 1rem;
}

.view-pass-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.view-pass-btn:hover {
  color: #3b82f6;
}

/* Actions Column */
.actions-column {
  text-align: center;
  width: 120px;
}

.actions-cell {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.action-btn-premium {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
}

.edit-btn { background: #3b82f6; }
.edit-btn:hover { background: #2563eb; transform: translateY(-1px); }

.delete-btn { background: #ef4444; }
.delete-btn:hover { background: #dc2626; transform: translateY(-1px); }

/* Empty States */
.empty-state-premium {
  text-align: center;
  padding: 48px !important;
  color: #64748b;
  font-style: italic;
}

.loading-spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner-premium {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Modais (Mantendo estrutura interna mas refinando) */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 600px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.modal-header {
  padding: 24px;
  background: #f8fafc;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 20px 24px;
  background: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #e2e8f0;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 6px;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus, .form-group select:focus {
  border-color: #3b82f6;
}
</style>
