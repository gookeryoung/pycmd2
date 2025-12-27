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
          // 优化的 chunk 分割策略 - 使用映射配置替代分支检测
          manualChunks: (id: string) => {
            // 非第三方库不分割
            if (!id.includes('node_modules')) {
              return undefined
            }

            // 包名到 chunk 的映射配置
            const chunkMapping: Record<string, string[]> = {
              'vue-core': ['vue'], // 核心 Vue 库
              vueuse: ['@vueuse'], // VueUse 工具库
              'element-plus': ['element-plus'], // UI 组件库
              charts: ['echarts'], // 图表库
              utils: ['lodash', 'dayjs', 'axios'] // 工具库
            }

            // 遍历映射配置，检查包名匹配
            for (const [chunkName, packages] of Object.entries(chunkMapping)) {
              // 检查是否匹配当前 chunk 的任何包名
              const matchesPackage = packages.some(pkg => id.includes(pkg))

              // 特殊处理：vue-core 需要排除 vue 生态系统中的其他包
              if (chunkName === 'vue-core' && matchesPackage) {
                const isVueEcosystem =
                  chunkMapping['vueuse'].some(pkg => id.includes(pkg)) ||
                  chunkMapping['element-plus'].some(pkg => id.includes(pkg))
                if (!isVueEcosystem) {
                  return chunkName
                }
              } else if (matchesPackage) {
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
      cssCodeSplit: true,
      // 使用 esbuild 进行压缩（Vite 默认，更快且无需额外依赖）
      minify: 'esbuild'
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
