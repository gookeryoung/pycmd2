<template>
  <div class="pinia-persistent-demo">
    <el-card header="持久化存储示例 - LocalStorage 集成">
      <div class="persistent-section">
        <el-alert
          title="持久化说明"
          type="info"
          :closable="false"
          description="此示例展示了如何将 Pinia 状态与 LocalStorage 集成，实现数据持久化。刷新页面后数据仍然保留。"
          style="margin-bottom: 20px"
        />

        <el-row :gutter="20">
          <!-- 设置面板 -->
          <el-col :span="24" :md="12">
            <el-card shadow="hover" class="settings-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Setting /></el-icon>
                  <span>应用设置</span>
                </div>
              </template>

              <el-form :model="appSettings" label-width="100px">
                <el-form-item label="应用主题">
                  <el-select v-model="appSettings.theme" @change="updateSetting('theme')">
                    <el-option label="浅色" value="light" />
                    <el-option label="深色" value="dark" />
                    <el-option label="自动" value="auto" />
                  </el-select>
                </el-form-item>

                <el-form-item label="语言">
                  <el-select v-model="appSettings.language" @change="updateSetting('language')">
                    <el-option label="中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                  </el-select>
                </el-form-item>

                <el-form-item label="字体大小">
                  <el-slider v-model="appSettings.fontSize" :min="12" :max="24" @change="updateSetting('fontSize')" />
                </el-form-item>

                <el-form-item label="自动保存">
                  <el-switch v-model="appSettings.autoSave" @change="updateSetting('autoSave')" />
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <!-- 用户数据 -->
          <el-col :span="24" :md="12">
            <el-card shadow="hover" class="data-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Document /></el-icon>
                  <span>用户数据</span>
                </div>
              </template>

              <div class="user-profile">
                <el-input v-model="userData.name" placeholder="用户名" @input="updateUserData">
                  <template #prepend>用户名</template>
                </el-input>

                <el-input v-model="userData.email" placeholder="邮箱" style="margin-top: 10px" @input="updateUserData">
                  <template #prepend>邮箱</template>
                </el-input>

                <el-input
                  v-model="userData.bio"
                  type="textarea"
                  :rows="3"
                  placeholder="个人简介"
                  style="margin-top: 10px"
                  @input="updateUserData"
                />
              </div>

              <el-divider />

              <div class="notes-section">
                <h4>便签 ({{ notes.length }})</h4>
                <el-input v-model="newNote" placeholder="添加新便签..." @keyup.enter="addNote">
                  <template #append>
                    <el-button @click="addNote">添加</el-button>
                  </template>
                </el-input>

                <div class="notes-list">
                  <el-tag
                    v-for="(note, index) in notes"
                    :key="index"
                    closable
                    @close="removeNote(index)"
                    style="margin: 5px"
                  >
                    {{ note }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 存储管理 -->
        <el-row style="margin-top: 20px">
          <el-col :span="24">
            <el-card shadow="hover" class="storage-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Folder /></el-icon>
                  <span>存储管理</span>
                </div>
              </template>

              <div class="storage-info">
                <el-descriptions :column="3" border>
                  <el-descriptions-item label="存储大小">
                    {{ formatBytes(storageSize) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="数据项数量">
                    {{ storageKeys.length }}
                  </el-descriptions-item>
                  <el-descriptions-item label="最后更新">
                    {{ lastUpdated || '从未' }}
                  </el-descriptions-item>
                </el-descriptions>

                <div class="storage-actions">
                  <el-button type="primary" @click="exportData">
                    <el-icon><Download /></el-icon>
                    导出数据
                  </el-button>

                  <el-button type="success" @click="showImportDialog = true">
                    <el-icon><Upload /></el-icon>
                    导入数据
                  </el-button>

                  <el-button type="warning" @click="refreshData">
                    <el-icon><Refresh /></el-icon>
                    刷新数据
                  </el-button>

                  <el-button type="danger" @click="clearAllData">
                    <el-icon><Delete /></el-icon>
                    清除所有数据
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 存储内容预览 -->
        <el-row style="margin-top: 20px">
          <el-col :span="24">
            <el-card shadow="hover" class="preview-card">
              <template #header>
                <div class="card-header">
                  <el-icon><View /></el-icon>
                  <span>存储内容预览</span>
                </div>
              </template>

              <el-tabs>
                <el-tab-pane v-for="key in storageKeys" :key="key" :label="getDisplayName(key)" :name="key">
                  <div class="content-viewer">
                    <el-button size="small" @click="copyToClipboard(storageData[key])" style="margin-bottom: 10px">
                      <el-icon><CopyDocument /></el-icon>
                      复制
                    </el-button>
                    <pre>{{ formatJson(storageData[key]) }}</pre>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入数据" width="500px">
      <el-input v-model="importData" type="textarea" :rows="10" placeholder="粘贴导出的 JSON 数据..." />

      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importDataHandler">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted } from 'vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    Setting,
    Document,
    Folder,
    Download,
    Upload,
    Refresh,
    Delete,
    View,
    CopyDocument
  } from '@element-plus/icons-vue'

  type StorageData = Record<string, unknown>

  // 应用设置
  const appSettings = reactive({
    theme: 'light',
    language: 'zh-CN',
    fontSize: 16,
    autoSave: true
  })

  // 用户数据
  const userData = reactive({
    name: '',
    email: '',
    bio: ''
  })

  // 便签数据
  const notes = ref<string[]>([])
  const newNote = ref('')

  // 存储管理
  const showImportDialog = ref(false)
  const importData = ref('')
  const lastUpdated = ref('')

  // 存储数据相关
  const storageKeys = computed(() => {
    const keys = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith('pinia-demo-')) {
        keys.push(key)
      }
    }
    return keys
  })

  const storageSize = computed(() => {
    let size = 0
    for (const key of storageKeys.value) {
      const value = localStorage.getItem(key)
      if (value) {
        size += value.length
      }
    }
    return size
  })

  const storageData = computed(() => {
    const data: StorageData = {}
    for (const key of storageKeys.value) {
      const value = localStorage.getItem(key)
      if (value) {
        try {
          data[key] = JSON.parse(value)
        } catch {
          data[key] = value
        }
      }
    }
    return data
  })

  // 初始化
  onMounted(() => {
    loadFromStorage()
  })

  // 从本地存储加载数据
  const loadFromStorage = () => {
    try {
      // 加载应用设置
      const settingsData = localStorage.getItem('pinia-demo-settings')
      if (settingsData) {
        Object.assign(appSettings, JSON.parse(settingsData))
      }

      // 加载用户数据
      const userDataStr = localStorage.getItem('pinia-demo-user')
      if (userDataStr) {
        Object.assign(userData, JSON.parse(userDataStr))
      }

      // 加载便签
      const notesData = localStorage.getItem('pinia-demo-notes')
      if (notesData) {
        notes.value = JSON.parse(notesData)
      }

      // 加载最后更新时间
      const lastUpdatedStr = localStorage.getItem('pinia-demo-lastUpdated')
      if (lastUpdatedStr) {
        lastUpdated.value = new Date(lastUpdatedStr).toLocaleString()
      }
    } catch (error) {
      ElMessage.error('加载数据失败: ' + error)
    }
  }

  // 保存到本地存储
  const saveToStorage = (key: string, data: unknown) => {
    try {
      localStorage.setItem(key, JSON.stringify(data))
      updateLastUpdated()
    } catch (error) {
      ElMessage.error('保存数据失败' + error)
    }
  }

  // 更新最后更新时间
  const updateLastUpdated = () => {
    const now = new Date().toISOString()
    localStorage.setItem('pinia-demo-lastUpdated', now)
    lastUpdated.value = new Date(now).toLocaleString()
  }

  // 更新设置
  const updateSetting = (key: string) => {
    saveToStorage('pinia-demo-settings', appSettings)
    ElMessage.success(`设置已保存: ${key}`)
  }

  // 更新用户数据
  const updateUserData = () => {
    saveToStorage('pinia-demo-user', userData)
  }

  // 添加便签
  const addNote = () => {
    if (newNote.value.trim()) {
      notes.value.push(newNote.value.trim())
      newNote.value = ''
      saveToStorage('pinia-demo-notes', notes.value)
      ElMessage.success('便签已添加')
    }
  }

  // 删除便签
  const removeNote = (index: number) => {
    notes.value.splice(index, 1)
    saveToStorage('pinia-demo-notes', notes.value)
  }

  // 导出数据
  const exportData = () => {
    const exportObj = {
      settings: appSettings,
      user: userData,
      notes: notes.value,
      exportTime: new Date().toISOString()
    }

    const dataStr = JSON.stringify(exportObj, null, 2)
    navigator.clipboard
      .writeText(dataStr)
      .then(() => {
        ElMessage.success('数据已复制到剪贴板')
      })
      .catch(() => {
        ElMessage.error('复制失败，请手动复制')
        showImportDialog.value = true
        importData.value = dataStr
      })
  }

  // 导入数据
  const importDataHandler = () => {
    try {
      const data = JSON.parse(importData.value)

      if (data.settings) {
        Object.assign(appSettings, data.settings)
        saveToStorage('pinia-demo-settings', appSettings)
      }

      if (data.user) {
        Object.assign(userData, data.user)
        saveToStorage('pinia-demo-user', userData)
      }

      if (data.notes) {
        notes.value = data.notes
        saveToStorage('pinia-demo-notes', notes.value)
      }

      ElMessage.success('数据导入成功')
      showImportDialog.value = false
      loadFromStorage()
    } catch (error) {
      ElMessage.error('数据格式错误，导入失败: ' + error)
    }
  }

  // 刷新数据
  const refreshData = () => {
    loadFromStorage()
    ElMessage.success('数据已刷新')
  }

  // 清除所有数据
  const clearAllData = () => {
    ElMessageBox.confirm('确定要清除所有数据吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(() => {
        for (const key of storageKeys.value) {
          localStorage.removeItem(key)
        }

        // 重置数据
        Object.assign(appSettings, {
          theme: 'light',
          language: 'zh-CN',
          fontSize: 16,
          autoSave: true
        })

        Object.assign(userData, {
          name: '',
          email: '',
          bio: ''
        })

        notes.value = []
        lastUpdated.value = ''

        ElMessage.success('所有数据已清除')
      })
      .catch(() => {
        ElMessage.info('操作已取消')
      })
  }

  // 复制到剪贴板
  const copyToClipboard = (data: unknown) => {
    navigator.clipboard
      .writeText(JSON.stringify(data, null, 2))
      .then(() => {
        ElMessage.success('已复制到剪贴板')
      })
      .catch(() => {
        ElMessage.error('复制失败')
      })
  }

  // 格式化字节大小
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 格式化 JSON
  const formatJson = (data: unknown) => {
    return JSON.stringify(data, null, 2)
  }

  // 获取显示名称
  const getDisplayName = (key: string) => {
    const nameMap: Record<string, string> = {
      'pinia-demo-settings': '应用设置',
      'pinia-demo-user': '用户数据',
      'pinia-demo-notes': '便签',
      'pinia-demo-lastUpdated': '最后更新'
    }
    return nameMap[key] || key
  }
</script>

<style scoped>
  .pinia-persistent-demo {
    padding: 20px;
  }

  .persistent-section {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .settings-card,
  .data-card,
  .storage-card,
  .preview-card {
    height: 100%;
    margin-bottom: 20px;
  }

  .user-profile {
    margin-bottom: 15px;
  }

  .notes-section {
    margin-top: 15px;
  }

  .notes-list {
    margin-top: 10px;
    max-height: 150px;
    overflow-y: auto;
  }

  .storage-info {
    margin: 10px 0;
  }

  .storage-actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }

  .content-viewer {
    position: relative;
  }

  pre {
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 4px;
    overflow-x: auto;
    max-height: 300px;
  }

  @media (max-width: 768px) {
    .storage-actions {
      flex-direction: column;
    }

    .storage-actions .el-button {
      width: 100%;
    }
  }
</style>
