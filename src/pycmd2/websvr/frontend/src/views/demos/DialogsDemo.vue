<template>
  <div class="demo-container">
    <h2>对话框示例</h2>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="12">
        <el-card header="基础用法">
          <el-button type="primary" @click="dialogVisible = true"> 打开对话框 </el-button>

          <el-dialog v-model="dialogVisible" title="提示" width="30%">
            <span>这是一段信息</span>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="dialogVisible = false"> 确认 </el-button>
              </span>
            </template>
          </el-dialog>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card header="自定义内容">
          <el-button type="text" @click="dialogTableVisible = true"> 打开嵌套表格的 Dialog </el-button>

          <el-dialog v-model="dialogTableVisible" title="收货地址" width="800">
            <el-table :data="gridData">
              <el-table-column property="date" label="日期" width="150" />
              <el-table-column property="name" label="姓名" width="200" />
              <el-table-column property="address" label="地址" />
            </el-table>
          </el-dialog>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="12">
        <el-card header="嵌套的 Dialog">
          <el-button type="text" @click="outerVisible = true"> 点击打开外层 Dialog </el-button>

          <el-dialog v-model="outerVisible" title="外层 Dialog">
            <el-dialog v-model="innerVisible" width="30%" title="内层 Dialog" append-to-body>
              <span>这是一个内层对话框</span>
            </el-dialog>
            <div class="dialog-content">
              <p>这是外层对话框的内容</p>
              <el-button type="primary" @click="innerVisible = true"> 打开内层 Dialog </el-button>
            </div>
          </el-dialog>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card header="居中布局">
          <el-button type="text" @click="centerDialogVisible = true"> 点击打开 Dialog </el-button>

          <el-dialog v-model="centerDialogVisible" title="提示" width="30%" center>
            <span> 需要注意的是内容是默认不居中的，居中需要自己处理样式 </span>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="centerDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="centerDialogVisible = false"> 确认 </el-button>
              </span>
            </template>
          </el-dialog>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="12">
        <el-card header="不允许拖动和关闭">
          <el-button type="text" @click="noDragDialogVisible = true"> 打开对话框 </el-button>

          <el-dialog
            v-model="noDragDialogVisible"
            title="提示"
            width="30%"
            :draggable="false"
            :close-on-click-modal="false"
            :close-on-press-escape="false"
            :show-close="false"
          >
            <span>这个对话框不允许拖动，也不允许点击遮罩层和按ESC键关闭</span>
            <template #footer>
              <span class="dialog-footer">
                <el-button type="primary" @click="noDragDialogVisible = false"> 确认 </el-button>
              </span>
            </template>
          </el-dialog>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card header="对话框内容滚动的设置">
          <el-button type="text" @click="scrollDialogVisible = true"> 打开对话框 </el-button>

          <el-dialog v-model="scrollDialogVisible" title="提示" width="500" fullscreen>
            <div class="scroll-content">
              <p v-for="i in 20" :key="i">
                这是第 {{ i }} 行内容，用于测试滚动效果。当内容超出对话框高度时，会出现滚动条。
              </p>
            </div>
          </el-dialog>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="确认消息框">
          <div class="button-group">
            <el-button type="success" @click="openConfirm1"> 成功消息确认框 </el-button>
            <el-button type="warning" @click="openConfirm2"> 警告消息确认框 </el-button>
            <el-button type="info" @click="openConfirm3"> 消息确认框 </el-button>
            <el-button type="danger" @click="openConfirm4"> 错误消息确认框 </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="提交内容">
          <div class="button-group">
            <el-button type="primary" @click="openPrompt"> 消息提示 </el-button>
            <el-button type="success" @click="openPrompt2"> 提交内容 </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="自定义插槽">
          <el-button type="primary" @click="slotDialogVisible = true"> 打开对话框 </el-button>

          <el-dialog v-model="slotDialogVisible" width="500">
            <template #header="{ close, titleId, titleClass }">
              <div class="my-header">
                <h4 :id="titleId" :class="titleClass">自定义标题</h4>
                <el-button type="danger" @click="close">
                  <el-icon class="el-icon--left">
                    <CircleCloseFilled />
                  </el-icon>
                  关闭
                </el-button>
              </div>
            </template>
            <div class="dialog-content">
              <p>这是使用自定义插槽的对话框内容</p>
              <el-form :model="form" label-width="80px">
                <el-form-item label="名称">
                  <el-input v-model="form.name" autocomplete="off" />
                </el-form-item>
                <el-form-item label="区域">
                  <el-select v-model="form.region" placeholder="请选择区域">
                    <el-option label="上海" value="shanghai" />
                    <el-option label="北京" value="beijing" />
                  </el-select>
                </el-form-item>
              </el-form>
            </div>
          </el-dialog>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive } from 'vue'
  import { ElMessageBox, ElMessage } from 'element-plus'
  import { CircleCloseFilled } from '@element-plus/icons-vue'

  // 基础对话框
  const dialogVisible = ref(false)
  const centerDialogVisible = ref(false)
  const outerVisible = ref(false)
  const innerVisible = ref(false)
  const noDragDialogVisible = ref(false)
  const scrollDialogVisible = ref(false)
  const slotDialogVisible = ref(false)

  // 表格对话框
  const dialogTableVisible = ref(false)
  const gridData = [
    {
      date: '2016-05-02',
      name: '王小虎',
      address: '上海市普陀区金沙江路 1518 弄'
    },
    {
      date: '2016-05-04',
      name: '王小虎',
      address: '上海市普陀区金沙江路 1518 弄'
    },
    {
      date: '2016-05-01',
      name: '王小虎',
      address: '上海市普陀区金沙江路 1518 弄'
    },
    {
      date: '2016-05-03',
      name: '王小虎',
      address: '上海市普陀区金沙江路 1518 弄'
    }
  ]

  // 表单数据
  const form = reactive({
    name: '',
    region: ''
  })

  // 确认消息框
  const openConfirm1 = () => {
    ElMessageBox.confirm('此操作将永久删除该文件, 是否继续?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    })
      .then(() => {
        ElMessage({
          type: 'success',
          message: '删除成功!'
        })
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除'
        })
      })
  }

  const openConfirm2 = () => {
    ElMessageBox.confirm('此操作将永久删除该文件, 是否继续?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(() => {
        ElMessage({
          type: 'success',
          message: '删除成功!'
        })
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除'
        })
      })
  }

  const openConfirm3 = () => {
    ElMessageBox.confirm('此操作将永久删除该文件, 是否继续?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
      .then(() => {
        ElMessage({
          type: 'success',
          message: '删除成功!'
        })
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除'
        })
      })
  }

  const openConfirm4 = () => {
    ElMessageBox.confirm('此操作将永久删除该文件, 是否继续?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error'
    })
      .then(() => {
        ElMessage({
          type: 'success',
          message: '删除成功!'
        })
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除'
        })
      })
  }

  // 提交内容
  const openPrompt = () => {
    ElMessageBox.alert('这是一段内容', '标题名称', {
      confirmButtonText: '确定',
      callback: (action: string) => {
        ElMessage({
          type: 'info',
          message: `action: ${action}`
        })
      }
    })
  }

  const openPrompt2 = () => {
    ElMessageBox.prompt('请输入邮箱', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern:
        /[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?/,
      inputErrorMessage: '邮箱格式不正确'
    })
      .then(({ value }) => {
        ElMessage({
          type: 'success',
          message: `你的邮箱是: ${value}`
        })
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '取消输入'
        })
      })
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

  .button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .button-group .el-button {
    margin: 0;
  }

  .my-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .dialog-content {
    padding: 20px 0;
  }

  .scroll-content {
    height: 60vh;
    overflow-y: auto;
    padding: 10px;
  }

  .scroll-content p {
    line-height: 1.5;
    margin-bottom: 10px;
  }
</style>
