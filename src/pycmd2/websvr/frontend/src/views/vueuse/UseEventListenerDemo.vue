<template>
  <div class="event-listener-demo">
    <el-card header="useEventListener - 事件监听">
      <el-alert
        title="VueUse useEventListener 示例"
        type="info"
        :closable="false"
        description="安全地添加和移除事件监听器，支持被动监听和自动清理。"
        style="margin-bottom: 20px"
      />

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" class="keyboard-card">
            <template #header>
              <div class="card-header">
                <el-icon><Keyboard /></el-icon>
                <span>键盘事件</span>
              </div>
            </template>

            <div class="keyboard-section">
              <div class="key-display">
                <h4>按键状态:</h4>
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="按键">
                    <el-tag>{{ lastKey || '无' }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="键码">
                    <el-tag type="info">{{ lastKeyCode || '-' }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="Ctrl">
                    <el-tag :type="modifiers.ctrl ? 'success' : 'info'">
                      {{ modifiers.ctrl ? '按下' : '释放' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="Shift">
                    <el-tag :type="modifiers.shift ? 'success' : 'info'">
                      {{ modifiers.shift ? '按下' : '释放' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="Alt">
                    <el-tag :type="modifiers.alt ? 'success' : 'info'">
                      {{ modifiers.alt ? '按下' : '释放' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="Meta">
                    <el-tag :type="modifiers.meta ? 'success' : 'info'">
                      {{ modifiers.meta ? '按下' : '释放' }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </div>

              <div class="shortcuts">
                <h4>快捷键示例:</h4>
                <el-space>
                  <el-button @click="toggleShortcut('ctrl+s')" :type="shortcuts['ctrl+s'] ? 'success' : 'info'">
                    Ctrl+S (保存)
                  </el-button>
                  <el-button @click="toggleShortcut('ctrl+z')" :type="shortcuts['ctrl+z'] ? 'success' : 'info'">
                    Ctrl+Z (撤销)
                  </el-button>
                  <el-button @click="toggleShortcut('enter')" :type="shortcuts.enter ? 'success' : 'info'">
                    Enter (确认)
                  </el-button>
                </el-space>
              </div>

              <div class="key-history">
                <h4>按键历史:</h4>
                <div class="history-container">
                  <el-tag v-for="(key, index) in keyHistory" :key="index" class="key-tag">
                    {{ key }}
                  </el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover" class="mouse-card">
            <template #header>
              <div class="card-header">
                <el-icon><Mouse /></el-icon>
                <span>鼠标事件</span>
              </div>
            </template>

            <div class="mouse-section">
              <div class="click-area" ref="clickAreaRef">
                <p>点击此区域测试鼠标事件</p>
                <div class="event-info">
                  <el-descriptions :column="1" border size="small">
                    <el-descriptions-item label="点击次数">
                      <el-tag>{{ clickCount }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="双击次数">
                      <el-tag type="success">{{ doubleClickCount }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="右键次数">
                      <el-tag type="warning">{{ rightClickCount }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="悬停状态">
                      <el-tag :type="isHovering ? 'success' : 'info'">
                        {{ isHovering ? '悬停中' : '未悬停' }}
                      </el-tag>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </div>

              <div class="wheel-demo">
                <h4>滚轮事件:</h4>
                <div class="wheel-area" ref="wheelAreaRef">
                  <p>在此区域滚动鼠标滚轮</p>
                  <div class="wheel-info">
                    <el-descriptions :column="1" border size="small">
                      <el-descriptions-item label="滚动方向">
                        <el-tag :type="wheelDelta > 0 ? 'primary' : 'warning'">
                          {{ wheelDelta > 0 ? '向上' : wheelDelta < 0 ? '向下' : '无' }}
                        </el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="滚动值">
                        <el-tag>{{ Math.abs(wheelDelta) }}</el-tag>
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
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
                <el-icon><Connection /></el-icon>
                <span>网络事件</span>
              </div>
            </template>

            <div class="network-section">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="network-status">
                    <h4>网络状态:</h4>
                    <el-descriptions :column="1" border>
                      <el-descriptions-item label="在线状态">
                        <el-tag :type="isOnline ? 'success' : 'danger'">
                          {{ isOnline ? '在线' : '离线' }}
                        </el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="连接类型">
                        <el-tag type="info">{{ connectionType || '未知' }}</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="有效带宽">
                        <el-tag type="warning">{{ downlink || '未知' }} Mbps</el-tag>
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-col>

                <el-col :span="8">
                  <div class="visibility-demo">
                    <h4>页面可见性:</h4>
                    <div class="visibility-status">
                      <el-progress
                        type="circle"
                        :percentage="isVisible ? 100 : 0"
                        :width="80"
                        :status="isVisible ? 'success' : 'exception'"
                      />
                      <p>{{ isVisible ? '页面可见' : '页面隐藏' }}</p>
                    </div>
                  </div>
                </el-col>

                <el-col :span="8">
                  <div class="device-orientation">
                    <h4>设备方向:</h4>
                    <el-descriptions :column="1" border size="small">
                      <el-descriptions-item label="Alpha">
                        <el-tag>{{ orientation.alpha || 0 }}°</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="Beta">
                        <el-tag>{{ orientation.beta || 0 }}°</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="Gamma">
                        <el-tag>{{ orientation.gamma || 0 }}°</el-tag>
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-col>
              </el-row>
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
                <span>自定义事件监听</span>
              </div>
            </template>

            <div class="custom-events">
              <el-form label-width="120px">
                <el-form-item label="事件名称">
                  <el-input v-model="customEventName" placeholder="输入事件名称" />
                </el-form-item>
                <el-form-item label="事件数据">
                  <el-input v-model="customEventData" placeholder="输入事件数据" />
                </el-form-item>
                <el-form-item>
                  <el-space>
                    <el-button @click="fireCustomEvent" type="primary"> 触发自定义事件 </el-button>
                    <el-button @click="toggleCustomListener" :type="isCustomListenerActive ? 'success' : 'info'">
                      {{ isCustomListenerActive ? '停止监听' : '开始监听' }}
                    </el-button>
                  </el-space>
                </el-form-item>
              </el-form>

              <div class="custom-event-log">
                <h4>自定义事件日志:</h4>
                <div class="log-container">
                  <el-timeline>
                    <el-timeline-item
                      v-for="(log, index) in customEventLogs"
                      :key="index"
                      :timestamp="log.timestamp"
                      type="primary"
                    >
                      <strong>{{ log.event }}:</strong> {{ log.data }}
                    </el-timeline-item>
                  </el-timeline>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { useEventListener, useOnline, useNetwork, useDocumentVisibility, useDeviceOrientation } from '@vueuse/core'
  import { ref, reactive } from 'vue'
  import { Mouse, Connection, Timer } from '@element-plus/icons-vue'

  // 键盘事件相关
  const lastKey = ref('')
  const lastKeyCode = ref('')
  const modifiers = reactive({
    ctrl: false,
    shift: false,
    alt: false,
    meta: false
  })
  const keyHistory = ref<string[]>([])
  const shortcuts = ref<Record<string, boolean>>({})

  // 鼠标事件相关
  const clickAreaRef = ref<HTMLElement>()
  const wheelAreaRef = ref<HTMLElement>()
  const clickCount = ref(0)
  const doubleClickCount = ref(0)
  const rightClickCount = ref(0)
  const isHovering = ref(false)
  const wheelDelta = ref(0)

  // 网络相关
  const isOnline = useOnline()
  const { effectiveType: connectionType, downlink } = useNetwork()

  // 页面可见性
  const { value: isVisible } = useDocumentVisibility()

  // 设备方向
  const orientation = useDeviceOrientation()

  // 自定义事件
  const customEventName = ref('myCustomEvent')
  const customEventData = ref('Hello from custom event!')
  const isCustomListenerActive = ref(false)
  const customEventLogs = ref<Array<{ event: string; data: string; timestamp: string }>>([])

  // 键盘事件监听
  useEventListener('keydown', (event: KeyboardEvent) => {
    lastKey.value = event.key
    lastKeyCode.value = event.code
    modifiers.ctrl = event.ctrlKey
    modifiers.shift = event.shiftKey
    modifiers.alt = event.altKey
    modifiers.meta = event.metaKey

    // 添加到历史
    keyHistory.value.unshift(`${event.key} (${event.code})`)
    if (keyHistory.value.length > 10) {
      keyHistory.value = keyHistory.value.slice(0, 10)
    }

    // 检查快捷键
    const shortcut = getShortcutString(event)
    if (shortcuts.value[shortcut]) {
      console.log(`快捷键触发: ${shortcut}`)
    }
  })

  // 鼠标事件监听
  if (clickAreaRef.value) {
    useEventListener(clickAreaRef.value, 'click', () => {
      clickCount.value++
    })

    useEventListener(clickAreaRef.value, 'dblclick', () => {
      doubleClickCount.value++
    })

    useEventListener(clickAreaRef.value, 'contextmenu', event => {
      event.preventDefault()
      rightClickCount.value++
    })

    useEventListener(clickAreaRef.value, 'mouseenter', () => {
      isHovering.value = true
    })

    useEventListener(clickAreaRef.value, 'mouseleave', () => {
      isHovering.value = false
    })
  }

  // 滚轮事件监听
  if (wheelAreaRef.value) {
    useEventListener(wheelAreaRef.value, 'wheel', (event: WheelEvent) => {
      wheelDelta.value = event.deltaY
    })
  }

  // 获取快捷键字符串
  const getShortcutString = (event: KeyboardEvent) => {
    const parts: string[] = []
    if (event.ctrlKey) parts.push('ctrl')
    if (event.shiftKey) parts.push('shift')
    if (event.altKey) parts.push('alt')
    if (event.metaKey) parts.push('meta')
    parts.push(event.key.toLowerCase())
    return parts.join('+')
  }

  // 切换快捷键
  const toggleShortcut = (shortcut: string) => {
    shortcuts.value[shortcut] = !shortcuts.value[shortcut]
  }

  // 触发自定义事件
  const fireCustomEvent = () => {
    const event = new CustomEvent(customEventName.value, {
      detail: customEventData.value
    })
    window.dispatchEvent(event)
  }

  // 切换自定义事件监听器
  const toggleCustomListener = () => {
    if (isCustomListenerActive.value) {
      window.removeEventListener(customEventName.value, handleCustomEvent as (event: Event) => void)
      isCustomListenerActive.value = false
    } else {
      window.addEventListener(customEventName.value, handleCustomEvent as (event: Event) => void)
      isCustomListenerActive.value = true
    }
  }

  // 处理自定义事件
  const handleCustomEvent = (event: Event) => {
    // 将event转换为CustomEvent以访问detail属性
    const customEvent = event as CustomEvent
    customEventLogs.value.unshift({
      event: event.type,
      data: customEvent.detail,
      timestamp: new Date().toLocaleTimeString()
    })

    if (customEventLogs.value.length > 10) {
      customEventLogs.value = customEventLogs.value.slice(0, 10)
    }
  }
</script>

<style scoped>
  .event-listener-demo {
    padding: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .keyboard-card,
  .mouse-card {
    height: 100%;
  }

  .keyboard-section,
  .mouse-section {
    padding: 10px 0;
  }

  .key-display,
  .shortcuts,
  .key-history {
    margin-bottom: 20px;
  }

  .key-display h4,
  .shortcuts h4,
  .key-history h4 {
    margin-bottom: 10px;
  }

  .history-container {
    max-height: 150px;
    overflow-y: auto;
    padding: 10px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
  }

  .key-tag {
    margin: 5px;
    font-family: 'Courier New', monospace;
  }

  .click-area,
  .wheel-area {
    border: 2px dashed #409eff;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
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
    transition: all 0.3s ease;
  }

  .click-area:hover,
  .wheel-area:hover {
    border-color: #67c23a;
    background-color: rgba(103, 194, 58, 0.05);
  }

  .event-info {
    margin-top: 15px;
  }

  .wheel-demo h4 {
    margin-bottom: 10px;
  }

  .wheel-info {
    margin-top: 10px;
  }

  .network-section {
    padding: 20px 0;
  }

  .network-status h4,
  .visibility-demo h4,
  .device-orientation h4 {
    margin-bottom: 15px;
  }

  .visibility-status {
    text-align: center;
  }

  .visibility-status p {
    margin-top: 10px;
    font-weight: bold;
  }

  .custom-events {
    padding: 20px 0;
  }

  .custom-event-log {
    margin-top: 20px;
  }

  .custom-event-log h4 {
    margin-bottom: 10px;
  }

  .log-container {
    max-height: 300px;
    overflow-y: auto;
    padding: 10px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .history-container {
      max-height: 100px;
    }

    .click-area,
    .wheel-area {
      padding: 15px;
    }

    .log-container {
      max-height: 200px;
    }
  }
</style>
