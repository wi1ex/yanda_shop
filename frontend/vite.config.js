import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 8080
  },
  root: 'frontend/src',
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: './src/index.html',
    },
  },
});
