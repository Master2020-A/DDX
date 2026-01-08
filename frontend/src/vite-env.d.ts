/// <reference types="vite/client" />

import { Buffer } from 'buffer'
import process from 'process'

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  // Agrega más variables de entorno aquí según sea necesario
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare global {
  interface Window {
    Buffer: typeof Buffer
    process: typeof process
    global: Window
  }
}
