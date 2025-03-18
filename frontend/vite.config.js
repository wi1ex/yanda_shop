import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  root: ".", // Корень проекта
  publicDir: "public", // Папка со статическими файлами (index.html)
  build: {
    outDir: "dist", // Куда будет собираться проект
  }
});
