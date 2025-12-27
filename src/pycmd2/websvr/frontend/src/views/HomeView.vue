<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>欢迎使用 PyCmd2 WebUI</h2>
              <ElButtonGroup>
                <el-button type="primary" @click="showWelcome">更多功能</el-button>
                <el-button type="info" @click="showMoreInfo">更多信息</el-button>
              </ElButtonGroup>
            </div>
          </template>
          <div class="welcome-content">
            <p>这是一个基于 Vue 3 和 Element Plus 构建的现代化 Web 界面。</p>
            <p>您可以通过顶部的导航菜单访问不同的功能和示例页面。</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-row">
      <el-col :span="24">
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

          <AppsCard />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-row">
      <el-col :span="8">
        <el-card shadow="hover" class="feature-card">
          <template #header>
            <div class="card-header">
              <h3>
                <el-icon>
                  <Setting />
                </el-icon>
                命令管理
              </h3>
            </div>
          </template>
          <p>管理和执行各种命令，支持历史记录和收藏夹功能。</p>
          <div class="card-actions">
            <el-button type="primary" plain>查看详情</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="feature-card">
          <template #header>
            <div class="card-header">
              <h3>
                <el-icon>
                  <Document />
                </el-icon>
                脚本管理
              </h3>
            </div>
          </template>
          <p>创建、编辑和执行常用脚本，提高工作效率。</p>
          <div class="card-actions">
            <el-button type="primary" plain>查看详情</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="feature-card">
          <template #header>
            <div class="card-header">
              <h3>
                <el-icon>
                  <TrendCharts />
                </el-icon>
                数据可视化
              </h3>
            </div>
          </template>
          <p>基于ECharts的丰富图表组件，支持折线图、柱状图、饼图等多种图表类型。</p>
          <div class="card-actions">
            <router-link to="/demos/echarts">
              <el-button type="primary" plain>查看示例</el-button>
            </router-link>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <h3>
                <el-icon>
                  <Collection />
                </el-icon>
                Element Plus 示例
              </h3>
            </div>
          </template>
          <p>点击下面的链接，查看各种 Element Plus 组件的使用示例：</p>
          <div class="demo-links">
            <router-link to="/demos/buttons">
              <el-link type="primary" :underline="false">按钮示例</el-link>
            </router-link>
            <router-link to="/demos/forms">
              <el-link type="success" :underline="false">表单示例</el-link>
            </router-link>
            <router-link to="/demos/tables">
              <el-link type="warning" :underline="false">表格示例</el-link>
            </router-link>
            <router-link to="/demos/notifications">
              <el-link type="danger" :underline="false">通知提示</el-link>
            </router-link>
            <router-link to="/demos/dialogs">
              <el-link type="info" :underline="false">对话框</el-link>
            </router-link>
            <router-link to="/demos/echarts">
              <el-link type="primary" :underline="false">ECharts图表</el-link>
            </router-link>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { ElButtonGroup, ElMessage } from 'element-plus'
  import { Setting, Document, Collection, Grid, TrendCharts } from '@element-plus/icons-vue'
  import AppsCard from './apps/AppsCard.vue'

  const showWelcome = () => {
    ElMessage({
      message: '欢迎使用 PyCmd2 WebUI！更多功能正在开发中...',
      type: 'success'
    })
  }

  const showMoreInfo = () => {
    ElMessage({
      message: '更多详情请参考项目文档',
      type: 'info'
    })
  }
</script>

<style scoped>
  .home-container {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
  }

  .welcome-card {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .card-header h2,
  .card-header h3 {
    margin: 0;
    display: flex;
    align-items: center;
  }

  .card-header h2 {
    color: #409eff;
  }

  .card-header .el-icon {
    margin-right: 8px;
  }

  .welcome-content {
    font-size: 16px;
    line-height: 1.6;
  }

  .feature-row {
    margin-bottom: 20px;
  }

  .feature-card {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .feature-card .el-card__body {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .card-actions {
    margin-top: 15px;
    text-align: center;
  }

  .demo-links {
    margin-top: 15px;
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
  }

  .demo-links .el-link {
    margin-right: 15px;
    font-size: 16px;
  }

  .demo-links a {
    margin-right: 15px;
    margin-bottom: 10px;
  }

  /* 响应式布局 */
  @media (max-width: 768px) {
    .home-container {
      padding: 0 10px;
    }

    .card-header {
      flex-direction: column;
      align-items: flex-start;
    }

    .card-header .el-button {
      margin-top: 10px;
      align-self: flex-end;
    }

    .welcome-content {
      font-size: 15px;
    }

    .demo-links {
      justify-content: center;
    }

    .demo-links a {
      margin-right: 10px;
      margin-left: 10px;
    }
  }

  @media (max-width: 576px) {
    .demo-links {
      flex-direction: column;
      align-items: center;
    }

    .demo-links a {
      margin: 5px 0;
      text-align: center;
    }
  }
</style>
