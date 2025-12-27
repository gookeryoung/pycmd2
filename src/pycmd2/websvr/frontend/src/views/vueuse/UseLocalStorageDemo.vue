<template>
  <div class="localstorage-demo">
    <el-card header="useLocalStorage - 本地存储">
      <el-alert
        title="VueUse useLocalStorage 示例"
        type="info"
        :closable="false"
        description="响应式地使用 localStorage，支持自动序列化和反序列化。"
        style="margin-bottom: 20px"
      />

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" class="storage-card">
            <template #header>
              <div class="card-header">
                <el-icon><FolderOpened /></el-icon>
                <span>用户设置存储</span>
              </div>
            </template>

            <div class="settings-form">
              <el-form :model="userSettings" label-width="100px">
                <el-form-item label="用户名">
                  <el-input v-model="userSettings.username" placeholder="请输入用户名" />
                </el-form-item>

                <el-form-item label="主题">
                  <el-select v-model="userSettings.theme" style="width: 100%">
                    <el-option label="亮色" value="light" />
                    <el-option label="暗黑" value="dark" />
                    <el-option label="自动" value="auto" />
                  </el-select>
                </el-form-item>

                <el-form-item label="语言">
                  <el-select v-model="userSettings.language" style="width: 100%">
                    <el-option label="中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                  </el-select>
                </el-form-item>

                <el-form-item label="通知">
                  <el-switch v-model="userSettings.notifications" />
                </el-form-item>

                <el-form-item label="自动保存">
                  <el-switch v-model="userSettings.autoSave" />
                </el-form-item>
              </el-form>

              <div class="form-actions">
                <el-button @click="resetSettings">重置设置</el-button>
                <el-button @click="exportSettings" type="primary">导出设置</el-button>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover" class="storage-card">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>实时数据预览</span>
              </div>
            </template>

            <div class="data-preview">
              <div class="preview-section">
                <h4>当前设置值:</h4>
                <pre class="json-preview">{{ JSON.stringify(userSettings, null, 2) }}</pre>
              </div>

              <el-divider />

              <div class="storage-info">
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="存储键名">
                    <el-tag>{{ storageKey }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="数据大小">
                    <el-tag>{{ formatBytes(JSON.stringify(userSettings).length) }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="最后更新">
                    <el-tag type="success">{{ lastUpdated || '从未更新' }}</el-tag>
                  </el-descriptions-item>
                </el-descriptions>
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
                <el-icon><List /></el-icon>
                <span>待办事项列表</span>
              </div>
            </template>

            <div class="todo-section">
              <div class="todo-input">
                <el-input v-model="newTodo" placeholder="添加新待办事项..." @keyup.enter="addTodo">
                  <template #append>
                    <el-button @click="addTodo" :disabled="!newTodo.trim()">
                      <el-icon><Plus /></el-icon>
                      添加
                    </el-button>
                  </template>
                </el-input>
              </div>

              <div class="todo-list">
                <el-empty v-if="todos.length === 0" description="暂无待办事项" />
                <el-checkbox-group v-model="completedTodos" v-else>
                  <div v-for="(todo, index) in todos" :key="todo.id" class="todo-item">
                    <el-checkbox :label="todo.id">
                      <span :class="{ completed: todo.completed }">{{ todo.text }}</span>
                      <el-tag size="small" :type="todo.completed ? 'success' : 'info'" class="todo-tag">
                        {{ todo.completed ? '已完成' : '待完成' }}
                      </el-tag>
                    </el-checkbox>
                    <el-button size="small" type="danger" @click="removeTodo(index)" circle :icon="Delete" />
                  </div>
                </el-checkbox-group>
              </div>

              <div class="todo-stats">
                <el-statistic title="总任务" :value="todos.length" />
                <el-statistic title="已完成" :value="completedCount" value-style="color: #67c23a" />
                <el-statistic title="待完成" :value="pendingCount" value-style="color: #f56c6c" />
                <el-button @click="clearCompleted" size="small">清除已完成</el-button>
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
                <el-icon><Operation /></el-icon>
                <span>存储管理</span>
              </div>
            </template>

            <div class="storage-management">
              <el-space>
                <el-button @click="refreshStorage">
                  <el-icon><Refresh /></el-icon>
                  刷新存储
                </el-button>

                <el-button @click="showImportDialog = true" type="primary">
                  <el-icon><Upload /></el-icon>
                  导入数据
                </el-button>

                <el-button @click="clearAllStorage" type="danger">
                  <el-icon><Delete /></el-icon>
                  清除所有
                </el-button>
              </el-space>

              <div class="storage-keys">
                <h4>当前存储的键:</h4>
                <el-tag v-for="key in storageKeys" :key="key" closable @close="removeStorageKey(key)" class="key-tag">
                  {{ key }}
                </el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入数据" width="500px">
      <el-input v-model="importData" type="textarea" :rows="10" placeholder="粘贴 JSON 数据..." />
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button @click="importSettings" type="primary">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { useLocalStorage } from '@vueuse/core'
  import { ref, computed, onMounted } from 'vue'
  import { FolderOpened, Document, List, Plus, Delete, Refresh, Upload, Operation } from '@element-plus/icons-vue'
  import { ElMessage } from 'element-plus'

  // 用户设置类型定义
  interface UserSettings {
    username: string
    theme: 'light' | 'dark' | 'auto'
    language: 'zh-CN' | 'en-US'
    notifications: boolean
    autoSave: boolean
  }

  // 待办事项类型定义
  interface Todo {
    id: number
    text: string
    completed: boolean
    createdAt: string
  }

  // 存储键名
  const storageKey = ref('vueuse-demo-settings')

  // 使用 useLocalStorage 存储用户设置
  const userSettings = useLocalStorage<UserSettings>(storageKey.value, {
    username: '',
    theme: 'light',
    language: 'zh-CN',
    notifications: true,
    autoSave: true
  })

  // 使用 useLocalStorage 存储待办事项
  const todos = useLocalStorage<Todo[]>('vueuse-demo-todos', [])

  // 待办相关状态
  const newTodo = ref('')
  const completedTodos = ref<number[]>([])

  // 存储管理相关
  const storageKeys = ref<string[]>([])
  const lastUpdated = ref('')
  const showImportDialog = ref(false)
  const importData = ref('')

  // 计算属性
  const completedCount = computed(() => todos.value.filter(todo => todo.completed).length)
  const pendingCount = computed(() => todos.value.filter(todo => !todo.completed).length)

  // 格式化字节数
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 重置设置
  const resetSettings = () => {
    userSettings.value = {
      username: '',
      theme: 'light',
      language: 'zh-CN',
      notifications: true,
      autoSave: true
    }
    updateLastUpdated()
  }

  // 导出设置
  const exportSettings = () => {
    const data = JSON.stringify(userSettings.value, null, 2)
    navigator.clipboard.writeText(data).then(() => {
      ElMessage.success('设置已复制到剪贴板')
    })
  }

  // 导入设置
  const importSettings = () => {
    try {
      const data = JSON.parse(importData.value)
      Object.assign(userSettings.value, data)
      showImportDialog.value = false
      importData.value = ''
      updateLastUpdated()
      ElMessage.success('设置导入成功')
    } catch (error) {
      ElMessage.error('数据格式错误: ' + JSON.stringify(error))
    }
  }

  // 添加待办事项
  const addTodo = () => {
    if (newTodo.value.trim()) {
      todos.value.push({
        id: Date.now(),
        text: newTodo.value.trim(),
        completed: false,
        createdAt: new Date().toISOString()
      })
      newTodo.value = ''
    }
  }

  // 删除待办事项
  const removeTodo = (index: number) => {
    todos.value.splice(index, 1)
  }

  // 清除已完成的待办事项
  const clearCompleted = () => {
    todos.value = todos.value.filter(todo => !todo.completed)
  }

  // 更新最后更新时间
  const updateLastUpdated = () => {
    lastUpdated.value = new Date().toLocaleString()
  }

  // 刷新存储键列表
  const refreshStorage = () => {
    const keys: string[] = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith('vueuse-demo-')) {
        keys.push(key)
      }
    }
    storageKeys.value = keys
  }

  // 移除存储键
  const removeStorageKey = (key: string) => {
    localStorage.removeItem(key)
    refreshStorage()
  }

  // 清除所有存储
  const clearAllStorage = () => {
    storageKeys.value.forEach(key => localStorage.removeItem(key))
    refreshStorage()
  }

  // 监听设置变化
  const unwatchSettings = computed(() => {
    return userSettings.value
  })

  // 监听设置变化，更新时间
  import { watch } from 'vue'
  watch(
    unwatchSettings,
    () => {
      updateLastUpdated()
    },
    { deep: true }
  )

  // 初始化
  onMounted(() => {
    refreshStorage()
    updateLastUpdated()
  })
