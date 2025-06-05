import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  root: '.',
  publicDir: 'public',
  plugins: [vue()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') }
  },
  build: {
    outDir: 'dist',
    rollupOptions: { input: path.resolve(__dirname, 'index.html') }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @import "src/styles/_variables.scss";
          @import "src/styles/_mixins.scss";
        `
      }
    }
  }
})
