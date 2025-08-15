<template>
  <div>
    <label for="cargo">Cargo:</label>
    <select v-model="selectedCargo" @change="$emit('update:cargo', selectedCargo)">
      <option value="">Selecione o cargo</option>
      <option v-for="cargo in cargos" :key="cargo.id" :value="cargo.id">
        {{ cargo.nome }} - {{ cargo.funcao }} - {{ cargo.nivel }}
      </option>
    </select>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../api';

export default {
  props: {
    cargo: {
      type: [Number, String],
      default: ''
    }
  },
  data() {
    return {
      cargos: [],
      selectedCargo: this.cargo
    };
  },
  watch: {
    cargo(val) {
      this.selectedCargo = val;
    }
  },
  mounted() {
    axios.get(`${API_BASE_URL}/cargos/`).then(res => {
      this.cargos = res.data;
    });
  }
};
</script>
