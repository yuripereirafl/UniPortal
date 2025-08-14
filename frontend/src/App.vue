<template>
  <div id="app">
    <router-view v-if="!erroPermissao" />
    <div v-else class="erro-permissao">
      <h1>Acesso Negado</h1>
      <p>Você não tem permissão para acessar esta página.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default {
  name: 'App',
  data() {
    return {
      erroPermissao: false
    };
  },
  async mounted() {
    try {
      await axios.get('/verificar-permissao');
    } catch (error) {
      if (error.response && error.response.status === 403) {
        this.erroPermissao = true;
      }
    }
  }
};
</script>

<style>
:root {
  --cor-primaria: #144179;
  --cor-destaque: #fcca32;
  --cor-branco: #ffffff;
  --cor-sec1: #58aadf;
  --cor-sec2: #3567b0;
  --cor-sec3: #fcc361;
  --font-titulo: 'Segoe UI Semibold', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  --font-corpo: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

#app {
  font-family: var(--font-corpo);
  margin: 0;
  padding: 0;
  background: var(--cor-branco);
}

.erro-permissao {
  text-align: center;
  margin-top: 50px;
}
.erro-permissao h1 {
  color: red;
}
</style>
