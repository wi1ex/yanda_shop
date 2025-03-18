import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  root: "/frontend",
  publicDir: "public",
  resolve: {
    alias: {
      '@': '/frontend/src'
    }
  },
  optimizeDeps: {
    exclude: ["vue"]
  },
  build: {
    outDir: "dist",
    rollupOptions: {
      external: ["vue"],
      input: "/frontend/public/index.html"
    }
  }
});
