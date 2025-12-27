import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import type { UserConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  const isAnalyze = mode === 'analyze'

  const baseConfig: UserConfig = {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    build: {
      // 设置输出目录为 output
      outDir: 'output',
      // 优化 chunk 分割
      rollupOptions: {
        output: {
          // 优化的手动分割第三方库 - 使用映射表提高性能
          manualChunks: (id: string) => {
            // 非第三方库不分割，返回 undefined 让 Rollup 处理
            if (!id.includes('node_modules')) {
              return undefined
            }

            // 高效的映射表匹配 - O(n) 时间复杂度
            const chunkMapping: Record<string, string> = {
              vue: 'vue-vendor',
              'vue-router': 'vue-vendor',
              pinia: 'vue-vendor',
              'element-plus': 'element-plus',
              '@element-plus': 'element-plus',
              echarts: 'charts',
              'vue-echarts': 'charts',
              '@vueuse': 'vueuse'
              // 'lodash': 'utils',
              // 'dayjs': 'utils',
              // 'axios': 'utils'
            }

            // 使用 for...of 循环进行高效匹配
            for (const [key, chunkName] of Object.entries(chunkMapping)) {
              if (id.includes(key)) {
                return chunkName
              }
            }

            // 其他第三方库归类
            return 'vendor'
          },
          // 优化 chunk 命名
          chunkFileNames: (chunkInfo: { facadeModuleId?: string }) => {
            const facadeModuleId = chunkInfo.facadeModuleId
            if (facadeModuleId) {
              const fileName = facadeModuleId.split('/').pop() || 'chunk'
              return `js/${fileName}-[hash].js`
            }
            return 'js/[name]-[hash].js'
          },
          // 静态资源命名
          assetFileNames: (assetInfo: { name?: string }) => {
            const info = assetInfo.name?.split('.') || []
            const extType = info[info.length - 1] || ''
            if (/\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/i.test(assetInfo.name || '')) {
              return `media/[name]-[hash][extname]`
            }
            if (/\.(png|jpe?g|gif|svg)(\?.*)?$/i.test(assetInfo.name || '')) {
              return `images/[name]-[hash][extname]`
            }
            if (/\.(woff2?|eot|ttf|otf)(\?.*)?$/i.test(assetInfo.name || '')) {
              return `fonts/[name]-[hash][extname]`
            }
            return `assets/[name]-[hash][extname]`
          }
        }
      },
      // 设置 chunk 大小警告限制
      chunkSizeWarningLimit: 1000,
      // 启用 CSS 代码分割
      cssCodeSplit: true
    },
    server: {
      host: '0.0.0.0', // 允许从任何IP地址访问
      port: 5173,
      // 启用 CORS 以便 WebView 可以访问
      cors: true,
      // 监听文件变化
      watch: {
        usePolling: true,
        interval: 100
      }
    }
  }

  return baseConfig
})
