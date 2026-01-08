import { Buffer } from 'buffer'
import process from 'process'

// Polyfills globales para librerías de Node.js
window.Buffer = Buffer
window.process = process
window.global = window