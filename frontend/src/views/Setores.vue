



<template>
  <div class="card-setores">
    <div class="header-setores">
      <h2>Setores</h2>
      <div style="display:flex;gap:14px;align-items:center;">
        <input v-model="buscaSetor" placeholder="Buscar setor..." class="input-busca-setor" />
        <button class="btn-setor" @click="showForm = true"><span style="font-size:1.2em;">➕</span> Novo Setor</button>
      </div>
    </div>
    <table class="tabela-setores">
      <thead>
        <tr>
          <th @click="toggleOrdenacaoNome" style="cursor:pointer">
            Nome do Setor
            <span v-if="ordenacaoNome === 'asc'">▲</span>
            <span v-else>▼</span>
          </th>
          <th>Descrição</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="setor in setoresFiltrados" :key="setor.id">
          <td>{{ setor.nome }}</td>
          <td>{{ setor.descricao }}</td>
          <td>
            <button class="btn-setor-edit" title="Editar" @click="abrirEditar(setor)"><span>✏️ Editar</span></button>
            <button class="btn-setor-delete" title="Excluir" @click="excluirSetor(setor.id)"><span>🗑️ Excluir</span></button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="showForm" class="modal-overlay">
      <div class="form-modal">
        <form @submit.prevent="editando ? salvarEdicao() : criarSetor()">
          <h3 style="margin-bottom:16px;">{{ editando ? 'Editar Setor' : 'Novo Setor' }}</h3>
          <input v-model="novoSetor.nome" placeholder="Nome do setor" required />
          <input v-model="novoSetor.descricao" placeholder="Descrição" />
          <div style="display:flex;gap:12px;margin-top:18px;">
            <button type="submit" class="btn-setor-salvar"><span>💾</span> Salvar</button>
            <button type="button" class="btn-setor-cancelar" @click="fecharModal"><span>❌</span> Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>


<script>
import { API_BASE_URL } from '../api';

export default {
  name: 'Setores',
  data() {
    return {
      setores: [],
      novoSetor: {
        nome: '',
        descricao: ''
      },
      showForm: false,
      editando: false,
      setorEditId: null,
      buscaSetor: ''
      ,ordenacaoNome: 'asc'
    }
  },
  computed: {
    setoresFiltrados() {
      let lista = this.setores;
      if (this.buscaSetor) {
        const busca = this.buscaSetor.toLowerCase();
        lista = lista.filter(s => {
          const nome = (s.nome || '').toLowerCase();
          const descricao = (s.descricao || '').toLowerCase();
          return nome.includes(busca) || descricao.includes(busca);
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
    }
  },
  async mounted() {
    await this.carregarSetores();
  },
  methods: {
    toggleOrdenacaoNome() {
      this.ordenacaoNome = this.ordenacaoNome === 'asc' ? 'desc' : 'asc';
    },
    async carregarSetores() {
      const response = await fetch(`${API_BASE_URL}/setores/`);
      this.setores = await response.json();
    },
    async criarSetor() {
      if (!this.novoSetor.nome.trim()) return;
      await fetch(`${API_BASE_URL}/setores/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.novoSetor)
      });
      this.novoSetor = { nome: '', descricao: '' };
      this.showForm = false;
      this.editando = false;
      this.setorEditId = null;
      await this.carregarSetores();
    },
    abrirEditar(setor) {
      this.novoSetor = { nome: setor.nome, descricao: setor.descricao };
      this.setorEditId = setor.id;
      this.editando = true;
      this.showForm = true;
    },
    async salvarEdicao() {
      if (!this.novoSetor.nome.trim()) return;
      await fetch(`${API_BASE_URL}/setores/${this.setorEditId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.novoSetor)
      });
      this.novoSetor = { nome: '', descricao: '' };
      this.showForm = false;
      this.editando = false;
      this.setorEditId = null;
      await this.carregarSetores();
    },
    async excluirSetor(id) {
      await fetch(`${API_BASE_URL}/setores/${id}`, {
        method: 'DELETE'
      });
      await this.carregarSetores();
    },
    fecharModal() {
      this.showForm = false;
      this.editando = false;
      this.setorEditId = null;
      this.novoSetor = { nome: '', descricao: '' };
    }
  }
}
</script>

th, td {

<style scoped>
/* Estilos Setores */
.card-setores {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 2px 16px rgba(20,65,121,0.07);
  padding: 32px 24px;
  max-width: 1200px;
  margin: 32px 0 0 12px;
}
.input-busca-setor {
  padding: 10px 18px;
  border-radius: 8px;
  border: 1.5px solid var(--cor-sec2);
  min-width: 220px;
  font-size: 16px;
  font-family: var(--font-corpo);
  background: #f8fafc;
  transition: border 0.2s;
}
.input-busca-setor:focus {
  border: 2px solid var(--cor-destaque);
  outline: none;
}
.header-setores {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.header-setores h2 {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
  font-size: 2rem;
}
.btn-setor {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  border: none;
  border-radius: 6px;
  padding: 10px 22px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-setor:hover {
  background: var(--cor-sec3);
}
.tabela-setores {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}
.tabela-setores th {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
  font-size: 1rem;
  padding: 10px 8px;
  border-bottom: 2px solid var(--cor-destaque);
  text-align: left;
}
.tabela-setores td {
  padding: 10px 8px;
  border-bottom: 2px solid var(--cor-destaque);
  font-size: 1rem;
}
.btn-setor-edit {
  background: var(--cor-sec1);
  color: var(--cor-branco);
  border: none;
  border-radius: 4px;
  padding: 6px 10px;
  margin-right: 6px;
  cursor: pointer;
  font-size: 1em;
  display: flex;
  align-items: center;
  gap: 4px;
}
.btn-setor-delete {
  background: #e74c3c;
  color: var(--cor-branco);
  border: none;
  border-radius: 4px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 1em;
  display: flex;
  align-items: center;
  gap: 4px;
}
.btn-setor-salvar {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  border: none;
  border-radius: 6px;
  padding: 10px 22px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-setor-salvar:hover {
  background: var(--cor-sec3);
}
.btn-setor-cancelar {
  background: var(--cor-sec1);
  color: var(--cor-branco);
  border: none;
  border-radius: 6px;
  padding: 10px 22px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(20,65,121,0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.form-modal {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(20,65,121,0.12);
  padding: 32px 40px;
  min-width: 340px;
}
.form-modal input {
  width: 100%;
  margin-bottom: 12px;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 1rem;
}
</style>
