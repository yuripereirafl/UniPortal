<template>
  <div class="dashboard-container">
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <!-- Header do Sidebar -->
      <div class="sidebar-header">
        <div class="logo" v-show="!isCollapsed">
          <img src="@/assets/logo.png" alt="Logo" class="logo-img" />
        </div>
        <button class="hamburger-btn" @click="toggleSidebar">
          <i :class="['fas', isCollapsed ? 'fa-arrow-right' : 'fa-arrow-left']"></i>
        </button>
      </div>

      <!-- Menu de Navegação -->
      <nav class="menu">
        <button 
          v-if="$auth && $auth.hasPermission('adm')"
          class="menu-item" 
          :class="{active: activePanel==='dashboard'}" 
          @click="activePanel='dashboard'"
        >
          <i class="fas fa-chart-pie menu-icon"></i>
          <span class="menu-text">Dashboard</span>
        </button>
        
        <button 
          v-if="$auth && ($auth.hasPermission('adm') || $auth.hasPermission('infra'))"
          class="menu-item" 
          :class="{active: activePanel==='sla'}" 
          @click="activePanel='sla'"
        >
          <i class="fas fa-clipboard-check menu-icon"></i>
          <span class="menu-text">Auditoria SLA</span>
        </button>
        
        <button
          v-if="$auth && ($auth.hasPermission('editar_colaborador') || $auth.hasPermission('adm'))"
          class="menu-item"
          :class="{active: activePanel==='funcionarios'}"
          @click="activePanel='funcionarios'"
        >
          <i class="fas fa-users menu-icon"></i>
          <span class="menu-text">Funcionários</span>
        </button>
        
        <button
          v-if="$auth && ($auth.hasPermission('adm'))"
          class="menu-item"
          :class="{active: activePanel==='sistemas'}"
          @click="activePanel='sistemas'"
        >
          <i class="fas fa-server menu-icon"></i>
          <span class="menu-text">Sistemas</span>
        </button>
        
        <button
          v-if="$auth && ($auth.hasPermission('adm'))"
          class="menu-item"
          :class="{active: activePanel==='setores'}"
          @click="activePanel='setores'"
        >
          <i class="fas fa-building menu-icon"></i>
          <span class="menu-text">Setores</span>
        </button>
        
        <button
          v-if="$auth && ($auth.hasPermission('adm'))"
          class="menu-item"
          :class="{active: activePanel==='cargos'}"
          @click="activePanel='cargos'"
        >
          <i class="fas fa-briefcase menu-icon"></i>
          <span class="menu-text">Cargos</span>
        </button>
        
        <button
          v-if="$auth && ($auth.hasPermission('adm'))"
          class="menu-item"
          :class="{active: activePanel==='celulares'}"
          @click="activePanel='celulares'"
        >
          <i class="fas fa-mobile-alt menu-icon"></i>
          <span class="menu-text">Celulares</span>
        </button>

        <button
          v-if="$auth && ($auth.hasPermission('adm'))"
          class="menu-item"
          :class="{active: activePanel==='notebooks'}"
          @click="activePanel='notebooks'"
        >
          <i class="fas fa-laptop menu-icon"></i>
          <span class="menu-text">Notebooks</span>
        </button>

        <button
          v-if="$auth && ($auth.hasPermission('adm'))"
          class="menu-item"
          :class="{active: activePanel==='dominios'}"
          @click="activePanel='dominios'"
        >
          <i class="fas fa-globe menu-icon"></i>
          <span class="menu-text">Domínios</span>
        </button>
        
        <!-- REMOVIDO: Quadro de Colaboradores e Meta Colaborador -->
        
        <button
          v-if="$auth && ($auth.hasPermission('adm'))"
          class="menu-item"
          :class="{active: activePanel==='gruposPasta'}"
          @click="activePanel='gruposPasta'"
        >
          <i class="fas fa-folder-open menu-icon"></i>
          <span class="menu-text">Grupo de Pastas</span>
        </button>
        
        <button
          v-if="$auth && ($auth.hasPermission('ADM'))"
          class="menu-item"
          :class="{active: activePanel === 'gruposEmail'}"
          @click="activePanel = 'gruposEmail'"
        >
          <i class="fas fa-envelope menu-icon"></i>
          <span class="menu-text">Grupo de E-mail</span>
        </button>
        
        <button
          v-if="$auth && ($auth.hasPermission('ADM'))"
          class="menu-item"
          :class="{active: activePanel === 'gruposWhatsapp'}"
          @click="activePanel = 'gruposWhatsapp'"
        >
          <i class="fab fa-whatsapp menu-icon"></i>
          <span class="menu-text">Grupo de WhatsApp</span>
        </button>
        
        <button
          v-if="$auth && ($auth.hasPermission('adm') || $auth.hasPermission('editar_usuario'))"
          class="menu-item"
          :class="{active: activePanel === 'usuarios'}"
          @click="activePanel = 'usuarios'"
        >
          <i class="fas fa-user-shield menu-icon"></i>
          <span class="menu-text">Usuários</span>
        </button>
      </nav>

      <!-- Footer do Sidebar -->
      <div class="sidebar-footer">
        <button class="menu-item logout-btn" @click="logout">
          <i class="fas fa-sign-out-alt menu-icon"></i>
          <span class="menu-text">Sair</span>
        </button>
        
        <div class="user-info" v-show="!isCollapsed">
          <span class="company-name">CONTROLE DE GESTÃO</span>
        </div>
      </div>
    </aside>

    <!-- Overlay para mobile -->
    <div class="sidebar-overlay" v-if="isCollapsed && isMobile" @click="toggleSidebar"></div>

    <!-- Conteúdo Principal -->
    <main class="main-content" :class="{ expanded: isCollapsed }">
      <component :is="panelComponent" />
    </main>

    <!-- Modal de Alerta de Domínios -->
    <div v-if="showDominioAlert" class="modal-overlay alert-modal">
      <div class="modal-content alert-content">
        <div class="alert-header">
          <h3><i class="fas fa-exclamation-triangle"></i> Atenção: Domínios Vencendo</h3>
        </div>
        <div class="alert-body">
          <p class="alert-desc">Os seguintes domínios estão com vencimento próximo ou já expiraram. Por favor, regularize-os para evitar inatividade do sistema:</p>
          <ul class="alert-list">
            <li v-for="dom in dominiosAlertList" :key="dom.id">
              <strong>{{ dom.dominio }}</strong>
              <span class="alert-days">{{ dom.diasTexto }}</span>
            </li>
          </ul>
        </div>
        <div class="alert-footer">
          <button class="alert-btn" @click="showDominioAlert = false">Estou Ciente</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Funcionarios from './Funcionarios.vue';
