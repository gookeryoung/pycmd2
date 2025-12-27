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
        <el-sub-menu index="/demos">
          <template #title>
            <el-icon>
              <Collection />
            </el-icon>
            <span>UI组件示例</span>
          </template>
          <el-menu-item index="/demos/buttons">按钮示例</el-menu-item>
          <el-menu-item index="/demos/forms">表单示例</el-menu-item>
          <el-menu-item index="/demos/tables">表格示例</el-menu-item>
          <el-menu-item index="/demos/notifications">通知提示</el-menu-item>
          <el-menu-item index="/demos/dialogs">对话框</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/pinia-demos">
          <template #title>
            <el-icon>
              <DataBoard />
            </el-icon>
            <span>Pinia状态管理</span>
          </template>
          <el-menu-item index="/pinia-demos/basic">基础状态管理</el-menu-item>
          <el-menu-item index="/pinia-demos/todos">待办事项管理</el-menu-item>
          <el-menu-item index="/pinia-demos/user">用户认证管理</el-menu-item>
          <el-menu-item index="/pinia-demos/composition">Store组合使用</el-menu-item>
          <el-menu-item index="/pinia-demos/persistent">持久化存储</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/about">
          <el-icon>
            <InfoFilled />
          </el-icon>
          <span>关于</span>
        </el-menu-item>
      </el-menu>
    </el-header>

    <el-main class="main-content">
      <RouterView />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  const activeIndex = ref('1');
</script>

<style scoped>
  .layout-container {
    min-height: 100vh;
    width: 100%;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    background-color: #fff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    border-bottom: solid 1px #a0c0fd;
    height: 60px;
  }

  .logo-container h1 {
    margin: 0;
    color: #409eff;
    font-size: 22px;
    white-space: nowrap;
  }

  .nav-menu {
    flex-grow: 1;
    max-width: 80%;
    justify-content: flex-end;
  }

  .main-content {
    padding: 20px;
    background-color: #f5f7fa;
    overflow-y: auto;
    height: calc(100vh - 60px);
    /* 减去header高度 */
    box-sizing: border-box;
  }

  /* 响应式布局 */
  @media (max-width: 768px) {
    .header {
      flex-direction: column;
      height: auto;
      padding: 10px;
    }

    .logo-container {
      margin-bottom: 10px;
      width: 100%;
      text-align: center;
    }

    .logo-container h1 {
      font-size: 20px;
    }

    .nav-menu {
      margin-left: 0;
      max-width: 100%;
    }

    .el-menu--horizontal {
      border-bottom: none;
    }

    .main-content {
      height: calc(100vh - 120px);
      /* 适应新的header高度 */
      padding: 15px;
    }
  }

  @media (max-width: 576px) {
    .header {
      padding: 5px;
    }

    .logo-container h1 {
      font-size: 18px;
    }

    .main-content {
      height: calc(100vh - 100px);
      /* 适应更紧凑的header */
      padding: 10px;
    }
  }
</style>
