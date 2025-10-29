import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { setupMemoryCleanup } from '@/config/performance';
import auth from '@/services/auth';

import '@/assets/css/performance.css';

setupMemoryCleanup();

async function bootstrap() {
  const app = createApp(App, {
    compilerOptions: {
      comments: process.env.NODE_ENV !== 'production'
    }
  });

  app.config.globalProperties.$performance = {
    startTime: Date.now(),
    measureTime: (label) => {
      const time = Date.now() - app.config.globalProperties.$performance.startTime;
      console.log(`[Performance] ${label}: ${time}ms`);
    }
  };

  // Expor utilitário auth globalmente
  app.config.globalProperties.$auth = auth;

  // guardar instância globalmente para o router poder checar permissoes em beforeEach
  try {
    window.appInstance = app;
  } catch (e) {
    // ambiente não-browser, ignorar
  }

  app.use(router);

  // Tentar carregar usuário atual antes de montar a aplicação
  try {
    await auth.loadCurrentUser();
  } catch (err) {
    // continuar mesmo se falhar (rota /login cuidará da autenticação)
    console.warn('Falha ao carregar usuário antes do bootstrap:', err && err.message ? err.message : err);
  }

  app.mount('#app');
}

bootstrap();
