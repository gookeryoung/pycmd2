import { defineStore } from 'pinia'

export interface User {
  id: number
  name: string
  email: string
  avatar: string
  preferences: {
    theme: 'light' | 'dark'
    language: string
    notifications: boolean
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
    isAuthenticated: false,
    loading: false,
    error: null as string | null
  }),

  getters: {
    fullName: state => {
      if (!state.user) return ''
      return state.user.name
    },
    isDarkTheme: state => {
      return state.user?.preferences.theme === 'dark'
    },
    notificationsEnabled: state => {
      return state.user?.preferences.notifications ?? true
    }
  },

  actions: {
    async login(email: string, password: string) {
      this.loading = true
      this.error = null

      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))

        // 模拟登录成功
        if (email === 'demo@example.com' && password === 'password') {
          this.user = {
            id: 1,
            name: '演示用户',
            email: 'demo@example.com',
            avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
            preferences: {
              theme: 'light',
              language: 'zh-CN',
              notifications: true
            }
          }
          this.isAuthenticated = true
          return true
        } else {
          this.error = '邮箱或密码错误'
          return false
        }
      } catch (error) {
        this.error = '登录失败: ' + error
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      this.isAuthenticated = false
      this.error = null
    },

    updateProfile(updates: Partial<User>) {
      if (!this.user) return

      this.user = { ...this.user, ...updates }
    },

    updatePreferences(preferences: Partial<User['preferences']>) {
      if (!this.user) return

      this.user.preferences = { ...this.user.preferences, ...preferences }
    },

    toggleTheme() {
      if (!this.user) return

      this.user.preferences.theme = this.user.preferences.theme === 'light' ? 'dark' : 'light'
    },

    toggleNotifications() {
      if (!this.user) return

      this.user.preferences.notifications = !this.user.preferences.notifications
    }
  }
})
