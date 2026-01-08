import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // Polyfills para Node.js modules
      stream: 'stream-browserify',
      util: 'util/',
      buffer: 'buffer/',
      process: 'process/browser',
      events: 'events/',
    },
  },
  define: {
    global: 'globalThis',
    // Agregar process.env
    'process.env': {},
    'process.browser': true,
    'process.version': JSON.stringify(''),
  },
  optimizeDeps: {
    include: ['simple-peer', 'buffer', 'process'],
    esbuildOptions: {
      define: {
        global: 'globalThis',
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8612',
        changeOrigin: true,
      },
    },
  },
})