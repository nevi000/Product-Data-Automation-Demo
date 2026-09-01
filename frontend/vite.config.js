import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// dev server proxies /api to the FastAPI backend. Override with VITE_API_PROXY.
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