import Sistemas from './Sistemas.vue';
import DashboardPanel from './DashboardPanel.vue';
import Setores from './Setores.vue';
import GruposEmail from './GruposEmail.vue';
import GruposWhatsapp from './GruposWhatsapp.vue';
import Usuarios from './Usuarios.vue';
import GruposPasta from './GruposPasta.vue';
import Cargos from './Cargos.vue';
import Celulares from './Celulares.vue';
import Notebooks from './Notebooks.vue';
import Dominios from './Dominios.vue';
import SlaAudit from './SlaAudit.vue';
// REMOVIDOS: QuadroColaboradores, MetaColaborador (funcionalidades desabilitadas)

import { API_BASE_URL } from '@/api.js';

export default {
  name: 'Dashboard',
  components: { Funcionarios, Sistemas, DashboardPanel, Setores, GruposEmail, GruposWhatsapp, Usuarios, GruposPasta, Cargos, Celulares, Notebooks, Dominios, SlaAudit },
  data() {
    return {
      // não definir por padrão 'dashboard' — vamos escolher no mounted() com base nas permissões
      activePanel: null,
      funcionarios: [],
      isCollapsed: false,
      isMobile: false,
      showDominioAlert: false,
      dominiosAlertList: []
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
        case 'gruposWhatsapp': return 'GruposWhatsapp';
        case 'cargos': return 'Cargos';
        case 'celulares': return 'Celulares';
        case 'notebooks': return 'Notebooks';
        case 'dominios': return 'Dominios';
        case 'sla': return 'SlaAudit';
        case 'configuracoes': return { template: '<div><h2 style="color:var(--cor-primaria);font-family:var(--font-titulo);">Configurações</h2><p>Configurações do sistema aparecerão aqui.</p></div>' };
        default: return 'DashboardPanel';
      }
    }
  },
  mounted() {
    // definir painel inicial com base nas permissões do usuário
    this.selectInitialPanel();

    // reagir a mudanças de auth (ex: admin atualiza permissões e faz reload do current user)
    const onAuthUpdated = () => this.selectInitialPanel();
    window.addEventListener('auth:updated', onAuthUpdated);
    this._onAuthUpdated = onAuthUpdated;

    this.carregarFuncionarios();
    
    // Checar se o user tem permissão de admin para checar domínios
    if (this.$auth && this.$auth.hasPermission('adm')) {
      this.checkDominiosExpiration();
    }

    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize);
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize);
    if (this._onAuthUpdated) window.removeEventListener('auth:updated', this._onAuthUpdated);
  },
  methods: {
    selectInitialPanel() {
      try {
        const auth = this.$auth;
        if (auth && typeof auth.hasPermission === 'function') {
          // Verificar permissões específicas
          const temPermissaoMeta = auth.hasPermission('meta_colaborador');
          const temPermissaoAdmin = auth.hasPermission('adm');
          const temPermissaoInfra = auth.hasPermission('infra');
          const temPermissaoEditarColaborador = auth.hasPermission('editar_colaborador');
          const temPermissaoEditarUsuario = auth.hasPermission('editar_usuario');

          // Se tem permissão admin, pode ver tudo
          if (temPermissaoAdmin) {
            this.activePanel = 'dashboard';
            return;
          }

          // Se tem permissão de infra (e não é admin), vai para SLA
          if (temPermissaoInfra) {
            console.log('Usuário tem permissão infra - direcionando para Auditoria SLA');
            this.activePanel = 'sla';
            return;
          }

          // Se tem permissão de meta_colaborador (funcionalidade removida), vai para dashboard
          if (temPermissaoMeta) {
            console.log('Usuário tinha permissão meta_colaborador - direcionando para dashboard');
            this.activePanel = 'dashboard';
            return;
          }

          // Se tem permissão para editar usuários
          if (temPermissaoEditarUsuario) {
            this.activePanel = 'usuarios';
            return;
          }

          // Se tem permissão para editar colaboradores
          if (temPermissaoEditarColaborador) {
            this.activePanel = 'funcionarios';
            return;
          }
        }
        
        // Se nenhum dos casos acima, fallback para dashboard
        this.activePanel = 'dashboard';
      } catch (e) {
        this.activePanel = 'dashboard';
      }
    },
    async carregarFuncionarios() {
      try {
        console.log('Carregando funcionários de:', `${API_BASE_URL}/funcionarios/`);
        const response = await fetch(`${API_BASE_URL}/funcionarios/`);
        console.log('Response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Funcionários carregados:', data);
        this.funcionarios = data;
      } catch (e) {
        console.error('Erro ao carregar funcionários:', e);
        this.funcionarios = [];
      }
    },
    async checkDominiosExpiration() {
      try {
        const response = await fetch(`${API_BASE_URL}/dominios/`);
        if (!response.ok) return;
        const dominios = await response.json();
        
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        
        const expiring = [];
        dominios.forEach(d => {
          if (!d.data_vencimento) return;
          const venc = new Date(d.data_vencimento + 'T00:00:00');
          const diff = venc.getTime() - hoje.getTime();
          const dias = Math.ceil(diff / (1000 * 3600 * 24));
          
          if (dias <= 20) {
            let texto = `Expira em ${dias} dia(s)`;
            if (dias < 0) texto = `Expirado há ${Math.abs(dias)} dia(s)`;
            else if (dias === 0) texto = "Expira HOJE";
            
            expiring.push({
              id: d.id,
              dominio: d.dominio,
              dias,
              diasTexto: texto
            });
          }
        });
        
        if (expiring.length > 0) {
          // Sort so the most urgent (lowest days) is at the top
          expiring.sort((a, b) => a.dias - b.dias);
          this.dominiosAlertList = expiring;
          this.showDominioAlert = true;
        }
      } catch (e) {
        console.error('Erro ao checar domínios:', e);
      }
    },
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
    },
    checkScreenSize() {
      this.isMobile = window.innerWidth <= 768;
      if (this.isMobile) {
        this.isCollapsed = true;
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
/* Container Principal */
.dashboard-container {
  height: 100vh;
  background: #050a18;
  position: relative;
  overflow: hidden;
}

/* CORTE ABSOLUTO - NADA PODE PASSAR DESTA LINHA */
.sidebar {
  width: 280px;
  min-width: 280px;
  background: #0f172a;
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  transition: width 0.2s ease, min-width 0.2s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  overflow: hidden;
  will-change: width;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Remover a máscara que estava ocultando o botão sair */

.sidebar.collapsed {
  width: 70px;
  min-width: 70px;
}

/* Header do Sidebar */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 80px;
  position: relative;
}

.logo {
  transition: opacity 0.2s ease, transform 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1;
  max-width: calc(100% - 140px); /* Reserva mais espaço para o botão hambúrguer */
  padding-right: 60px; /* Força o logo para a esquerda */
}

.logo-img {
  max-width: 170px; 
  max-height: 50px; 
  object-fit: contain;
  /* Garante visibilidade da logo em fundos escuros */
  filter: brightness(0) invert(1);
  opacity: 0.9;
  will-change: transform;
}

.collapsed .logo {
  opacity: 0;
  transform: translateX(-50%) scale(0.8);
  pointer-events: none;
}

.hamburger-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: white;
  padding: 0.75rem;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
  font-size: 1.2rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  position: absolute;
  right: 1.5rem;
  z-index: 2;
  will-change: transform;
}

.hamburger-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}