</script>

<style scoped>
  .localstorage-demo {
    padding: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .storage-card {
    height: 100%;
  }

  .settings-form {
    padding: 10px 0;
  }

  .form-actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
  }

  .data-preview {
    padding: 10px 0;
  }

  .preview-section {
    margin-bottom: 20px;
  }

  .preview-section h4 {
    margin-bottom: 10px;
  }

  .json-preview {
    background: var(--el-fill-color-lighter);
    padding: 15px;
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    max-height: 200px;
    overflow-y: auto;
  }

  .storage-info {
    margin-top: 15px;
  }

  .todo-section {
    padding: 20px 0;
  }

  .todo-input {
    margin-bottom: 20px;
  }

  .todo-list {
    margin-bottom: 20px;
    max-height: 300px;
    overflow-y: auto;
  }

  .todo-item {
    display: flex;
    align-items: center;
    padding: 10px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    margin-bottom: 10px;
    transition: all 0.3s ease;
  }

  .todo-item:hover {
    background: var(--el-fill-color-lighter);
  }

  .todo-item .el-checkbox {
    flex-grow: 1;
  }

  .completed {
    text-decoration: line-through;
    color: var(--el-text-color-placeholder);
  }

  .todo-tag {
    margin-left: 10px;
  }

  .todo-stats {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 15px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
  }

  .storage-management {
    padding: 20px 0;
  }

  .storage-keys {
    margin-top: 20px;
  }

  .storage-keys h4 {
    margin-bottom: 10px;
  }

  .key-tag {
    margin: 5px;
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .todo-stats {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }

    .todo-item {
      flex-direction: column;
      align-items: flex-start;
    }

    .todo-tag {
      margin-left: 0;
      margin-top: 5px;
    }
  }
</style>
