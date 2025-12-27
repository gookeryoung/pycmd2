<template>
  <div class="echarts-demo">
    <el-container>
      <el-header>
        <h1>Vue ECharts 演示</h1>
        <p>基于 Vue ECharts 组件的数据可视化示例</p>
      </el-header>

      <el-main>
        <el-row :gutter="20">
          <!-- 折线图 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>折线图示例</span>
                  <el-button type="primary" size="small" @click="refreshLineChart" :loading="lineChartLoading">
                    刷新数据
                  </el-button>
                </div>
              </template>
              <VChart class="chart" :option="lineChartOption" :loading="lineChartLoading" autoresize />
            </el-card>
          </el-col>

          <!-- 柱状图 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>柱状图示例</span>
                  <el-button type="primary" size="small" @click="refreshBarChart" :loading="barChartLoading">
                    刷新数据
                  </el-button>
                </div>
              </template>
              <VChart class="chart" :option="barChartOption" :loading="barChartLoading" autoresize />
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <!-- 饼图 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>饼图示例</span>
                  <el-button type="primary" size="small" @click="refreshPieChart" :loading="pieChartLoading">
                    刷新数据
                  </el-button>
                </div>
              </template>
              <VChart class="chart" :option="pieChartOption" :loading="pieChartLoading" autoresize />
            </el-card>
          </el-col>

          <!-- 散点图 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>散点图示例</span>
                  <el-button type="primary" size="small" @click="refreshScatterChart" :loading="scatterChartLoading">
                    刷新数据
                  </el-button>
                </div>
              </template>
              <VChart class="chart" :option="scatterChartOption" :loading="scatterChartLoading" autoresize />
            </el-card>
          </el-col>
        </el-row>

        <el-row style="margin-top: 20px">
          <el-col :span="24">
            <el-card>
              <template #header>
                <span>实时数据演示</span>
                <div style="float: right">
                  <el-button type="primary" size="small" @click="toggleRealTimeChart">
                    {{ realTimeChartActive ? '停止' : '开始' }} 实时更新
                  </el-button>
                </div>
              </template>
              <VChart class="chart" :option="realTimeChartOption" autoresize />
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount } from 'vue'
  import VChart from 'vue-echarts'
  import { use } from 'echarts/core'
  import { LineChart, BarChart, PieChart, ScatterChart } from 'echarts/charts'
  import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    DatasetComponent,
    TransformComponent,
    DataZoomComponent
  } from 'echarts/components'
  import { UniversalTransition } from 'echarts/features'
  import { CanvasRenderer } from 'echarts/renderers'

  // 注册 ECharts 组件
  use([
    LineChart,
    BarChart,
    PieChart,
    ScatterChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    DatasetComponent,
    TransformComponent,
    DataZoomComponent,
    CanvasRenderer,
    UniversalTransition
  ])

  // 响应式变量
  const lineChartLoading = ref(false)
  const barChartLoading = ref(false)
  const pieChartLoading = ref(false)
  const scatterChartLoading = ref(false)
  const realTimeChartActive = ref(false)
  let realTimeInterval: number | null = null

  // 图表配置选项
  const lineChartOption = ref({
    title: {
      text: '月度销售趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['产品A', '产品B'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '产品A',
        type: 'line',
        smooth: true,
        data: [120, 132, 101, 134, 90, 230]
      },
      {
        name: '产品B',
        type: 'line',
        smooth: true,
        data: [220, 182, 191, 234, 290, 330]
      }
    ]
  })

  const barChartOption = ref({
    title: {
      text: '季度销售对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['2023年', '2024年'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: ['Q1', 'Q2', 'Q3', 'Q4']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '2023年',
        type: 'bar',
        data: [120, 200, 150, 80]
      },
      {
        name: '2024年',
        type: 'bar',
        data: [150, 230, 180, 120]
      }
    ]
  })

  const pieChartOption = ref({
    title: {
      text: '产品销售占比',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '销售占比',
        type: 'pie',
        radius: '60%',
        data: [
          { value: 1048, name: '电子产品' },
          { value: 735, name: '服装配饰' },
          { value: 580, name: '家居用品' },
          { value: 484, name: '食品饮料' },
          { value: 300, name: '其他' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  })

  const scatterChartOption = ref({
    title: {
      text: '身高体重分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: { value: number[] }) => {
        return `身高: ${params.value[0]}cm<br/>体重: ${params.value[1]}kg`
      }
    },
    xAxis: {
      type: 'value',
      name: '身高(cm)',
      scale: true
    },
    yAxis: {
      type: 'value',
      name: '体重(kg)',
      scale: true
    },
    series: [
      {
        name: '男性',
        type: 'scatter',
        data: generateScatterData(165, 180, 55, 80, 50)
      },
      {
        name: '女性',
        type: 'scatter',
        data: generateScatterData(155, 170, 45, 70, 50)
      }
    ]
  })

  const realTimeChartOption = ref({
    title: {
      text: '实时数据监控',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['CPU使用率', '内存使用率'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 20 }, () => '')
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: 'CPU使用率',
        type: 'line',
        smooth: true,
        data: generateRandomArray(20, 50)
      },
      {
        name: '内存使用率',
        type: 'line',
        smooth: true,
        data: generateRandomArray(20, 70)
      }
    ]
  })

  // 生成随机数组的工具函数
  function generateRandomArray(length: number, max: number): number[] {
    return Array.from({ length }, () => Math.round(Math.random() * max))
  }

  // 生成散点数据
  function generateScatterData(xMin: number, xMax: number, yMin: number, yMax: number, count: number) {
    return Array.from({ length: count }, () => [
      Math.round(xMin + Math.random() * (xMax - xMin)),
      Math.round(yMin + Math.random() * (yMax - yMin))
    ])
  }

  // 刷新折线图数据
  function refreshLineChart() {
    lineChartLoading.value = true
    setTimeout(() => {
      if (lineChartOption.value.series && lineChartOption.value.series[0] && lineChartOption.value.series[1]) {
        lineChartOption.value.series[0].data = generateRandomArray(6, 300)
        lineChartOption.value.series[1].data = generateRandomArray(6, 400)
      }
      lineChartLoading.value = false
    }, 1000)
  }

  // 刷新柱状图数据
  function refreshBarChart() {
    barChartLoading.value = true
    setTimeout(() => {
      if (barChartOption.value.series && barChartOption.value.series[0] && barChartOption.value.series[1]) {
        barChartOption.value.series[0].data = generateRandomArray(4, 250)
        barChartOption.value.series[1].data = generateRandomArray(4, 350)
      }
      barChartLoading.value = false
    }, 1000)
  }

  // 刷新饼图数据
  function refreshPieChart() {
    pieChartLoading.value = true
    setTimeout(() => {
      if (pieChartOption.value.series && pieChartOption.value.series[0]) {
        const data = [
          { value: Math.round(Math.random() * 1000), name: '电子产品' },
          { value: Math.round(Math.random() * 800), name: '服装配饰' },
          { value: Math.round(Math.random() * 700), name: '家居用品' },
          { value: Math.round(Math.random() * 600), name: '食品饮料' },
          { value: Math.round(Math.random() * 500), name: '其他' }
        ]
        pieChartOption.value.series[0].data = data
      }
      pieChartLoading.value = false
    }, 1000)
  }

  // 刷新散点图数据
  function refreshScatterChart() {
    scatterChartLoading.value = true
    setTimeout(() => {
      if (scatterChartOption.value.series && scatterChartOption.value.series[0] && scatterChartOption.value.series[1]) {
        scatterChartOption.value.series[0].data = generateScatterData(165, 180, 55, 80, 50)
        scatterChartOption.value.series[1].data = generateScatterData(155, 170, 45, 70, 50)
      }
      scatterChartLoading.value = false
    }, 1000)
  }

  // 生成时间标签字符串
  function generateTimeLabel(date: Date): string {
    return `${date.getHours().toString().padStart(2, '0')}:${date
      .getMinutes()
      .toString()
      .padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
  }

  // 切换实时图表
  function toggleRealTimeChart() {
    // 如果已经有定时器运行，先清除
    if (realTimeInterval) {
      clearInterval(realTimeInterval)
      realTimeInterval = null
    }

    realTimeChartActive.value = !realTimeChartActive.value

    if (realTimeChartActive.value) {
      realTimeInterval = setInterval(() => {
        const cpuData = realTimeChartOption.value.series[0]?.data
        const memData = realTimeChartOption.value.series[1]?.data
        const xAxisData = realTimeChartOption.value.xAxis?.data

        // 移除第一个数据点，添加新数据点
        if (cpuData) {
          cpuData.shift()
          cpuData.push(Math.round(Math.random() * 100))
        }

        if (memData) {
          memData.shift()
          memData.push(Math.round(Math.random() * 100))
        }

        // 更新X轴时间标签
        if (xAxisData) {
          const now = new Date()
          xAxisData.shift()
          xAxisData.push(generateTimeLabel(now))
        }
      }, 1000)
    }
  }

  // 组件挂载时初始化
  onMounted(() => {
    // 可以在这里进行初始化操作
  })

  // 组件卸载前清理定时器
  onBeforeUnmount(() => {
    if (realTimeInterval) {
      clearInterval(realTimeInterval)
      realTimeInterval = null
    }
  })
</script>

<style scoped>
  .echarts-demo {
    padding: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .chart {
    height: 300px;
    width: 100%;
  }

  .el-card {
    margin-bottom: 20px;
  }
</style>
