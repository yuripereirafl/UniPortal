<template>
  <div id="app">
    <header class="app-header">
      <div class="header-left">
        <!-- logo removed intentionally -->
      </div>
      <div class="header-right">
        <!-- username intentionally hidden -->
      </div>
    </header>
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
  background: var(--cor-branco);
}

.app-header {
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:12px 20px;
  border-bottom:1px solid #eee;
}
.logo { height:36px }
.header-right { display:flex; gap:12px; align-items:center }
.user-name { font-weight:600; color:#333 }
.btn-meta { background:#ffd700; border:none; padding:8px 12px; border-radius:8px; cursor:pointer }
</style>
