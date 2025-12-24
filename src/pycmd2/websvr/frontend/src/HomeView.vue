<template>
    <div class="home-container">
        <el-row :gutter="20">
            <el-col :span="24">
                <el-card class="welcome-card" shadow="hover">
                    <template #header>
                        <div class="card-header">
                            <h2>欢迎使用 PyCmd2 WebUI</h2>
                            <el-button type="primary" @click="showWelcome">更多功能</el-button>
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
            <el-col :span="8">
                <el-card shadow="hover" class="feature-card">
                    <template #header>
                        <div class="card-header">
                            <h3><el-icon>
                                    <Setting />
                                </el-icon> 命令管理</h3>
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
                            <h3><el-icon>
                                    <Document />
                                </el-icon> 脚本管理</h3>
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
                            <h3><el-icon>
                                    <Histogram />
                                </el-icon> 数据分析</h3>
                        </div>
                    </template>
                    <p>可视化数据，支持多种图表和统计分析功能。</p>
                    <div class="card-actions">
                        <el-button type="primary" plain>查看详情</el-button>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <el-row :gutter="20" class="feature-row">
            <el-col :span="24">
                <el-card shadow="hover">
                    <template #header>
                        <div class="card-header">
                            <h3><el-icon>
                                    <Collection />
                                </el-icon> Element Plus 示例</h3>
                        </div>
                    </template>
                    <p>点击下面的链接，查看各种 Element Plus 组件的使用示例：</p>
                    <div class="demo-links">
                        <el-link type="primary" href="/demos/buttons">按钮示例</el-link>
                        <el-link type="success" href="/demos/forms">表单示例</el-link>
                        <el-link type="warning" href="/demos/tables">表格示例</el-link>
                        <el-link type="danger" href="/demos/notifications">通知提示</el-link>
                        <el-link type="info" href="/demos/dialogs">对话框</el-link>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { Setting, Document, Histogram, Collection } from '@element-plus/icons-vue'

const showWelcome = () => {
    ElMessage({
        message: '欢迎使用 PyCmd2 WebUI！更多功能正在开发中...',
        type: 'success'
    })
}
</script>

<style scoped>
.home-container {
    max-width: 1200px;
    margin: 0 auto;
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
    color: #409EFF;
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
}
</style>
