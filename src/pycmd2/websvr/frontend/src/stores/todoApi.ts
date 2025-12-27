import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import { todoApi, type Todo, type TodoStats } from '@/services/todoApi'

export interface ApiState {
  todos: Todo[]
  loading: boolean
  error: string | null
  apiConnected: boolean
  lastSyncTime: Date | null
}

export const useTodoApiStore = defineStore('todoApi', {
  state: (): ApiState => ({
    todos: [],
    loading: false,
    error: null,
    apiConnected: false,
    lastSyncTime: null
  }),

  getters: {
    filteredTodos: state => (filter: 'all' | 'completed' | 'pending') => {
      switch (filter) {
        case 'completed':
          return state.todos.filter(todo => todo.completed)
        case 'pending':
          return state.todos.filter(todo => !todo.completed)
        default:
          return state.todos
      }
    },

    completedCount: state => state.todos.filter(todo => todo.completed).length,
    pendingCount: state => state.todos.filter(todo => !todo.completed).length,
    totalCount: state => state.todos.length,

    completionPercentage: state => {
      const total = state.todos.length
      if (total === 0) return 0
      return Math.round((state.todos.filter(todo => todo.completed).length / total) * 100)
    },

    connectionStatus: state => ({
      connected: state.apiConnected,
      lastSync: state.lastSyncTime,
      status: state.apiConnected ? '已连接' : '未连接'
    })
  },

  actions: {
    // 检查API连接
    async checkConnection(): Promise<boolean> {
      try {
        const health = await todoApi.healthCheck()
        this.apiConnected = health.status === 'healthy'
        return this.apiConnected
      } catch (error) {
        this.apiConnected = false
        this.setError('API连接失败: ' + (error instanceof Error ? error.message : '未知错误'))
        return false
      }
    },

    // 设置错误信息
    setError(message: string) {
      this.error = message
      ElMessage.error(message)
    },

    // 清除错误信息
    clearError() {
      this.error = null
    },

    // 设置加载状态
    setLoading(loading: boolean) {
      this.loading = loading
    },

    // 获取所有待办事项
    async fetchTodos(): Promise<void> {
      if (!this.apiConnected) {
        const connected = await this.checkConnection()
        if (!connected) return
      }

      this.setLoading(true)
      this.clearError()

      try {
        this.todos = await todoApi.getTodos()
        this.lastSyncTime = new Date()
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '获取待办事项失败')
      } finally {
        this.setLoading(false)
      }
    },

    // 添加待办事项
    async addTodo(text: string): Promise<void> {
      if (text.trim() === '') return

      if (!this.apiConnected) {
        this.setError('API未连接，无法添加待办事项')
        return
      }

      this.setLoading(true)
      this.clearError()

      try {
        const newTodo = await todoApi.createTodo({ text: text.trim() })
        this.todos.push(newTodo)
        this.lastSyncTime = new Date()
        ElMessage.success('待办事项已添加')
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '添加待办事项失败')
      } finally {
        this.setLoading(false)
      }
    },

    // 切换待办事项状态
    async toggleTodo(id: number): Promise<void> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法切换状态')
        return
      }

      this.setLoading(true)
      this.clearError()

      try {
        const updatedTodo = await todoApi.toggleTodo(id)
        const index = this.todos.findIndex(todo => todo.id === id)
        if (index !== -1) {
          this.todos[index] = updatedTodo
          this.lastSyncTime = new Date()
        }
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '切换状态失败')
      } finally {
        this.setLoading(false)
      }
    },

    // 更新待办事项
    async updateTodo(id: number, updates: { text?: string; completed?: boolean }): Promise<void> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法更新待办事项')
        return
      }

      this.setLoading(true)
      this.clearError()

      try {
        const updatedTodo = await todoApi.updateTodo(id, updates)
        const index = this.todos.findIndex(todo => todo.id === id)
        if (index !== -1) {
          this.todos[index] = updatedTodo
          this.lastSyncTime = new Date()
        }
        ElMessage.success('待办事项已更新')
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '更新待办事项失败')
      } finally {
        this.setLoading(false)
      }
    },

    // 删除待办事项
    async removeTodo(id: number): Promise<void> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法删除待办事项')
        return
      }

      this.setLoading(true)
      this.clearError()

      try {
        await todoApi.deleteTodo(id)
        this.todos = this.todos.filter(todo => todo.id !== id)
        this.lastSyncTime = new Date()
        ElMessage.success('待办事项已删除')
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '删除待办事项失败')
      } finally {
        this.setLoading(false)
      }
    },

    // 清除已完成的待办事项
    async clearCompleted(): Promise<void> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法清除待办事项')
        return
      }

      const completedCount = this.todos.filter(todo => todo.completed).length
      if (completedCount === 0) {
        ElMessage.info('没有已完成的待办事项需要清除')
        return
      }

      this.setLoading(true)
      this.clearError()

      try {
        await todoApi.clearCompleted()
        this.todos = this.todos.filter(todo => !todo.completed)
        this.lastSyncTime = new Date()
        ElMessage.success(`已清除 ${completedCount} 个已完成的待办事项`)
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '清除已完成待办事项失败')
      } finally {
        this.setLoading(false)
      }
    },

    // 清除所有待办事项
    async clearAllData(): Promise<void> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法清除数据')
        return
      }

      this.setLoading(true)
      this.clearError()

      try {
        await todoApi.clearAll()
        this.todos = []
        this.lastSyncTime = new Date()
        ElMessage.success('所有待办事项已清除')
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '清除所有数据失败')
      } finally {
        this.setLoading(false)
      }
    },

    // 搜索待办事项
    async searchTodos(query: string): Promise<Todo[]> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法搜索')
        return []
      }

      try {
        return await todoApi.searchTodos(query)
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '搜索失败')
        return []
      }
    },

    // 按状态过滤
    async filterByStatus(status: 'all' | 'completed' | 'pending'): Promise<Todo[]> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法过滤')
        return []
      }

      try {
        return await todoApi.filterByStatus(status)
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '过滤失败')
        return []
      }
    },

    // 导入待办事项
    async importTodos(todos: Todo[]): Promise<void> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法导入')
        return
      }

      if (todos.length === 0) {
        ElMessage.warning('没有可导入的待办事项')
        return
      }

      this.setLoading(true)
      this.clearError()

      try {
        await todoApi.importTodos(todos)
        await this.fetchTodos() // 重新获取数据
        ElMessage.success(`成功导入 ${todos.length} 个待办事项`)
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '导入失败')
      } finally {
        this.setLoading(false)
      }
    },

    // 导出待办事项
    async exportTodos(): Promise<Todo[]> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法导出')
        return []
      }

      try {
        const response = await todoApi.exportTodos()
        const todos = response.todos
        ElMessage.success('待办事项数据已导出')
        return todos
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '导出失败')
        return []
      }
    },

    // 获取统计信息
    async getStats(): Promise<TodoStats | null> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法获取统计信息')
        return null
      }

      try {
        return await todoApi.getStats()
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '获取统计信息失败')
        return null
      }
    },

    // 批量操作：标记所有为完成
    async markAllCompleted(): Promise<void> {
      if (!this.apiConnected) {
        this.setError('API未连接，无法批量操作')
        return
      }

      const pendingTodos = this.todos.filter(todo => !todo.completed)
      if (pendingTodos.length === 0) {
        ElMessage.info('没有待完成的待办事项')
        return
      }

      this.setLoading(true)
      this.clearError()

      try {
        const promises = pendingTodos.map(todo => this.updateTodo(todo.id, { completed: true }))
        await Promise.all(promises)
        ElMessage.success(`已标记 ${pendingTodos.length} 个待办事项为完成`)
      } catch (error) {
        this.setError(error instanceof Error ? error.message : '批量操作失败')
      } finally {
        this.setLoading(false)
      }
    },

    // 刷新数据
    async refresh(): Promise<void> {
      await this.fetchTodos()
      ElMessage.success('数据已刷新')
    }
  }
})
