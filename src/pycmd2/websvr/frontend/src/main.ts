import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './routes'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createPinia } from 'pinia'
import VChart from 'vue-echarts'

const app = createApp(App)
const pinia = createPinia()

app.component('VChart', VChart)
app.use(router)
app.use(pinia)
app.use(ElementPlus)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
