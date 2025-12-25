import { defineStore } from 'pinia'

export interface Todo {
  id: number
  text: string
  completed: boolean
  createdAt: Date
}

export const useTodosStore = defineStore('todos', {
  state: () => ({
    todos: [] as Todo[],
    filter: 'all' as 'all' | 'completed' | 'pending',
    loading: false,
    error: null as string | null
  }),

  getters: {
    filteredTodos: (state) => {
      switch (state.filter) {
        case 'completed':
          return state.todos.filter(todo => todo.completed)
        case 'pending':
          return state.todos.filter(todo => !todo.completed)
        default:
          return state.todos
      }
    },
    completedCount: (state) => state.todos.filter(todo => todo.completed).length,
    pendingCount: (state) => state.todos.filter(todo => !todo.completed).length,
    totalCount: (state) => state.todos.length,
    completionPercentage: (state) => {
      const total = state.todos.length
      if (total === 0) return 0
      return Math.round((state.todos.filter(todo => todo.completed).length / total) * 100)
    }
  },

  actions: {
    async addTodo(text: string) {
      if (text.trim() === '') return

      const newTodo: Todo = {
        id: Date.now(),
        text: text.trim(),
        completed: false,
        createdAt: new Date()
      }

      this.todos.push(newTodo)
    },

    toggleTodo(id: number) {
      const todo = this.todos.find(t => t.id === id)
      if (todo) {
        todo.completed = !todo.completed
      }
    },

    removeTodo(id: number) {
      const index = this.todos.findIndex(todo => todo.id === id)
      if (index !== -1) {
        this.todos.splice(index, 1)
      }
    },

    clearCompleted() {
      this.todos = this.todos.filter(todo => !todo.completed)
    },

    setFilter(filter: 'all' | 'completed' | 'pending') {
      this.filter = filter
    },

    async fetchTodos() {
      this.loading = true
      this.error = null

      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 500))

        // 模拟获取的todos数据
        const mockTodos: Todo[] = [
          { id: 1, text: '学习 Pinia 基础', completed: true, createdAt: new Date() },
          { id: 2, text: '创建第一个 Store', completed: true, createdAt: new Date() },
          { id: 3, text: '实现 Getters 计算属性', completed: false, createdAt: new Date() },
          { id: 4, text: '添加 Actions 操作', completed: false, createdAt: new Date() }
        ]

        this.todos = mockTodos
      } catch (error) {
        this.error = '获取待办事项失败'
        console.error('Error fetching todos:', error)
      } finally {
        this.loading = false
      }
    }
  }
})
