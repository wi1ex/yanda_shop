import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  base: "/",
  publicDir: "public",
  build: {
    outDir: "dist",
    rollupOptions: {
      input: "index.html"
    }
  }
});