.collapsed .hamburger-btn {
  position: relative;
  right: auto;
  margin: 0 auto;
}

.menu {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1001;
}

/* Scrollbar fina para o menu */
.menu::-webkit-scrollbar {
  width: 4px;
}
.menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

/* Barreira sutil apenas no final do menu - REMOVIDO PARA CLEAN LOOK */
.menu::after {
  display: none;
}

.menu-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.875rem 1.5rem;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
  text-align: left;
  border-left: 3px solid transparent !important;
  position: relative;
  will-change: transform;
}

/* DESABILITAR TODAS AS BORDAS AZUIS GLOBALMENTE */
.menu-item,
.menu-item:hover,
.menu-item:focus,
.menu-item:active,
.menu-item.active {
  border-left: 3px solid transparent !important;
  border-left-color: transparent !important;
}

/* REGRA GLOBAL PARA PREVENIR BORDAS AZUIS EM QUALQUER LUGAR */
.sidebar .menu-item,
.sidebar .menu-item:hover,
.sidebar .menu-item:focus,
.sidebar .menu-item:active,
.sidebar .menu-item.active,
.sidebar:not(.collapsed) .menu-item,
.sidebar:not(.collapsed) .menu-item:hover,
.sidebar:not(.collapsed) .menu-item:active,
.collapsed .menu-item,
.collapsed .menu-item:hover,
.collapsed .menu-item:active {
  border-left: 3px solid transparent !important;
  border-left-color: transparent !important;
  border-color: transparent !important;
}

