import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  root: "/frontend", // Корень проекта (учитываем путь в Docker)
  publicDir: "public", // Папка с index.html
  build: {
    outDir: "dist",
    rollupOptions: {
      input: "/frontend/public/index.html" // Новый путь
    }
  }
});
