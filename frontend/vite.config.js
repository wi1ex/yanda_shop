import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  root: path.resolve(__dirname, 'src'),  // Указываем корнем папку src
  build: {
    outDir: '../dist',
    rollupOptions: {
      input: path.resolve(__dirname, 'src/index.html')  // Новый путь
    }
  }
});