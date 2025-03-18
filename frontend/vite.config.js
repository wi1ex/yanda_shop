import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 8080,
  },
  root: 'frontend/src', // Корневая директория проекта
  build: {
    outDir: '../../dist', // Выходная директория относительно root
    rollupOptions: {
      input: './index.html', // Путь к точке входа относительно root
    },
  },
});