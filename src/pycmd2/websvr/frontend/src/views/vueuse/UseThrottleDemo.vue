<template>
  <div class="throttle-demo">
    <el-card header="useThrottleFn - 节流函数">
      <el-alert
        title="VueUse useThrottleFn 示例"
        type="info"
        :closable="false"
        description="节流函数可以限制函数的执行频率，在指定时间内最多执行一次。"
        style="margin-bottom: 20px"
      />

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" class="mouse-card">
            <template #header>
              <div class="card-header">
                <el-icon><Mouse /></el-icon>
                <span>鼠标移动节流</span>
              </div>
            </template>

            <div class="mouse-tracking" @mousemove="handleMouseMove">
              <div class="tracking-area">
                <p>在此区域移动鼠标</p>
                <div class="mouse-position">
                  <el-descriptions :column="1" size="small" border>
                    <el-descriptions-item label="原始移动次数">
                      <el-tag type="danger">{{ mouseMoveCount }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="节流后执行次数">
                      <el-tag type="success">{{ throttledMoveCount }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="当前坐标">
                      <el-tag>X: {{ mouseX }}, Y: {{ mouseY }}</el-tag>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </div>

              <div class="control-panel">
                <el-form label-width="100px" size="small">
                  <el-form-item label="节流延迟">
                    <el-slider
                      v-model="throttleDelay"
                      :min="50"
                      :max="1000"
                      :step="50"
                      show-input
                      @change="updateThrottle"
                    />
                  </el-form-item>
                </el-form>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover" class="scroll-card">
            <template #header>
              <div class="card-header">
                <el-icon><TopRight /></el-icon>
                <span>滚动事件节流</span>
              </div>
            </template>

            <div class="scroll-container" @scroll="handleScroll">
              <div class="scroll-content">
                <div v-for="i in 20" :key="i" class="scroll-item">滚动项目 {{ i }}</div>
              </div>

              <div class="scroll-info">
                <el-descriptions :column="1" size="small" border>
                  <el-descriptions-item label="滚动次数">
                    <el-tag>{{ scrollCount }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="节流后次数">
                    <el-tag type="success">{{ throttledScrollCount }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="滚动位置">
                    <el-tag>{{ scrollPosition }}px</el-tag>
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
                <el-icon><Crankshaft /></el-icon>
                <span>按钮点击节流</span>
              </div>
            </template>

            <div class="button-demo">
              <el-space>
                <el-button type="primary" @click="handleRapidClick" :disabled="isThrottled">
                  <el-icon><Pointer /></el-icon>
                  节流按钮 ({{ throttleDelay }}ms)
                </el-button>

                <el-button @click="handleLeadingClick"> 首次立即执行 </el-button>

                <el-button @click="handleTrailingClick"> 结尾执行 </el-button>

                <el-button @click="resetCounters">
                  <el-icon><Refresh /></el-icon>
                  重置计数
                </el-button>
              </el-space>

              <div class="click-info">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <el-statistic title="总点击次数" :value="clickCount" />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic title="实际执行次数" :value="executeCount" />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic title="节省次数" :value="clickCount - executeCount" value-style="color: #f56c6c" />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic
                      title="节省率"
                      :value="clickCount > 0 ? Math.round(((clickCount - executeCount) / clickCount) * 100) : 0"
                      suffix="%"
                      value-style="color: #67c23a"
                    />
                  </el-col>
                </el-row>
              </div>

              <div class="click-log">
                <h4>点击日志:</h4>
                <div class="log-container">
                  <el-tag v-for="(log, index) in clickLogs" :key="index" :type="log.type" class="log-item">
                    {{ log.message }}
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
                <el-icon><DataLine /></el-icon>
                <span>性能对比分析</span>
              </div>
            </template>

            <div class="performance-analysis">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="analysis-card">
                    <h4>鼠标移动</h4>
                    <el-progress
                      type="circle"
                      :percentage="mouseMoveCount > 0 ? Math.round((throttledMoveCount / mouseMoveCount) * 100) : 0"
                      :width="100"
                    />
                    <p>
                      优化率:
                      {{
                        mouseMoveCount > 0
                          ? Math.round(((mouseMoveCount - throttledMoveCount) / mouseMoveCount) * 100)
                          : 0
                      }}%
                    </p>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="analysis-card">
                    <h4>滚动事件</h4>
                    <el-progress
                      type="circle"
                      :percentage="scrollCount > 0 ? Math.round((throttledScrollCount / scrollCount) * 100) : 0"
                      :width="100"
                    />
                    <p>
                      优化率:
                      {{
                        scrollCount > 0 ? Math.round(((scrollCount - throttledScrollCount) / scrollCount) * 100) : 0
                      }}%
                    </p>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="analysis-card">
                    <h4>按钮点击</h4>
                    <el-progress
                      type="circle"
                      :percentage="clickCount > 0 ? Math.round((executeCount / clickCount) * 100) : 0"
                      :width="100"
                    />
                    <p>
                      优化率:
                      {{ clickCount > 0 ? Math.round(((clickCount - executeCount) / clickCount) * 100) : 0 }}%
                    </p>
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
  import { useThrottleFn } from '@vueuse/core'
  import { ref } from 'vue'
  import { Mouse, TopRight, Pointer, Refresh, DataLine } from '@element-plus/icons-vue'

  // 节流延迟
  const throttleDelay = ref(200)

  // 鼠标移动相关
  const mouseMoveCount = ref(0)
  const throttledMoveCount = ref(0)
  const mouseX = ref(0)
  const mouseY = ref(0)

  // 滚动相关
  const scrollCount = ref(0)
  const throttledScrollCount = ref(0)
  const scrollPosition = ref(0)

  // 按钮点击相关
  const clickCount = ref(0)
  const executeCount = ref(0)
  const isThrottled = ref(false)
  const clickLogs = ref<Array<{ message: string; type: string }>>([])

  // 节流函数 - 鼠标移动
  const throttledMouseMove = useThrottleFn((event: MouseEvent) => {
    throttledMoveCount.value++
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
    mouseX.value = Math.round(event.clientX - rect.left)
    mouseY.value = Math.round(event.clientY - rect.top)
  }, throttleDelay.value)

  // 节流函数 - 滚动
  const throttledScroll = useThrottleFn((event: Event) => {
    throttledScrollCount.value++
    scrollPosition.value = (event.target as HTMLElement).scrollTop
  }, throttleDelay.value)

  // 节流函数 - 按钮点击
  const throttledClick = useThrottleFn(() => {
    executeCount.value++
    isThrottled.value = true
    clickLogs.value.unshift({
      message: `执行 #${executeCount.value}`,
      type: 'success'
    })

    setTimeout(() => {
      isThrottled.value = false
    }, throttleDelay.value)
  }, throttleDelay.value)

  // 首次立即执行的节流函数
  const leadingThrottledClick = useThrottleFn(
    () => {
      executeCount.value++
      clickLogs.value.unshift({
        message: `立即执行 #${executeCount.value}`,
        type: 'primary'
      })
    },
    throttleDelay.value,
    false, // trailing 设置为 false
    true // leading 设置为 true
  )

  // 结尾执行的节流函数
  const trailingThrottledClick = useThrottleFn(
    () => {
      executeCount.value++
      clickLogs.value.unshift({
        message: `结尾执行 #${executeCount.value}`,
        type: 'warning'
      })
    },
    throttleDelay.value,
    true, // trailing 设置为 true
    false // leading 设置为 false
  )

  // 更新节流延迟
  const updateThrottle = () => {
    // 在实际应用中，这里需要重新创建节流函数
  }

  // 处理鼠标移动
  const handleMouseMove = (event: MouseEvent) => {
    mouseMoveCount.value++
    throttledMouseMove(event)
  }

  // 处理滚动
  const handleScroll = (event: Event) => {
    scrollCount.value++
    throttledScroll(event)
  }

  // 处理快速点击
  const handleRapidClick = () => {
    clickCount.value++
    throttledClick()
  }

  // 处理首次立即点击
  const handleLeadingClick = () => {
    clickCount.value++
    leadingThrottledClick()
  }

  // 处理结尾点击
  const handleTrailingClick = () => {
    clickCount.value++
    trailingThrottledClick()
  }

  // 重置计数器
  const resetCounters = () => {
    mouseMoveCount.value = 0
    throttledMoveCount.value = 0
    scrollCount.value = 0
    throttledScrollCount.value = 0
    clickCount.value = 0
    executeCount.value = 0
    clickLogs.value = []
    mouseX.value = 0
    mouseY.value = 0
    scrollPosition.value = 0
  }
</script>

<style scoped>
  .throttle-demo {
    padding: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .mouse-card,
  .scroll-card {
    height: 100%;
  }

  .mouse-tracking {
    height: 100%;
  }

  .tracking-area {
    height: 200px;
    border: 2px dashed #409eff;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    margin-bottom: 20px;
    background:
      linear-gradient(45deg, #f0f9ff 25%, transparent 25%), linear-gradient(-45deg, #f0f9ff 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #f0f9ff 75%), linear-gradient(-45deg, transparent 75%, #f0f9ff 75%);
    background-size: 20px 20px;
    background-position:
      0 0,
      0 10px,
      10px -10px,
      -10px 0px;
  }

  .mouse-position {
    background: rgba(255, 255, 255, 0.9);
    padding: 15px;
    border-radius: 8px;
    backdrop-filter: blur(5px);
  }

  .scroll-container {
    height: 250px;
    border: 1px solid #dcdfe6;
    border-radius: 8px;
    overflow-y: auto;
    position: relative;
  }

  .scroll-content {
    padding: 20px;
  }

  .scroll-item {
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
    background: var(--el-color-primary-light-9);
    border-radius: 4px;
  }

  .scroll-info {
    position: sticky;
    bottom: 0;
    background: var(--el-bg-color);
    padding: 15px;
    border-top: 1px solid var(--el-border-color);
    backdrop-filter: blur(5px);
  }

  .control-panel {
    padding: 10px 0;
  }

  .button-demo {
    padding: 20px 0;
  }

  .click-info {
    margin: 20px 0;
  }

  .click-log {
    margin-top: 20px;
  }

  .click-log h4 {
    margin-bottom: 10px;
  }

  .log-container {
    max-height: 200px;
    overflow-y: auto;
    padding: 10px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
  }

  .log-item {
    margin: 5px;
    display: inline-block;
  }

  .performance-analysis {
    padding: 20px 0;
  }

  .analysis-card {
    text-align: center;
    padding: 20px;
  }

  .analysis-card h4 {
    margin-bottom: 15px;
  }

  .analysis-card p {
    margin-top: 10px;
    color: var(--el-text-color-secondary);
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .tracking-area {
      height: 150px;
    }

    .scroll-container {
      height: 200px;
    }

    .log-container {
      max-height: 150px;
    }
  }
</style>
