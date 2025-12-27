import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,
    name: '计数器示例'
  }),

  getters: {
    doubleCount: state => state.count * 2,
    formattedCount: state => `当前计数: ${state.count}`,
    countHistory: _ => {
      // 这里只是示例，实际上我们会把历史记录保存在state中
      return [0, 1, 2, 3, 4, 5].map(n => n * 2)
    }
  },

  actions: {
    increment(amount = 1) {
      this.count += amount
    },
    decrement(amount = 1) {
      this.count -= amount
    },
    reset() {
      this.count = 0
    },
    async fetchRandomCount() {
      // 模拟异步API调用
      return new Promise(resolve => {
        setTimeout(() => {
          const randomValue = Math.floor(Math.random() * 100)
          this.count = randomValue
          resolve(randomValue)
        }, 500)
      })
    },
    setName(newName: string) {
      this.name = newName
    }
  }
})
