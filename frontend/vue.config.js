module.exports = {
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '^/quadro_colaboradores': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/funcionarios': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/cargos': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/setores': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
}
