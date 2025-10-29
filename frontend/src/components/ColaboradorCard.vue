<template>
  <div class="colaborador-card">
    <div class="colaborador-header">
      <h3>{{ colaborador.nome }}</h3>
      <span class="status" :class="colaborador.status">{{ colaborador.status }}</span>
    </div>
    <div class="colaborador-info">
      <div><strong>Cargo:</strong> {{ colaborador.cargo }}</div>
      <div><strong>Função:</strong> {{ colaborador.funcao }}</div>
      <div><strong>Equipe:</strong> {{ colaborador.equipe }}</div>
      <div><strong>Valor da meta:</strong> {{ colaborador.valor_meta }}</div>
      <div><strong>Tipo Pgto:</strong> {{ colaborador.tipo_pgto }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ColaboradorCard',
  props: {
    colaborador: {
      type: Object,
      required: true
    }
  }
};
</script>

<style scoped>
.colaborador-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
  padding: 24px;
  margin-bottom: 18px;
  min-width: 320px;
  max-width: 420px;
}
.colaborador-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.colaborador-header h3 {
  margin: 0;
  font-size: 1.3rem;
  color: #1a3760;
}
.status {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.95rem;
  font-weight: bold;
  background: #e0e0e0;
  color: #333;
}
.status.Ativo {
  background: #c8e6c9;
  color: #388e3c;
}
.status.Inativo {
  background: #ffcdd2;
  color: #c62828;
}
.colaborador-info div {
  margin-bottom: 6px;
  font-size: 1rem;
}
.colaborador-info strong {
  color: #1976d2;
}
</style>
