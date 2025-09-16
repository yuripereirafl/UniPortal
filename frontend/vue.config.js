// Usar variável de ambiente ou fallback para desenvolvimento
const API_TARGET = process.env.VUE_APP_API_URL || 'http://localhost:8000';

module.exports = {
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '^/quadro_colaboradores': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '^/funcionarios': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '^/cargos': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '^/setores': {
        target: API_TARGET,
        changeOrigin: true,
      }
    }
  }
}
