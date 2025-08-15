<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
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
</style>
