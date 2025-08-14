const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  devServer: {
    host: '0.0.0.0',
    port: 8080
  },
  configureWebpack: {
    plugins: [
      new (require('webpack')).DefinePlugin({
        __VUE_OPTIONS_API__: JSON.stringify(true),
        __VUE_PROD_DEVTOOLS__: JSON.stringify(false),
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false)
      })
    ]
  }
})
