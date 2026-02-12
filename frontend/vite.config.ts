import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: "/erp/resumefilter/",
  server: {
    host: true, // Listen on all addresses for Docker
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true, // Enable polling for Docker file watching
    },
    proxy: {
      "/api": {
        target:
          process.env.DOCKER_ENV === "true"
            ? "http://backend:8000"
            : "http://localhost:8000",
        changeOrigin: true,
        // Removed rewrite - keep /api prefix when forwarding
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'http-vendor': ['axios'],
        },
      },
    },
    chunkSizeWarningLimit: 500,
  },
});
