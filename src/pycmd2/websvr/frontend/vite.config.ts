import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import type { UserConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig(() => {
  const baseConfig: UserConfig = {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    build: {
      // 设置输出目录为 deploy
      outDir: 'deploy',
      // 优化的 chunk 分割策略 - 使用正则表达式配置
      rollupOptions: {
        output: {
          // 声明式 chunk 分割配置
          manualChunks: (id: string) => {
            // 非第三方库不分割
            if (!id.includes('node_modules')) {
              return undefined
            }

            // 使用正则表达式配置 - 更精确且易维护
            const chunkRules = [
              // Vue 生态系统 - 使用正则表达式避免复杂逻辑
              { name: 'vue-vendor', pattern: /(?:^|\/)node_modules\/(?:vue|@vueuse|pinia|vue-router)/ },

              // UI 组件库
              { name: 'ui-vendor', pattern: /(?:^|\/)node_modules\/element-plus/ },

              // 图表库
              { name: 'charts-vendor', pattern: /(?:^|\/)node_modules\/echarts/ },

              // 工具库
              { name: 'utils-vendor', pattern: /(?:^|\/)node_modules\/(?:lodash|dayjs|axios)/ }
            ]

            // 按优先级匹配 - 避免循环依赖问题
            for (const rule of chunkRules) {
              if (rule.pattern.test(id)) {
                return rule.name
              }
            }

            // 其他第三方库
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
