<template>
  <div class="cadastro-container">
    <h2>Criar Conta</h2>
    <form @submit.prevent="cadastrar">
      <input v-model="username" placeholder="Usuário" required />
      <input v-model="password" type="password" placeholder="Senha" required />
      <button type="submit">Cadastrar</button>
      <p v-if="erro" class="erro">{{ erro }}</p>
      <p v-if="sucesso" class="sucesso">{{ sucesso }}</p>
    </form>
    <router-link to="/login">Já tem conta? Faça login</router-link>
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
      sucesso: ''
    }
  },
  methods: {
    async cadastrar() {
      try {
        await axios.post('/usuarios/', null, {
          params: { username: this.username, password: this.password }
        });
        this.sucesso = 'Usuário criado com sucesso! Redirecionando para login...';
        this.erro = '';
        setTimeout(() => {
          this.$router.push('/login');
        }, 1500);
      } catch (e) {
        this.erro = 'Usuário já existe ou erro no cadastro!';
        this.sucesso = '';
      }
    }
  }
}
</script>

<style scoped>
.cadastro-container {
  max-width: 350px;
  margin: 80px auto;
  padding: 32px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(20,65,121,0.12);
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
  background: #1976d2;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
}
.erro {
  color: #d32f2f;
  margin-top: 10px;
}
.sucesso {
  color: #388e3c;
  margin-top: 10px;
}
</style>