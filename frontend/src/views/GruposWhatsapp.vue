<template>
  <div class="grupos-whatsapp-analytics">
    <!-- Header Premium -->
    <div class="grupos-header">
      <div class="header-content">
        <h1>
          <i class="fab fa-whatsapp"></i>
          Grupos de WhatsApp
        </h1>
        <p class="grupos-subtitle">Gerenciamento de grupos de comunicação</p>
      </div>
      <div class="header-actions">
        <div class="search-container">
          <i class="fas fa-search"></i>
          <input 
            v-model="filtro" 
            class="search-input" 
            placeholder="Buscar grupo..." 
          />
        </div>
        <button @click="abrirFormulario" class="btn-primary">
          <i class="fas fa-plus"></i>
          Novo Grupo
        </button>
      </div>
    </div>

    <!-- Cards de Estatísticas -->
    <div class="dashboard-cards">
      <div class="premium-card grupos-card">
        <div class="card-background">
          <div class="card-icon">
            <i class="fab fa-whatsapp"></i>
          </div>
          <div class="card-content">
            <div class="card-label">Total de Grupos</div>
            <div class="card-value">{{ grupos.length }}</div>
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
          Lista de Grupos
        </h3>
      </div>
      
      <div class="modern-table-wrapper">
        <table class="modern-table">
          <thead>
            <tr>
              <th>
                <div class="th-content">
                  <i class="fab fa-whatsapp"></i>
                  Nome do Grupo
                </div>
              </th>
              <th>
                <div class="th-content">
                  <i class="fas fa-info-circle"></i>
                  Descrição
                </div>
              </th>
              <th>
                <div class="th-content">
                  <i class="fas fa-users"></i>
                  Participantes
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
            <!-- Estado vazio quando não há grupos -->
            <tr v-if="gruposFiltrados.length === 0" class="empty-state-row">
              <td colspan="4">
                <div class="empty-state">
                  <div class="empty-icon">
                    <i class="fab fa-whatsapp"></i>
                  </div>
                  <h3>{{ grupos.length === 0 ? 'Nenhum grupo criado ainda' : 'Nenhum grupo encontrado' }}</h3>
                  <p>{{ grupos.length === 0 ? 'Crie seu primeiro grupo de WhatsApp para começar a organizar suas comunicações!' : 'Tente ajustar os filtros de busca ou criar um novo grupo.' }}</p>
                  <button v-if="grupos.length === 0" @click="abrirFormulario" class="btn-primary">
                    <i class="fas fa-plus"></i>
                    Criar Primeiro Grupo
                  </button>
                </div>
              </td>
            </tr>
            
            <!-- Lista de grupos -->
            <tr v-for="grupo in gruposFiltrados" :key="grupo.id" class="table-row">
              <td>
                <div class="grupo-info">
                  <div class="grupo-avatar">
                    <i class="fab fa-whatsapp"></i>
                  </div>
                  <div class="grupo-details">
                    <div class="grupo-name">{{ grupo.nome }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span class="description-text">
                  {{ grupo.descricao || 'Sem descrição' }}
                </span>
              </td>
              <td>
                <span class="participants-count">
                  <i class="fas fa-users"></i>
                  {{ grupo.funcionarios?.length || 0 }} participante(s)
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editarGrupo(grupo)" class="btn-action btn-edit" title="Editar">
                    <i class="fas fa-edit"></i>
                    <span>Editar</span>
                  </button>
                  <button @click="gerenciarParticipantes(grupo)" class="btn-action btn-users" title="Gerenciar Participantes">
                    <i class="fas fa-users-cog"></i>
                    <span>Participantes</span>
                  </button>
                  <button @click="excluirGrupo(grupo.id)" class="btn-action btn-delete" title="Excluir">
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

    <!-- Modal de Criação/Edição -->
    <div v-if="mostrarFormulario" class="modal-overlay" @click="fecharFormulario">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="fab fa-whatsapp" v-if="!grupoEditando"></i>
            <i class="fas fa-edit" v-else></i>
            {{ grupoEditando ? 'Editar Grupo' : 'Novo Grupo' }}
          </h3>
          <button @click="fecharFormulario" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="salvarGrupo" class="grupo-form">
            <div class="form-group">
              <label>
                <i class="fab fa-whatsapp"></i>
                Nome do Grupo
              </label>
              <input 
                v-model="form.nome" 
                class="form-input"
                placeholder="Digite o nome do grupo" 
                required 
              />
            </div>
            
            <div class="form-group">
              <label>
                <i class="fas fa-info-circle"></i>
                Descrição
              </label>
              <textarea 
                v-model="form.descricao" 
                class="form-textarea"
                placeholder="Digite uma descrição para o grupo (opcional)" 
                rows="3"
              ></textarea>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button type="button" @click="fecharFormulario" class="btn-secondary">
            <i class="fas fa-times"></i>
            Cancelar
          </button>
          <button type="submit" @click="salvarGrupo" class="btn-primary" :disabled="salvando">
            <i class="fas fa-save" v-if="!salvando"></i>
            <i class="fas fa-spinner fa-spin" v-if="salvando"></i>
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Gerenciar Participantes -->
    <div v-if="mostrarModalParticipantes" class="modal-overlay" @click="fecharModalParticipantes">
      <div class="modal-container large-modal" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="fas fa-users-cog"></i>
            Gerenciar Participantes - {{ grupoSelecionado?.nome }}
          </h3>
          <button @click="fecharModalParticipantes" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="participants-section">
            <h4>
              <i class="fas fa-users"></i>
              Participantes Atuais ({{ participantes.length }})
            </h4>
            <div class="participants-list">
              <div v-for="participante in participantes" :key="participante.id" class="participant-item">
                <div class="participant-info">
                  <div class="participant-avatar">
                    <i class="fas fa-user"></i>
                  </div>
                  <div class="participant-details">
                    <span class="participant-name">{{ participante.nome }} {{ participante.sobrenome }}</span>
                    <span class="participant-email">{{ participante.email }}</span>
                  </div>
                </div>
                <button @click="removerParticipante(participante.id)" class="btn-remove">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>

          <div class="add-participants-section">
            <h4>
              <i class="fas fa-user-plus"></i>
              Adicionar Participantes
            </h4>
            <div class="search-participants">
              <input 
                v-model="filtroFuncionarios" 
                class="form-input"
                placeholder="Buscar funcionários..." 
              />
            </div>
            <div class="available-participants">
              <div v-for="funcionario in funcionariosDisponiveis" :key="funcionario.id" class="participant-item">
                <div class="participant-info">
                  <div class="participant-avatar">
                    <i class="fas fa-user"></i>
                  </div>
                  <div class="participant-details">
                    <span class="participant-name">{{ funcionario.nome }} {{ funcionario.sobrenome }}</span>
                    <span class="participant-email">{{ funcionario.email }}</span>
                  </div>
                </div>
                <button @click="adicionarParticipante(funcionario.id)" class="btn-add">
                  <i class="fas fa-plus"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" @click="fecharModalParticipantes" class="btn-primary">
            <i class="fas fa-check"></i>
            Concluído
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from '@/api.js'

export default {
  name: 'GruposWhatsapp',
  data() {
    return {
      grupos: [],
      funcionarios: [],
      participantes: [],
      mostrarFormulario: false,
      mostrarModalParticipantes: false,
      grupoEditando: null,
      grupoSelecionado: null,
      salvando: false,
      filtro: '',
      filtroFuncionarios: '',
      form: {
        nome: '',
        descricao: ''
      }
    };
  },
  computed: {
    gruposFiltrados() {
      if (!this.filtro) return this.grupos;
      return this.grupos.filter(g => 
        (g.nome && g.nome.toLowerCase().includes(this.filtro.toLowerCase())) ||
        (g.descricao && g.descricao.toLowerCase().includes(this.filtro.toLowerCase()))
      );
    },
    funcionariosDisponiveis() {
      const participantesIds = this.participantes.map(p => p.id);
      let disponiveis = this.funcionarios.filter(f => !participantesIds.includes(f.id));
      
      if (this.filtroFuncionarios) {
        disponiveis = disponiveis.filter(f => 
          (f.nome && f.nome.toLowerCase().includes(this.filtroFuncionarios.toLowerCase())) ||
          (f.sobrenome && f.sobrenome.toLowerCase().includes(this.filtroFuncionarios.toLowerCase())) ||
          (f.email && f.email.toLowerCase().includes(this.filtroFuncionarios.toLowerCase()))
        );
      }
      
      return disponiveis;
    }
  },
  methods: {
    async carregarGrupos() {
      try {
        const response = await fetch(`${API_BASE_URL}/grupos_whatsapp/`);
        this.grupos = await response.json();
      } catch (error) {
        console.error('Erro ao carregar grupos:', error);
        this.grupos = [];
      }
    },

    async carregarFuncionarios() {
      try {
        const response = await fetch(`${API_BASE_URL}/funcionarios/`);
        this.funcionarios = await response.json();
      } catch (error) {
        console.error('Erro ao carregar funcionários:', error);
        this.funcionarios = [];
      }
    },

    async carregarParticipantes(grupoId) {
      try {
        const response = await fetch(`${API_BASE_URL}/grupos_whatsapp/${grupoId}`);
        const grupo = await response.json();
        this.participantes = grupo.funcionarios || [];
      } catch (error) {
        console.error('Erro ao carregar participantes:', error);
        this.participantes = [];
      }
    },
    
    abrirFormulario() {
      this.mostrarFormulario = true;
      this.grupoEditando = null;
      this.form = { nome: '', descricao: '' };
    },
    
    fecharFormulario() {
      this.mostrarFormulario = false;
      this.grupoEditando = null;
      this.salvando = false;
    },
    
    async salvarGrupo() {
      this.salvando = true;
      try {
        if (this.grupoEditando) {
          const response = await fetch(`${API_BASE_URL}/grupos_whatsapp/${this.grupoEditando.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.form)
          });
          if (!response.ok) throw new Error('Erro ao atualizar grupo');
        } else {
          const response = await fetch(`${API_BASE_URL}/grupos_whatsapp/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.form)
          });
          if (!response.ok) throw new Error('Erro ao criar grupo');
        }
        this.fecharFormulario();
        this.carregarGrupos();
      } catch (error) {
        console.error('Erro ao salvar grupo:', error);
        alert('Erro ao salvar grupo!');
      }
      this.salvando = false;
    },
    
    editarGrupo(grupo) {
      this.grupoEditando = grupo;
      this.form = { 
        nome: grupo.nome, 
        descricao: grupo.descricao || '' 
      };
      this.mostrarFormulario = true;
    },
    
    async excluirGrupo(id) {
      if (confirm('Deseja realmente excluir este grupo?')) {
        try {
          const response = await fetch(`${API_BASE_URL}/grupos_whatsapp/${id}`, {
            method: 'DELETE'
          });
          if (!response.ok) throw new Error('Erro ao excluir grupo');
          this.carregarGrupos();
        } catch (error) {
          console.error('Erro ao excluir grupo:', error);
          alert('Erro ao excluir grupo!');
        }
      }
    },

    async gerenciarParticipantes(grupo) {
      this.grupoSelecionado = grupo;
      this.mostrarModalParticipantes = true;
      await this.carregarParticipantes(grupo.id);
    },

    fecharModalParticipantes() {
      this.mostrarModalParticipantes = false;
      this.grupoSelecionado = null;
      this.participantes = [];
      this.filtroFuncionarios = '';
      this.carregarGrupos(); // Recarregar para atualizar contadores
    },

    async adicionarParticipante(funcionarioId) {
      try {
        const response = await fetch(
          `${API_BASE_URL}/grupos_whatsapp/${this.grupoSelecionado.id}/funcionarios/${funcionarioId}`, 
          { method: 'POST' }
        );
        if (!response.ok) throw new Error('Erro ao adicionar participante');
        await this.carregarParticipantes(this.grupoSelecionado.id);
      } catch (error) {
        console.error('Erro ao adicionar participante:', error);
        alert('Erro ao adicionar participante!');
      }
    },

    async removerParticipante(funcionarioId) {
      if (confirm('Deseja remover este participante do grupo?')) {
        try {
          const response = await fetch(
            `${API_BASE_URL}/grupos_whatsapp/${this.grupoSelecionado.id}/funcionarios/${funcionarioId}`, 
            { method: 'DELETE' }
          );
          if (!response.ok) throw new Error('Erro ao remover participante');
          await this.carregarParticipantes(this.grupoSelecionado.id);
        } catch (error) {
          console.error('Erro ao remover participante:', error);
          alert('Erro ao remover participante!');
        }
      }
    }
  },
  
  async mounted() {
    await this.carregarGrupos();
    await this.carregarFuncionarios();
  }
};
</script>