.menu-icon {
  font-size: 1.1rem;
  min-width: 24px;
  margin-right: 1rem;
  transition: all 0.3s ease;
}

.menu-text {
  transition: all 0.3s ease;
  white-space: nowrap;
}

.collapsed .menu-text {
  opacity: 0;
  width: 0;
  overflow: hidden;
  margin: 0;
}

.collapsed .menu-icon {
  margin-right: 0;
  display: flex;
  justify-content: center;
  width: 100%;
}

/* Estados dos menu items - REMOVENDO TODAS AS BORDAS AZUIS */
.sidebar:not(.collapsed) .menu-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.15);
  border-left: 3px solid transparent !important;
  transform: translateX(2px);
  max-height: 60px;
  overflow: hidden;
}

.sidebar:not(.collapsed) .menu-item.active {
  color: white;
  background: rgba(96, 165, 250, 0.3);
  border-left: 3px solid transparent !important;
  font-weight: 600;
  max-height: 60px;
  overflow: hidden;
}

/* Garantir que no modo expandido, menu items normais não tenham borda */
.sidebar:not(.collapsed) .menu-item {
  border-left: 3px solid transparent !important;
  max-height: 60px;
  overflow: hidden;
}

/* Remover completamente todos os efeitos visuais no modo colapsado */
.collapsed .menu-item {
  border-left: 3px solid transparent !important;
}

.collapsed .menu-item:hover {
  border-left: 3px solid transparent !important;
  border-left-color: transparent !important;
  transform: none !important;
  background: rgba(255, 255, 255, 0.1);
}

.collapsed .menu-item.active {
  border-left: 3px solid transparent !important;
  border-left-color: transparent !important;
  background: rgba(96, 165, 250, 0.2);
}

.menu-item.active .menu-icon {
  color: #60a5fa;
}

/* Garantir que ícones ativos funcionem em ambos os modos */
.sidebar:not(.collapsed) .menu-item.active .menu-icon,
.collapsed .menu-item.active .menu-icon {
  color: #60a5fa;
}

