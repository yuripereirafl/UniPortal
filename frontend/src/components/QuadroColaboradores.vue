<template>
  <div class="dashboard-colaboradores">
    <h2 style="color:#1a3760;margin-bottom:18px;">Quadro de Colaboradores</h2>
    <table class="quadro-table">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Cargo</th>
          <th>Status</th>
          <th>Função</th>
          <th>Equipe</th>
          <th>Valor da meta</th>
          <th>Tipo Pgto</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="colab in colaboradores" :key="colab.id">
          <td>{{ colab.nome }}</td>
          <td>{{ colab.cargo }}</td>
          <td>{{ colab.status }}</td>
          <td>{{ colab.funcao }}</td>
          <td>{{ colab.equipe }}</td>
          <td>{{ colab.valor_meta }}</td>
          <td>{{ colab.tipo_pgto }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'QuadroColaboradores',
  props: {
    colaboradores: {
      type: Array,
      required: true
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
