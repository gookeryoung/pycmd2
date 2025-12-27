import { defineStore } from 'pinia'

// 本地存储键名
const TODOS_STORAGE_KEY = 'pycmd2-todos'
const FILTER_STORAGE_KEY = 'pycmd2-todos-filter'

export interface Todo {
  id: number;
  text: string;
  completed: boolean;
  createdAt: Date;
}

// 本地存储工具函数
const localStorageUtils = {
  // 获取待办事项
  getTodos(): Todo[] | null {
    try {
      const data = localStorage.getItem(TODOS_STORAGE_KEY)
      if (!data) {
        console.log('没有待办事项数据')
        return null
      }

      const todos = JSON.parse(data)
      // 将字符串日期转换回Date对象
      return todos.map((todo: Todo) => ({
        ...todo,
        createdAt: new Date(todo.createdAt)
      }))
    } catch (error) {
      console.error('获取待办事项失败:', error)
      return null
    }
  },

  // 保存待办事项
  saveTodos(todos: Todo[]): void {
    try {
      localStorage.setItem(TODOS_STORAGE_KEY, JSON.stringify(todos))
    } catch (error) {
      console.error('保存待办事项失败:', error)
    }
  },

  // 获取过滤器设置
  getFilter(): 'all' | 'completed' | 'pending' | null {
    try {
      const filter = localStorage.getItem(FILTER_STORAGE_KEY)
      return (filter as 'all' | 'completed' | 'pending') || null
    } catch (error) {
      console.error('获取过滤器设置失败:', error)
      return null
    }
  },

  // 保存过滤器设置
  saveFilter(filter: 'all' | 'completed' | 'pending'): void {
    try {
      localStorage.setItem(FILTER_STORAGE_KEY, filter)
    } catch (error) {
      console.error('保存过滤器设置失败:', error)
    }
  },

  // 清除所有数据
  clearAll(): void {
    try {
      localStorage.removeItem(TODOS_STORAGE_KEY)
      localStorage.removeItem(FILTER_STORAGE_KEY)
    } catch (error) {
      console.error('清除数据失败:', error)
    }
  }
}

export const useTodosStore = defineStore('todos', {
  state: () => ({
    todos: [] as Todo[],
    filter: 'all' as 'all' | 'completed' | 'pending',
    loading: false,
    error: null as string | null
  }),

  getters: {
    filteredTodos: state => {
      switch (state.filter) {
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
    }
  },

  actions: {
    // 初始化：从本地存储加载数据
    async fetchTodos() {
      this.loading = true
      this.error = null

      try {
        // 尝试从本地存储加载待办事项
        const savedTodos = localStorageUtils.getTodos()
        if (savedTodos) {
          this.todos = savedTodos
        } else {
          // 如果没有保存的数据，使用示例数据
          const mockTodos: Todo[] = [
            { id: 1, text: '学习 Pinia 基础', completed: true, createdAt: new Date() },
            { id: 2, text: '创建第一个 Store', completed: true, createdAt: new Date() },
            { id: 3, text: '实现 Getters 计算属性', completed: false, createdAt: new Date() },
            { id: 4, text: '添加 Actions 操作', completed: false, createdAt: new Date() }
          ]
          this.todos = mockTodos
        }

        // 加载过滤器设置
        const savedFilter = localStorageUtils.getFilter()
        if (savedFilter) {
          this.filter = savedFilter
        }
      } catch (error) {
        this.error = '获取待办事项失败'
        console.error('Error fetching todos:', error)
      } finally {
        this.loading = false
      }
    },

    // 添加待办事项并保存到本地存储
    async addTodo(text: string) {
      if (text.trim() === '') return

      const newTodo: Todo = {
        id: Date.now(),
        text: text.trim(),
        completed: false,
        createdAt: new Date()
      }

      this.todos.push(newTodo)
      localStorageUtils.saveTodos(this.todos)
    },

    // 切换待办事项状态并保存到本地存储
    async toggleTodo(id: number) {
      const todo = this.todos.find(t => t.id === id)
      if (todo) {
        todo.completed = !todo.completed
        localStorageUtils.saveTodos(this.todos)
      }
    },

    // 删除待办事项并保存到本地存储
    async removeTodo(id: number) {
      const index = this.todos.findIndex(todo => todo.id === id)
      if (index !== -1) {
        this.todos.splice(index, 1)
        localStorageUtils.saveTodos(this.todos)
      }
    },

    // 清除已完成的待办事项并保存到本地存储
    async clearCompleted() {
      this.todos = this.todos.filter(todo => !todo.completed)
      localStorageUtils.saveTodos(this.todos)
    },

    // 设置过滤器并保存到本地存储
    setFilter(filter: 'all' | 'completed' | 'pending') {
      this.filter = filter
      localStorageUtils.saveFilter(filter)
    },

    // 清除所有本地存储数据
    clearAllData() {
      this.todos = []
      this.filter = 'all'
      localStorageUtils.clearAll()
    }
  }
})
