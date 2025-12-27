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
          <el-icon :size="32" color="white">
            <component :is="app.icon" />
          </el-icon>
        </div>
        <h4>{{ app.name }}</h4>
        <p>{{ app.description }}</p>
        <el-button type="primary" size="small" plain>打开应用</el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
  import { useRouter } from 'vue-router';
  import { Grid } from '@element-plus/icons-vue';

  const apps = [
    {
      id: 'todo',
      name: '待办事项',
      description: '管理您的待办事项，提高工作效率',
      icon: 'List',
      color: '#409EFF',
      route: '/apps/todo',
      component: () => import('./todo/TodoApp.vue')
    }
  ];

  const router = useRouter();
  const navigateToApp = (route: string) => {
    router.push(route);
  };
</script>

<style>
  .apps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 15px;
  }

  .app-card {
    background: hwb(191 91% 0%);
    border-radius: 16px;
    padding: 12px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    border: 1px solid #ebeef5;
  }

  .app-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    border-color: #409eff;
  }

  .app-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 15px;
  }

  .app-card h4 {
    margin: 0 0 10px;
    font-size: 18px;
    color: #303133;
  }

  .app-card p {
    margin: 0 0 15px;
    color: #606266;
    font-size: 14px;
    line-height: 1.5;
  }
</style>
