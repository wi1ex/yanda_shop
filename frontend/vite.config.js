import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  root: "/frontend",
  publicDir: "public",
  base: "/",
  build: {
    outDir: "dist",
    manifest: true,
    rollupOptions: {
      input: "/frontend/public/index.html"
    }
  }
});