/* Reset para o botão de logout quando ativo */
.logout-btn.active,
.sidebar-footer .logout-btn.active {
  color: #ef4444 !important;
  background: rgba(239, 68, 68, 0.2) !important;
  border-left: 3px solid transparent !important;
  border-left-color: transparent !important;
}

/* Prevenir qualquer elemento de aparecer sobre o footer */
.sidebar-footer {
  isolation: isolate;
}

.sidebar-footer * {
  z-index: 10001 !important;
}

/* Bloquear qualquer pseudo-elemento na área do footer */
.menu .menu-item:nth-last-child(-n+2)::before,
.menu .menu-item:nth-last-child(-n+2)::after,
.menu .menu-item:nth-last-child(-n+2):hover::before,
.menu .menu-item:nth-last-child(-n+2):hover::after {
  display: none !important;
  opacity: 0 !important;
  visibility: hidden !important;
}

/* Tooltip para modo colapsado */
.collapsed .menu-item {
  position: relative;
  justify-content: center;
  padding: 0.875rem 0;
  display: flex;
  align-items: center;
}

.collapsed .menu-item .menu-icon {
  margin: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.collapsed .menu-item:hover::after {
  display: none !important;
}

/* Remover completamente todos os tooltips no modo colapsado */
.collapsed .menu-item::after,
.collapsed .menu-item:hover::after,
.collapsed .menu-item:focus::after {
  display: none !important;
  content: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
}

/* Remover completamente todos os tooltips no modo colapsado */
.collapsed .menu-item::after,
.collapsed .menu-item:hover::after,
.collapsed .menu-item:focus::after {
  display: none !important;
  content: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
}

/* Desabilitar todas as regras de tooltip específicas */
.menu .collapsed .menu-item:hover::after,
.sidebar-footer .collapsed .menu-item:hover::after,
.collapsed .sidebar-footer .menu-item:hover::after,
.collapsed .sidebar-footer .menu-item:hover::before {
  display: none !important;
  content: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  margin-top: auto;
  flex-shrink: 0;
  position: relative;
  z-index: 9999;
  background: #0f172a;
  padding: 0.5rem 0;
}

/* Barreira apenas na parte superior do footer - REMOVIDO PARA CLEAN LOOK */
.sidebar-footer::before {
  display: none;
}

/* Melhorar o estilo do botão sair */
.sidebar-footer .logout-btn {
  color: #ef4444 !important;
  background: rgba(239, 68, 68, 0.1) !important;
  border-left: 3px solid transparent !important;
  border-left-color: transparent !important;
  position: relative;
  z-index: 99999 !important;
  margin: 0.5rem 1rem;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.1);
}

.sidebar-footer .logout-btn:hover {
  background: rgba(239, 68, 68, 0.2) !important;
  border-left: 3px solid transparent !important;
  border-left-color: transparent !important;
  z-index: 99999 !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.sidebar-footer .logout-btn .menu-icon {
  color: #ef4444 !important;
  z-index: 99999 !important;
  font-size: 1.1rem;
}

/* Estilo do botão sair no modo colapsado */
.collapsed .sidebar-footer .logout-btn {
  margin: 0.5rem;
  padding: 0.75rem;
  justify-content: center;
}

.collapsed .sidebar-footer .logout-btn .menu-text {
  display: none;
}

.collapsed .sidebar-footer .logout-btn .menu-icon {
  margin-right: 0;
}

/* Garantir que os estilos de logout sempre prevaleçam */
.sidebar-footer .logout-btn {
  color: #ef4444 !important;
  background: none !important;
  border-left: 3px solid transparent !important;
  margin: 0;
}

.sidebar-footer .logout-btn:hover {
  background: rgba(239, 68, 68, 0.1) !important;
  border-left-color: #ef4444 !important;
}

.sidebar-footer .logout-btn .menu-icon {
  color: #ef4444 !important;
}

.user-info {
  padding: 1rem 1.5rem;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 0.5rem;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 8px 8px 0 0;
}

.company-name {
  font-size: 0.8rem;
  font-weight: 600;
  display: block;
  margin-bottom: 0.25rem;
  opacity: 0.9;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.9);
}

.version {
  font-size: 0.65rem;
  opacity: 0.8;
  color: #60a5fa;
  font-weight: 500;
  background: rgba(96, 165, 250, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  display: inline-block;
}

/* Overlay para Mobile */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: none;
}

