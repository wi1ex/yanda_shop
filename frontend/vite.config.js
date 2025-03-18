import { defineConfig } from 'vite';

export default defineConfig({
  root: "/frontend",
  publicDir: "public",
  resolve: {
    alias: {
      '@': '/frontend/src'
    }
  },
  build: {
    outDir: "dist",
    rollupOptions: {
      input: "/frontend/public/index.html"
    }
  }
});
