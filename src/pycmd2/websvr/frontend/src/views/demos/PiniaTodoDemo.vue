<template>
  <div class="pinia-todo-demo">
    <el-card header="待办事项管理示例 - Todo Store">
      <div class="todo-section">
        <div class="add-todo">
          <el-input v-model="newTodo" placeholder="添加新的待办事项..." @keyup.enter="addTodo" clearable>
            <template #append>
              <el-button type="primary" @click="addTodo">
                <el-icon>
                  <Plus />
                </el-icon>
                添加
              </el-button>
            </template>
          </el-input>
        </div>

        <div class="filters">
          <el-radio-group v-model="todosStore.filter" @change="onFilterChange">
            <el-radio-button label="all">全部 ({{ todosStore.totalCount }})</el-radio-button>
            <el-radio-button label="pending"> 待完成 ({{ todosStore.pendingCount }}) </el-radio-button>
            <el-radio-button label="completed"> 已完成 ({{ todosStore.completedCount }}) </el-radio-button>
          </el-radio-group>
        </div>

        <div class="progress-section">
          <el-progress :percentage="todosStore.completionPercentage" :color="getProgressColor" />
          <div class="progress-text">完成进度: {{ todosStore.completedCount }} / {{ todosStore.totalCount }}</div>
        </div>

        <el-divider />

        <div class="loading-section" v-if="todosStore.loading">
          <el-skeleton :rows="3" animated />
        </div>

        <div class="error-section" v-if="todosStore.error">
          <el-alert :title="todosStore.error" type="error" :closable="false" />
        </div>

        <div class="todo-list" v-if="!todosStore.loading && !todosStore.error">
          <el-empty v-if="filteredTodos.length === 0" description="暂无待办事项" />

          <el-checkbox-group v-model="selectedTodos" v-else>
            <div v-for="todo in filteredTodos" :key="todo.id" class="todo-item">
              <el-card shadow="hover" class="todo-card">
                <div class="todo-content">
                  <el-checkbox :model-value="todo.completed" @change="toggleTodo(todo.id)" :label="todo.id">
                    <span :class="{ completed: todo.completed }" class="todo-text">
                      {{ todo.text }}
                    </span>
                  </el-checkbox>

                  <div class="todo-actions">
                    <el-button type="danger" size="small" @click="removeTodo(todo.id)" :icon="Delete" circle />
                  </div>
                </div>

                <div class="todo-meta">
                  <el-tag size="small" :type="todo.completed ? 'success' : 'info'">
                    {{ todo.completed ? '已完成' : '待完成' }}
                  </el-tag>
                  <span class="created-time"> 创建于: {{ formatTime(todo.createdAt) }} </span>
                </div>
              </el-card>
            </div>
          </el-checkbox-group>
        </div>

        <div class="bulk-actions" v-if="filteredTodos.length > 0">
          <el-button type="warning" @click="clearCompleted" :disabled="todosStore.completedCount === 0">
            <el-icon>
              <Delete />
            </el-icon>
            清除已完成
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card header="Store 状态查看" class="state-view">
      <el-collapse>
        <el-collapse-item title="完整状态" name="state">
          <pre>{{ JSON.stringify(todosStore.$state, null, 2) }}</pre>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useTodosStore } from '@/stores/todos'
  import { ElMessage } from 'element-plus'
  import { Plus, Delete } from '@element-plus/icons-vue'

  const todosStore = useTodosStore()
  const newTodo = ref('')
  const selectedTodos = ref<number[]>([])

  // 使用 store 的 getter
  const filteredTodos = computed(() => todosStore.filteredTodos)

  // 根据完成度设置进度条颜色
  const getProgressColor = computed(() => {
    const percentage = todosStore.completionPercentage
    if (percentage === 100) return '#67c23a'
    if (percentage >= 50) return '#409eff'
    return '#e6a23c'
  })

  onMounted(() => {
    // 初始化时获取待办事项
    todosStore.fetchTodos()
  })

  const addTodo = () => {
    if (newTodo.value.trim()) {
      todosStore.addTodo(newTodo.value)
      newTodo.value = ''
      ElMessage.success('待办事项已添加')
    }
  }

  const toggleTodo = (id: number) => {
    todosStore.toggleTodo(id)
  }

  const removeTodo = (id: number) => {
    todosStore.removeTodo(id)
    ElMessage.success('待办事项已删除')
  }

  const clearCompleted = () => {
    todosStore.clearCompleted()
    selectedTodos.value = []
    ElMessage.success('已完成的待办事项已清除')
  }

  const onFilterChange = () => {
    selectedTodos.value = []
  }

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }
</script>

<style scoped>
  .pinia-todo-demo {
    padding: 20px;
  }

  .todo-section {
    margin-bottom: 20px;
  }

  .add-todo {
    margin-bottom: 20px;
  }

  .filters {
    margin: 20px 0;
    text-align: center;
  }

  .progress-section {
    margin: 20px 0;
    text-align: center;
  }

  .progress-text {
    margin-top: 10px;
    font-size: 14px;
    color: #606266;
  }

  .loading-section,
  .error-section {
    margin: 20px 0;
  }

  .todo-list {
    margin: 20px 0;
    max-height: 400px;
    overflow-y: auto;
  }

  .todo-item {
    margin-bottom: 10px;
  }

  .todo-card {
    transition: all 0.3s ease;
  }

  .todo-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .todo-text {
    font-size: 16px;
    transition: all 0.3s ease;
  }

  .todo-text.completed {
    text-decoration: line-through;
    color: #909399;
  }

  .todo-actions {
    flex-shrink: 0;
  }

  .todo-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
  }

  .created-time {
    font-size: 12px;
    color: #909399;
  }

  .bulk-actions {
    margin-top: 20px;
    text-align: center;
  }

  .state-view {
    margin-top: 20px;
  }

  pre {
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 4px;
    overflow-x: auto;
    max-height: 300px;
  }

  @media (max-width: 768px) {
    .filters {
      display: flex;
      justify-content: center;
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
    }
  }
</style>
