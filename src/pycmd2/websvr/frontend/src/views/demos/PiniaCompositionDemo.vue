<template>
  <div class="pinia-composition-demo">
    <el-card header="Store 组合示例 - 多 Store 协同工作">
      <div class="composition-section">
        <el-row :gutter="20">
          <!-- 用户信息区域 -->
          <el-col :span="24" :md="12">
            <el-card shadow="hover" class="section-card">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <User />
                  </el-icon>
                  <span>用户信息</span>
                </div>
              </template>

              <div v-if="userStore.isAuthenticated" class="user-info">
                <el-avatar :size="50" :src="userStore.user?.avatar" />
                <div class="user-details">
                  <h3>{{ userStore.fullName }}</h3>
                  <p>{{ userStore.user?.email }}</p>
                  <el-tag :type="userStore.isDarkTheme ? 'info' : 'primary'">
                    {{ userStore.isDarkTheme ? '深色主题' : '浅色主题' }}
                  </el-tag>
                </div>

                <el-button type="danger" size="small" @click="userStore.logout" style="margin-top: 15px">
                  退出登录
                </el-button>
              </div>

              <div v-else class="login-prompt">
                <el-empty description="请先登录" :image-size="80" />
                <el-button type="primary" @click="showLoginDialog">登录</el-button>
              </div>
            </el-card>
          </el-col>

          <!-- 计数器区域 -->
          <el-col :span="24" :md="12">
            <el-card shadow="hover" class="section-card">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <Counter />
                  </el-icon>
                  <span>计数器</span>
                </div>
              </template>

              <div class="counter-display">
                <el-statistic title="当前计数" :value="counterStore.count" />
                <el-statistic title="双倍计数" :value="counterStore.doubleCount" />
              </div>

              <div class="counter-actions">
                <el-button-group>
                  <el-button @click="counterStore.decrement()">-</el-button>
                  <el-button type="primary" @click="counterStore.increment()">+</el-button>
                </el-button-group>

                <el-button type="warning" size="small" @click="counterStore.reset()"> 重置 </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 用户活动统计 -->
        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="24">
            <el-card shadow="hover" class="section-card">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <DataAnalysis />
                  </el-icon>
                  <span>用户活动统计</span>
                </div>
              </template>

              <div class="stats-container">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <el-statistic title="用户状态" :value="userStore.isAuthenticated ? '已登录' : '未登录'" />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic title="计数操作" :value="totalOperations" />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic title="待办事项" :value="todosStore.totalCount" />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic title="完成率" :value="todosStore.completionPercentage" suffix="%" />
                  </el-col>
                </el-row>

                <el-progress :percentage="overallProgress" :status="getProgressStatus" style="margin-top: 20px" />
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 快速操作区域 -->
        <el-row style="margin-top: 20px">
          <el-col :span="24">
            <el-card shadow="hover" class="section-card">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <Operation />
                  </el-icon>
                  <span>快速操作</span>
                </div>
              </template>

              <div class="quick-actions">
                <el-button type="primary" @click="performComplexOperation" :loading="isProcessing || operationLock">
                  <el-icon>
                    <Magic />
                  </el-icon>
                  执行组合操作
                </el-button>

                <el-button type="success" @click="syncUserData" :disabled="!userStore.isAuthenticated || operationLock">
                  <el-icon>
                    <Refresh />
                  </el-icon>
                  同步数据
                </el-button>

                <el-button type="warning" @click="resetAllStores" :disabled="operationLock">
                  <el-icon>
                    <Warning />
                  </el-icon>
                  重置所有状态
                </el-button>
              </div>

              <div v-if="lastOperation" class="operation-result">
                <el-alert :title="lastOperation" type="success" :closable="false" />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 登录对话框 -->
    <el-dialog v-model="loginDialogVisible" title="快速登录" width="400px">
      <el-form :model="quickLoginForm" label-width="80px">
        <el-form-item label="邮箱">
          <el-input v-model="quickLoginForm.email" placeholder="demo@example.com" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="quickLoginForm.password" type="password" placeholder="password" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="loginDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="quickLogin">登录</el-button>
      </template>
    </el-dialog>

    <el-card header="Store 状态查看" class="state-view">
      <el-tabs>
        <el-tab-pane label="User Store" name="user">
          <pre>{{ JSON.stringify(userStore.$state, null, 2) }}</pre>
        </el-tab-pane>
        <el-tab-pane label="Counter Store" name="counter">
          <pre>{{ JSON.stringify(counterStore.$state, null, 2) }}</pre>
        </el-tab-pane>
        <el-tab-pane label="Todos Store" name="todos">
          <pre>{{ JSON.stringify(todosStore.$state, null, 2) }}</pre>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted } from 'vue'
  import { useUserStore } from '@/stores/user'
  import { useCounterStore } from '@/stores/counter'
  import { useTodosStore } from '@/stores/todos'
  import { ElMessage } from 'element-plus'
  import { User, DataAnalysis, Operation, Refresh, Warning } from '@element-plus/icons-vue'

  // 初始化所有 stores
  const userStore = useUserStore()
  const counterStore = useCounterStore()
  const todosStore = useTodosStore()

  // 响应式数据
  const isProcessing = ref(false)
  const lastOperation = ref('')
  const loginDialogVisible = ref(false)
  const operationLock = ref(false) // 操作锁，防止并发操作

  // 快速登录表单
  const quickLoginForm = reactive({
    email: 'demo@example.com',
    password: 'password'
  })

  // 计算属性 - 组合多个 store 的数据
  // 优化：缓存计算结果，只在依赖项变化时重新计算
  const totalOperations = computed(() => {
    // 这里可以添加更复杂的计算逻辑
    // 使用 Math.abs 确保结果为正数，避免负数混淆
    return Math.abs(counterStore.count * 2 + todosStore.totalCount)
  })

  const overallProgress = computed(() => {
    // 综合用户活动、计数器、待办事项的整体进度
    let progress = 0

    // 用户登录状态占 30%
    if (userStore.isAuthenticated) progress += 30

    // 计数器进度占 30% (假设 20 为满分)
    progress += Math.min(counterStore.count * 1.5, 30)

    // 待办事项完成率占 40%
    progress += todosStore.completionPercentage * 0.4

    return Math.round(progress)
  })

  const getProgressStatus = computed(() => {
    const progress = overallProgress.value
    if (progress === 100) return 'success'
    if (progress >= 60) return 'warning'
    return 'exception'
  })

  // 方法
  const showLoginDialog = () => {
    loginDialogVisible.value = true
  }

  const quickLogin = async () => {
    const success = await userStore.login(quickLoginForm.email, quickLoginForm.password)
    if (success) {
      loginDialogVisible.value = false
      ElMessage.success('登录成功')
      // 初始化一些示例数据
      await todosStore.fetchTodos()
    } else {
      ElMessage.error('登录失败，请检查邮箱和密码')
    }
  }

  const performComplexOperation = async () => {
    // 检查操作锁，防止并发操作
    if (operationLock.value) {
      ElMessage.warning('操作正在进行中，请稍候...')
      return
    }

    isProcessing.value = true
    operationLock.value = true
    lastOperation.value = ''

    try {
      // 模拟复杂操作：修改多个 store 的状态
      await new Promise(resolve => setTimeout(resolve, 1000))

      // 增加计数器
      counterStore.increment(10)

      // 添加待办事项
      if (userStore.isAuthenticated) {
        todosStore.addTodo(`由 ${userStore.user?.name} 创建的任务`)
      } else {
        todosStore.addTodo('执行了组合操作')
      }

      // 更新用户偏好
      if (userStore.isAuthenticated) {
        userStore.updatePreferences({
          theme: userStore.isDarkTheme ? 'light' : 'dark'
        })
      }

      lastOperation.value = '组合操作执行成功！已更新多个 Store 的状态'
      ElMessage.success('操作完成')
    } catch (error) {
      ElMessage.error('操作失败')
      console.error('Complex operation failed:', error)
    } finally {
      isProcessing.value = false
      operationLock.value = false
    }
  }

  const syncUserData = async () => {
    // 检查操作锁，防止并发操作
    if (operationLock.value) {
      ElMessage.warning('操作正在进行中，请稍候...')
      return
    }

    if (!userStore.isAuthenticated) {
      ElMessage.warning('请先登录')
      return
    }

    operationLock.value = true

    try {
      // 模拟同步数据
      await new Promise(resolve => setTimeout(resolve, 800))

      // 重置计数器并设置一个基于用户名的值
      counterStore.reset()
      const userInitial = userStore.user?.name.charCodeAt(0) || 0
      counterStore.increment(userInitial % 10)

      // 添加用户特定的待办事项
      todosStore.addTodo(`${userStore.user?.name} 的待办事项`)

      ElMessage.success('数据同步成功')
    } catch (error) {
      ElMessage.error('同步失败')
      console.error('Data sync failed:', error)
    } finally {
      operationLock.value = false
    }
  }

  const resetAllStores = () => {
    counterStore.reset()
    todosStore.clearCompleted()
    // 重置本地状态
    lastOperation.value = ''
    operationLock.value = false
    ElMessage.success('所有 Store 状态已重置')
  }

  // 组件挂载时初始化数据
  onMounted(async () => {
    try {
      // 如果用户已认证，获取待办事项
      if (userStore.isAuthenticated) {
        await todosStore.fetchTodos()
      }
    } catch (error) {
      ElMessage.error('初始化数据失败')
      console.error('Initialization failed:', error)
    }
  })
</script>

<style scoped>
  .pinia-composition-demo {
    padding: 20px;
  }

  .composition-section {
    margin-bottom: 20px;
  }

  .section-card {
    height: 100%;
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .user-info {
    text-align: center;
  }

  .user-details {
    margin: 15px 0;
  }

  .user-details h3 {
    margin: 10px 0 5px 0;
  }

  .user-details p {
    margin: 5px 0;
    color: #606266;
  }

  .login-prompt {
    text-align: center;
    padding: 20px 0;
  }

  .counter-display {
    display: flex;
    justify-content: space-around;
    margin: 20px 0;
  }

  .counter-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
  }

  .stats-container {
    padding: 10px 0;
  }

  .quick-actions {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
  }

  .operation-result {
    margin-top: 20px;
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
    .quick-actions {
      flex-direction: column;
    }

    .counter-actions {
      flex-direction: column;
      gap: 10px;
    }
  }
</style>
