import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  root: "/frontend",
  publicDir: "public",
  resolve: {
    alias: {
      '@': '/frontend/src',
    },
  },
  build: {
    outDir: "dist",
    rollupOptions: {
      input: "/frontend/index.html",
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "/frontend/src/styles/_variables.scss";`,
      },
    },
  },
});
