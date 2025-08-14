<template>
  <div class="login-bg">
    <div class="login-container">
      <img src="@/assets/logo2.png" alt="Logo" class="login-logo" />
      <form @submit.prevent="login">
        <input v-model="username" placeholder="Usuário" required />
        <input v-model="password" type="password" placeholder="Senha" required />
        <button type="submit">Entrar</button>
        <p v-if="erro" class="erro">{{ erro }}</p>
      </form>
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
      erro: ''
    }
  },
  methods: {
    async login() {
      try {
        const params = new URLSearchParams();
        params.append('username', this.username);
        params.append('password', this.password);
        const res = await axios.post('/login', params);
        localStorage.setItem('token', res.data.access_token);
        this.$router.push('/'); // Redireciona para o dashboard
      } catch (e) {
        this.erro = 'Usuário ou senha inválidos!';
      }
    }
  }
}
</script>

<style scoped>
.login-logo {
  max-width: 350px;
  max-height: 140px;
  display: block;
  margin: 0 auto 32px auto;
}
.login-bg {
  min-height: 100vh;
  width: 100vw;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.login-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  background: radial-gradient(circle at 60% 40%, var(--cor-sec2, #ffc107) 0%, transparent 60%),
              radial-gradient(circle at 20% 80%, var(--cor-primaria, #1a3972) 0%, transparent 70%),
              linear-gradient(135deg, var(--cor-primaria, #1a3972) 60%, var(--cor-sec2, #ffc107) 100%);
  filter: blur(8px) brightness(1.1);
  opacity: 0.85;
}
.login-container {
  position: relative;
  z-index: 1;
  max-width: 350px;
  margin: 40px auto;
  padding: 32px 28px;
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  box-shadow: 0 2px 24px rgba(20,65,121,0.22);
  text-align: center;
  backdrop-filter: blur(2px);
}
.login-container {
  max-width: 350px;
  margin: 40px auto;
  padding: 32px 28px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(20,65,121,0.18);
  text-align: center;
}
input {
  width: 90%;
  margin-bottom: 16px;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
}
button {
  width: 100%;
  padding: 10px;
  background: var(--cor-primaria, #1a3972);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
}
button:hover {
  background: var(--cor-sec2, #ffc107);
  color: var(--cor-primaria, #1a3972);
}
.erro {
  color: #d32f2f;
  margin-top: 10px;
}
</style>