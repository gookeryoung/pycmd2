<template>
  <div class="pinia-basic-demo">
    <el-card header="基础状态管理示例 - Counter Store">
      <div class="counter-section">
        <h3>{{ counterStore.name }}</h3>
        <div class="counter-display">
          <el-tag size="large" type="primary">当前计数: {{ counterStore.count }}</el-tag>
          <el-tag size="large" type="success">双倍计数: {{ counterStore.doubleCount }}</el-tag>
        </div>
        <div class="formatted-display">
          <el-alert :title="counterStore.formattedCount" type="info" :closable="false" />
        </div>

        <div class="action-buttons">
          <el-button type="primary" @click="counterStore.increment()">
            <el-icon>
              <Plus />
            </el-icon>
            增加 (+1)
          </el-button>
          <el-button type="success" @click="counterStore.increment(5)">
            <el-icon>
              <Plus />
            </el-icon>
            增加 (+5)
          </el-button>
          <el-button type="danger" @click="counterStore.decrement()">
            <el-icon>
              <Minus />
            </el-icon>
            减少 (-1)
          </el-button>
          <el-button type="warning" @click="counterStore.reset()">
            <el-icon>
              <Refresh />
            </el-icon>
            重置
          </el-button>
        </div>

        <div class="async-section">
          <el-divider>异步操作示例</el-divider>
          <el-button type="info" @click="fetchRandomCount" :loading="isLoading">
            <el-icon>
              <Refresh />
            </el-icon>
            获取随机计数
          </el-button>
        </div>

        <div class="name-section">
          <el-divider>修改 Store 名称</el-divider>
          <el-input v-model="newName" placeholder="输入新名称">
            <template #append>
              <el-button @click="updateName">更新</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </el-card>

    <el-card header="Store 状态查看" class="state-view">
      <el-collapse>
        <el-collapse-item title="完整状态" name="state">
          <pre>{{ JSON.stringify(counterStore.$state, null, 2) }}</pre>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import { useCounterStore } from '@/stores/counter'
  import { ElMessage } from 'element-plus'
  import { Plus, Minus, Refresh } from '@element-plus/icons-vue'

  const counterStore = useCounterStore()
  const newName = ref('')
  const isLoading = ref(false)

  const fetchRandomCount = async () => {
    isLoading.value = true
    try {
      await counterStore.fetchRandomCount()
      ElMessage.success(`随机计数已更新为: ${counterStore.count}`)
    } catch (error) {
      ElMessage.error('获取随机计数失败: ' + error)
    } finally {
      isLoading.value = false
    }
  }

  const updateName = () => {
    if (newName.value.trim()) {
      counterStore.setName(newName.value.trim())
      newName.value = ''
      ElMessage.success('名称已更新')
    }
  }
</script>

<style scoped>
  .pinia-basic-demo {
    padding: 20px;
  }

  .counter-section {
    margin-bottom: 20px;
  }

  .counter-display {
    display: flex;
    gap: 10px;
    margin: 20px 0;
  }

  .formatted-display {
    margin: 20px 0;
  }

  .action-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 20px 0;
  }

  .async-section,
  .name-section {
    margin-top: 30px;
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
    .action-buttons {
      justify-content: center;
    }

    .counter-display {
      flex-direction: column;
    }
  }
</style>
