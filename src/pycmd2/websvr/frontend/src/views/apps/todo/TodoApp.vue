<template>
  <div class="todo-app">
    <el-card class="todo-container" shadow="always">
      <template #header>
        <div class="card-header">
          <h2>📝 我的待办事项</h2>
          <el-tag type="primary">Todo App</el-tag>
        </div>
      </template>

      <!-- 添加新待办事项 -->
      <div class="add-todo-section">
        <el-input
          v-model="newTodoText"
          placeholder="添加新的待办事项..."
          @keyup.enter="addTodo"
          clearable
          size="large"
        >
          <template #append>
            <el-button type="primary" @click="addTodo" :disabled="!newTodoText.trim()">
              <el-icon>
                <Plus />
              </el-icon>
              添加
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 过滤选项和统计信息 -->
      <div class="filter-stats-section">
        <el-radio-group v-model="currentFilter" @change="handleFilterChange" class="filter-group">
          <el-radio-button label="all"> 全部 ({{ todosStore.totalCount }}) </el-radio-button>
          <el-radio-button label="pending">
            待完成 ({{ todosStore.pendingCount }})
          </el-radio-button>
          <el-radio-button label="completed">
            已完成 ({{ todosStore.completedCount }})
          </el-radio-button>
        </el-radio-group>

        <div class="progress-container">
          <el-progress
            :percentage="todosStore.completionPercentage"
            :color="progressColor"
            :stroke-width="8"
          />
          <div class="progress-text">
            完成进度: {{ todosStore.completedCount }} / {{ todosStore.totalCount }}
          </div>
        </div>
      </div>

      <el-divider />

      <!-- 加载状态 -->
      <div v-if="todosStore.loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>

      <!-- 错误提示 -->
      <div v-else-if="todosStore.error" class="error-container">
        <el-alert :title="todosStore.error"
                  type="error"
                  :closable="false"
                  show-icon />
      </div>

      <!-- 待办事项列表 -->
      <div v-else class="todo-list-container">
        <el-empty v-if="filteredTodos.length === 0" description="暂无待办事项">
          <el-button type="primary" @click="addSampleTodos">添加示例待办事项</el-button>
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
                  />

                  <div class="todo-text-container">
                    <p class="todo-text" :class="{ completed: todo.completed }">
                      {{ todo.text }}
                    </p>
                    <div class="todo-meta">
                      <el-tag size="small" :type="todo.completed ? 'success' : 'info'">
                        {{ todo.completed ? '已完成' : '待完成' }}
                      </el-tag>
                      <span class="created-time">
                        {{ formatRelativeTime(todo.createdAt) }}
                      </span>
                    </div>
                  </div>

                  <div class="todo-actions">
                    <el-button
                      type="danger"
                      size="small"
                      @click="confirmRemoveTodo(todo)"
                      :icon="Delete"
                      circle
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
            type="warning"
            @click="clearCompleted"
            :disabled="todosStore.completedCount === 0"
          >
            <el-icon>
              <Delete />
            </el-icon>
            清除已完成
          </el-button>

          <el-button type="info" @click="refreshTodos" :icon="Refresh"> 刷新 </el-button>

          <el-button type="danger" @click="confirmClearAllData" :icon="Delete">
            清除所有数据
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue';
  import { useTodosStore } from '../../../stores/todos';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import { Plus, Delete, Refresh } from '@element-plus/icons-vue';

  const todosStore = useTodosStore();
  const newTodoText = ref('');
  const currentFilter = ref<'all' | 'completed' | 'pending'>('all');

  // 使用 store 的 getter
  const filteredTodos = computed(() => todosStore.filteredTodos);

  // 根据完成度设置进度条颜色
  const progressColor = computed(() => {
    const percentage = todosStore.completionPercentage;
    if (percentage === 100) return '#67c23a';
    if (percentage >= 50) return '#409eff';
    return '#e6a23c';
  });

  onMounted(() => {
    // 初始化时获取待办事项
    todosStore.fetchTodos();
  });

  const addTodo = () => {
    if (newTodoText.value.trim()) {
      todosStore.addTodo(newTodoText.value);
      newTodoText.value = '';
      ElMessage.success('待办事项已添加');
    }
  };

  const toggleTodo = (id: number) => {
    todosStore.toggleTodo(id);
  };

  const confirmRemoveTodo = (todo: any) => {
    ElMessageBox.confirm(`确定要删除待办事项"${todo.text}"吗?`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(() => {
        todosStore.removeTodo(todo.id);
        ElMessage.success('待办事项已删除');
      })
      .catch(() => {
        // 用户取消删除
      });
  };

  const clearCompleted = () => {
    if (todosStore.completedCount === 0) return;

    ElMessageBox.confirm(
      `确定要清除所有已完成的 ${todosStore.completedCount} 项待办事项吗?`,
      '确认清除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
      .then(() => {
        todosStore.clearCompleted();
        ElMessage.success('已清除所有已完成的待办事项');
      })
      .catch(() => {
        // 用户取消清除
      });
  };

  const handleFilterChange = () => {
    todosStore.setFilter(currentFilter.value);
  };

  const refreshTodos = () => {
    todosStore.fetchTodos();
    ElMessage.success('待办事项已刷新');
  };

  const addSampleTodos = () => {
    const sampleTodos = ['学习 Vue 3 组合式 API', '完成项目文档', '准备明天的会议', '锻炼身体'];

    sampleTodos.forEach(text => {
      todosStore.addTodo(text);
    });

    ElMessage.success('已添加示例待办事项');
  };

  const confirmClearAllData = () => {
    ElMessageBox.confirm('确定要清除所有待办事项数据吗？此操作不可恢复！', '危险操作', {
      confirmButtonText: '确定清除',
      cancelButtonText: '取消',
      type: 'error',
      dangerouslyUseHTMLString: true
    })
      .then(() => {
        todosStore.clearAllData();
        ElMessage.success('所有数据已清除');
      })
      .catch(() => {
        // 用户取消清除
      });
  };

  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;

    return new Intl.DateTimeFormat('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };
</script>

<style scoped>
  .todo-app {
    padding: 20px;
    max-width: 800px;
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

  .add-todo-section {
    margin-bottom: 24px;
  }

  .filter-stats-section {
    margin: 20px 0;
  }

  .filter-group {
    width: 100%;
    margin-bottom: 16px;
  }

  .progress-container {
    text-align: center;
  }

  .progress-text {
    margin-top: 8px;
    font-size: 14px;
    color: #606266;
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
  }

  .created-time {
    font-size: 12px;
    color: #909399;
  }

  .todo-actions {
    flex-shrink: 0;
  }

  .bulk-actions {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    gap: 12px;
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
    .todo-app {
      padding: 10px;
    }

    .filter-group {
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
      gap: 6px;
    }

    .bulk-actions {
      flex-direction: column;
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
