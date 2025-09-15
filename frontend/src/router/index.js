import axios from 'axios';
import { API_BASE_URL } from '../api';
axios.defaults.baseURL = API_BASE_URL;
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
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
    next();
  }
});

export default router;
