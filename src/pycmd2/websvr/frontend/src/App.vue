<script setup lang="ts">
import { ref } from 'vue'

const activeIndex = ref('1')
</script>

<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="logo-container">
        <h1>PyCmd2 WebUI</h1>
      </div>
      <el-menu :default-active="activeIndex" mode="horizontal" :router="true" class="nav-menu">
        <el-menu-item index="/">
          <el-icon>
            <HomeFilled />
          </el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/about">
          <el-icon>
            <InfoFilled />
          </el-icon>
          <span>关于</span>
        </el-menu-item>
        <el-sub-menu index="/demos">
          <template #title>
            <el-icon>
              <Collection />
            </el-icon>
            <span>演示示例</span>
          </template>
          <el-menu-item index="/demos/buttons">按钮示例</el-menu-item>
          <el-menu-item index="/demos/forms">表单示例</el-menu-item>
          <el-menu-item index="/demos/tables">表格示例</el-menu-item>
          <el-menu-item index="/demos/notifications">通知提示</el-menu-item>
          <el-menu-item index="/demos/dialogs">对话框</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-header>

    <el-main class="main-content">
      <RouterView />
    </el-main>
  </el-container>
</template>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo-container h1 {
  margin: 0;
  color: #409EFF;
  font-size: 22px;
}

.nav-menu {
  flex-grow: 1;
  max-width: 600px;
  margin-left: 20px;
}

.main-content {
  padding: 20px;
  background-color: #f5f7fa;
}
</style>
