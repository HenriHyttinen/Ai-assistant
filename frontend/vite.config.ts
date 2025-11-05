import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react({
    typescript: {
      // Skip type checking during build (for Docker)
      check: false,
    },
  })],
  resolve: {
    dedupe: ['react', 'react-dom', '@emotion/react', '@emotion/styled'],
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify('http://localhost:8000'),
  },
})
