module.exports = {
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '^/quadro_colaboradores': {
        target: 'http://192.168.1.37:8000',
        changeOrigin: true,
      },
      '^/funcionarios': {
        target: 'http://192.168.1.37:8000',
        changeOrigin: true,
      },
      '^/cargos': {
        target: 'http://192.168.1.37:8000',
        changeOrigin: true,
      },
      '^/setores': {
        target: 'http://192.168.1.37:8000',
        changeOrigin: true,
      }
    }
  }
}