/* Conteúdo Principal */
.main-content {
  flex: 1;
  margin-left: 280px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
  overflow-x: hidden;
  background: #050a18;
  height: 100vh;
}

.main-content.expanded {
  margin-left: 70px;
}

/* Responsividade */
@media (max-width: 1024px) {
  .sidebar {
    width: 260px;
    min-width: 260px;
  }
  
  .main-content {
    margin-left: 260px;
  }
  
  .main-content.expanded {
    margin-left: 70px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 280px;
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  .sidebar-overlay {
    display: block;
  }
  
  .main-content {
    width: 100%;
    margin-left: 0 !important;
  }
  
  .hamburger-btn {
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 1001;
    background: #1e40af;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }
}

@media (max-width: 480px) {
  .sidebar {
    width: 100%;
    min-width: 100%;
  }
  
  .menu-item {
    padding: 1rem 1.5rem;
    font-size: 1rem;
  }
  
  .menu-icon {
    font-size: 1.2rem;
    margin-right: 1.25rem;
  }
}

/* Scrollbar personalizada */
.menu::-webkit-scrollbar {
  width: 4px;
}

.menu::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.menu::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Animações */
@keyframes slideIn {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-100%);
  }
}

/* Modal de Alerta de Domínios - Premium Design */
.alert-modal { 
  position: fixed; 
  inset: 0; 
  background: rgba(5, 10, 24, 0.7); 
  backdrop-filter: blur(12px); 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  z-index: 99999; 
  padding: 20px;
}
.alert-content { 
  background: #ffffff; 
  border-radius: 24px; 
  width: 100%; 
  max-width: 480px; 
  box-shadow: 0 25px 50px -12px rgba(239, 68, 68, 0.25), 0 0 0 1px rgba(239, 68, 68, 0.1); 
  overflow: hidden; 
  animation: modalAlertIn 0.5s cubic-bezier(0.16, 1, 0.3, 1); 
  display: flex;
  flex-direction: column;
  border: none;
}
@keyframes modalAlertIn { 
  from { opacity: 0; transform: translateY(40px) scale(0.95); } 
  to { opacity: 1; transform: translateY(0) scale(1); } 
}
.alert-header { 
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); 
  padding: 24px 32px; 
  border-bottom: 1px solid rgba(239, 68, 68, 0.1);
}
.alert-header h3 { 
  margin: 0; 
  color: #b91c1c; 
  font-size: 1.4rem; 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  font-weight: 800; 
}
.alert-header h3 i {
  font-size: 1.6rem;
  color: #ef4444;
}
.alert-body {
  padding: 32px;
}
.alert-desc { 
  color: #475569; 
  font-size: 15px; 
  margin-top: 0; 
  margin-bottom: 24px; 
  line-height: 1.5;
}
.alert-list { 
  list-style: none; 
  padding: 0; 
  margin: 0; 
  max-height: 280px; 
  overflow-y: auto; 
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 8px;
}
.alert-list::-webkit-scrollbar { width: 6px; }
.alert-list::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
.alert-list li { 
  background: #f8fafc; 
  border: 1px solid #e2e8f0; 
  padding: 16px; 
  border-radius: 12px; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  transition: transform 0.2s, box-shadow 0.2s;
}
.alert-list li:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border-color: #cbd5e1;
}
.alert-list li strong { 
  color: #0f172a; 
  font-size: 15px; 
  font-weight: 700;
}
.alert-days { 
  font-size: 13px; 
  font-weight: 700; 
  color: #ef4444; 
  background: #fef2f2; 
  padding: 6px 12px; 
  border-radius: 20px; 
  border: 1px solid #fee2e2;
  white-space: nowrap;
}
.alert-footer {
  padding: 0 32px 32px 32px;
}
.alert-btn { 
  width: 100%; 
  padding: 16px; 
  font-size: 16px; 
  font-weight: 700;
  color: white;
  text-transform: uppercase; 
  letter-spacing: 1px; 
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); 
  border: none;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}
.alert-btn:hover { 
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}
.alert-btn:active {
  transform: translateY(0);
}

/* Responsividade do modal */
@media (max-width: 480px) {
  .alert-header { padding: 20px; }
  .alert-body { padding: 20px; }
  .alert-footer { padding: 0 20px 20px 20px; }
  .alert-list li { flex-direction: column; align-items: flex-start; gap: 8px; }
  .alert-days { align-self: flex-start; }
}
</style>
