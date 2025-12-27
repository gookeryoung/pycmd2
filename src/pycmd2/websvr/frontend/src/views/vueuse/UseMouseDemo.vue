<template>
  <div class="mouse-demo">
    <el-card header="useMouse - 鼠标位置跟踪">
      <el-alert
        title="VueUse useMouse 示例"
        type="info"
        :closable="false"
        description="实时跟踪鼠标的位置坐标，支持页面和相对坐标。"
        style="margin-bottom: 20px"
      />

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" class="info-card">
            <template #header>
              <div class="card-header">
                <el-icon><Mouse /></el-icon>
                <span>鼠标坐标</span>
              </div>
            </template>

            <el-descriptions :column="1" border>
              <el-descriptions-item label="页面 X 坐标">
                <el-tag type="primary">{{ mouse.x }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="页面 Y 坐标">
                <el-tag type="primary">{{ mouse.y }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="源类型">
                <el-tag :type="mouse.sourceType.value === 'mouse' ? 'success' : 'warning'">
                  {{ mouse.sourceType }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover" class="info-card">
            <template #header>
              <div class="card-header">
                <el-icon><Position /></el-icon>
                <span>元素相对坐标</span>
              </div>
            </template>

            <div ref="targetRef" class="mouse-tracking-area">
              <div class="tracking-info">
                <p>在此区域内移动鼠标</p>
                <el-descriptions :column="1" size="small">
                  <el-descriptions-item label="相对 X 坐标">
                    <el-tag>{{ relativePos.x }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="相对 Y 坐标">
                    <el-tag>{{ relativePos.y }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="是否在元素内">
                    <el-tag :type="isOutside ? 'danger' : 'success'">
                      {{ isOutside ? '否' : '是' }}
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
                <el-icon><DataLine /></el-icon>
                <span>实时坐标图表</span>
              </div>
            </template>

            <div class="coordinate-chart">
              <div class="chart-area" ref="chartRef">
                <div
                  class="mouse-pointer"
                  :style="{
                    left: `${(mouse.x.value / windowWidth) * 100}%`,
                    top: `${(mouse.y.value / windowHeight) * 100}%`
                  }"
                >
                  <el-icon><Mouse /></el-icon>
                </div>
              </div>
              <div class="chart-info">
                <p>
                  红点表示当前鼠标位置在整个页面中的相对位置
                  <br />
                  坐标: ({{ mouse.x }}, {{ mouse.y }})
                </p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { useMouse, useElementBounding, useWindowSize } from '@vueuse/core'
  import { ref, watch } from 'vue'
  import { Mouse, Position, DataLine } from '@element-plus/icons-vue'

  // 获取鼠标位置
  const mouse = useMouse()

  // 获取目标元素的引用
  const targetRef = ref<HTMLElement>()

  // 获取元素边界信息
  const { x: elementX, y: elementY } = useElementBounding(targetRef)

  // 获取窗口大小
  const { width: windowWidth, height: windowHeight } = useWindowSize()

  const isOutside = ref(false)
  const relativePos = ref({ x: 0, y: 0 })

  // 监听鼠标位置变化，判断是否在元素内
  watch(
    () => [mouse.x.value, mouse.y.value],

    () => {
      if (targetRef.value) {
        const rect = targetRef.value.getBoundingClientRect()
        isOutside.value =
          mouse.x.value < rect.left ||
          mouse.x.value > rect.right ||
          mouse.y.value < rect.top ||
          mouse.y.value > rect.bottom

        relativePos.value = {
          x: mouse.x.value - elementX.value,
          y: mouse.y.value - elementY.value
        }
      }
    },

    { immediate: true }
  )
</script>

<style scoped>
  .mouse-demo {
    padding: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .info-card {
    height: 100%;
  }

  .mouse-tracking-area {
    height: 300px;
    border: 2px dashed #409eff;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background:
      linear-gradient(45deg, #f0f9ff 25%, transparent 25%),
      linear-gradient(-45deg, #f0f9ff 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #f0f9ff 75%),
      linear-gradient(-45deg, transparent 75%, #f0f9ff 75%);
    background-size: 20px 20px;
    background-position:
      0 0,
      0 10px,
      10px -10px,
      -10px 0px;
  }

  .tracking-info {
    text-align: center;
    background: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 8px;
    backdrop-filter: blur(5px);
  }

  .coordinate-chart {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .chart-area {
    height: 200px;
    border: 1px solid #dcdfe6;
    border-radius: 8px;
    position: relative;
    background-color: #fafafa;
    overflow: hidden;
  }

  .mouse-pointer {
    position: absolute;
    color: #f56565;
    font-size: 20px;
    transform: translate(-50%, -50%);
    transition: all 0.1s ease-out;
    z-index: 10;
  }

  .mouse-pointer::after {
    content: '';
    position: absolute;
    width: 10px;
    height: 10px;
    background-color: #f56565;
    border-radius: 50%;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation: pulse 2s infinite;
  }

  .chart-info {
    text-align: center;
    color: #606266;
    font-size: 14px;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(245, 101, 101, 0.7);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(245, 101, 101, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(245, 101, 101, 0);
    }
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .mouse-tracking-area {
      height: 200px;
    }

    .chart-area {
      height: 150px;
    }
  }
</style>
