
<template>
  <div class="usuarios-analytics">
    <!-- Header Premium -->
    <div class="usuarios-header">
      <div class="header-content">
        <h1>
          <i class="fas fa-user-shield"></i>
          Gerenciamento de Usuários
        </h1>
        <p class="usuarios-subtitle">Controle de acesso e permissões do sistema</p>
      </div>
      <div class="header-actions">
        <div class="search-container">
          <i class="fas fa-search"></i>
          <input 
            v-model="filtro" 
            class="search-input" 
            placeholder="Buscar usuário..." 
          />
        </div>
        <button @click="abrirFormulario" class="btn-primary">
          <i class="fas fa-plus"></i>
          Novo Usuário
        </button>
      </div>
    </div>

    <!-- Cards de Estatísticas -->
    <div class="dashboard-cards">
      <div class="premium-card usuarios-card">
        <div class="card-background">
          <div class="card-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="card-content">
            <div class="card-label">Total de Usuários</div>
            <div class="card-value">{{ usuarios.length }}</div>
            <div class="card-trend">
              <i class="fas fa-arrow-up"></i>
              Ativos no sistema
            </div>
          </div>
          <div class="card-decoration"></div>
        </div>
      </div>
    </div>

    <!-- Tabela Premium -->
    <div class="table-container">
      <div class="table-header">
        <h3>
          <i class="fas fa-list"></i>
          Lista de Usuários
        </h3>
      </div>
      
      <div class="modern-table-wrapper">
        <table class="modern-table">
          <thead>
            <tr>
              <th>
                <div class="th-content">
                  <i class="fas fa-user"></i>
                  Nome de Usuário
                </div>
              </th>
              <th>
                <div class="th-content">
                  <i class="fas fa-shield-alt"></i>
                  Status
                </div>
              </th>
              <th>
                <div class="th-content">
                      <i class="fas fa-user-shield"></i>
                      Permissão
                </div>
              </th>
                  <th>
                    <div class="th-content">
                      <i class="fas fa-cogs"></i>
                      Ações
                    </div>
                  </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="usuario in usuariosFiltrados" :key="usuario.id" class="table-row">
              <td>
                <div class="user-info">
                  <div class="user-avatar">
                    <i class="fas fa-user"></i>
                  </div>
                  <div class="user-details">
                    <div class="user-name">{{ usuario.username }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span class="status-badge status-active">
                  <i class="fas fa-check-circle"></i>
                  Ativo
                </span>
              </td>
              <td>
                <div>
                  <div v-if="usuario.permissoes && usuario.permissoes.length > 0">
                    <small v-for="p in usuario.permissoes" :key="p.id" class="perm-chip">{{ p.codigo }}</small>
                  </div>
                  <div v-else>
                    <small class="perm-chip perm-none">Nenhuma</small>
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button v-if="$auth && ($auth.hasPermission('editar_permissoes') || $auth.hasPermission('adm'))" @click="abrirEditarPermissoes(usuario)" class="btn-action btn-perm" title="Editar Permissões">
                    <i class="fas fa-user-lock"></i>
                    <span>Permissões</span>
                  </button>
                  <button v-if="$auth && ($auth.hasPermission('editar_usuario') || $auth.hasPermission('adm'))" @click="editarUsuario(usuario)" class="btn-action btn-edit" title="Editar">
                    <i class="fas fa-edit"></i>
                    <span>Editar</span>
                  </button>
                  <button v-if="$auth && ($auth.hasPermission('excluir_usuario') || $auth.hasPermission('adm'))" @click="excluirUsuario(usuario.id)" class="btn-action btn-delete" title="Excluir">
                    <i class="fas fa-trash"></i>
                    <span>Excluir</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Premium -->
    <div v-if="mostrarFormulario" class="modal-overlay" @click="fecharFormulario">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="fas fa-user-plus" v-if="!usuarioEditando"></i>
            <i class="fas fa-user-edit" v-else></i>
            {{ usuarioEditando ? 'Editar Usuário' : 'Novo Usuário' }}
          </h3>
          <button @click="fecharFormulario" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="salvarUsuario" class="usuario-form">
            <div class="form-group">
              <label>
                <i class="fas fa-user"></i>
                Nome de Usuário
              </label>
              <input 
                v-model="form.username" 
                class="form-input"
                placeholder="Digite o nome de usuário" 
                required 
              />
            </div>
            <div class="form-group">
              <label>
                <i class="fas fa-lock"></i>
                Senha
              </label>
              <input 
                v-model="form.password" 
                type="password" 
                class="form-input"
                placeholder="Digite a senha" 
                :required="!usuarioEditando" 
              />
              <small v-if="usuarioEditando" class="form-hint">
                Deixe em branco para manter a senha atual
              </small>
              <label>
                <i class="fas fa-building"></i>
                Setores de acesso
              </label>
              <div class="multi-select-container">
                <div class="selected-items" style="margin-bottom: 8px;">
                  <span v-for="id in form.setores_ids" :key="id" class="selected-chip" @click="removerSetorUsuario(id)" style="background:#e3e7fa;color:#3a3a3a;margin-right:4px;cursor:pointer;display:inline-block;padding:2px 10px;border-radius:12px;font-size:13px;">
                    {{ getSetorNomeUsuario(id) }} <span class="chip-close" style="margin-left:4px;font-weight:bold;">&times;</span>
                  </span>
                </div>
                <select v-model="novoSetorIdUsuario" @change="adicionarSetorUsuario" class="form-input">
                  <option value="">+ Adicionar setor...</option>
                  <option v-for="setor in setores" :key="setor.id" :value="setor.id">
                    {{ setor.nome }}
                  </option>
                </select>
              </div>
            </div>
            <small v-if="form.setores_ids.length === 0" class="form-hint">Selecione pelo menos um setor para acesso</small>
          </form>
        </div>
        
        <div class="modal-footer">
          <button type="button" @click="fecharFormulario" class="btn-secondary">
            <i class="fas fa-times"></i>
            Cancelar
          </button>
          <button type="submit" @click="salvarUsuario" class="btn-primary" :disabled="salvando">
            <i class="fas fa-save" v-if="!salvando"></i>
            <i class="fas fa-spinner fa-spin" v-if="salvando"></i>
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Permissões -->
    <div v-if="mostrarModalPermissoes" class="modal-overlay" @click="mostrarModalPermissoes = false">
      <div class="modal-container modal-permissoes" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="fas fa-user-lock"></i>
            Editar Permissões - {{ usuarioPermissoesEditando ? usuarioPermissoesEditando.username : '' }}
          </h3>
          <button @click="mostrarModalPermissoes = false" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="permissoes-list">
            <label v-for="p in permissoes" :key="p.id" class="perm-item">
              <input type="checkbox" :value="p.id" v-model="permissoesSelecionadas" />
              <div class="perm-text">
                <div class="perm-code">{{ p.codigo }}</div>
                <div class="perm-desc">{{ p.descricao }}</div>
              </div>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="mostrarModalPermissoes = false" class="btn-secondary">Cancelar</button>
          <button @click="salvarPermissoesUsuario" class="btn-primary perm-save">Salvar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '@/api.js'

export default {
  name: 'Usuarios',
  data() {
    return {
      usuarios: [],
        permissoes: [],
      mostrarFormulario: false,
      usuarioEditando: null,
      salvando: false,
      form: {
        username: '',
        password: '',
        setores_ids: []
      },
        mostrarModalPermissoes: false,
        usuarioPermissoesEditando: null,
        permissoesSelecionadas: [],
      setores: [],
      filtro: '',
      novoSetorIdUsuario: ''
    };
  },
  computed: {
    usuariosFiltrados() {
      if (!this.filtro) return this.usuarios;
      return this.usuarios.filter(u => 
        u.username.toLowerCase().includes(this.filtro.toLowerCase())
      );
    }
  },
  methods: {
    async carregarSetores() {
      try {
        const res = await axios.get(`${API_BASE_URL}/setores/`);
        this.setores = res.data;
      } catch (error) {
        console.error('Erro ao carregar setores:', error);
        this.setores = [];
      }
    },
    async carregarUsuarios() {
      try {
        const res = await axios.get(`${API_BASE_URL}/usuarios/`);
        this.usuarios = res.data;
      } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        this.usuarios = [];
      }
    },
    async carregarPermissoes() {
      try {
        const res = await axios.get(`${API_BASE_URL}/permissoes/`);
        this.permissoes = res.data;
      } catch (error) {
        console.error('Erro ao carregar permissões:', error);
        this.permissoes = [];
      }
    },
    
    abrirFormulario() {
      this.mostrarFormulario = true;
      this.usuarioEditando = null;
      this.form = { username: '', password: '', setores_ids: [] };
      this.novoSetorIdUsuario = '';
    },
    getSetorNomeUsuario(id) {
      const setor = this.setores.find(s => String(s.id) === String(id));
      return setor ? setor.nome : 'Setor não encontrado';
    },
    adicionarSetorUsuario() {
      const id = parseInt(this.novoSetorIdUsuario);
      if (id && !this.form.setores_ids.includes(id)) {
        this.form.setores_ids.push(id);
      }
      this.novoSetorIdUsuario = '';
    },
    removerSetorUsuario(id) {
      this.form.setores_ids = this.form.setores_ids.filter(sId => String(sId) !== String(id));
    },
    
    fecharFormulario() {
      this.mostrarFormulario = false;
      this.usuarioEditando = null;
      this.salvando = false;
    },
    
    async salvarUsuario() {
      this.salvando = true;
      try {
        if (this.usuarioEditando) {
          await axios.put(`${API_BASE_URL}/usuarios/${this.usuarioEditando.id}`, this.form);
        } else {
          await axios.post(`${API_BASE_URL}/usuarios/`, this.form);
        }
        this.fecharFormulario();
        this.carregarUsuarios();
      } catch (error) {
        console.error('Erro ao salvar usuário:', error);
        alert('Erro ao salvar usuário!');
      }
      this.salvando = false;
    },
    
    async editarUsuario(usuario) {
      // Garante que setores estejam carregados antes de abrir o formulário
      if (!this.setores || this.setores.length === 0) {
        await this.carregarSetores();
      }
      console.log('Usuário selecionado para edição:', usuario);
      this.usuarioEditando = usuario;
      this.form = { 
        username: usuario.username, 
        password: '',
        setores_ids: Array.isArray(usuario.setores)
          ? usuario.setores.map(s => s.id)
          : []
      };
      console.log('Setores vinculados:', this.form.setores_ids);
      this.mostrarFormulario = true;
    },
    
    async excluirUsuario(id) {
      if (confirm('Deseja realmente excluir este usuário?')) {
        try {
          await axios.delete(`${API_BASE_URL}/usuarios/${id}`);
          this.carregarUsuarios();
        } catch (error) {
          console.error('Erro ao excluir usuário:', error);
          alert('Erro ao excluir usuário!');
        }
      }
    }
    ,
    abrirEditarPermissoes(usuario) {
      this.usuarioPermissoesEditando = usuario;
      this.permissoesSelecionadas = Array.isArray(usuario.permissoes) ? usuario.permissoes.map(p => p.id) : [];
      this.mostrarModalPermissoes = true;
      // garante que as permissoes estejam carregadas
      if (!this.permissoes || this.permissoes.length === 0) {
        this.carregarPermissoes();
      }
    },
    async salvarPermissoesUsuario() {
      if (!this.usuarioPermissoesEditando) return;
      try {
        const payload = { permissoes_ids: this.permissoesSelecionadas };
        const res = await axios.put(`${API_BASE_URL}/usuarios/${this.usuarioPermissoesEditando.id}/permissoes`, payload);
        // Atualiza a lista local de usuários rapidamente
        this.usuarios = this.usuarios.map(u => u.id === this.usuarioPermissoesEditando.id ? { ...u, permissoes: res.data.permissoes } : u);

        // Recarrega o usuário autenticado no frontend (atualiza localStorage e $auth)
        try {
          if (this.$auth && typeof this.$auth.loadCurrentUser === 'function') {
            await this.$auth.loadCurrentUser();
            // Emite evento global para componentes que queiram reagir à mudança de permissões
            try {
              window.dispatchEvent(new CustomEvent('auth:updated', { detail: { user: this.$auth.getCurrentUser() } }));
            } catch (evErr) {
              // browsers antigos podem falhar na construção do CustomEvent
              window.dispatchEvent(new Event('auth:updated'));
            }
          }
        } catch (authErr) {
          console.warn('Falha ao recarregar usuário após salvar permissões:', authErr);
        }

        this.mostrarModalPermissoes = false;
        this.usuarioPermissoesEditando = null;
      } catch (error) {
        console.error('Erro ao salvar permissões:', error);
        alert('Erro ao salvar permissões');
      }
    }
  },
  
  mounted() {
  this.carregarUsuarios();
  this.carregarSetores();
  }
};
</script>

