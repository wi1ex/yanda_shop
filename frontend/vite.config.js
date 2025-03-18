import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  root: __dirname,
  base: "/",
  publicDir: "public",
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: 'public/index.html'
    }
  }
});
