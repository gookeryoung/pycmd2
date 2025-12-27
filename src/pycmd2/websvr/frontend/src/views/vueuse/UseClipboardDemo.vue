<template>
  <div class="clipboard-demo">
    <el-card header="useClipboard - 剪贴板操作">
      <el-alert
        title="VueUse useClipboard 示例"
        type="info"
        :closable="false"
        description="安全地读写剪贴板内容，支持权限检查和错误处理。"
        style="margin-bottom: 20px"
      />

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" class="copy-card">
            <template #header>
              <div class="card-header">
                <el-icon><CopyDocument /></el-icon>
                <span>复制文本</span>
              </div>
            </template>

            <div class="copy-section">
              <el-form label-width="80px">
                <el-form-item label="内容">
                  <el-input v-model="textToCopy" type="textarea" :rows="4" placeholder="输入要复制的内容..." />
                </el-form-item>

                <el-form-item>
                  <el-button
                    @click="copy(textToCopy)"
                    type="primary"
                    :disabled="!textToCopy.trim()"
                    :loading="isSupported && isCopying"
                  >
                    <el-icon><CopyDocument /></el-icon>
                    {{ isSupported ? '复制到剪贴板' : '浏览器不支持' }}
                  </el-button>
                </el-form-item>
              </el-form>

              <div class="quick-copy">
                <h4>快速复制:</h4>
                <el-space>
                  <el-button @click="copy('Hello, VueUse!')">复制问候语</el-button>
                  <el-button @click="copy('https://vueuse.org')">复制网址</el-button>
                  <el-button @click="copy('vue@latest')">复制包名</el-button>
                </el-space>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover" class="paste-card">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>剪贴板内容</span>
              </div>
            </template>

            <div class="paste-section">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="支持状态">
                  <el-tag :type="isSupported ? 'success' : 'danger'">
                    {{ isSupported ? '支持' : '不支持' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="权限状态">
                  <el-tag :type="permission === 'granted' ? 'success' : 'warning'">
                    {{ permission || '未知' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="复制状态">
                  <el-tag :type="copied ? 'success' : 'info'">
                    {{ copied ? '已复制' : '等待复制' }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <div class="clipboard-content">
                <h4>剪贴板内容:</h4>
                <el-input
                  v-model="clipboardContent"
                  type="textarea"
                  :rows="4"
                  placeholder="剪贴板内容将显示在这里..."
                  readonly
                />
              </div>

              <el-button @click="readFromClipboard" type="success" style="margin-top: 10px">
                <el-icon><View /></el-icon>
                读取剪贴板
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><DataBoard /></el-icon>
                <span>高级功能演示</span>
              </div>
            </template>

            <div class="advanced-features">
              <el-tabs>
                <el-tab-pane label="复制 HTML" name="html">
                  <div class="html-copy">
                    <el-form label-width="100px">
                      <el-form-item label="HTML 内容">
                        <el-input
                          v-model="htmlContent"
                          type="textarea"
                          :rows="3"
                          placeholder="<b>粗体</b> <i>斜体</i>"
                        />
                      </el-form-item>
                      <el-form-item label="纯文本">
                        <el-input v-model="plainText" placeholder="对应的纯文本内容" />
                      </el-form-item>
                      <el-form-item>
                        <el-button @click="copyHtml" type="primary">复制 HTML</el-button>
                      </el-form-item>
                    </el-form>
                  </div>
                </el-tab-pane>

                <el-tab-pane label="复制图片" name="image">
                  <div class="image-copy">
                    <el-form label-width="100px">
                      <el-form-item label="图片 URL">
                        <el-input v-model="imageUrl" placeholder="https://example.com/image.png" />
                      </el-form-item>
                      <el-form-item>
                        <el-button @click="copyImage" type="primary">复制图片</el-button>
                      </el-form-item>
                    </el-form>

                    <div class="image-preview" v-if="imageUrl">
                      <img :src="imageUrl" alt="预览图片" style="max-width: 200px; max-height: 200px" />
                    </div>
                  </div>
                </el-tab-pane>

                <el-tab-pane label="复制表格数据" name="table">
                  <div class="table-copy">
                    <el-table :data="tableData" style="width: 100%">
                      <el-table-column prop="name" label="姓名" />
                      <el-table-column prop="age" label="年龄" />
                      <el-table-column prop="city" label="城市" />
                      <el-table-column label="操作">
                        <template #default="scope">
                          <el-button @click="copyTableRow(scope.row)" size="small"> 复制行 </el-button>
                        </template>
                      </el-table-column>
                    </el-table>

                    <el-button @click="copyTableData" type="primary" style="margin-top: 10px">
                      <el-icon><CopyDocument /></el-icon>
                      复制整个表格
                    </el-button>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Monitor /></el-icon>
                <span>操作历史</span>
              </div>
            </template>

            <div class="history">
              <el-timeline>
                <el-timeline-item
                  v-for="(item, index) in history"
                  :key="index"
                  :timestamp="item.timestamp"
                  :type="item.type"
                >
                  <div class="history-item">
                    <strong>{{ item.action }}:</strong>
                    <code>{{ truncateText(item.content, 50) }}</code>
                  </div>
                </el-timeline-item>
              </el-timeline>

              <el-button @click="clearHistory" size="small" style="margin-top: 10px"> 清除历史 </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { useClipboard, usePermission } from '@vueuse/core'
  import { ref } from 'vue'
  import { CopyDocument, Document, View, DataBoard, Monitor } from '@element-plus/icons-vue'
  import { ElMessage } from 'element-plus'

  interface RowData {
    name: string
    age: number
    city: string
  }

  // 剪贴板功能
  const { copy: rawCopy, copied, isSupported } = useClipboard()

  // 复制状态
  const isCopying = ref(false)

  // 带有加载状态的复制方法
  const copy = async (text: string) => {
    if (!isSupported.value) {
      ElMessage.error('浏览器不支持剪贴板 API')
      return
    }

    isCopying.value = true
    try {
      await rawCopy(text)
      ElMessage.success('复制成功')
    } catch (error) {
      ElMessage.error('复制失败: ' + error)
    } finally {
      isCopying.value = false
    }
  }

  // 剪贴板权限
  const permission = usePermission('clipboard-read')

  // 基础状态
  const textToCopy = ref('Hello from VueUse!')
  const clipboardContent = ref('')
  const history = ref<
    Array<{
      action: string
      content: string
      timestamp: string
      type: 'primary' | 'success' | 'warning' | 'danger'
    }>
  >([])

  // 高级功能状态
  const htmlContent = ref('<b>粗体文本</b> 和 <i>斜体文本</i>')
  const plainText = ref('粗体文本 和 斜体文本')
  const imageUrl = ref('https://vueuse.org/logo.svg')

  // 表格数据
  const tableData = ref([
    { name: '张三', age: 25, city: '北京' },
    { name: '李四', age: 30, city: '上海' },
    { name: '王五', age: 28, city: '广州' }
  ])

  // 读取剪贴板内容
  const readFromClipboard = async () => {
    try {
      if (!isSupported.value) {
        ElMessage.error('浏览器不支持剪贴板 API')
        return
      }

      const text = await navigator.clipboard.readText()
      clipboardContent.value = text

      addToHistory('读取', text, 'success')
      ElMessage.success('剪贴板内容已读取')
    } catch (error) {
      ElMessage.error('读取剪贴板失败: ' + error)
      addToHistory('读取失败', String(error), 'danger')
    }
  }

  // 复制 HTML 内容
  const copyHtml = async () => {
    try {
      if (!isSupported.value) {
        ElMessage.error('浏览器不支持剪贴板 API')
        return
      }

      const htmlItem = new ClipboardItem({
        'text/html': new Blob([htmlContent.value], { type: 'text/html' }),
        'text/plain': new Blob([plainText.value], { type: 'text/plain' })
      })

      await navigator.clipboard.write([htmlItem])

      addToHistory('复制 HTML', htmlContent.value, 'success')
      ElMessage.success('HTML 内容已复制到剪贴板')
    } catch (error) {
      ElMessage.error('复制 HTML 失败: ' + error)
      addToHistory('复制 HTML 失败', String(error), 'danger')
    }
  }

  // 复制图片
  const copyImage = async () => {
    try {
      if (!imageUrl.value) {
        ElMessage.warning('请输入图片 URL')
        return
      }

      const response = await fetch(imageUrl.value)
      const blob = await response.blob()

      const imageItem = new ClipboardItem({
        [blob.type]: blob
      })

      await navigator.clipboard.write([imageItem])

      addToHistory('复制图片', imageUrl.value, 'success')
      ElMessage.success('图片已复制到剪贴板')
    } catch (error) {
      ElMessage.error('复制图片失败: ' + error)
      addToHistory('复制图片失败', String(error), 'danger')
    }
  }

  // 复制表格行
  const copyTableRow = (row: RowData) => {
    const text = `${row.name}, ${row.age}, ${row.city}`
    copy(text)
    addToHistory('复制行', text, 'success')
  }

  // 复制整个表格
  const copyTableData = () => {
    const headers = ['姓名', '年龄', '城市']
    const rows = tableData.value.map(row => [row.name, row.age, row.city])

    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')

    copy(csvContent)
    addToHistory('复制表格', csvContent, 'success')
  }

  // 添加到历史记录
  const addToHistory = (action: string, content: string, type: 'primary' | 'success' | 'warning' | 'danger') => {
    history.value.unshift({
      action,
      content,
      timestamp: new Date().toLocaleTimeString(),
      type
    })

    // 限制历史记录数量
    if (history.value.length > 10) {
      history.value = history.value.slice(0, 10)
    }
  }

  // 截断文本
  const truncateText = (text: string, maxLength: number) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
  }

  // 清除历史
  const clearHistory = () => {
    history.value = []
  }
</script>

<style scoped>
  .clipboard-demo {
    padding: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .copy-card,
  .paste-card {
    height: 100%;
  }

  .copy-section,
  .paste-section {
    padding: 10px 0;
  }

  .quick-copy {
    margin-top: 20px;
  }

  .quick-copy h4 {
    margin-bottom: 10px;
  }

  .clipboard-content {
    margin-top: 20px;
  }

  .clipboard-content h4 {
    margin-bottom: 10px;
  }

  .advanced-features {
    padding: 20px 0;
  }

  .html-copy,
  .image-copy,
  .table-copy {
    padding: 20px 0;
  }

  .image-preview {
    margin-top: 20px;
    text-align: center;
  }

  .history {
    padding: 20px 0;
  }

  .history-item {
    font-family: 'Courier New', monospace;
    font-size: 14px;
  }

  .history-item code {
    background: var(--el-fill-color-lighter);
    padding: 2px 6px;
    border-radius: 4px;
    margin-left: 8px;
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .quick-copy .el-space {
      flex-direction: column;
      width: 100%;
    }

    .quick-copy .el-button {
      width: 100%;
    }
  }
</style>
