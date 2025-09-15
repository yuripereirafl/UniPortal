import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { setupMemoryCleanup } from '@/config/performance';

import '@/assets/css/performance.css';

setupMemoryCleanup();

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

app.use(router);
app.mount('#app');
