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
      selectedCargo: this.modelValue,
      isLoading: false,
      _cacheExpiry: null,
      _cacheTimeout: 5 * 60 * 1000 // 5 minutos
    };
  },
  
  watch: {
    modelValue(val) {
      this.selectedCargo = val;
    }
  },
  
  computed: {
    cargosOrdenados() {
      if (!this.cargos.length) return [];
      return [...this.cargos].sort((a, b) => a.nome.localeCompare(b.nome));
    }
  },
  
  methods: {
    updateCargo() {
      this.$emit('update:modelValue', this.selectedCargo);
    },
    
    async carregarCargos() {
      // Verificar cache
      if (this.cargos.length && this._cacheExpiry && Date.now() < this._cacheExpiry) {
        return;
      }
      
      if (this.isLoading) return;
      
      this.isLoading = true;
      try {
        const res = await axios.get(`${API_BASE_URL}/cargos/`);
        this.cargos = res.data;
        this._cacheExpiry = Date.now() + this._cacheTimeout;
      } catch (error) {
        console.error('Erro ao carregar cargos:', error);
      } finally {
        this.isLoading = false;
      }
    }
  },
  
  mounted() {
    this.carregarCargos();
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
