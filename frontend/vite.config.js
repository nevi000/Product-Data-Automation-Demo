import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The dev server proxies /api to the FastAPI backend so the frontend needs no
// base-URL configuration. Override the backend location with VITE_API_PROXY
// (e.g. VITE_API_PROXY=http://localhost:8001) when port 8000 is taken.
const target = process.env.VITE_API_PROXY || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target, changeOrigin: true },
    },
  },
})
