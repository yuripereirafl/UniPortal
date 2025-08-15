<template>
  <div>
    <select id="cargo-select" v-model="selectedCargo" @change="updateCargo" class="cargo-select">
      <option value="">+ Adicionar cargo...</option>
      <option v-for="cargo in cargosOrdenados" :key="cargo.id" :value="cargo.id">
        {{ cargo.nome }}<span v-if="cargo.funcao"> - {{ cargo.funcao }}</span><span v-if="cargo.nivel"> - {{ cargo.nivel }}</span>
      </option>
    </select>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../api';

export default {
  name: 'CargoMultiSelect',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    }
  },
  data() {
    return {
      cargos: [],
      selectedCargo: this.modelValue
    };
  },
  watch: {
    modelValue(val) {
      this.selectedCargo = val;
    }
  },
  computed: {
    cargosOrdenados() {
      return [...this.cargos].sort((a, b) => a.nome.localeCompare(b.nome));
    }
  },
  methods: {
    updateCargo() {
      this.$emit('update:modelValue', this.selectedCargo);
    }
  },
  mounted() {
    axios.get(`${API_BASE_URL}/cargos/`).then(res => {
      this.cargos = res.data;
    });
  }
};
</script>

<style scoped>
.cargo-select {
  width: 100%;
  padding: 6px 8px;
  font-size: 14px;
  border-radius: 6px;
  border: 1px solid #bdbdbd;
  margin-top: 4px;
  margin-bottom: 8px;
}
</style>
