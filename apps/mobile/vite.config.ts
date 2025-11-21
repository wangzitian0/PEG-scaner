import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

const ROOT = path.resolve(__dirname, '../../');

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      'react-native': 'react-native-web',
      react: path.resolve(ROOT, 'node_modules/react'),
      'react-dom': path.resolve(ROOT, 'node_modules/react-dom'),
    },
  },
  define: {
    global: 'globalThis',
  },
  server: {
    host: '0.0.0.0',
    port: Number(process.env.MOBILE_WEB_PORT || 5173),
  },
});
