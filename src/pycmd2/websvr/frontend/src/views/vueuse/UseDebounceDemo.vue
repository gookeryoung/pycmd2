<template>
  <div class="debounce-demo">
    <el-card header="useDebounceFn - 防抖函数">
      <el-alert
        title="VueUse useDebounceFn 示例"
        type="info"
        :closable="false"
        description="防抖函数可以延迟执行函数，在指定时间内多次调用只会执行最后一次。"
        style="margin-bottom: 20px"
      />

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" class="input-card">
            <template #header>
              <div class="card-header">
                <el-icon><EditPen /></el-icon>
                <span>搜索输入框</span>
              </div>
            </template>

            <div class="input-section">
              <el-form>
                <el-form-item label="搜索内容">
                  <el-input v-model="searchInput" placeholder="输入搜索内容..." @input="handleSearch" clearable />
                </el-form-item>

                <el-form-item label="防抖延迟">
                  <el-slider
                    v-model="debounceDelay"
                    :min="100"
                    :max="2000"
                    :step="100"
                    show-input
                    @change="updateDebouncedSearch"
                  />
                </el-form-item>

                <el-form-item label="输入状态">
                  <el-tag :type="isTyping ? 'warning' : 'success'">
                    {{ isTyping ? '正在输入...' : '输入完成' }}
                  </el-tag>
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover" class="result-card">
            <template #header>
              <div class="card-header">
                <el-icon><Search /></el-icon>
                <span>搜索结果</span>
              </div>
            </template>

            <div class="result-section">
              <div class="result-info">
                <p><strong>原始输入值:</strong> {{ searchInput || '(空)' }}</p>
                <p><strong>防抖后的值:</strong> {{ debouncedValue || '(空)' }}</p>
                <p><strong>搜索次数:</strong> {{ searchCount }}</p>
                <p><strong>实际执行次数:</strong> {{ actualSearchCount }}</p>
              </div>

              <el-divider />

              <div class="mock-results">
                <h4>模拟搜索结果:</h4>
                <el-empty v-if="!debouncedValue" description="请输入搜索内容" :image-size="100" />
                <div v-else class="result-list">
                  <el-tag v-for="(result, index) in searchResults" :key="index" class="result-item">
                    {{ result }}
                  </el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Operation /></el-icon>
                <span>按钮防抖示例</span>
              </div>
            </template>

            <div class="button-demo">
              <el-space>
                <el-button type="primary" @click="handleButtonClick" :loading="buttonLoading">
                  防抖按钮 ({{ debounceDelay }}ms)
                </el-button>

                <el-button @click="handleImmediateClick"> 立即执行按钮 </el-button>

                <el-button @click="handleReset">
                  <el-icon><Refresh /></el-icon>
                  重置计数
                </el-button>
              </el-space>

              <div class="button-info">
                <el-descriptions :column="4" border>
                  <el-descriptions-item label="按钮点击次数">
                    <el-tag>{{ buttonClickCount }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="实际执行次数">
                    <el-tag type="success">{{ buttonExecuteCount }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="节省执行次数">
                    <el-tag type="warning">{{ buttonClickCount - buttonExecuteCount }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="节省率">
                    <el-tag type="info">
                      {{ Math.round(((buttonClickCount - buttonExecuteCount) / buttonClickCount) * 100) }}%
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Timer /></el-icon>
                <span>性能对比</span>
              </div>
            </template>

            <div class="performance-chart">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-item">
                    <h4>无防抖 - 每次输入都触发</h4>
                    <el-progress :percentage="100" status="exception" :stroke-width="10" />
                    <p>输入次数: {{ searchCount }} | 执行次数: {{ searchCount }}</p>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-item">
                    <h4>有防抖 - 只执行最后一次</h4>
                    <el-progress
                      :percentage="searchCount > 0 ? Math.round((actualSearchCount / searchCount) * 100) : 0"
                      status="success"
                      :stroke-width="10"
                    />
                    <p>输入次数: {{ searchCount }} | 执行次数: {{ actualSearchCount }}</p>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { useDebounceFn } from '@vueuse/core'
  import { ref } from 'vue'
  import { EditPen, Search, Operation, Refresh, Timer } from '@element-plus/icons-vue'

  // 搜索相关状态
  const searchInput = ref('')
  const debouncedValue = ref('')
  const searchCount = ref(0)
  const actualSearchCount = ref(0)
  const isTyping = ref(false)
  const debounceDelay = ref(500)

  // 按钮相关状态
  const buttonClickCount = ref(0)
  const buttonExecuteCount = ref(0)
  const buttonLoading = ref(false)

  // 模拟搜索结果
  const searchResults = ref<string[]>([])

  // 防抖搜索函数
  const debouncedSearch = useDebounceFn((value: string) => {
    actualSearchCount.value++
    debouncedValue.value = value
    isTyping.value = false

    // 模拟搜索结果
    if (value.trim()) {
      searchResults.value = [
        `${value} - 结果 1`,
        `${value} - 结果 2`,
        `${value} - 结果 3`,
        `${value} - 相关建议`,
        `${value} - 热门内容`
      ]
    } else {
      searchResults.value = []
    }
  }, debounceDelay.value)

  // 防抖按钮点击函数
  const debouncedButtonClick = useDebounceFn(() => {
    buttonExecuteCount.value++
    buttonLoading.value = true

    // 模拟异步操作
    setTimeout(() => {
      buttonLoading.value = false
    }, 500)
  }, debounceDelay.value)

  // 立即执行的防抖函数
  const immediateDebouncedClick = useDebounceFn(
    () => {
      buttonExecuteCount.value++
      console.log('立即执行点击')
    },
    debounceDelay.value,
    { maxWait: 100 }
  )

  // 更新防抖延迟
  const updateDebouncedSearch = () => {
    // 这里重新创建防抖函数（在实际项目中可能需要更复杂的处理）
  }

  // 处理搜索输入
  const handleSearch = (value: string) => {
    searchCount.value++
    isTyping.value = true
    debouncedSearch(value)
  }

  // 处理按钮点击
  const handleButtonClick = () => {
    buttonClickCount.value++
    debouncedButtonClick()
  }

  // 处理立即点击
  const handleImmediateClick = () => {
    buttonClickCount.value++
    immediateDebouncedClick()
  }

  // 重置计数
  const handleReset = () => {
    searchCount.value = 0
    actualSearchCount.value = 0
    buttonClickCount.value = 0
    buttonExecuteCount.value = 0
    searchResults.value = []
  }
</script>

<style scoped>
  .debounce-demo {
    padding: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .input-card,
  .result-card {
    height: 100%;
  }

  .input-section,
  .result-section {
    padding: 10px 0;
  }

  .result-info {
    margin-bottom: 20px;
  }

  .result-info p {
    margin: 5px 0;
  }

  .mock-results h4 {
    margin-bottom: 15px;
  }

  .result-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .result-item {
    margin: 5px 0;
  }

  .button-demo {
    padding: 20px 0;
  }

  .button-info {
    margin-top: 20px;
  }

  .performance-chart {
    padding: 20px 0;
  }

  .chart-item {
    text-align: center;
    padding: 20px;
  }

  .chart-item h4 {
    margin-bottom: 15px;
  }

  .chart-item p {
    margin-top: 10px;
    color: var(--el-text-color-secondary);
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .input-section,
    .result-section {
      padding: 5px 0;
    }

    .button-demo {
      padding: 10px 0;
    }

    .performance-chart {
      padding: 10px 0;
    }

    .chart-item {
      padding: 10px;
    }
  }
</style>
