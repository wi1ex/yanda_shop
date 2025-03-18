import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  root: "/frontend",
  publicDir: "public",
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: "dist",
    rollupOptions: {
      input: "/frontend/public/index.html"
    }
  }
});
