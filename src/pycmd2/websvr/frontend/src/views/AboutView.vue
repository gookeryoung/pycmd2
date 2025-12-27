<template>
  <div class="about-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>
                <el-icon>
                  <InfoFilled />
                </el-icon>
                关于 PyCmd2 WebUI
              </h2>
            </div>
          </template>

          <el-divider content-position="left">项目介绍</el-divider>
          <p>PyCmd2 WebUI 是一个基于 Python 的命令行工具的 Web 界面，旨在提供更加友好和直观的用户体验。</p>
          <p>本界面采用 Vue 3 + TypeScript + Element Plus 技术栈构建，提供了现代化的界面设计和丰富的交互功能。</p>

          <el-divider content-position="left">技术栈</el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="前端框架">Vue 3</el-descriptions-item>
            <el-descriptions-item label="UI 库">Element Plus</el-descriptions-item>
            <el-descriptions-item label="开发语言">TypeScript</el-descriptions-item>
            <el-descriptions-item label="构建工具">Vite</el-descriptions-item>
          </el-descriptions>

          <el-divider content-position="left">主要特性</el-divider>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in activities"
              :key="index"
              :icon="activity.icon"
              :color="activity.color"
              :timestamp="activity.timestamp"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>

          <el-divider content-position="left">版本信息</el-divider>
          <el-tag type="success" size="large">版本: v1.0.0</el-tag>
          <el-tag type="primary" size="large" style="margin-left: 10px">发布日期: 2023-12-24</el-tag>

          <el-divider content-position="left">贡献指南</el-divider>
          <p>欢迎提交问题和建议，帮助改进 PyCmd2 WebUI。</p>
          <el-button type="primary" @click="showMoreInfo">了解更多</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { ElMessage } from 'element-plus'
  import { InfoFilled, Trophy, Star, Opportunity } from '@element-plus/icons-vue'

  const activities = [
    {
      content: '提供直观的命令管理界面',
      timestamp: '功能一',
      icon: Trophy,
      color: '#0bbd87',
      size: 'large'
    },
    {
      content: '支持脚本编辑和执行',
      timestamp: '功能二',
      icon: Star,
      color: '#1989fa',
      size: 'large'
    },
    {
      content: '数据可视化分析',
      timestamp: '功能三',
      icon: Opportunity,
      color: '#f56c6c',
      size: 'large'
    }
  ]

  const showMoreInfo = () => {
    ElMessage({
      message: '更多详情请参考项目文档',
      type: 'info'
    })
  }
</script>

<style scoped>
  .about-container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .card-header {
    display: flex;
    align-items: center;
  }

  .card-header h2 {
    margin: 0;
    color: #409eff;
  }

  .card-header .el-icon {
    margin-right: 8px;
  }

  .el-timeline-item {
    padding-bottom: 20px;
  }
</style>
