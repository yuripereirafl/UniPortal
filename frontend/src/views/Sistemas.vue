<template>
  <div class="tabela-sistemas">
    <div class="header header-sistemas">
      <h2>Sistemas</h2>
      <div class="busca-adicionar">
        <input v-model="buscaSistema" placeholder="Buscar sistema..." class="input-busca" />
        <button class="btn-cadastrar" @click="showForm = !showForm">
          + Adicionar Sistema
        </button>
      </div>
    </div>
    <table>
      <thead>
        <tr>
          <th @click="toggleOrdenacaoNome" style="cursor:pointer">
            Nome
            <span v-if="ordenacaoNome === 'asc'">▲</span>
            <span v-else>▼</span>
          </th>
          <th>Descrição</th>
          <th>Status</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="sistema in sistemasFiltrados" :key="sistema.id">
          <td>{{ sistema.nome }}</td>
          <td>{{ sistema.descricao }}</td>
          <td>{{ sistema.status }}</td>
          <td>
            <button class="btn-editar" @click="abrirEditar(sistema)">✏️</button>
            <button class="btn-excluir" @click="excluirSistema(sistema.id)">🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay">
      <div class="form-modal">
        <h3>{{ editando ? 'Editar Sistema' : 'Adicionar Sistema' }}</h3>
        <form @submit.prevent="editando ? salvarEdicao() : cadastrarSistema()">
          <input v-model="form.nome" placeholder="Nome do Sistema" required />
          <input v-model="form.descricao" placeholder="Descrição" />
          <input v-model="form.status" placeholder="Status" required />
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
      sistemas: [],
      showForm: false,
      editando: false,
      sistemaEditId: null,
      form: {
        nome: '',
        descricao: '',
        status: ''
      },
      buscaSistema: ''
      ,ordenacaoNome: 'asc'
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
  mounted() {
    this.carregarSistemas();
  },
  methods: {
    toggleOrdenacaoNome() {
      this.ordenacaoNome = this.ordenacaoNome === 'asc' ? 'desc' : 'asc';
    },
    async carregarSistemas() {
      const res = await axios.get(`${API_BASE_URL}/sistemas/`);
      this.sistemas = res.data;
    },
    async cadastrarSistema() {
      await axios.post(`${API_BASE_URL}/sistemas/`, this.form);
      this.carregarSistemas();
      this.fecharModal();
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
      await axios.put(`${API_BASE_URL}/sistemas/${this.sistemaEditId}`, this.form);
      this.carregarSistemas();
      this.fecharModal();
    },
    fecharModal() {
      this.showForm = false;
      this.editando = false;
      this.sistemaEditId = null;
      this.form = { nome: '', descricao: '', status: '' };
    },
    async excluirSistema(id) {
      if (confirm('Tem certeza que deseja excluir este sistema?')) {
        await axios.delete(`${API_BASE_URL}/sistemas/${id}`);
        this.carregarSistemas();
      }
    }
  }
}
</script>

<style scoped>
/* Espaçamento reduzido e filtro igual Funcionários */
.tabela-sistemas {
  background: var(--cor-branco);
  border-radius: 12px;
  padding: 24px 20px;
  margin: 20px 0 0 -8px;
  box-shadow: 0 2px 8px rgba(20,65,121,0.08);
  overflow-x: auto;
}

.header-sistemas {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
  gap: 20px;
}
.busca-adicionar {
  display: flex;
  gap: 16px;
  align-items: center;
}
.input-busca {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1.5px solid var(--cor-sec2);
  min-width: 220px;
  font-size: 15px;
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
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 16px;
  background: #fff;
  box-shadow: 0 1px 6px rgba(20,65,121,0.06);
  border-radius: 10px;
  overflow: hidden;
}
th, td {
  padding: 10px 8px;
  text-align: left;
  border-bottom: 1.5px solid #f3e6c2;
  font-family: var(--font-corpo);
  font-size: 14px;
}
th {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
  background: var(--cor-branco);
  border-bottom: 2px solid var(--cor-destaque);
  font-size: 15px;
  padding: 12px 8px;
}

tbody tr:hover {
  background: #f6f8fa;
}

tbody tr:last-child td {
  border-bottom: none;
}
.btn-editar {
  background: var(--cor-sec1);
  color: var(--cor-branco);
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  margin-right: 4px;
  cursor: pointer;
  font-size: 14px;
}
.btn-excluir {
  background: #d32f2f;
  color: var(--cor-branco);
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 14px;
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
