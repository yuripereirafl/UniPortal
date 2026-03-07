<template>
  <div class="login-wrapper">
    <!-- Fundo tecnológico animado -->
    <div class="tech-bg">
      <div class="glow-circle glow-1"></div>
      <div class="glow-circle glow-2"></div>
      <div class="grid-overlay"></div>
    </div>
    
    <div class="login-card">
      <div class="login-header">
        <div class="logo-container">
          <img src="@/assets/logo2.png" alt="UniPortal" class="login-logo" />
        </div>
        <h1>Bem-vindo ao <span>UniPortal</span></h1>
        <p>Acesse a plataforma de gestão tecnológica</p>
      </div>

      <form @submit.prevent="login" class="login-form">
        <div class="input-group">
          <label>Usuário</label>
          <div class="input-wrapper">
            <i class="fas fa-user"></i>
            <input 
              v-model="username" 
              placeholder="Digite seu usuário" 
              required 
              :disabled="acessando"
              autocomplete="username"
            />
          </div>
        </div>

        <div class="input-group">
          <label>Senha</label>
          <div class="input-wrapper">
            <i class="fas fa-lock"></i>
            <input 
              v-model="password" 
              type="password" 
              placeholder="Digite sua senha" 
              required 
              :disabled="acessando"
              autocomplete="current-password"
            />
          </div>
        </div>

        <button type="submit" :disabled="acessando" class="btn-login">
          <div v-if="acessando" class="loader"></div>
          <span v-else>Entrar no Sistema</span>
          <i v-if="!acessando" class="fas fa-arrow-right"></i>
        </button>

        <Transition name="fade">
          <div v-if="erro" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ erro }}
          </div>
        </Transition>
      </form>
      
      <div class="login-footer">
        <p>&copy; 2024 UniPortal • Tecnologia & Gestão</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      erro: '',
      acessando: false
    }
  },
  methods: {
    async login() {
      if (this.acessando) return;
      this.acessando = true;
      this.erro = '';
      try {
        const params = new URLSearchParams();
        params.append('username', this.username);
        params.append('password', this.password);
        const res = await axios.post('/login', params);
        localStorage.setItem('token', res.data.access_token);
        
        try {
          if (this.$auth && typeof this.$auth.loadCurrentUser === 'function') {
            await this.$auth.loadCurrentUser();
          }
        } catch (e) {
          console.warn('Falha ao carregar usuário após login:', e);
        }

        this.$router.push('/');
      } catch (e) {
        if (e.response && e.response.status === 401) {
          this.erro = 'Usuário ou senha inválidos!';
        } else {
          this.erro = 'Erro ao conectar ao servidor. Verifique sua rede.';
          console.error('Erro no login:', e);
        }
      } finally {
        this.acessando = false;
      }
    }
  }
}
</script>

<style scoped>
/* Reset Local */
.login-wrapper {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #050a18;
  font-family: 'Inter', -apple-system, sans-serif;
  overflow: hidden;
  position: relative;
}

/* Background Tech */
.tech-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(circle at center, black, transparent 80%);
}

.glow-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  z-index: 1;
}

.glow-1 {
  width: 400px;
  height: 400px;
  background: #3b82f6;
  top: -100px;
  right: -50px;
  animation: float 10s infinite alternate;
}

.glow-2 {
  width: 350px;
  height: 350px;
  background: #1e3a8a;
  bottom: -50px;
  left: -50px;
  animation: float 8s infinite alternate-reverse;
}

@keyframes float {
  from { transform: translate(0, 0); }
  to { transform: translate(30px, 40px); }
}

/* Login Card (Glassmorphism) */
.login-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 400px;
  padding: 30px;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-header {
  text-align: center;
  margin-bottom: 20px;
}

.logo-container {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.login-logo {
  max-width: 190px;
  height: auto;
  display: block;
  /* Torna o logo preto (em fundo branco) para branco (em fundo transparente) */
  filter: invert(1) brightness(1.5);
  mix-blend-mode: screen;
}

h1 {
  color: #f8fafc;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}

h1 span {
  color: #3b82f6;
}

p {
  color: #94a3b8;
  font-size: 0.9rem;
}

/* Form Styles */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  color: #cbd5e1;
  font-size: 0.85rem;
  font-weight: 500;
  margin-left: 4px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper i {
  position: absolute;
  left: 16px;
  color: #64748b;
  font-size: 0.9rem;
  transition: color 0.3s;
}

.input-wrapper input {
  width: 100%;
  padding: 14px 16px 14px 44px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #f8fafc;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(30, 41, 59, 0.8);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.input-wrapper input:focus + i {
  color: #3b82f6;
}

/* Button */
.btn-login {
  width: 100%;
  padding: 14px;
  margin-top: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(37, 99, 235, 0.4);
  filter: brightness(1.1);
}

.btn-login:active:not(:disabled) {
  transform: translateY(0);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

/* Error Message */
.error-message {
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #f87171;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* Loader */
.loader {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer {
  margin-top: 24px;
  text-align: center;
}

.login-footer p {
  font-size: 0.75rem;
  color: #64748b;
}

/* Mobile Adjustments */
@media (max-width: 480px) {
  .login-card {
    margin: 20px;
    padding: 30px 20px;
  }
}
</style>