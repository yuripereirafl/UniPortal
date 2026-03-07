<template>
  <div id="app">
    <!-- Barra superior removida para maximizar espaço e visibilidade -->
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  mounted() {
    // escutar atualizações de auth para forçar re-render do cabeçalho
    const onAuthUpdated = () => {
      this.$forceUpdate && this.$forceUpdate();
    };
    window.addEventListener('auth:updated', onAuthUpdated);
    this._onAuthUpdated = onAuthUpdated;
  },
  beforeUnmount() {
    if (this._onAuthUpdated) window.removeEventListener('auth:updated', this._onAuthUpdated);
  }
}
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
  background: #050a18;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* Reset Global para transições suaves */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>
