<template>
  <div>
    
    <ul v-if="sistemas.length">
      <li v-for="s in sistemas" :key="s.id">
        <strong>{{ s.nome }}</strong> - {{ s.status }}
      </li>
    </ul>
    <p v-else>Nenhum sistema vinculado.</p>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../api';

export default {
  props: ['funcionarioId'],
  data() {
    return {
      sistemas: []
    }
  },
  async mounted() {
    try {
      const res = await axios.get(`${API_BASE_URL}/funcionarios/${this.funcionarioId}/sistemas`);
      this.sistemas = res.data;
    } catch (error) {
      this.sistemas = [];
    }
  }
}
</script>
