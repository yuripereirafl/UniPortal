<template>
  <div class="usuarios-container">
    <div class="usuarios-header">
      <h2>Usuários</h2>
      <div class="usuarios-actions">
        <input v-model="filtro" class="usuarios-filtro" placeholder="Buscar usuário..." />
        <button class="btn-amarelo" @click="abrirFormulario">+ Adicionar Usuário</button>
      </div>
    </div>
    <table class="usuarios-tabela">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Grupos</th>
          <th>Unidades</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="usuario in usuariosFiltrados" :key="usuario.id">
          <tr>
                        <td>{{ usuario.username }}</td>
            <td class="grupos-cell">
              <div class="grupos-container">
                <span v-if="usuario.grupos && usuario.grupos.length" class="grupos-list">
                  <span v-for="grupo in usuario.grupos" :key="grupo.id" class="grupo-tag">
                    {{ grupo.nome }}
                  </span>
                </span>
                <span v-else class="sem-grupo">Sem grupos</span>
              </div>
            </td>
            <td class="unidades-cell">
              <div class="unidades-container">
                <span v-if="usuario.unidades && usuario.unidades.length" class="unidades-list">
                  <span v-for="(unidade, idx) in usuario.unidades" :key="unidade.id" class="unidade-tag">
                    {{ unidade.unidade }}
                  </span>
                </span>
                <span v-else class="sem-unidade">Sem unidades</span>
              </div>
            </td>
            <td class="acoes-cell">
              <div class="acoes-container">
                <button class="btn-acao editar" @click="editarUsuario(usuario)" title="Editar usuário">
                  <span class="icon">✏️</span>
                </button>
                <button class="btn-acao excluir" @click="excluirUsuario(usuario.id)" title="Excluir usuário">
                  <span class="icon">🗑️</span>
                </button>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
    <!-- Formulário de usuário -->
    <div v-if="mostrarFormulario" class="form-overlay">
      <div class="usuarios-formulario">
        <div class="form-header">
          <h3>{{ usuarioEditando ? 'Editar Usuário' : 'Adicionar Novo Usuário' }}</h3>
          <button class="btn-fechar" @click="fecharFormulario">×</button>
        </div>
        <form @submit.prevent="salvarUsuario" class="form-content">
          <div class="form-row">
            <div class="form-group">
              <label for="username">Nome de usuário:</label>
              <input id="username" v-model="form.username" placeholder="Digite o nome de usuário" required />
            </div>
            <div class="form-group">
              <label for="password">Senha:</label>
              <input id="password" v-model="form.password" type="password" placeholder="Digite a senha" :required="!usuarioEditando" />
            </div>
          </div>
          
          <div class="form-group">
            <label for="grupo">Permissão (Grupo):</label>
            <select id="grupo" v-model="form.grupo_id" required>
              <option value="" disabled>Selecione o grupo</option>
              <option v-for="grupo in grupos" :key="grupo.id" :value="grupo.id">{{ grupo.nome }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>Unidades:</label>
            <div class="multi-select-container">
              <div class="selected-items" v-if="form.unidades_ids.length > 0">
                <span v-for="unidadeId in form.unidades_ids" :key="unidadeId" class="selected-item">
                  {{ getUnidadeNome(unidadeId) }}
                  <button type="button" @click="removerUnidade(unidadeId)" class="remove-item">×</button>
                </span>
              </div>
              <select @change="adicionarUnidade" class="unidade-selector">
                <option value="">Selecione uma unidade para adicionar</option>
                <option 
                  v-for="unidade in unidadesDisponiveis" 
                  :key="unidade.id" 
                  :value="unidade.id"
                >
                  {{ unidade.unidade }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-salvar">{{ usuarioEditando ? 'Atualizar' : 'Criar Usuário' }}</button>
            <button type="button" class="btn-cancelar" @click="fecharFormulario">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      usuarios: [],
      grupos: [],
      unidades: [],
      mostrarFormulario: false,
      usuarioEditando: null,
      form: {
        username: '',
        password: '',
        grupo_id: null,
        unidades_ids: []
      },
      filtro: ''
    };
  },
  computed: {
    usuariosFiltrados() {
      if (!this.filtro) return this.usuarios;
      return this.usuarios.filter(u => u.username.toLowerCase().includes(this.filtro.toLowerCase()));
    },
    unidadesDisponiveis() {
      return this.unidades.filter(unidade => !this.form.unidades_ids.includes(unidade.id));
    }
  },
  methods: {
    async carregarUsuarios() {
      const token = localStorage.getItem('token');
      const res = await axios.get('/usuarios/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      this.usuarios = res.data;
    },
    async carregarGrupos() {
      const token = localStorage.getItem('token');
      const res = await axios.get('/grupos/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      this.grupos = res.data;
    },
    async carregarUnidades() {
      const token = localStorage.getItem('token');
      const res = await axios.get('/filiais/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      this.unidades = res.data;
    },
    abrirFormulario() {
      this.mostrarFormulario = true;
      this.usuarioEditando = null;
      this.form = { username: '', password: '', grupo_id: null, unidades_ids: [] };
    },
    fecharFormulario() {
      this.mostrarFormulario = false;
    },
    async salvarUsuario() {
      const token = localStorage.getItem('token');
      const dadosUsuario = {
        nome: this.form.username,
        email: this.form.username, // Usando username como email temporariamente
        grupos_ids: this.form.grupo_id ? [this.form.grupo_id] : [],
        unidades_ids: this.form.unidades_ids,
        password: this.form.password || undefined
      };

      try {
        if (this.usuarioEditando) {
          // Editando usuário existente
          await axios.put(`/usuarios/${this.usuarioEditando.id}`, dadosUsuario, {
            headers: { Authorization: `Bearer ${token}` }
          });
        } else {
          // Criando novo usuário
          // Para criação, a senha é obrigatória
          if (!this.form.password) {
            alert('Senha é obrigatória para novo usuário');
            return;
          }
          await axios.post('/usuarios/', dadosUsuario, {
            headers: { Authorization: `Bearer ${token}` }
          });
        }
        
        this.resetarFormulario();
        this.carregarUsuarios();
        alert('Usuário salvo com sucesso!');
      } catch (error) {
        console.error('Erro ao salvar usuário:', error);
        alert('Erro ao salvar usuário. Verifique os dados e tente novamente.');
      }
    },
    adicionarUnidade(event) {
      const unidadeId = parseInt(event.target.value);
      if (unidadeId && !this.form.unidades_ids.includes(unidadeId)) {
        this.form.unidades_ids.push(unidadeId);
      }
      event.target.value = ''; // Reset do select
    },
    removerUnidade(unidadeId) {
      const index = this.form.unidades_ids.indexOf(unidadeId);
      if (index > -1) {
        this.form.unidades_ids.splice(index, 1);
      }
    },
    getUnidadeNome(unidadeId) {
      const unidade = this.unidades.find(u => u.id === unidadeId);
      return unidade ? unidade.unidade : 'Unidade não encontrada';
    },
    resetarFormulario() {
      this.form = {
        username: '',
        password: '',
        grupo_id: null,
        unidades_ids: []
      };
      this.mostrarFormulario = false;
      this.usuarioEditando = null;
    },
    editarUsuario(usuario) {
      this.usuarioEditando = usuario;
      this.form = {
        username: usuario.username,
        password: '',
        grupo_id: usuario.grupos && usuario.grupos.length > 0 ? usuario.grupos[0].id : null,
        unidades_ids: usuario.unidades ? usuario.unidades.map(u => u.id) : []
      };
      this.mostrarFormulario = true;
    },
    async excluirUsuario(id) {
      if (confirm('Deseja realmente excluir este usuário? Esta ação também removerá todos os vínculos com grupos e unidades.')) {
        try {
          const token = localStorage.getItem('token');
          await axios.delete(`/usuarios/${id}`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          this.carregarUsuarios();
          alert('Usuário excluído com sucesso!');
        } catch (error) {
          console.error('Erro ao excluir usuário:', error);
          alert('Erro ao excluir usuário. Tente novamente.');
        }
      }
    },
    getUnidadeNome(unidadeId) {
      const unidade = this.unidades.find(u => u.id === unidadeId);
      return unidade ? unidade.unidade : 'Unidade não encontrada';
    }
  },
  mounted() {
    this.carregarUsuarios();
    this.carregarGrupos();
    this.carregarUnidades();
  }
};

</script>

<style scoped>
.modal-unidade {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.modal-content {
  background: #fff;
  padding: 32px;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(20,65,121,0.12);
  min-width: 320px;
  text-align: center;
}

.usuarios-container {
  max-width: 900px;
  margin: 40px auto;
  background: #fff;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(20,65,121,0.12);
}
.usuarios-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.usuarios-header h2 {
  color: var(--cor-primaria, #1a3972);
  font-family: var(--font-titulo, sans-serif);
  font-size: 2rem;
  margin: 0;
}
.usuarios-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.usuarios-filtro {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #bdbdbd;
  font-size: 1rem;
  outline: none;
}
.btn-amarelo {
  background: #ffc107;
  color: #1a3972;
  font-weight: bold;
  border: none;
  border-radius: 6px;
  padding: 10px 22px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-amarelo:hover {
  background: #ffb300;
}
/* Estilos da tabela */
.usuarios-tabela {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.usuarios-tabela th {
  background: #1a3972;
  color: #fff;
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #ffc107;
}
.usuarios-tabela td {
  padding: 12px 15px;
  border-bottom: 1px solid #eee;
  vertical-align: top;
}
.usuarios-tabela tr:hover {
  background-color: #f8f9fa;
}

/* Estilos para grupos */
.grupos-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.grupo-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 500;
  display: inline-block;
}
.sem-grupo {
  color: #666;
  font-style: italic;
}

/* Estilos para unidades */
.unidades-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-width: 300px;
}
.unidade-tag {
  background: #f3e5f5;
  color: #7b1fa2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 500;
  display: inline-block;
}
.sem-unidade {
  color: #666;
  font-style: italic;
}

/* Estilos para ações */
.acoes-container {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}
.btn-acao {
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  min-width: 36px;
  justify-content: center;
}
.btn-acao.editar {
  background: #64b5f6;
  color: #fff;
}
.btn-acao.editar:hover {
  background: #1976d2;
  transform: translateY(-1px);
}
.btn-acao.excluir {
  background: #e57373;
  color: #fff;
}
.btn-acao.excluir:hover {
  background: #c62828;
  transform: translateY(-1px);
}
.btn-acao.vincular {
  background: #ffe066;
  color: #333;
  font-weight: 500;
}
.btn-acao.vincular:hover {
  background: #ffd700;
  transform: translateY(-1px);
}
.btn-text {
  font-size: 0.8rem;
}

/* Modal overlay */
.modal-overlay, .form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* Modal de unidades */
.modal-unidade {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.modal-header {
  background: #1a3972;
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
}
.btn-fechar {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-fechar:hover {
  background: rgba(255,255,255,0.2);
}
.modal-body {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}
.usuario-info {
  margin-bottom: 20px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}
.unidades-selection h4 {
  margin-bottom: 12px;
  color: #333;
}
.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
  max-height: 250px;
  overflow-y: auto;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fafafa;
}
.checkbox-item {
  display: flex !important;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}
.checkbox-item:hover {
  background: #e3f2fd;
}
.checkbox-label {
  font-size: 0.9rem;
  color: #333;
}
.no-units {
  grid-column: 1 / -1;
  text-align: center;
  padding: 20px;
}
.warning-text {
  color: #d32f2f;
  font-weight: 500;
}
.modal-footer {
  padding: 16px 20px;
  background: #f8f9fa;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Formulário */
.usuarios-formulario {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.form-header {
  background: #1a3972;
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.form-header h3 {
  margin: 0;
  font-size: 1.2rem;
}
.form-content {
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
}
.form-group input, .form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}
.form-group input:focus, .form-group select:focus {
  border-color: #1976d2;
  outline: none;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

/* Seleção múltipla de unidades */
.multi-select-container {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 8px;
  background: #fff;
}
.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
  min-height: 20px;
}
.selected-item {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 16px;
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 6px;
}
.remove-item {
  background: none;
  border: none;
  color: #1976d2;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}
.remove-item:hover {
  background: rgba(25, 118, 210, 0.1);
}
.unidade-selector {
  width: 100%;
  border: none;
  outline: none;
  padding: 6px 0;
  font-size: 0.9rem;
  background: transparent;
}
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

/* Botões */
.btn-salvar {
  background: #4caf50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}
.btn-salvar:hover {
  background: #388e3c;
}
.btn-cancelar {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-cancelar:hover {
  background: #e0e0e0;
}
</style>