<style scoped>
/* ===== TEMA PREMIUM GRUPOS WHATSAPP ===== */
.grupos-whatsapp-analytics {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ===== HEADER PREMIUM ===== */
.grupos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 30px rgba(37, 211, 102, 0.2);
}

.header-content h1 {
  color: white;
  font-size: 2.8rem;
  font-weight: 800;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content h1 i {
  color: rgba(255, 255, 255, 0.95);
  font-size: 2.5rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.grupos-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.2rem;
  margin: 0.5rem 0 0 0;
  font-weight: 400;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
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
  color: #718096;
  z-index: 1;
  font-weight: 500;
}

.search-input {
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  padding: 0.8rem 1rem 0.8rem 2.5rem;
  color: #2d3748;
  font-size: 1rem;
  width: 300px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.search-input::placeholder {
  color: #718096;
  font-weight: 400;
}

.search-input:focus {
  outline: none;
  background: white;
  border-color: #25D366;
  box-shadow: 0 0 20px rgba(37, 211, 102, 0.3);
}

.btn-primary {
  background: linear-gradient(45deg, #25D366, #128C7E);
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
  box-shadow: 0 6px 20px rgba(37, 211, 102, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(37, 211, 102, 0.5);
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

.grupos-card .card-background {
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
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
  background: white;
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.table-header h3 {
  color: #1a202c;
  font-size: 1.6rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.table-header h3 i {
  color: #25D366;
  font-size: 1.4rem;
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
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
}

.modern-table th {
  padding: 1.2rem;
  color: white;
  font-weight: 700;
  text-align: center;
  border: none;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.th-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.modern-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
  text-align: center;
}

.table-row:hover {
  background: #f8fafc;
}

.grupo-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.grupo-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.grupo-details {
  flex: 1;
}

.grupo-name {
  font-weight: 700;
  color: #1a202c;
  font-size: 1.1rem;
  letter-spacing: 0.3px;
}

.description-text {
  color: #4a5568;
  font-size: 0.95rem;
  font-style: italic;
  font-weight: 500;
}

.participants-count {
  color: #2d3748;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-weight: 600;
}

.participants-count i {
  color: #25D366;
  font-size: 1rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.btn-action {
  border: none;
  border-radius: 10px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.btn-edit {
  background: #e6f3ff;
  color: #1e40af;
  border: 1px solid #93c5fd;
}

.btn-edit:hover {
  background: #dbeafe;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.25);
}

.btn-users {
  background: #dcfce7;
  color: #16a34a;
  border: 1px solid #86efac;
}

.btn-users:hover {
  background: #bbf7d0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.25);
}

.btn-delete {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.btn-delete:hover {
  background: #fecaca;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25);
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

.large-modal {
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
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
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
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

.grupo-form {
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
  color: #25D366;
}

.form-input,
.form-textarea {
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.8rem;
  font-size: 1rem;
  transition: all 0.2s ease;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #25D366;
  box-shadow: 0 0 0 3px rgba(37, 211, 102, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
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

/* ===== MODAL PARTICIPANTES ===== */
.participants-section,
.add-participants-section {
  margin-bottom: 2rem;
}

.participants-section h4,
.add-participants-section h4 {
  color: #1a202c;
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.participants-section h4 i {
  color: #25D366;
  font-size: 1.2rem;
}

.add-participants-section h4 i {
  color: #3182ce;
  font-size: 1.2rem;
}

.participants-list,
.available-participants {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem;
}

.participant-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: background 0.2s ease;
}

.participant-item:hover {
  background: #f7fafc;
}

.participant-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.participant-avatar {
  width: 35px;
  height: 35px;
  border-radius: 8px;
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
}

.participant-details {
  display: flex;
  flex-direction: column;
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

.btn-remove,
.btn-add {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.btn-remove {
  background: #fed7d7;
  color: #c53030;
}

.btn-remove:hover {
  background: #feb2b2;
  transform: scale(1.1);
}

.btn-add {
  background: #c6f6d5;
  color: #25855a;
}

.btn-add:hover {
  background: #9ae6b4;
  transform: scale(1.1);
}

.search-participants {
  margin-bottom: 1rem;
}

/* ===== ESTADO VAZIO ===== */
.empty-state-row {
  border: none !important;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #4a5568;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
  box-shadow: 0 8px 25px rgba(37, 211, 102, 0.3);
}

.empty-state h3 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #718096;
  font-size: 1rem;
  margin-bottom: 2rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

/* ===== RESPONSIVIDADE ===== */
@media (max-width: 768px) {
  .grupos-whatsapp-analytics {
    padding: 1rem;
  }
  
  .grupos-header {
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
    min-width: 700px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .modal-container {
    margin: 1rem;
    width: calc(100% - 2rem);
  }

  .large-modal {
    max-height: 90vh;
  }
}
</style>
