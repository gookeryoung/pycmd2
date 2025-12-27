<template>
  <div class="demo-container">
    <h2>按钮示例</h2>
    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <h3>基础按钮</h3>
        <div class="button-group">
          <el-button>默认按钮</el-button>
          <el-button type="primary">主要按钮</el-button>
          <el-button type="success">成功按钮</el-button>
          <el-button type="info">信息按钮</el-button>
          <el-button type="warning">警告按钮</el-button>
          <el-button type="danger">危险按钮</el-button>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <h3>朴素按钮</h3>
        <div class="button-group">
          <el-button plain>朴素按钮</el-button>
          <el-button type="primary" plain>主要按钮</el-button>
          <el-button type="success" plain>成功按钮</el-button>
          <el-button type="info" plain>信息按钮</el-button>
          <el-button type="warning" plain>警告按钮</el-button>
          <el-button type="danger" plain>危险按钮</el-button>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <h3>圆角按钮</h3>
        <div class="button-group">
          <el-button round>圆角按钮</el-button>
          <el-button type="primary" round>主要按钮</el-button>
          <el-button type="success" round>成功按钮</el-button>
          <el-button type="info" round>信息按钮</el-button>
          <el-button type="warning" round>警告按钮</el-button>
          <el-button type="danger" round>危险按钮</el-button>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <h3>带图标的按钮</h3>
        <div class="button-group">
          <el-button type="primary" :icon="Search">搜索</el-button>
          <el-button type="success" :icon="Edit">编辑</el-button>
          <el-button type="info" :icon="Message">消息</el-button>
          <el-button type="warning" :icon="Star">收藏</el-button>
          <el-button type="danger" :icon="Delete">删除</el-button>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <h3>加载状态</h3>
        <div class="button-group">
          <el-button type="primary" :loading="true">加载中</el-button>
          <el-button type="success" :loading="true">加载中</el-button>
          <el-button type="info" :loading="true">加载中</el-button>
          <el-button type="warning" :loading="true">加载中</el-button>
          <el-button type="danger" :loading="true">加载中</el-button>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <h3>不同尺寸</h3>
        <div class="button-group">
          <el-button size="large">大型按钮</el-button>
          <el-button>默认按钮</el-button>
          <el-button size="small">小型按钮</el-button>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <h3>按钮组</h3>
        <el-button-group>
          <el-button type="primary" :icon="ArrowLeft">上一页</el-button>
          <el-button type="primary">中间</el-button>
          <el-button type="primary">
            下一页<el-icon class="el-icon--right"> <ArrowRight /> </el-icon>
          </el-button>
        </el-button-group>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { Search, Edit, Message, Star, Delete, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
</script>

<style scoped>
  .demo-container {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
  }

  .demo-section {
    margin-bottom: 24px;
    padding: 20px;
    background-color: #fff;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }

  .demo-section h3 {
    margin-top: 0;
    margin-bottom: 16px;
    color: #303133;
    font-size: 18px;
  }

  .button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  /* 响应式布局 */
  @media (max-width: 768px) {
    .demo-container {
      padding: 0 10px;
    }

    .demo-section {
      padding: 15px;
    }

    .demo-section h3 {
      font-size: 16px;
    }

    .button-group {
      gap: 8px;
    }
  }

  @media (max-width: 576px) {
    .demo-section {
      padding: 10px;
    }

    .button-group {
      flex-direction: column;
      gap: 8px;
    }

    .button-group .el-button {
      width: 100%;
    }
  }
</style>
