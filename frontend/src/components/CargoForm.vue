<template>
  <div class="card">
    <h2>Lista de Cargos</h2>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <div></div>
      <button class="novo-cargo-btn" @click="abrirModal">+ Novo Cargo</button>
    </div>
    <table class="cargo-table">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Função</th>
          <th>Equipe</th>
          <th>Nível</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in cargos" :key="item.id">
          <td>{{ item.nome }}</td>
          <td>{{ item.funcao }}</td>
          <td>{{ item.equipe }}</td>
          <td>{{ item.nivel }}</td>
          <td>
            <button class="editar-btn" @click="editarCargo(item)">Editar</button>
            <button class="excluir-btn" @click="excluirCargo(item.id)">Excluir</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="modalAberto" class="modal-overlay">
      <div class="modal">
        <h3>{{ editando ? 'Editar Cargo' : 'Cadastrar Cargo' }}</h3>
        <form @submit.prevent="editando ? atualizarCargo() : criarCargo()">
          <input v-model="cargo.nome" placeholder="Nome" required />
          <input v-model="cargo.funcao" placeholder="Função" />
          <input v-model="cargo.equipe" placeholder="Equipe" />
          <input v-model="cargo.nivel" placeholder="Nível" />
          <button type="submit">{{ editando ? 'Salvar' : 'Cadastrar' }}</button>
          <button type="button" @click="fecharModal">Cancelar</button>
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
      cargo: {
        nome: '',
        funcao: '',
        equipe: '',
        nivel: ''
      },
      cargos: [],
      modalAberto: false,
      editando: false,
      cargoEditId: null
    };
  },
  mounted() {
    this.buscarCargos();
  },
  methods: {
    buscarCargos() {
      axios.get(`${API_BASE_URL}/cargos/`).then(res => {
        this.cargos = res.data;
      });
    },
    criarCargo() {
      axios.post(`${API_BASE_URL}/cargos/`, this.cargo).then(() => {
        this.cargo = { nome: '', funcao: '', equipe: '', nivel: '' };
        this.buscarCargos();
        this.fecharModal();
      });
    },
    editarCargo(item) {
      this.cargo = { nome: item.nome, funcao: item.funcao, equipe: item.equipe, nivel: item.nivel };
      this.cargoEditId = item.id;
      this.editando = true;
      this.modalAberto = true;
    },
    atualizarCargo() {
      axios.put(`${API_BASE_URL}/cargos/${this.cargoEditId}`, this.cargo).then(() => {
        this.cargo = { nome: '', funcao: '', equipe: '', nivel: '' };
        this.buscarCargos();
        this.fecharModal();
      });
    },
    excluirCargo(id) {
      if (confirm('Tem certeza que deseja excluir este cargo?')) {
        axios.delete(`${API_BASE_URL}/cargos/${id}`).then(() => {
          this.buscarCargos();
        });
      }
    },
    abrirModal() {
      this.modalAberto = true;
      this.editando = false;
      this.cargo = { nome: '', funcao: '', equipe: '', nivel: '' };
      this.cargoEditId = null;
    },
    fecharModal() {
      this.modalAberto = false;
      this.cargo = { nome: '', funcao: '', equipe: '', nivel: '' };
      this.editando = false;
      this.cargoEditId = null;
    }
  }
};
</script>

<style scoped>
/* Tabela de cargos */
.cargo-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 24px;
}
.cargo-table th, .cargo-table td {
  border-bottom: 2px solid #fbc02d;
  padding: 10px 8px;
  text-align: left;
}
.cargo-table th {
  color: #1a3760;
  font-weight: bold;
}
.cargo-table td {
  color: #222;
}
.novo-cargo-btn {
  background: #fbc02d;
  color: #1a3760;
  border: none;
  border-radius: 6px;
  padding: 8px 18px;
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}
.novo-cargo-btn:hover {
  background: #ffd54f;
}
.editar-btn {
  background: #42a5f5;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  margin-right: 6px;
  cursor: pointer;
}
.editar-btn:hover {
  background: #1976d2;
}
.excluir-btn {
  background: #ef5350;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
}
.excluir-btn:hover {
  background: #c62828;
}
.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 24px;
  margin-bottom: 24px;
}
input {
  margin: 4px;
  padding: 6px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
button {
  margin-top: 8px;
  padding: 8px 16px;
  border-radius: 4px;
  background: #1976d2;
  color: #fff;
  border: none;
  cursor: pointer;
}
button:hover {
  background: #1565c0;
}
/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  padding: 32px;
  min-width: 320px;
}
</style>