<style scoped>
/* ===== TEMA PREMIUM USUARIOS ===== */
.usuarios-analytics {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ===== HEADER PREMIUM ===== */
.usuarios-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-content h1 {
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-content h1 i {
  background: linear-gradient(45deg, #ffd700, #ffed4e);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.2rem;
}

.usuarios-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  margin: 0.5rem 0 0 0;
  font-weight: 300;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-container {
  position: relative;
  display: flex;
  align-items: center;
}

.search-container i {
  position: absolute;
  left: 1rem;
  color: rgba(255, 255, 255, 0.6);
  z-index: 1;
}

.search-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  padding: 0.8rem 1rem 0.8rem 2.5rem;
  color: white;
  font-size: 1rem;
  width: 300px;
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.2);
  border-color: #ffd700;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
}

.btn-primary {
  background: linear-gradient(45deg, #ffd700, #ffed4e);
  color: #1a1a1a;
  font-weight: 600;
  border: none;
  border-radius: 25px;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4);
}

/* ===== CARDS PREMIUM ===== */
.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.premium-card {
  height: 140px;
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.premium-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.usuarios-card .card-background {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-background {
  position: relative;
  width: 100%;
  height: 100%;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  overflow: hidden;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: white;
  flex-shrink: 0;
}

.card-content {
  flex: 1;
  color: white;
}

.card-label {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 0.5rem;
}

.card-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.card-trend {
  font-size: 0.8rem;
  opacity: 0.7;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.card-decoration {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

/* ===== TABELA PREMIUM ===== */
.table-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.table-header h3 {
  color: #2d3748;
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.table-header h3 i {
  color: #667eea;
}

.modern-table-wrapper {
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.modern-table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.modern-table th {
  padding: 1rem;
  color: white;
  font-weight: 600;
  text-align: left;
  border: none;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modern-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.table-row:hover {
  background: #f8fafc;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #2d3748;
  font-size: 1rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-active {
  background: #c6f6d5;
  color: #22543d;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
  font-weight: 500;
}

.btn-edit {
  background: #bee3f8;
  color: #2b6cb0;
}

.btn-edit:hover {
  background: #90cdf4;
  transform: translateY(-1px);
}

.btn-delete {
  background: #fed7d7;
  color: #c53030;
}

.btn-delete:hover {
  background: #feb2b2;
  transform: translateY(-1px);
}

/* ===== MODAL PREMIUM ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  animation: modalSlideIn 0.3s ease-out;
}

/* Modal de permissões específico */
.modal-permissoes {
  max-width: 640px;
  width: 95%;
}

.permissoes-list {
  max-height: 320px;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.perm-item {
  display: flex;
  gap: 0.8rem;
  align-items: flex-start;
  padding: 0.6rem 0.2rem;
  border-bottom: 1px dashed #eef2ff;
}

.perm-item input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin-top: 4px;
}

.perm-text {
  display: flex;
  flex-direction: column;
}

.perm-code {
  font-weight: 700;
  color: #2d3748;
}

.perm-desc {
  font-size: 0.88rem;
  color: #606f7b;
}

.btn-primary.perm-save {
  background: linear-gradient(45deg, #ffd700, #ffcf33);
  color: #111;
  box-shadow: 0 8px 30px rgba(255, 203, 6, 0.25);
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

.modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: background 0.2s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 2rem;
}

.usuario-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-group label i {
  color: #667eea;
}

.form-input {
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.8rem;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-hint {
  color: #718096;
  font-size: 0.8rem;
  margin-top: 0.2rem;
}

.modal-footer {
  background: #f7fafc;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-secondary {
  background: #edf2f7;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.8rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.btn-secondary:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ===== RESPONSIVIDADE ===== */
@media (max-width: 768px) {
  .usuarios-analytics {
    padding: 1rem;
  }
  
  .usuarios-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .search-input {
    width: 100%;
  }
  
  .dashboard-cards {
    grid-template-columns: 1fr;
  }
  
  .table-container {
    padding: 1rem;
    overflow-x: auto;
  }
  
  .modern-table {
    min-width: 600px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .modal-container {
    margin: 1rem;
    width: calc(100% - 2rem);
  }
}
</style>
