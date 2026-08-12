import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const assistant = mode === 'assistant'
  return {
    plugins: [react()],
    define: { 'import.meta.env.VITE_APP_MODE': JSON.stringify(assistant ? 'assistant' : 'dashboard') },
    server: { port: assistant ? 5174 : 5173 },
  }
})
