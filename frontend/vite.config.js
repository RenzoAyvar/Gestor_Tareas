import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    proxy: {
      '/auth': {
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
      '/tasks': {
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: { environment: 'jsdom', setupFiles: ['./src/test/setup.js'], globals: true },
})
