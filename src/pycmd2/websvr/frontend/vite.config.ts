import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  const isAnalyze = mode === 'analyze'

  const baseConfig: any = {
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
          // 手动分割第三方库
          manualChunks: id => {
            // 第三方库分组策略
            if (id.includes('node_modules')) {
              // Vue 生态系统
              if (id.includes('vue') || id.includes('vue-router') || id.includes('pinia')) {
                return 'vue-vendor'
              }

              // Element Plus UI 库
              if (id.includes('element-plus') || id.includes('@element-plus')) {
                return 'element-plus'
              }

              // 图表库
              if (id.includes('echarts') || id.includes('vue-echarts')) {
                return 'charts'
              }

              // VueUse 工具库
              if (id.includes('@vueuse')) {
                return 'vueuse'
              }

              // 其他工具库
              if (id.includes('lodash') || id.includes('dayjs') || id.includes('axios')) {
                return 'utils'
              }

              // 其他第三方库
              return 'vendor'
            }
          },
          // 优化 chunk 命名
          chunkFileNames: chunkInfo => {
            const facadeModuleId = chunkInfo.facadeModuleId
            if (facadeModuleId) {
              const fileName = facadeModuleId.split('/').pop() || 'chunk'
              return `js/${fileName}-[hash].js`
            }
            return 'js/[name]-[hash].js'
          },
          // 静态资源命名
          assetFileNames: assetInfo => {
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

  // 如果是分析模式，添加打包分析插件
  if (isAnalyze && baseConfig.plugins) {
    // 安装: npm install --save-dev rollup-plugin-visualizer
    // 然后取消下面注释:
    // import { visualizer } from 'rollup-plugin-visualizer'
    // baseConfig.plugins.push(visualizer({
    //   filename: 'output/stats.html',
    //   open: true,
    //   gzipSize: true,
    //   brotliSize: true
    // }))
  }

  return baseConfig
})
