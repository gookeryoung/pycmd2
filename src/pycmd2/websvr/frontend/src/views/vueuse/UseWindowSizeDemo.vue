<template>
  <div class="demo-container">
    <h2>VueUse - useWindowSize 窗口尺寸监听</h2>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="12">
        <el-card header="窗口尺寸信息">
          <div class="window-info">
            <el-statistic title="窗口宽度" :value="width" suffix="px" />
            <el-statistic title="窗口高度" :value="height" suffix="px" />
            <el-divider />
            <div class="size-info">
              <p>
                <strong>窗口类型:</strong>
                <el-tag :type="windowType.color">{{ windowType.label }}</el-tag>
              </p>
              <p>
                <strong>屏幕方向:</strong>
                <el-tag :type="orientation === 'landscape' ? 'primary' : 'success'">
                  {{ orientation === 'landscape' ? '横向' : '纵向' }}
                </el-tag>
              </p>
              <p><strong>设备像素比:</strong> {{ pixelRatio }}</p>
              <p><strong>总像素数:</strong> {{ totalPixels.toLocaleString() }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="实时监听控制">
          <div class="listener-controls">
            <h4>监听状态:</h4>
            <el-switch v-model="isListening" active-text="监听中" inactive-text="已暂停" @change="toggleListener" />
            <el-divider />
            <h4>监听选项:</h4>
            <el-checkbox-group v-model="listenOptions">
              <el-checkbox label="width">宽度变化</el-checkbox>
              <el-checkbox label="height">高度变化</el-checkbox>
              <el-checkbox label="orientation">方向变化</el-checkbox>
            </el-checkbox-group>
            <el-divider />
            <h4>更新频率:</h4>
            <el-radio-group v-model="updateFrequency" @change="updateFrequencyChange">
              <el-radio label="realtime">实时</el-radio>
              <el-radio label="throttled">节流 (100ms)</el-radio>
              <el-radio label="debounced">防抖 (300ms)</el-radio>
            </el-radio-group>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="可视化窗口尺寸">
          <div class="window-visualization">
            <div class="visualization-container">
              <div class="window-box" :style="windowBoxStyle">
                <div class="window-content">
                  <p>{{ width }} x {{ height }}</p>
                  <p>{{ windowType.label }}</p>
                </div>
              </div>
            </div>
            <div class="size-changes">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-statistic title="最小宽度" :value="minWidth" suffix="px" />
                </el-col>
                <el-col :span="8">
                  <el-statistic title="最大宽度" :value="maxWidth" suffix="px" />
                </el-col>
                <el-col :span="8">
                  <el-statistic title="平均宽度" :value="avgWidth" suffix="px" />
                </el-col>
              </el-row>
              <el-row :gutter="20" style="margin-top: 10px">
                <el-col :span="8">
                  <el-statistic title="最小高度" :value="minHeight" suffix="px" />
                </el-col>
                <el-col :span="8">
                  <el-statistic title="最大高度" :value="maxHeight" suffix="px" />
                </el-col>
                <el-col :span="8">
                  <el-statistic title="平均高度" :value="avgHeight" suffix="px" />
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="12">
        <el-card header="响应式断点测试">
          <div class="breakpoint-demo">
            <h4>当前断点:</h4>
            <div class="current-breakpoint">
              <el-tag
                v-for="bp in breakpoints"
                :key="bp.name"
                :type="bp.active ? 'primary' : 'info'"
                :effect="bp.active ? 'dark' : 'plain'"
                style="margin: 5px"
              >
                {{ bp.name }} (≥{{ bp.minWidth }}px)
              </el-tag>
            </div>
            <el-divider />
            <h4>响应式布局:</h4>
            <div class="responsive-layout" :class="currentBreakpoint">
              <div class="layout-item">1</div>
              <div class="layout-item">2</div>
              <div class="layout-item">3</div>
              <div class="layout-item">4</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="尺寸变化历史">
          <div class="size-history">
            <el-button @click="clearHistory" type="warning" size="small" style="margin-bottom: 10px">
              清空历史
            </el-button>
            <el-table :data="sizeHistory" height="200" stripe>
              <el-table-column prop="timestamp" label="时间" width="180" />
              <el-table-column prop="width" label="宽度" width="80" />
              <el-table-column prop="height" label="高度" width="80" />
              <el-table-column prop="type" label="变化类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.type === 'both' ? 'primary' : 'info'" size="small">
                    {{ row.type === 'both' ? '全部' : row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="trigger" label="触发器" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="实时图表">
          <div class="size-chart">
            <h4>窗口尺寸变化趋势图:</h4>
            <div class="chart-container">
              <canvas ref="sizeChart" width="800" height="300" />
            </div>
            <div class="chart-controls">
              <el-button @click="toggleChart" type="primary" size="small">
                {{ chartActive ? '暂停图表' : '开始图表' }}
              </el-button>
              <el-button @click="clearChart" type="warning" size="small"> 清空图表 </el-button>
              <el-select v-model="chartType" style="width: 120px; margin-left: 10px">
                <el-option label="宽度" value="width" />
                <el-option label="高度" value="height" />
                <el-option label="全部" value="both" />
              </el-select>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="模拟器">
          <div class="simulator">
            <h4>设备模拟:</h4>
            <el-row :gutter="15">
              <el-col :span="4" v-for="device in devices" :key="device.name">
                <div class="device-card" @click="simulateDevice(device)">
                  <div class="device-preview" :style="device.previewStyle">
                    <div class="device-screen" />
                  </div>
                  <p>{{ device.name }}</p>
                  <small>{{ device.width }}x{{ device.height }}</small>
                </div>
              </el-col>
            </el-row>
            <el-divider />
            <h4>自定义尺寸:</h4>
            <el-row :gutter="15">
              <el-col :span="8">
                <el-input-number v-model="customWidth" :min="200" :max="4000" placeholder="宽度" style="width: 100%" />
              </el-col>
              <el-col :span="8">
                <el-input-number v-model="customHeight" :min="200" :max="4000" placeholder="高度" style="width: 100%" />
              </el-col>
              <el-col :span="8">
                <el-button @click="simulateCustom" type="primary" style="width: 100%"> 应用尺寸 </el-button>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { useDebounceFn, useThrottleFn, useWindowSize } from '@vueuse/core'
  import { ElMessage } from 'element-plus'
  import { computed, onMounted, ref, watch } from 'vue'

  // 全局类型声明
  declare global {
    interface Window {
      readonly innerWidth: number
      readonly innerHeight: number
    }
  }

  // 基础窗口尺寸
  const { width, height } = useWindowSize()

  // 计算属性
  const orientation = computed(() => {
    return width.value > height.value ? 'landscape' : 'portrait'
  })

  const pixelRatio = ref(window.devicePixelRatio || 1)
  const totalPixels = computed(() => width.value * height.value)

  const windowType = computed(() => {
    if (width.value < 576) return { label: '手机', color: 'danger' }
    if (width.value < 768) return { label: '平板', color: 'warning' }
    if (width.value < 992) return { label: '小屏', color: 'info' }
    if (width.value < 1200) return { label: '中屏', color: 'primary' }
    return { label: '大屏', color: 'success' }
  })

  // 监听控制
  const isListening = ref(true)
  const listenOptions = ref(['width', 'height', 'orientation'])
  const updateFrequency = ref('realtime')

  const toggleListener = (enabled: boolean) => {
    if (enabled) {
      ElMessage.success('窗口尺寸监听已开启')
    } else {
      ElMessage.info('窗口尺寸监听已暂停')
    }
  }

  const updateFrequencyChange = () => {
    ElMessage.info(`更新频率已切换为${updateFrequency.value}`)
  }

  // 统计数据
  const minWidth = ref(Infinity)
  const maxWidth = ref(0)
  const minHeight = ref(Infinity)
  const maxHeight = ref(0)
  const widthHistory = ref<number[]>([])
  const heightHistory = ref<number[]>([])

  const avgWidth = computed(() => {
    if (widthHistory.value.length === 0) return 0
    return Math.round(widthHistory.value.reduce((a, b) => a + b, 0) / widthHistory.value.length)
  })

  const avgHeight = computed(() => {
    if (heightHistory.value.length === 0) return 0
    return Math.round(heightHistory.value.reduce((a, b) => a + b, 0) / heightHistory.value.length)
  })

  // 可视化样式
  const windowBoxStyle = computed(() => {
    const scale = Math.min(600 / width.value, 400 / height.value, 1)
    return {
      width: `${width.value * scale}px`,
      height: `${height.value * scale}px`,
      transform: `scale(${scale})`
    }
  })

  // 断点测试
  const breakpoints = computed(() => [
    { name: 'XS', minWidth: 0, active: width.value >= 0 },
    { name: 'SM', minWidth: 576, active: width.value >= 576 },
    { name: 'MD', minWidth: 768, active: width.value >= 768 },
    { name: 'LG', minWidth: 992, active: width.value >= 992 },
    { name: 'XL', minWidth: 1200, active: width.value >= 1200 },
    { name: 'XXL', minWidth: 1400, active: width.value >= 1400 }
  ])

  const currentBreakpoint = computed(() => {
    if (width.value >= 1400) return 'xxl'
    if (width.value >= 1200) return 'xl'
    if (width.value >= 992) return 'lg'
    if (width.value >= 768) return 'md'
    if (width.value >= 576) return 'sm'
    return 'xs'
  })

  // 历史记录
  interface SizeHistoryItem {
    timestamp: string
    width: number
    height: number
    type: string
    trigger: string
  }

  const sizeHistory = ref<SizeHistoryItem[]>([])
  let lastWidth = width.value
  let lastHeight = height.value

  // 图表相关
  const sizeChart = ref<HTMLCanvasElement>()
  const chartActive = ref(false)
  const chartType = ref('both')
  let chartContext: CanvasRenderingContext2D | null = null
  let chartData: Array<{ time: number; width: number; height: number }> = []

  // 设备模拟
  const devices = ref([
    {
      name: 'iPhone 12',
      width: 390,
      height: 844,
      previewStyle: { width: '39px', height: '84px' }
    },
    {
      name: 'iPad',
      width: 768,
      height: 1024,
      previewStyle: { width: '77px', height: '102px' }
    },
    {
      name: 'MacBook',
      width: 1280,
      height: 800,
      previewStyle: { width: '128px', height: '80px' }
    },
    {
      name: '4K显示器',
      width: 3840,
      height: 2160,
      previewStyle: { width: '192px', height: '108px' }
    }
  ])

  const customWidth = ref(1024)
  const customHeight = ref(768)

  // 监听器
  const throttledUpdate = useThrottleFn(() => {
    updateStats()
    addHistory('throttled')
    updateChart()
  }, 100)

  const debouncedUpdate = useDebounceFn(() => {
    updateStats()
    addHistory('debounced')
    updateChart()
  }, 300)

  const updateStats = () => {
    minWidth.value = Math.min(minWidth.value, width.value)
    maxWidth.value = Math.max(maxWidth.value, width.value)
    minHeight.value = Math.min(minHeight.value, height.value)
    maxHeight.value = Math.max(maxHeight.value, height.value)

    widthHistory.value.push(width.value)
    heightHistory.value.push(height.value)

    if (widthHistory.value.length > 100) {
      widthHistory.value.shift()
    }
    if (heightHistory.value.length > 100) {
      heightHistory.value.shift()
    }
  }

  const addHistory = (trigger: string) => {
    let changeType = 'none'
    if (width.value !== lastWidth && height.value !== lastHeight) {
      changeType = 'both'
    } else if (width.value !== lastWidth) {
      changeType = 'width'
    } else if (height.value !== lastHeight) {
      changeType = 'height'
    }

    if (changeType !== 'none') {
      sizeHistory.value.unshift({
        timestamp: new Date().toLocaleString(),
        width: width.value,
        height: height.value,
        type: changeType,
        trigger
      })

      if (sizeHistory.value.length > 20) {
        sizeHistory.value.pop()
      }

      lastWidth = width.value
      lastHeight = height.value
    }
  }

  // 图表绘制
  const initChart = () => {
    if (!sizeChart.value) return
    chartContext = sizeChart.value.getContext('2d')
  }

  const updateChart = () => {
    if (!chartActive.value || !chartContext || !sizeChart.value) return

    const now = Date.now()
    chartData.push({ time: now, width: width.value, height: height.value })

    if (chartData.length > 50) {
      chartData.shift()
    }

    drawChart()
  }

  const drawChart = () => {
    if (!chartContext || !sizeChart.value) return

    const ctx = chartContext
    const canvas = sizeChart.value
    const width = canvas.width
    const height = canvas.height

    ctx.clearRect(0, 0, width, height)

    if (chartData.length < 2) return

    const maxVal = Math.max(
      ...chartData.map(d =>
        chartType.value === 'width' ? d.width : chartType.value === 'height' ? d.height : Math.max(d.width, d.height)
      )
    )
    const minVal = Math.min(
      ...chartData.map(d =>
        chartType.value === 'width' ? d.width : chartType.value === 'height' ? d.height : Math.min(d.width, d.height)
      )
    )
    const range = maxVal - minVal || 1

    const xStep = width / (chartData.length - 1)

    if (chartType.value === 'width' || chartType.value === 'both') {
      ctx.strokeStyle = '#409eff'
      ctx.lineWidth = 2
      ctx.beginPath()
      chartData.forEach((point, index) => {
        const x = index * xStep
        const y = height - ((point.width - minVal) / range) * height * 0.9 - height * 0.05
        if (index === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      })
      ctx.stroke()
    }

    if (chartType.value === 'height' || chartType.value === 'both') {
      ctx.strokeStyle = '#67c23a'
      ctx.lineWidth = 2
      ctx.beginPath()
      chartData.forEach((point, index) => {
        const x = index * xStep
        const y = height - ((point.height - minVal) / range) * height * 0.9 - height * 0.05
        if (index === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      })
      ctx.stroke()
    }
  }

  const toggleChart = () => {
    chartActive.value = !chartActive.value
    if (chartActive.value) {
      ElMessage.success('图表已开启')
      initChart()
      updateChart()
    } else {
      ElMessage.info('图表已暂停')
    }
  }

  const clearChart = () => {
    chartData = []
    if (chartContext && sizeChart.value) {
      chartContext.clearRect(0, 0, sizeChart.value.width, sizeChart.value.height)
    }
    ElMessage.success('图表已清空')
  }

  // 设备模拟
  const simulateDevice = (device: { name: string; width: number; height: number }) => {
    ElMessage.info(`模拟 ${device.name} (${device.width}x${device.height})`)
    // 注意：实际应用中不应该直接改变窗口大小
    // 这里仅用于演示
    Object.defineProperty(window, 'innerWidth', { value: device.width, configurable: true })
    Object.defineProperty(window, 'innerHeight', { value: device.height, configurable: true })
    window.dispatchEvent(new Event('resize'))
  }

  const simulateCustom = () => {
    ElMessage.info(`模拟自定义尺寸 (${customWidth.value}x${customHeight.value})`)
    Object.defineProperty(window, 'innerWidth', { value: customWidth.value, configurable: true })
    Object.defineProperty(window, 'innerHeight', { value: customHeight.value, configurable: true })
    window.dispatchEvent(new Event('resize'))
  }

  const clearHistory = () => {
    sizeHistory.value = []
    ElMessage.success('历史记录已清空')
  }

  // 监听窗口变化
  watch([width, height], () => {
    if (!isListening.value) return

    switch (updateFrequency.value) {
      case 'throttled':
        throttledUpdate()
        break
      case 'debounced':
        debouncedUpdate()
        break
      default:
        updateStats()
        addHistory('realtime')
        updateChart()
    }
  })

  onMounted(() => {
    updateStats()
    initChart()
    addHistory('init')
  })
</script>

<style scoped>
  .demo-container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .demo-section {
    margin-bottom: 24px;
  }

  .window-info {
    text-align: center;
  }

  .size-info {
    text-align: left;
    line-height: 1.8;
  }

  .size-info p {
    margin: 8px 0;
  }

  .listener-controls {
    text-align: center;
  }

  .listener-controls h4 {
    margin-bottom: 10px;
  }

  .window-visualization {
    text-align: center;
  }

  .visualization-container {
    height: 500px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px dashed var(--el-color-primary);
    border-radius: 8px;
    margin-bottom: 20px;
    background: var(--el-fill-color-lighter);
  }

  .window-box {
    border: 2px solid var(--el-color-primary);
    background: white;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .window-content {
    text-align: center;
    font-weight: bold;
    color: var(--el-color-primary);
  }

  .size-changes {
    padding: 20px;
    background: var(--el-fill-color-lighter);
    border-radius: 4px;
  }

  .breakpoint-demo h4 {
    margin-bottom: 10px;
  }

  .current-breakpoint {
    margin-bottom: 15px;
    min-height: 40px;
  }

  .responsive-layout {
    display: grid;
    gap: 10px;
    padding: 15px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 4px;
    background: white;
  }

  .responsive-layout.xs {
    grid-template-columns: 1fr;
  }
  .responsive-layout.sm {
    grid-template-columns: 1fr 1fr;
  }
  .responsive-layout.md {
    grid-template-columns: 1fr 1fr 1fr 1fr;
  }
  .responsive-layout.lg {
    grid-template-columns: repeat(4, 1fr);
  }
  .responsive-layout.xl {
    grid-template-columns: repeat(4, 1fr);
  }
  .responsive-layout.xxl {
    grid-template-columns: repeat(4, 1fr);
  }

  .layout-item {
    height: 60px;
    background: var(--el-color-primary-light-9);
    border: 1px solid var(--el-color-primary-light-7);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: var(--el-color-primary);
  }

  .size-history {
    max-height: 300px;
  }

  .size-chart h4 {
    margin-bottom: 15px;
  }

  .chart-container {
    border: 1px solid var(--el-border-color-light);
    border-radius: 4px;
    margin-bottom: 10px;
    background: white;
  }

  .chart-controls {
    text-align: center;
  }

  .simulator h4 {
    margin-bottom: 15px;
  }

  .device-card {
    text-align: center;
    padding: 10px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
  }

  .device-card:hover {
    border-color: var(--el-color-primary);
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  }

  .device-preview {
    margin: 0 auto 10px;
    border: 2px solid var(--el-color-primary);
    border-radius: 2px;
    position: relative;
    background: var(--el-fill-color-lighter);
  }

  .device-screen {
    width: 100%;
    height: 100%;
    background: var(--el-color-primary-light-9);
  }

  .device-card p {
    margin: 5px 0;
    font-weight: bold;
  }

  .device-card small {
    color: var(--el-text-color-secondary);
  }

  /* 响应式布局 */
  @media (max-width: 768px) {
    .demo-container {
      padding: 0 10px;
    }

    .visualization-container {
      height: 300px;
    }

    .size-changes .el-col {
      margin-bottom: 10px;
    }

    .device-card {
      margin-bottom: 15px;
    }

    .responsive-layout {
      grid-template-columns: 1fr;
    }
  }
</style>
