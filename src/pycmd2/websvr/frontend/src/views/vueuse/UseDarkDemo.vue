<template>
  <div class="dark-demo">
    <el-card header="useDark - 暗黑模式切换">
      <el-alert
        title="VueUse useDark 示例"
        type="info"
        :closable="false"
        description="轻松实现暗黑模式切换，支持系统主题自动检测和本地存储。"
        style="margin-bottom: 20px"
      />

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" class="control-card">
            <template #header>
              <div class="card-header">
                <el-icon><Sunny /></el-icon>
                <span>主题控制</span>
              </div>
            </template>

            <div class="theme-controls">
              <el-form label-width="120px">
                <el-form-item label="当前模式">
                  <el-tag :type="isDark ? 'info' : 'success'">
                    {{ isDark ? '暗黑模式' : '亮色模式' }}
                  </el-tag>
                </el-form-item>

                <el-form-item label="手动切换">
                  <el-switch
                    v-model="isDark"
                    size="large"
                    :active-icon="Moon"
                    :inactive-icon="Sunny"
                    @change="handleThemeChange"
                  />
                </el-form-item>

                <el-form-item label="切换方式">
                  <el-select v-model="transitionMode" style="width: 100%">
                    <el-option label="切换动画" value="toggle" />
                    <el-option label="淡入淡出" value="fade" />
                    <el-option label="无动画" value="none" />
                  </el-select>
                </el-form-item>

                <el-form-item>
                  <el-button @click="toggleDark" type="primary">
                    <el-icon><Refresh /></el-icon>
                    切换主题
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover" class="preview-card">
            <template #header>
              <div class="card-header">
                <el-icon><View /></el-icon>
                <span>主题预览</span>
              </div>
            </template>

            <div class="theme-preview">
              <div class="preview-section">
                <h4>颜色示例</h4>
                <el-row :gutter="10">
                  <el-col :span="6">
                    <div class="color-box primary">Primary</div>
                  </el-col>
                  <el-col :span="6">
                    <div class="color-box success">Success</div>
                  </el-col>
                  <el-col :span="6">
                    <div class="color-box warning">Warning</div>
                  </el-col>
                  <el-col :span="6">
                    <div class="color-box danger">Danger</div>
                  </el-col>
                </el-row>
              </div>

              <div class="preview-section">
                <h4>组件示例</h4>
                <el-space>
                  <el-button type="primary">主要按钮</el-button>
                  <el-button>默认按钮</el-button>
                  <el-button type="success">成功按钮</el-button>
                </el-space>
              </div>

              <div class="preview-section">
                <h4>表单示例</h4>
                <el-input placeholder="输入内容..." style="margin-bottom: 10px" />
                <el-input-number :min="1" :max="10" />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Setting /></el-icon>
                <span>系统信息</span>
              </div>
            </template>

            <el-descriptions :column="3" border>
              <el-descriptions-item label="系统暗黑模式">
                <el-tag :type="systemDark ? 'info' : 'success'">
                  {{ systemDark ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="存储键名">
                <el-tag>{{ storageKey }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="元素选择器">
                <el-tag>{{ selector }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="当前值">
                <el-tag :type="isDark ? 'info' : 'success'">
                  {{ isDark ? 'dark' : 'light' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="值类型">
                <el-tag type="warning">boolean</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="自定义样式">
                <el-tag :type="customStyle ? 'success' : 'info'">
                  {{ customStyle ? '已应用' : '未应用' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { useDark, useToggle, usePreferredDark } from '@vueuse/core'
  import { ref, computed } from 'vue'
  import { Sunny, Moon, Refresh, View, Setting } from '@element-plus/icons-vue'

  // 使用 useDark 来管理暗黑模式
  const isDark = useDark({
    selector: 'html',
    attribute: 'class',
    valueDark: 'dark',
    valueLight: 'light'
  })

  // 切换暗黑模式
  const toggleDark = useToggle(isDark)

  // 获取系统偏好
  const systemDark = usePreferredDark()

  // 切换模式
  const transitionMode = ref('toggle')

  // 配置信息
  const storageKey = ref('vueuse-color-scheme')
  const selector = ref('html')

  // 自定义样式状态
  const customStyle = computed(() => {
    return document.documentElement.classList.contains('dark') || document.documentElement.classList.contains('light')
  })

  // 主题切换处理
  const handleThemeChange = () => {
    if (transitionMode.value === 'fade') {
      document.documentElement.style.transition = 'background-color 0.3s ease'
      setTimeout(() => {
        document.documentElement.style.transition = ''
      }, 300)
    }
  }
</script>

<style scoped>
  .dark-demo {
    padding: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .control-card,
  .preview-card {
    height: 100%;
  }

  .theme-controls {
    padding: 10px 0;
  }

  .theme-preview {
    padding: 10px 0;
  }

  .preview-section {
    margin-bottom: 20px;
  }

  .preview-section h4 {
    margin-bottom: 10px;
    color: var(--el-text-color-primary);
  }

  .color-box {
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    border-radius: 4px;
    font-weight: bold;
    margin-bottom: 10px;
  }

  .color-box.primary {
    background-color: var(--el-color-primary);
  }

  .color-box.success {
    background-color: var(--el-color-success);
  }

  .color-box.warning {
    background-color: var(--el-color-warning);
  }

  .color-box.danger {
    background-color: var(--el-color-danger);
  }

  /* 暗黑模式自定义样式 */
  :global(.dark) .dark-demo {
    background-color: var(--el-bg-color-page);
  }

  :global(.dark) .color-box {
    opacity: 0.9;
  }

  :global(.dark) .color-box:hover {
    opacity: 1;
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .theme-controls,
    .theme-preview {
      padding: 5px 0;
    }

    .preview-section {
      margin-bottom: 15px;
    }
  }
</style>
