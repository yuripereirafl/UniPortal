import axios from 'axios';
import { API_BASE_URL } from '../api';
axios.defaults.baseURL = API_BASE_URL;

// Proteção contra loop de requisições /me
let meRequestInProgress = false;
let lastMeRequestTime = 0;
const MIN_ME_REQUEST_INTERVAL = 1000; // Mínimo 1 segundo entre requisições

// Interceptor de requisição - adiciona token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Proteção contra múltiplas requisições /me simultâneas
  if (config.url === '/me') {
    const now = Date.now();

    // Se já tem uma requisição em andamento ou muito recente, bloquear
    if (meRequestInProgress || (now - lastMeRequestTime) < MIN_ME_REQUEST_INTERVAL) {
      console.warn('[AXIOS] Bloqueando requisição /me duplicada');
      return Promise.reject(new Error('Requisição /me bloqueada - já em andamento'));
    }

    meRequestInProgress = true;
    lastMeRequestTime = now;
    console.log('[AXIOS] Requisição /me iniciada');
  }

  return config;
});

// Flag para evitar múltiplos redirecionamentos
let isRedirecting = false;

// Interceptor de resposta - trata erros 401 (Unauthorized)
axios.interceptors.response.use(
  response => {
    // Resetar flag de requisição /me em andamento quando tiver sucesso
    if (response.config.url === '/me') {
      meRequestInProgress = false;
    }
    return response;
  },
  error => {
    // Resetar flag de requisição /me em andamento quando tiver erro
    if (error.config && error.config.url === '/me') {
      meRequestInProgress = false;
    }

    // Se for erro 401 (token expirado/inválido), redirecionar para login
    if (error.response && error.response.status === 401) {
      if (!isRedirecting) {
        isRedirecting = true;

        // Redirecionar para login apenas se NÃO for uma tentativa de login falha
        const urlString = error.config && error.config.url ? String(error.config.url) : '';
        const isLoginRequest = urlString === '/login' || urlString.endsWith('/login');

        if (!isLoginRequest) {
          console.warn('Sessão expirada (401). Redirecionando para login...');
          localStorage.removeItem('token');
          localStorage.removeItem('current_user');
          setTimeout(() => {
            window.location.href = '/login';
          }, 100);
        } else {
          // Se for erro no login, permitir que o usuário veja a mensagem de "usuário ou senha inválidos"
          isRedirecting = false;
        }
      }
    }
    return Promise.reject(error);
  }
);

import { createRouter, createWebHistory } from 'vue-router';

// Lazy loading para melhor performance
const Dashboard = () => import('../views/Dashboard.vue');
const CadastroUsuario = () => import('../views/CadastroUsuario.vue');
const Cadastro = () => import('../views/Cadastro.vue');
const Funcionarios = () => import('../views/Funcionarios.vue');
const Sistemas = () => import('../views/Sistemas.vue');
const GruposPasta = () => import('../views/GruposPasta.vue');
const GruposEmail = () => import('../views/GruposEmail.vue');
const Usuarios = () => import('../views/Usuarios.vue');
const Login = () => import('../views/Login.vue');

const Configuracoes = { template: '<div><h2 style="color:var(--cor-primaria);font-family:var(--font-titulo);">Configurações</h2><p>Configurações do sistema aparecerão aqui.</p></div>' };

const routes = [
  { path: '/login', component: Login },
  { path: '/cadastro-usuario', component: CadastroUsuario },
  { path: '/', component: Dashboard },
  { path: '/cadastro', component: Cadastro },
  { path: '/sistemas', component: Sistemas },
  { path: '/funcionarios', component: Funcionarios },
  { path: '/grupos-pasta', component: GruposPasta },
  { path: '/grupos-email', component: GruposEmail },
  { path: '/configuracoes', component: Configuracoes },
  { path: '/usuarios', component: Usuarios }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (to.path === '/login') {
    next();
    return;
  }
  if (!token) {
    next('/login');
  } else {
    // se a rota exige permissão, validar via $auth (se app estiver montado)
    const required = to.meta && to.meta.requiredPermission;
    if (required) {
      try {
        const auth = window?.appInstance?.config?.globalProperties?.$auth || null;
        if (auth && typeof auth.hasPermission === 'function') {
          if (!auth.hasPermission(required)) {
            return next('/');
          }
        }
      } catch (e) {
        console.warn('Erro ao checar permissão no router:', e);
      }
    }
    next();
  }
});

export default router;
