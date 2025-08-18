<template>
  <div class="dashboard-colaboradores">
    <h2 style="color:#1a3760;margin-bottom:18px;">Quadro de Colaboradores</h2>
    <table class="quadro-table">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Sobrenome</th>
          <th>Setor</th>
          <th>Cargo</th>
          <th>Função</th>
          <th>Equipe</th>
          <th>Nível</th>
          <th>Status</th>
          <th>Valor da meta</th>
          <th>Tipo Pgto</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="colab in colaboradores" :key="colab.id">
          <td>{{ colab.nome }}</td>
          <td>{{ colab.sobrenome || '-' }}</td>
          <td>
            <span v-if="colab.setores && colab.setores.length">
              {{ colab.setores.join(', ') }}
            </span>
            <span v-else>—</span>
          </td>
          <td>{{ colab.cargo && colab.cargo.nome ? colab.cargo.nome : '-' }}</td>
          <td>{{ colab.cargo && colab.cargo.funcao ? colab.cargo.funcao : '-' }}</td>
          <td>{{ colab.cargo && colab.cargo.equipe ? colab.cargo.equipe : '-' }}</td>
          <td>{{ colab.cargo && colab.cargo.nivel ? colab.cargo.nivel : '-' }}</td>
          <td>{{ colab.filial && colab.filial.nome ? colab.filial.nome : '-' }}</td>
          <td>{{ colab.meta && colab.meta.calc_meta !== undefined ? colab.meta.calc_meta : '-' }}</td>
          <td>{{ colab.meta && colab.meta.tipo_pgto ? colab.meta.tipo_pgto : '-' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'QuadroColaboradores',
  data() {
    return {
      colaboradores: [],
      carregando: false,
      erro: null
    }
  },
  mounted() {
    this.carregarColaboradores();
  },
  methods: {
    async carregarColaboradores() {
      this.carregando = true;
      this.erro = null;
      try {
        const response = await fetch('http://localhost:8000/quadro_colaboradores/');
        this.colaboradores = await response.json();
      } catch (e) {
        this.erro = 'Erro ao carregar colaboradores.';
        this.colaboradores = [];
      }
      this.carregando = false;
    }
  }
}
</script>

<style scoped>
.dashboard-colaboradores {
  margin-top: 32px;
}
.quadro-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}
.quadro-table th, .quadro-table td {
  border-bottom: 2px solid #fbc02d;
  padding: 10px 8px;
  text-align: left;
}
.quadro-table th {
  color: #1a3760;
  font-weight: bold;
}
.quadro-table td {
  color: #222;
}
</style>
