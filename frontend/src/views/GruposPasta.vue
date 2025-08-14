<template>
  <div class="tabela-grupos-pasta">
    <div class="header header-grupos-pasta">
      <h2>Grupos de Pastas</h2>
      <div class="busca-adicionar">
        <input v-model="buscaGrupo" placeholder="Buscar grupo..." class="input-busca" />
        <button class="btn-cadastrar" @click="showForm = !showForm">
          + Adicionar Grupo de Pastas
        </button>
      </div>
    </div>
    <table>
      <thead>
        <tr>
          <th @click="toggleOrdenacaoNome" style="cursor:pointer">
            Nome do Grupo
            <span v-if="ordenacaoNome === 'asc'">▲</span>
            <span v-else>▼</span>
          </th>
          <th>Descrição</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="grupo in gruposFiltrados" :key="grupo.id">
          <td>{{ grupo.nome }}</td>
          <td>{{ grupo.descricao }}</td>
          <td>
            <button class="btn-editar" @click="abrirEditar(grupo)">✏️</button>
            <button class="btn-excluir" @click="excluirGrupo(grupo.id)">🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay">
      <div class="form-modal">
        <h3>{{ editando ? 'Editar Grupo' : 'Adicionar Grupo de Pastas' }}</h3>
        <form @submit.prevent="editando ? salvarEdicaoGrupo() : cadastrarGrupo()">
          <input v-model="form.nome" placeholder="Nome do Grupo" required />
          <input v-model="form.descricao" placeholder="Descrição (opcional)" />
          <div class="modal-actions">
            <button type="submit" class="btn-cadastrar">Salvar</button>
            <button type="button" @click="fecharModal">Cancelar</button>
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
        nome: '',
        descricao: ''
      },
      buscaGrupo: '',
      ordenacaoNome: 'asc',
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
    fecharModal() {
      this.showForm = false;
      this.editando = false;
      this.grupoEditId = null;
      this.form = { nome: '', descricao: '' };
    },
    async carregarGrupos() {
      const res = await axios.get(`${API_BASE_URL}/grupos-pasta/`);
      this.grupos = res.data;
    }
  },
  mounted() {
    this.carregarGrupos();
  }
}
</script>

<style scoped>
.tabela-grupos-pasta {
  background: var(--cor-branco);
  border-radius: 12px;
  padding: 32px 24px;
  max-width: 800px;
  margin: 32px 0 0 12px;
  box-shadow: 0 2px 8px rgba(20,65,121,0.08);
}
.header-grupos-pasta {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
  gap: 24px;
}
.busca-adicionar {
  display: flex;
  gap: 18px;
  align-items: center;
}
.input-busca {
  padding: 10px 18px;
  border-radius: 8px;
  border: 1.5px solid var(--cor-sec2);
  min-width: 220px;
  font-size: 16px;
  font-family: var(--font-corpo);
  background: #f8fafc;
  transition: border 0.2s;
}
.input-busca:focus {
  border: 2px solid var(--cor-destaque);
  outline: none;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header h2 {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
}
.btn-cadastrar {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  border: none;
  border-radius: 4px;
  padding: 10px 18px;
  font-size: 15px;
  font-family: var(--font-titulo);
  cursor: pointer;
  transition: background 0.2s;
}
.btn-cadastrar:hover {
  background: var(--cor-sec3);
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}
th, td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 2px solid var(--cor-destaque);
  font-family: var(--font-corpo);
}
th {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
  background: var(--cor-branco);
}
.btn-editar {
  background: var(--cor-sec1);
  color: var(--cor-branco);
  border: none;
  border-radius: 4px;
  padding: 6px 10px;
  margin-right: 4px;
  cursor: pointer;
}
.btn-excluir {
  background: #d32f2f;
  color: var(--cor-branco);
  border: none;
  border-radius: 4px;
  padding: 6px 10px;
  cursor: pointer;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(20,65,121,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.form-modal {
  background: var(--cor-branco);
  border: 1px solid var(--cor-sec1);
  border-radius: 8px;
  padding: 32px 24px;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 2px 16px rgba(20,65,121,0.18);
  font-family: var(--font-corpo);
}
.form-modal h3 {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
  margin-bottom: 24px;
  text-align: center;
}
.form-modal input {
  width: 100%;
  padding: 10px;
  margin-bottom: 16px;
  border: 1px solid var(--cor-sec2);
  border-radius: 4px;
  font-size: 15px;
  font-family: var(--font-corpo);
}
.form-modal input:focus {
  outline: 2px solid var(--cor-destaque);
}
.modal-actions {
  display: flex;
  justify-content: space-between;
}
.form-modal button {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  border: none;
  border-radius: 4px;
  padding: 10px 18px;
  font-size: 15px;
  font-family: var(--font-titulo);
  cursor: pointer;
  margin-right: 8px;
  transition: background 0.2s;
}
.form-modal button:last-child {
  background: var(--cor-sec1);
  color: var(--cor-branco);
  margin-right: 0;
}
.form-modal button:hover {
  background: var(--cor-sec3);
}
</style>
