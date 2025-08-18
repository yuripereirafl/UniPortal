<template>
  <div class="container">
    <aside class="sidebar">
      <div class="logo-menu">
        <div class="logo">
          <img src="@/assets/logo.png" alt="Logo" style="max-width:140px;max-height:60px;display:block;margin:0 auto;" />
        </div>
        <nav class="menu">
          <button class="menu-item" :class="{active: activePanel==='dashboard'}" @click="activePanel='dashboard'">Dashboard</button>
          <button class="menu-item" :class="{active: activePanel==='funcionarios'}" @click="activePanel='funcionarios'">Funcionários</button>
          <button class="menu-item" :class="{active: activePanel==='sistemas'}" @click="activePanel='sistemas'">Sistemas</button>
          <button class="menu-item" :class="{active: activePanel==='setores'}" @click="activePanel='setores'">Setores</button>
          <button class="menu-item" :class="{active: activePanel==='cargos'}" @click="activePanel='cargos'">Cargos</button>
          <button class="menu-item" :class="{active: activePanel==='quadroColaboradores'}" @click="activePanel='quadroColaboradores'">Quadro de Colaboradores</button>
          <button class="menu-item" :class="{active: activePanel==='gruposPasta'}" @click="activePanel='gruposPasta'">Grupo de Pastas</button>
          <button class="menu-item" :class="{active: activePanel==='gruposEmail'}" @click="activePanel='gruposEmail'">Grupo de E-mail</button>
          <button class="menu-item" :class="{active: activePanel==='usuarios'}" @click="activePanel='usuarios'">Usuários</button>
          <button class="menu-item" @click="logout">Sair</button>
        </nav>
      </div>
      <div class="user-info">
        <span style="font-size:12px;">CONTROLE DE GESTÃO DA TI</span>
      </div>
    </aside>
    <main class="main-content">
      <component :is="panelComponent" v-if="activePanel !== 'quadroColaboradores'" />
      <QuadroColaboradores v-else :colaboradores="funcionarios.map(f => ({
        id: f.id,
        nome: f.nome,
        sobrenome: f.sobrenome,
        setores: f.setores,
        cargo: f.cargo
      }))" />
    </main>
  </div>
</template>

<script>
import Funcionarios from './Funcionarios.vue';
import Sistemas from './Sistemas.vue';
import DashboardPanel from './DashboardPanel.vue';
import Setores from './Setores.vue';
import GruposEmail from './GruposEmail.vue';
import Usuarios from './Usuarios.vue';
import GruposPasta from './GruposPasta.vue';
import Cargos from './Cargos.vue';
import QuadroColaboradores from '../components/QuadroColaboradores.vue';

export default {
  name: 'Dashboard',
  components: { Funcionarios, Sistemas, DashboardPanel, Setores, GruposEmail, Usuarios, GruposPasta, Cargos, QuadroColaboradores },
  data() {
    return {
      activePanel: 'dashboard',
      funcionarios: []
    }
  },
  computed: {
    panelComponent() {
      switch (this.activePanel) {
        case 'funcionarios': return 'Funcionarios';
        case 'sistemas': return 'Sistemas';
        case 'dashboard': return 'DashboardPanel';
        case 'setores': return 'Setores';
        case 'usuarios': return 'Usuarios';
        case 'gruposPasta': return 'GruposPasta';
        case 'gruposEmail': return 'GruposEmail';
        case 'cargos': return 'Cargos';
        case 'quadroColaboradores': return 'QuadroColaboradores';
        case 'configuracoes': return { template: '<div><h2 style="color:var(--cor-primaria);font-family:var(--font-titulo);">Configurações</h2><p>Configurações do sistema aparecerão aqui.</p></div>' };
        default: return 'DashboardPanel';
      }
    }
  },
  mounted() {
    this.carregarFuncionarios();
  },
  methods: {
    async carregarFuncionarios() {
      try {
        const response = await fetch('http://localhost:8000/funcionarios/');
        this.funcionarios = await response.json();
      } catch (e) {
        this.funcionarios = [];
      }
    },
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>

.container {
  display: flex;
  min-height: 100vh;
}
  .sidebar {
    min-width: 220px;
    max-width: 220px;
    width: 220px;
    background: var(--cor-primaria);
    color: var(--cor-branco);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 0 0 16px 0;
    font-family: var(--font-titulo);
    box-sizing: border-box;
  }
  .logo-menu {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    margin-top: 24px;
  }
  .logo {
    text-align: center;
    margin-bottom: 8px;
    color: var(--cor-destaque);
  }
  .menu {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding-left: 24px;
  }
  .menu-item {
    color: var(--cor-branco);
    text-decoration: none;
    font-size: 16px;
    padding: 8px 0;
    border-radius: 4px;
    transition: background 0.2s;
    background: none;
    border: none;
    text-align: left;
    cursor: pointer;
  }
  .menu-item.active {
    background: var(--cor-sec2);
    color: var(--cor-destaque);
    width: 100%;
    box-sizing: border-box;
  }
  .user-info {
    background: var(--cor-sec2);
    padding: 12px 0;
    text-align: center;
    border-radius: 0 0 8px 0;
    color: var(--cor-branco);
  }
  .main-content {
    flex: 1;
    padding: 40px;
    background: var(--cor-branco);
    font-family: var(--font-corpo);
  }
  h1 {
    color: var(--cor-primaria);
    font-family: var(--font-titulo);
  }
</style>
