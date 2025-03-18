import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  root: "/frontend",
  publicDir: "public",
  base: "/",
  build: {
    outDir: "dist",
    rollupOptions: {
      input: "/frontend/public/index.html"
    }
  }
});
