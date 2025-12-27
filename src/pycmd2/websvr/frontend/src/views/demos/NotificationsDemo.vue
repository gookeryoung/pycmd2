<template>
  <div class="demo-container">
    <h2>通知提示示例</h2>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="消息提示">
          <el-button :plain="true" @click="open1">成功</el-button>
          <el-button :plain="true" @click="open2">警告</el-button>
          <el-button :plain="true" @click="open3">消息</el-button>
          <el-button :plain="true" @click="open4">错误</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="可关闭的消息提示">
          <el-button :plain="true" @click="open5">成功</el-button>
          <el-button :plain="true" @click="open6">警告</el-button>
          <el-button :plain="true" @click="open7">消息</el-button>
          <el-button :plain="true" @click="open8">错误</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="自定义持续时间">
          <el-button :plain="true" @click="open9">不会自动关闭</el-button>
          <el-button :plain="true" @click="open10">5秒后关闭</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="带有偏移量的消息提示">
          <el-button plain @click="open11">偏移量为 20px</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="使用 HTML 片段">
          <el-button plain @click="open12">HTML 片段</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="消息队列">
          <el-button plain @click="open13">打开多个消息提示</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="可关闭的全局消息">
          <div class="notification-controls">
            <el-input v-model="title" placeholder="标题" style="width: 200px; margin-right: 10px" />
            <el-input v-model="message" placeholder="消息内容" style="width: 300px; margin-right: 10px" />
            <el-select v-model="type" style="width: 120px; margin-right: 10px">
              <el-option label="成功" value="success" />
              <el-option label="警告" value="warning" />
              <el-option label="信息" value="info" />
              <el-option label="错误" value="error" />
            </el-select>
            <el-button @click="openNotify">发送通知</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="Loading 加载">
          <el-button type="primary" @click="openLoading1">全屏加载</el-button>
          <el-button type="primary" @click="openLoading2">自定义加载</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="Alert 警告">
          <el-alert title="成功提示的文案" type="success" show-icon />
          <el-alert title="消息提示的文案" type="info" show-icon />
          <el-alert title="警告提示的文案" type="warning" show-icon />
          <el-alert title="错误提示的文案" type="error" show-icon />

          <el-divider>可关闭的警告</el-divider>
          <el-alert
            title="可关闭的警告"
            type="warning"
            description="这是一段文字这是一段文字这是一段文字这是一段文字这是一段文字这是一段文字"
            show-icon
            closable
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { ElMessage, ElNotification, ElLoading } from 'element-plus'
  import { ref } from 'vue'

  const title = ref('标题')
  const message = ref('这是一条消息')
  const type = ref<'success' | 'warning' | 'info' | 'error'>('success')

  // 基础消息提示
  const open1 = () => {
    ElMessage({
      message: '恭喜你，这是一条成功消息',
      type: 'success'
    })
  }

  const open2 = () => {
    ElMessage({
      message: '警告哦，这是一条警告消息',
      type: 'warning'
    })
  }

  const open3 = () => {
    ElMessage({
      message: '这是一条消息提示',
      type: 'info'
    })
  }

  const open4 = () => {
    ElMessage.error('错了哦，这是一条错误消息')
  }

  // 可关闭的消息提示
  const open5 = () => {
    ElMessage({
      showClose: true,
      message: '恭喜你，这是一条成功消息',
      type: 'success'
    })
  }

  const open6 = () => {
    ElMessage({
      showClose: true,
      message: '警告哦，这是一条警告消息',
      type: 'warning'
    })
  }

  const open7 = () => {
    ElMessage({
      showClose: true,
      message: '这是一条消息提示',
      type: 'info'
    })
  }

  const open8 = () => {
    ElMessage({
      showClose: true,
      message: '错了哦，这是一条错误消息',
      type: 'error'
    })
  }

  // 自定义持续时间
  const open9 = () => {
    ElMessage({
      showClose: true,
      message: '这条消息不会自动关闭',
      duration: 0
    })
  }

  const open10 = () => {
    ElMessage({
      showClose: true,
      message: '这条消息会在5秒后关闭',
      duration: 5000
    })
  }

  // 带有偏移量的消息提示
  const open11 = () => {
    ElMessage({
      showClose: true,
      message: '偏移量为 20px',
      offset: 20
    })
  }

  // 使用 HTML 片段
  const open12 = () => {
    ElMessage({
      dangerouslyUseHTMLString: true,
      message: '<strong>这是 <i>HTML</i> 片段</strong>'
    })
  }

  // 消息队列
  const open13 = () => {
    for (let i = 0; i < 5; i++) {
      ElMessage({
        showClose: true,
        message: '这是第 ' + (i + 1) + ' 条消息',
        type: i % 2 === 0 ? 'success' : 'warning',
        duration: 1000 * (i + 1)
      })
    }
  }

  // 通知
  const openNotify = () => {
    ElNotification({
      title: title.value,
      message: message.value,
      type: type.value
    })
  }

  // Loading 加载
  const openLoading1 = () => {
    const loading = ElLoading.service({
      lock: true,
      text: '加载中...',
      background: 'rgba(0, 0, 0, 0.7)'
    })

    setTimeout(() => {
      loading.close()
    }, 3000)
  }

  const openLoading2 = () => {
    const loading = ElLoading.service({
      lock: true,
      text: '自定义加载中...',
      background: 'rgba(0, 0, 0, 0.7)',
      spinner: 'el-icon-loading',
      customClass: 'custom-loading'
    })

    setTimeout(() => {
      loading.close()
    }, 3000)
  }
</script>

<style scoped>
  .demo-container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .demo-section {
    margin-bottom: 24px;
  }

  .demo-section .el-button {
    margin-right: 10px;
    margin-bottom: 10px;
  }

  .notification-controls {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  .el-alert {
    margin-bottom: 10px;
  }

  .el-divider {
    margin: 20px 0;
  }
</style>
