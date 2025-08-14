import axios from 'axios';
import { API_BASE_URL } from '../api';
// Configura a baseURL do axios para o backend correto
axios.defaults.baseURL = API_BASE_URL;
// Interceptor para adicionar o token JWT em todas as requisições
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import CadastroUsuario from '../views/CadastroUsuario.vue';
import Cadastro from '../views/Cadastro.vue';
import Funcionarios from '../views/Funcionarios.vue';
import Sistemas from '../views/Sistemas.vue';
import GruposPasta from '../views/GruposPasta.vue';
import Login from '../views/Login.vue';

const Configuracoes = { template: '<div><h2 style="color:var(--cor-primaria);font-family:var(--font-titulo);">Configurações</h2><p>Configurações do sistema aparecerão aqui.</p></div>' };

const routes = [
  { path: '/login', component: Login },
  { path: '/cadastro-usuario', component: CadastroUsuario },
  { path: '/', component: Dashboard },
  { path: '/cadastro', component: Cadastro },
  { path: '/sistemas', component: Sistemas },
  { path: '/funcionarios', component: Funcionarios },
  { path: '/grupos-pasta', component: GruposPasta },
  { path: '/grupos-email', component: require('../views/GruposEmail.vue').default },
  { path: '/configuracoes', component: Configuracoes },
  { path: '/usuarios', component: require('../views/Usuarios.vue').default }
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
