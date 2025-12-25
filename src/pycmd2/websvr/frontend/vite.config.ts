import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    // 设置输出目录为 output
    outDir: 'output',
  },
  server: {
    host: '0.0.0.0', // 允许从任何IP地址访问
    port: 5173,
    // 启用 CORS 以便 WebView 可以访问
    cors: true,
    // 监听文件变化
    watch: {
      usePolling: true,
      interval: 100,
    },
  },
})
