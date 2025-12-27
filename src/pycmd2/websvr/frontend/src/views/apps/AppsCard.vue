<template>
  <el-card shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>
          <el-icon>
            <Grid />
          </el-icon>
          应用中心
        </h3>
      </div>
    </template>

    <div class="apps-grid">
      <div v-for="app in apps" :key="app.id" class="app-card" @click="navigateToApp(app.route)">
        <div class="app-icon" :style="{ backgroundColor: app.color }">
          <el-icon :size="18" color="white">
            <component :is="app.icon" />
          </el-icon>
        </div>
        <h4>{{ app.name }}</h4>
        <p>{{ app.description }}</p>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
  import { useRouter } from 'vue-router'
  import { Grid } from '@element-plus/icons-vue'

  const apps = [
    {
      id: 'todo',
      name: '待办事项',
      description: '管理待办事项',
      icon: 'List',
      color: '#409EFF',
      route: '/apps/todo-api',
      component: () => import('./todo/TodoApiApp.vue')
    },
    {
      id: 'emoji-viewer',
      name: '表情包浏览器',
      description: '浏览和搜索表情包',
      icon: 'Smile',
      color: '#E6A23C',
      route: '/apps/emoji-viewer',
      component: () => import('./EmojiViewer.vue')
    }
  ]

  const router = useRouter()
  const navigateToApp = (route: string) => {
    router.push(route)
  }
</script>

<style>
  .apps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }

  .app-card {
    background: #006aff1a;
    border-radius: 12px;
    padding: 8px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    border: 2px solid #ebeef5;
    width: 80%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .app-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    border-color: #409eff;
  }

  .app-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 8px;
  }

  .app-card h4 {
    margin: 0 0 6px;
    font-size: 15px;
    color: #303133;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .app-card p {
    margin: 0;
    color: #909399;
    font-size: 12px;
    line-height: 1.4;
    text-align: center;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
