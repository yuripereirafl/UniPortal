// Usar variável de ambiente ou fallback para desenvolvimento
// Usa variável de ambiente para apontar para a API; por padrão aponta para a VM 192.168.1.37
const API_TARGET = process.env.VUE_APP_API_URL || 'http://192.168.1.37:8000';

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
  },
  configureWebpack: {
    plugins: [
  new (require('webpack').DefinePlugin)({
        __VUE_OPTIONS_API__: true,
        __VUE_PROD_DEVTOOLS__: false,
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
      })
    ]
  }
}
