<template>
  <div class="pinia-user-demo">
    <!-- 登录表单 -->
    <el-card v-if="!userStore.isAuthenticated" header="用户认证示例 - User Store" class="auth-card">
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="loginForm.email" placeholder="demo@example.com" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="userStore.loading" class="login-button">
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <el-alert v-if="userStore.error" :title="userStore.error" type="error" :closable="false" class="error-alert" />

      <el-divider>提示</el-divider>
      <p>测试账号: demo@example.com</p>
      <p>测试密码: password</p>
    </el-card>

    <!-- 用户信息展示 -->
    <div v-else class="user-info-section">
      <el-card header="用户信息" class="user-card">
        <div class="user-profile">
          <el-avatar :size="80" :src="userStore.user?.avatar" class="avatar" />
          <div class="user-details">
            <h2>{{ userStore.fullName }}</h2>
            <p>
              <el-icon><Message /></el-icon> {{ userStore.user?.email }}
            </p>
          </div>
        </div>

        <el-divider />

        <div class="preferences-section">
          <h3>用户偏好设置</h3>

          <div class="preference-item">
            <label>主题模式:</label>
            <el-switch
              v-model="isDarkTheme"
              @change="toggleTheme"
              active-text="深色"
              inactive-text="浅色"
              :active-icon="Moon"
              :inactive-icon="Sunny"
            />
          </div>

          <div class="preference-item">
            <label>语言设置:</label>
            <el-select v-model="selectedLanguage" @change="updateLanguage" placeholder="选择语言">
              <el-option label="中文" value="zh-CN" />
              <el-option label="English" value="en-US" />
              <el-option label="日本語" value="ja-JP" />
            </el-select>
          </div>

          <div class="preference-item">
            <label>通知设置:</label>
            <el-switch
              v-model="notificationsEnabled"
              @change="toggleNotifications"
              active-text="开启"
              inactive-text="关闭"
            />
          </div>
        </div>

        <el-divider />

        <div class="profile-edit">
          <h3>编辑个人资料</h3>
          <el-form :model="profileForm" label-width="80px">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.name" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile">更新资料</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>

      <div class="action-section">
        <el-button type="danger" @click="handleLogout" size="large">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </div>

    <el-card header="Store 状态查看" class="state-view">
      <el-collapse>
        <el-collapse-item title="完整状态" name="state">
          <pre>{{ JSON.stringify(userStore.$state, null, 2) }}</pre>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, reactive, onMounted } from 'vue'
  import { useUserStore } from '@/stores/user'
  import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
  import { Message, Moon, Sunny, SwitchButton } from '@element-plus/icons-vue'

  const userStore = useUserStore()
  const loginFormRef = ref<FormInstance>()

  // 登录表单数据
  const loginForm = reactive({
    email: 'demo@example.com',
    password: 'password'
  })

  // 表单验证规则
  const rules: FormRules = {
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
    ]
  }

  // 个人资料表单
  const profileForm = reactive({
    name: '',
    email: ''
  })

  // 偏好设置的响应式引用
  const isDarkTheme = computed({
    get: () => userStore.isDarkTheme,
    set: () => {} // 实际更新通过 toggleTheme 方法处理
  })

  const notificationsEnabled = computed({
    get: () => userStore.notificationsEnabled,
    set: () => {} // 实际更新通过 toggleNotifications 方法处理
  })

  const selectedLanguage = ref('zh-CN')

  // 初始化个人资料表单
  onMounted(() => {
    if (userStore.user) {
      profileForm.name = userStore.user.name
      profileForm.email = userStore.user.email
      selectedLanguage.value = userStore.user.preferences.language
    }
  })

  // 登录处理
  const handleLogin = async () => {
    if (!loginFormRef.value) return

    await loginFormRef.value.validate(async valid => {
      if (valid) {
        const success = await userStore.login(loginForm.email, loginForm.password)
        if (success) {
          // 初始化个人资料表单
          if (userStore.user) {
            profileForm.name = userStore.user.name
            profileForm.email = userStore.user.email
            selectedLanguage.value = userStore.user.preferences.language
          }
          ElMessage.success('登录成功')
        }
      }
    })
  }

  // 退出登录
  const handleLogout = () => {
    userStore.logout()
    ElMessage.success('已退出登录')
  }

  // 切换主题
  const toggleTheme = () => {
    userStore.toggleTheme()
    ElMessage.success(`主题已切换为${userStore.isDarkTheme ? '深色' : '浅色'}模式`)
  }

  // 切换通知
  const toggleNotifications = () => {
    userStore.toggleNotifications()
    ElMessage.success(`通知已${userStore.notificationsEnabled ? '开启' : '关闭'}`)
  }

  // 更新语言
  const updateLanguage = () => {
    userStore.updatePreferences({ language: selectedLanguage.value })
    ElMessage.success(`语言已更新为 ${selectedLanguage.value}`)
  }

  // 更新个人资料
  const updateProfile = () => {
    userStore.updateProfile({
      name: profileForm.name,
      email: profileForm.email
    })
    ElMessage.success('个人资料已更新')
  }
</script>

<style scoped>
  .pinia-user-demo {
    padding: 20px;
  }

  .auth-card,
  .user-card {
    margin-bottom: 20px;
  }

  .login-button {
    width: 100%;
  }

  .error-alert {
    margin-top: 20px;
  }

  .user-info-section {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .user-profile {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .avatar {
    flex-shrink: 0;
  }

  .user-details h2 {
    margin: 0 0 10px 0;
  }

  .user-details p {
    display: flex;
    align-items: center;
    gap: 5px;
    margin: 5px 0;
    color: #606266;
  }

  .preferences-section,
  .profile-edit {
    margin-top: 20px;
  }

  .preference-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding: 10px 0;
  }

  .preference-item label {
    font-weight: 500;
    min-width: 100px;
  }

  .action-section {
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
    .user-profile {
      flex-direction: column;
      text-align: center;
    }

    .preference-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }

    .preference-item label {
      min-width: auto;
    }
  }
</style>
