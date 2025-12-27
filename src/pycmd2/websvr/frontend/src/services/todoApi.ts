/**
 * Todo API 客户端服务
 * 与 FastAPI 后端通信
 */

export interface Todo {
  id: number
  text: string
  completed: boolean
  createdAt: string
}

export interface TodoCreate {
  text: string
}

export interface TodoUpdate {
  text?: string
  completed?: boolean
}

export interface TodoStats {
  total: number
  completed: number
  pending: number
  completion_rate: number
}

export interface ApiResponse<T = object> {
  data?: T
  message?: string
  error?: string
}

class TodoApiService {
  private baseUrl: string
  private defaultHeaders: Record<string, string>

  constructor(baseUrl: string = 'http://127.0.0.1:8001') {
    this.baseUrl = baseUrl
    this.defaultHeaders = {
      'Content-Type': 'application/json'
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const config: RequestInit = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API请求失败 [${endpoint}]:`, error)
      throw error
    }
  }

  // 获取所有待办事项
  async getTodos(): Promise<Todo[]> {
    return this.request<Todo[]>('/api/todos')
  }

  // 创建新的待办事项
  async createTodo(todoData: TodoCreate): Promise<Todo> {
    return this.request<Todo>('/api/todos', {
      method: 'POST',
      body: JSON.stringify(todoData)
    })
  }

  // 获取指定ID的待办事项
  async getTodo(id: number): Promise<Todo> {
    return this.request<Todo>(`/api/todos/${id}`)
  }

  // 更新待办事项
  async updateTodo(id: number, todoData: TodoUpdate): Promise<Todo> {
    return this.request<Todo>(`/api/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(todoData)
    })
  }

  // 删除待办事项
  async deleteTodo(id: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/todos/${id}`, {
      method: 'DELETE'
    })
  }

  // 清除已完成的待办事项
  async clearCompleted(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/todos', {
      method: 'DELETE'
    })
  }

  // 清除所有待办事项
  async clearAll(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/todos/all', {
      method: 'DELETE'
    })
  }

  // 获取统计信息
  async getStats(): Promise<TodoStats> {
    return this.request<TodoStats>('/api/todos/stats')
  }

  // 导入待办事项
  async importTodos(todos: Todo[]): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/todos/import', {
      method: 'POST',
      body: JSON.stringify({ todos })
    })
  }

  // 导出待办事项
  async exportTodos(): Promise<{ todos: Todo[] }> {
    return this.request<{ todos: Todo[] }>('/api/todos/export')
  }

  // 健康检查
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request<{ status: string; service: string }>('/health')
  }

  // 切换待办事项状态
  async toggleTodo(id: number): Promise<Todo> {
    const todo = await this.getTodo(id)
    return this.updateTodo(id, { completed: !todo.completed })
  }

  // 批量更新待办事项状态
  async toggleMultiple(ids: number[], completed: boolean): Promise<Todo[]> {
    const promises = ids.map(id => this.updateTodo(id, { completed }))
    return Promise.all(promises)
  }

  // 搜索待办事项
  async searchTodos(query: string): Promise<Todo[]> {
    const todos = await this.getTodos()
    const lowerQuery = query.toLowerCase().trim()

    if (!lowerQuery) {
      return todos
    }

    return todos.filter(todo => todo.text.toLowerCase().includes(lowerQuery))
  }

  // 按状态过滤待办事项
  async filterByStatus(status: 'all' | 'completed' | 'pending'): Promise<Todo[]> {
    const todos = await this.getTodos()

    switch (status) {
      case 'completed':
        return todos.filter(todo => todo.completed)
      case 'pending':
        return todos.filter(todo => !todo.completed)
      default:
        return todos
    }
  }
}

// 创建默认实例
export const todoApi = new TodoApiService()

// 导出类以支持创建自定义实例
export { TodoApiService }

// 错误处理工具
export class ApiError extends Error {
  status?: number
  endpoint?: string

  constructor(message: string, status?: number, endpoint?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.endpoint = endpoint
  }
}

// 响应包装工具
export function wrapApiResponse<T>(promise: Promise<T>): Promise<[T | null, Error | null]> {
  return promise.then<[T, null]>(data => [data, null]).catch<[null, Error]>(error => [null, error])
}
