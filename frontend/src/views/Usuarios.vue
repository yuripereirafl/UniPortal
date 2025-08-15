
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
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="usuario in usuariosFiltrados" :key="usuario.id">
          <td>{{ usuario.username }}</td>
          <td>
            <button class="btn-acao editar" @click="editarUsuario(usuario)"><span class="icon">✏️</span></button>
            <button class="btn-acao excluir" @click="excluirUsuario(usuario.id)"><span class="icon">🗑️</span></button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="mostrarFormulario" class="formulario">
      <h3>{{ usuarioEditando ? 'Editar Usuário' : 'Novo Usuário' }}</h3>
      <form @submit.prevent="salvarUsuario">
        <input v-model="form.username" placeholder="Usuário" required />
        <input v-model="form.password" type="password" placeholder="Senha" required />
        <button type="submit" class="btn-amarelo">Salvar</button>
        <button type="button" @click="fecharFormulario">Cancelar</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      usuarios: [],
      mostrarFormulario: false,
      usuarioEditando: null,
      form: {
        username: '',
        password: ''
      },
      filtro: ''
    };
  },
  computed: {
    usuariosFiltrados() {
      if (!this.filtro) return this.usuarios;
      return this.usuarios.filter(u => u.username.toLowerCase().includes(this.filtro.toLowerCase()));
    }
  },
  methods: {
    async carregarUsuarios() {
      const res = await axios.get('/usuarios/');
      this.usuarios = res.data;
    },
    abrirFormulario() {
      this.mostrarFormulario = true;
      this.usuarioEditando = null;
      this.form = { username: '', password: '' };
    },
    fecharFormulario() {
      this.mostrarFormulario = false;
    },
    async salvarUsuario() {
      if (this.usuarioEditando) {
        await axios.put(`/usuarios/${this.usuarioEditando.id}`, this.form);
      } else {
        await axios.post('/usuarios/', this.form);
      }
      this.fecharFormulario();
      this.carregarUsuarios();
    },
    editarUsuario(usuario) {
      this.usuarioEditando = usuario;
      this.form = { username: usuario.username, password: '' };
      this.mostrarFormulario = true;
    },
    async excluirUsuario(id) {
      if (confirm('Deseja realmente excluir este usuário?')) {
        await axios.delete(`/usuarios/${id}`);
        this.carregarUsuarios();
      }
    }
  },
  mounted() {
    this.carregarUsuarios();
  }
};
</script>

<style scoped>

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
.usuarios-tabela {
  width: 100%;
  border-collapse: collapse;
  margin-top: 18px;
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 6px rgba(20,65,121,0.08);
}
.usuarios-tabela th {
  background: #fff;
  color: #1a3972;
  font-size: 1.1rem;
  font-weight: 600;
  padding: 12px 8px;
  border-bottom: 2px solid #ffc107;
}
.usuarios-tabela td {
  padding: 10px 8px;
  border-bottom: 1px solid #eee;
}
.btn-acao {
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  margin-right: 6px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
  display: inline-flex;
  align-items: center;
}
.btn-acao.editar {
  background: #64b5f6;
  color: #fff;
}
.btn-acao.editar:hover {
  background: #1976d2;
}
.btn-acao.excluir {
  background: #e57373;
  color: #fff;
}
.btn-acao.excluir:hover {
  background: #c62828;
}
.icon {
  font-size: 1.2rem;
}
.formulario {
  margin-top: 30px;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}
</style>
