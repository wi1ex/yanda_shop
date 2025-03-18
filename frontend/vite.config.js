import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  root: "./",
  publicDir: "public",
  build: {
    outDir: "dist",
    rollupOptions: {
      input: path.resolve(__dirname, "public/index.html")
    }
  }
});
