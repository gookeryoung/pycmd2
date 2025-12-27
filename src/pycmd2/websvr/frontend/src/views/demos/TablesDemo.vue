<template>
  <div class="demo-container">
    <h2>表格示例</h2>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="基础表格">
          <el-table :data="tableData" style="width: 100%">
            <el-table-column prop="date" label="日期" width="180" />
            <el-table-column prop="name" label="姓名" width="180" />
            <el-table-column prop="address" label="地址" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="带斑马纹表格">
          <el-table :data="tableData" stripe style="width: 100%">
            <el-table-column prop="date" label="日期" width="180" />
            <el-table-column prop="name" label="姓名" width="180" />
            <el-table-column prop="address" label="地址" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="带边框表格">
          <el-table :data="tableData" border style="width: 100%">
            <el-table-column prop="date" label="日期" width="180" />
            <el-table-column prop="name" label="姓名" width="180" />
            <el-table-column prop="address" label="地址" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="带状态表格">
          <el-table :data="statusTableData" style="width: 100%">
            <el-table-column prop="name" label="产品名称" />
            <el-table-column prop="sell" label="销量" />
            <el-table-column prop="price" label="单价" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.status === '热销' ? 'success' : 'info'">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="固定列和表头">
          <el-table :data="largeTableData" style="width: 100%" height="250">
            <el-table-column fixed prop="date" label="日期" width="150" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="state" label="省份" width="120" />
            <el-table-column prop="city" label="市区" width="120" />
            <el-table-column prop="address" label="地址" width="300" />
            <el-table-column prop="zip" label="邮编" width="120" />
            <el-table-column fixed="right" label="操作" width="120">
              <template #default>
                <el-button link type="primary" size="small">查看</el-button>
                <el-button link type="primary" size="small">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="可展开表格">
          <el-table :data="expandTableData" style="width: 100%">
            <el-table-column type="expand">
              <template #default="props">
                <p style="margin-left: 20px">状态: {{ props.row.state }}</p>
                <p style="margin-left: 20px">城市: {{ props.row.city }}</p>
                <p style="margin-left: 20px">地址: {{ props.row.address }}</p>
                <p style="margin-left: 20px">邮编: {{ props.row.zip }}</p>
              </template>
            </el-table-column>
            <el-table-column label="日期" prop="date" />
            <el-table-column label="姓名" prop="name" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="demo-section">
      <el-col :span="24">
        <el-card header="自定义表头">
          <el-table :data="customHeaderTableData" style="width: 100%">
            <el-table-column>
              <template #header>
                <div style="display: flex; align-items: center">
                  <el-icon style="margin-right: 5px">
                    <Calendar />
                  </el-icon>
                  <span>日期</span>
                </div>
              </template>
              <template #default="scope">
                <span style="margin-left: 10px">{{ scope.row.date }}</span>
              </template>
            </el-table-column>
            <el-table-column label="姓名">
              <template #default="scope">
                <el-popover effect="light" trigger="hover" placement="top" width="auto">
                  <template #default>
                    <div>姓名: {{ scope.row.name }}</div>
                    <div>地址: {{ scope.row.address }}</div>
                  </template>
                  <template #reference>
                    <el-tag>{{ scope.row.name }}</el-tag>
                  </template>
                </el-popover>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #header>
                <el-input v-model="search" size="small" placeholder="搜索姓名" />
              </template>
              <template #default="scope">
                <el-button size="small" @click="handleEdit(scope.$index, scope.row)"> 编辑 </el-button>
                <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)"> 删除 </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import { Calendar } from '@element-plus/icons-vue'

  interface User {
    date: string
    name: string
    address: string
  }

  const search = ref('')

  // 基础表格数据
  const tableData: User[] = [
    {
      date: '2016-05-03',
      name: '张三',
      address: '北京市朝阳区普陀区金沙江路 1518 弄'
    },
    {
      date: '2016-05-02',
      name: '李四',
      address: '北京市朝阳区普陀区金沙江路 1517 弄'
    },
    {
      date: '2016-05-04',
      name: '王五',
      address: '北京市朝阳区普陀区金沙江路 1519 弄'
    },
    {
      date: '2016-05-01',
      name: '赵六',
      address: '北京市朝阳区普陀区金沙江路 1516 弄'
    }
  ]

  // 状态表格数据
  const statusTableData = [
    {
      name: 'iPhone 14',
      sell: 3200,
      price: 5999,
      status: '热销'
    },
    {
      name: 'iPad Pro',
      sell: 1200,
      price: 6799,
      status: '缺货'
    },
    {
      name: 'MacBook Air',
      sell: 850,
      price: 7999,
      status: '热销'
    },
    {
      name: 'Apple Watch',
      sell: 2100,
      price: 2999,
      status: '热销'
    },
    {
      name: 'AirPods Pro',
      sell: 3800,
      price: 1999,
      status: '缺货'
    }
  ]

  // 大型表格数据
  const largeTableData = [
    {
      date: '2016-05-03',
      name: '王小虎',
      state: '上海',
      city: '普陀区',
      address: '上海市普陀区金沙江路 1518 弄',
      zip: 200333
    },
    {
      date: '2016-05-02',
      name: '王小虎',
      state: '上海',
      city: '普陀区',
      address: '上海市普陀区金沙江路 1518 弄',
      zip: 200333
    },
    {
      date: '2016-05-04',
      name: '王小虎',
      state: '上海',
      city: '普陀区',
      address: '上海市普陀区金沙江路 1518 弄',
      zip: 200333
    },
    {
      date: '2016-05-01',
      name: '王小虎',
      state: '上海',
      city: '普陀区',
      address: '上海市普陀区金沙江路 1518 弄',
      zip: 200333
    },
    {
      date: '2016-05-08',
      name: '王小虎',
      state: '上海',
      city: '普陀区',
      address: '上海市普陀区金沙江路 1518 弄',
      zip: 200333
    },
    {
      date: '2016-05-06',
      name: '王小虎',
      state: '上海',
      city: '普陀区',
      address: '上海市普陀区金沙江路 1518 弄',
      zip: 200333
    },
    {
      date: '2016-05-07',
      name: '王小虎',
      state: '上海',
      city: '普陀区',
      address: '上海市普陀区金沙江路 1518 弄',
      zip: 200333
    }
  ]

  // 可展开表格数据
  const expandTableData = [
    {
      date: '2016-05-03',
      name: 'Tom',
      state: 'California',
      city: 'Los Angeles',
      address: 'No. 189, Grove St, Los Angeles',
      zip: 'CA 90036'
    },
    {
      date: '2016-05-02',
      name: 'Tom',
      state: 'California',
      city: 'Los Angeles',
      address: 'No. 189, Grove St, Los Angeles',
      zip: 'CA 90036'
    },
    {
      date: '2016-05-04',
      name: 'Tom',
      state: 'California',
      city: 'Los Angeles',
      address: 'No. 189, Grove St, Los Angeles',
      zip: 'CA 90036'
    },
    {
      date: '2016-05-01',
      name: 'Tom',
      state: 'California',
      city: 'Los Angeles',
      address: 'No. 189, Grove St, Los Angeles',
      zip: 'CA 90036'
    }
  ]

  // 自定义表头表格数据
  const customHeaderTableData = [
    {
      date: '2016-05-03',
      name: 'Tom',
      address: 'No. 189, Grove St, Los Angeles'
    },
    {
      date: '2016-05-02',
      name: 'John',
      address: 'No. 189, Grove St, Los Angeles'
    },
    {
      date: '2016-05-04',
      name: 'Morgan',
      address: 'No. 189, Grove St, Los Angeles'
    },
    {
      date: '2016-05-01',
      name: 'Jessy',
      address: 'No. 189, Grove St, Los Angeles'
    }
  ]

  // 操作方法
  const handleEdit = (index: number, row: User) => {
    console.log(index, row)
  }

  const handleDelete = (index: number, row: User) => {
    console.log(index, row)
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
</style>
