<template>
  <div class="todo-api-app">
    <el-card class="todo-container" shadow="always">
      <template #header>
        <div class="card-header">
          <h2>📕 待办事项</h2>
          <div class="header-actions">
            <el-tag :type="apiStore.connectionStatus.connected ? 'success' : 'danger'">
              {{ apiStore.connectionStatus.status }}
            </el-tag>
            <el-button @click="checkConnection" :icon="Refresh" size="small" :loading="apiStore.loading">
              连接
            </el-button>
          </div>
        </div>
      </template>

      <!-- 连接状态提示 -->
      <div v-if="!apiStore.connectionStatus.connected" class="connection-warning">
        <el-alert
          title="API未连接"
          description="请确保FastAPI服务器正在运行 (http://127.0.0.1:8001)，然后点击连接按钮"
          type="warning"
          :closable="false"
          show-icon
        />
      </div>

      <!-- API统计信息 -->
      <div v-if="apiStore.connectionStatus.connected" class="api-stats">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="总数">
            <el-tag type="info">{{ apiStore.totalCount }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="已完成">
            <el-tag type="success">{{ apiStore.completedCount }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="待完成">
            <el-tag type="warning">{{ apiStore.pendingCount }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="完成率" span="3">
            <el-progress :percentage="apiStore.completionPercentage" :color="progressColor" :stroke-width="6" />
          </el-descriptions-item>
          <el-descriptions-item label="最后同步" span="3">
            {{ formatTime(apiStore.lastSyncTime) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 添加新待办事项 -->
      <div class="add-todo-section">
        <el-input
          v-model="newTodoText"
          placeholder="添加新的待办事项..."
          @keyup.enter="addTodo"
          clearable
          size="large"
          :disabled="!apiStore.connectionStatus.connected"
        >
          <template #append>
            <el-button
              type="primary"
              @click="addTodo"
              :disabled="!newTodoText.trim() || !apiStore.connectionStatus.connected"
              :loading="apiStore.loading"
            >
              <el-icon>
                <Plus />
              </el-icon>
              添加
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 过滤选项 -->
      <div class="filter-section">
        <el-radio-group
          v-model="currentFilter"
          @change="handleFilterChange"
          class="filter-group"
          :disabled="!apiStore.connectionStatus.connected"
        >
          <el-radio-button label="all"> 全部 ({{ filteredTodos.length }}) </el-radio-button>
          <el-radio-button label="pending"> 待完成 ({{ apiStore.pendingCount }}) </el-radio-button>
          <el-radio-button label="completed"> 已完成 ({{ apiStore.completedCount }}) </el-radio-button>
        </el-radio-group>

        <div class="search-section">
          <el-input
            v-model="searchQuery"
            placeholder="搜索待办事项..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
            :disabled="!apiStore.connectionStatus.connected"
          />
        </div>
      </div>

      <el-divider />

      <!-- 加载状态 -->
      <div v-if="apiStore.loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>

      <!-- 错误提示 -->
      <div v-else-if="apiStore.error" class="error-container">
        <el-alert :title="apiStore.error" type="error" :closable="false" show-icon />
      </div>

      <!-- 待办事项列表 -->
      <div v-else class="todo-list-container">
        <el-empty v-if="filteredTodos.length === 0" description="暂无待办事项">
          <el-button type="primary" @click="addSampleTodos" :disabled="!apiStore.connectionStatus.connected">
            添加示例待办事项
          </el-button>
        </el-empty>

        <div v-else class="todo-list">
          <transition-group name="todo-list" tag="div">
            <div v-for="todo in filteredTodos" :key="todo.id" class="todo-item">
              <el-card shadow="hover" class="todo-card" :class="{ completed: todo.completed }">
                <div class="todo-content">
                  <el-checkbox
                    :model-value="todo.completed"
                    @change="toggleTodo(todo.id)"
                    size="large"
                    :disabled="!apiStore.connectionStatus.connected"
                  />

                  <div class="todo-text-container">
                    <p class="todo-text" :class="{ completed: todo.completed }">
                      {{ todo.text }}
                    </p>
                    <div class="todo-meta">
                      <el-tag size="small" :type="todo.completed ? 'success' : 'info'">
                        {{ todo.completed ? '已完成' : '待完成' }}
                      </el-tag>
                      <span class="todo-id">ID: {{ todo.id }}</span>
                      <span class="created-time">
                        {{ formatTime(todo.createdAt) }}
                      </span>
                    </div>
                  </div>

                  <div class="todo-actions">
                    <el-button
                      type="primary"
                      size="small"
                      @click="startEditTodo(todo)"
                      :icon="Edit"
                      circle
                      :disabled="!apiStore.connectionStatus.connected"
                    />
                    <el-button
                      type="danger"
                      size="small"
                      @click="confirmRemoveTodo(todo)"
                      :icon="Delete"
                      circle
                      :disabled="!apiStore.connectionStatus.connected"
                    />
                  </div>
                </div>
              </el-card>
            </div>
          </transition-group>
        </div>

        <!-- 批量操作 -->
        <div v-if="filteredTodos.length > 0" class="bulk-actions">
          <el-button
            type="success"
            @click="markAllCompleted"
            :disabled="apiStore.pendingCount === 0 || !apiStore.connectionStatus.connected"
          >
            <el-icon>
              <Check />
            </el-icon>
            全部完成
          </el-button>

          <el-button
            type="warning"
            @click="clearCompleted"
            :disabled="apiStore.completedCount === 0 || !apiStore.connectionStatus.connected"
          >
            <el-icon>
              <Delete />
            </el-icon>
            清除已完成
          </el-button>

          <el-button type="info" @click="refreshTodos" :icon="Refresh" :disabled="!apiStore.connectionStatus.connected">
            刷新
          </el-button>

          <el-button
            type="danger"
            @click="confirmClearAllData"
            :icon="Delete"
            :disabled="!apiStore.connectionStatus.connected"
          >
            清除所有数据
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑待办事项" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="内容">
          <el-input v-model="editForm.text" placeholder="请输入待办事项内容" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="editForm.completed" active-text="已完成" inactive-text="待完成" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="apiStore.loading"> 保存 </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useTodoApiStore } from '@/stores/todoApi'
  import type { Todo } from '@/services/todoApi'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Plus, Delete, Refresh, Search, Edit, Check } from '@element-plus/icons-vue'

  const apiStore = useTodoApiStore()
  const newTodoText = ref('')
  const currentFilter = ref<'all' | 'completed' | 'pending'>('all')
  const searchQuery = ref('')
  const editDialogVisible = ref(false)
  const editForm = ref({
    id: 0,
    text: '',
    completed: false
  })

  // 过滤后的待办事项
  const filteredTodos = computed(() => {
    let todos = apiStore.todos

    // 应用搜索过滤
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase().trim()
      todos = todos.filter(todo => todo.text.toLowerCase().includes(query))
    }

    // 应用状态过滤
    switch (currentFilter.value) {
      case 'completed':
        return todos.filter(todo => todo.completed)
      case 'pending':
        return todos.filter(todo => !todo.completed)
      default:
        return todos
    }
  })

  // 进度条颜色
  const progressColor = computed(() => {
    const percentage = apiStore.completionPercentage
    if (percentage === 100) return '#67c23a'
    if (percentage >= 50) return '#409eff'
    return '#e6a23c'
  })

  onMounted(() => {
    checkConnection()
  })

  // 检查API连接
  const checkConnection = async () => {
    const connected = await apiStore.checkConnection()
    if (connected) {
      await apiStore.fetchTodos()
    }
  }

  // 添加待办事项
  const addTodo = () => {
    if (newTodoText.value.trim()) {
      apiStore.addTodo(newTodoText.value)
      newTodoText.value = ''
    }
  }

  // 切换待办事项状态
  const toggleTodo = (id: number) => {
    apiStore.toggleTodo(id)
  }

  // 开始编辑待办事项
  const startEditTodo = (todo: Todo) => {
    editForm.value = {
      id: todo.id,
      text: todo.text,
      completed: todo.completed
    }
    editDialogVisible.value = true
  }

  // 保存编辑
  const saveEdit = () => {
    if (!editForm.value.text.trim()) {
      ElMessage.error('待办事项内容不能为空')
      return
    }

    apiStore.updateTodo(editForm.value.id, {
      text: editForm.value.text.trim(),
      completed: editForm.value.completed
    })

    editDialogVisible.value = false
  }

  // 确认删除待办事项
  const confirmRemoveTodo = (todo: Todo) => {
    ElMessageBox.confirm(`确定要删除待办事项"${todo.text}"吗?`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(() => {
        apiStore.removeTodo(todo.id)
      })
      .catch(() => {
        // 用户取消删除
      })
  }

  // 标记所有为完成
  const markAllCompleted = () => {
    apiStore.markAllCompleted()
  }

  // 清除已完成的待办事项
  const clearCompleted = () => {
    if (apiStore.completedCount === 0) return

    ElMessageBox.confirm(`确定要清除所有已完成的 ${apiStore.completedCount} 项待办事项吗?`, '确认清除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(() => {
        apiStore.clearCompleted()
      })
      .catch(() => {
        // 用户取消清除
      })
  }

  // 刷新数据
  const refreshTodos = () => {
    apiStore.refresh()
  }

  // 添加示例待办事项
  const addSampleTodos = () => {
    const sampleTodos = [
      '学习 FastAPI 基础知识',
      '创建 RESTful API',
      '实现前后端分离',
      '测试 API 接口',
      '部署应用到服务器'
    ]

    sampleTodos.forEach(text => {
      apiStore.addTodo(text)
    })
  }

  // 确认清除所有数据
  const confirmClearAllData = () => {
    ElMessageBox.confirm('确定要清除所有待办事项数据吗？此操作不可恢复！', '危险操作', {
      confirmButtonText: '确定清除',
      cancelButtonText: '取消',
      type: 'error'
    })
      .then(() => {
        apiStore.clearAllData()
      })
      .catch(() => {
        // 用户取消清除
      })
  }

  // 处理过滤变化
  const handleFilterChange = () => {
    // 过滤逻辑已在 computed 中处理
  }

  // 处理搜索
  const handleSearch = () => {
    // 搜索逻辑已在 computed 中处理
  }

  // 格式化时间
  const formatTime = (date: Date | string | null) => {
    if (!date) return '未知'

    const dateObj = typeof date === 'string' ? new Date(date) : date
    if (isNaN(dateObj.getTime())) return '无效时间'

    const now = new Date()
    const diff = now.getTime() - dateObj.getTime()
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`

    return dateObj.toLocaleString('zh-CN')
  }
</script>

<style scoped>
  .todo-api-app {
    padding: 20px;
    max-width: 1000px;
    margin: 0 auto;
  }

  .todo-container {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .card-header h2 {
    margin: 0;
    color: #303133;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .connection-warning {
    margin-bottom: 20px;
  }

  .api-stats {
    margin-bottom: 20px;
  }

  .add-todo-section {
    margin-bottom: 24px;
  }

  .filter-section {
    margin: 20px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }

  .filter-group {
    flex-grow: 1;
    min-width: 300px;
  }

  .search-section {
    width: 200px;
  }

  .loading-container,
  .error-container {
    margin: 20px 0;
  }

  .todo-list-container {
    margin: 20px 0;
  }

  .todo-list {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 8px;
  }

  .todo-item {
    margin-bottom: 12px;
  }

  .todo-card {
    transition: all 0.3s ease;
    border-left: 4px solid #409eff;
  }

  .todo-card.completed {
    border-left-color: #67c23a;
    opacity: 0.8;
  }

  .todo-content {
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }

  .todo-text-container {
    flex-grow: 1;
  }

  .todo-text {
    margin: 0 0 8px 0;
    font-size: 16px;
    line-height: 1.5;
    word-break: break-word;
  }

  .todo-text.completed {
    text-decoration: line-through;
    color: #909399;
  }

  .todo-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px;
    color: #909399;
  }

  .todo-id {
    color: #606266;
    font-family: monospace;
  }

  .todo-actions {
    flex-shrink: 0;
    display: flex;
    gap: 8px;
  }

  .bulk-actions {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  /* 列表动画 */
  .todo-list-enter-active,
  .todo-list-leave-active {
    transition: all 0.3s ease;
  }

  .todo-list-enter-from,
  .todo-list-leave-to {
    opacity: 0;
    transform: translateX(30px);
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .todo-api-app {
      padding: 10px;
    }

    .filter-section {
      flex-direction: column;
      align-items: stretch;
    }

    .filter-group {
      min-width: auto;
    }

    .search-section {
      width: 100%;
    }

    .todo-content {
      flex-direction: column;
      align-items: flex-start;
    }

    .todo-actions {
      margin-top: 10px;
      align-self: flex-end;
    }

    .todo-meta {
      flex-direction: column;
      align-items: flex-start;
      gap: 6px;
    }

    .bulk-actions {
      flex-direction: column;
    }

    .header-actions {
      flex-direction: column;
      gap: 8px;
    }
  }

  /* 滚动条样式 */
  .todo-list::-webkit-scrollbar {
    width: 6px;
  }

  .todo-list::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  .todo-list::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }

  .todo-list::-webkit-scrollbar-thumb:hover {
    background: #a1a1a1;
  }
</style>
