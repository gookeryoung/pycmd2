import { createWebHistory, createRouter } from 'vue-router'

import HomeView from './views/HomeView.vue'
import AboutView from './views/AboutView.vue'

// Demo views - 使用魔法注释进行代码分割分组
const ButtonsDemo = () => import(/* webpackChunkName: "element-demos" */ './views/demos/ButtonsDemo.vue')
const FormsDemo = () => import(/* webpackChunkName: "element-demos" */ './views/demos/FormsDemo.vue')
const TablesDemo = () => import(/* webpackChunkName: "element-demos" */ './views/demos/TablesDemo.vue')
const NotificationsDemo = () => import(/* webpackChunkName: "element-demos" */ './views/demos/NotificationsDemo.vue')
const DialogsDemo = () => import(/* webpackChunkName: "element-demos" */ './views/demos/DialogsDemo.vue')
const EChartsDemo = () => import(/* webpackChunkName: "chart-demos" */ './views/demos/EChartsDemo.vue')

// Pinia Demo views - 分组到 pinia-demos chunk
const PiniaBasicDemo = () => import(/* webpackChunkName: "pinia-demos" */ './views/demos/PiniaBasicDemo.vue')
const PiniaTodoDemo = () => import(/* webpackChunkName: "pinia-demos" */ './views/demos/PiniaTodoDemo.vue')
const PiniaUserDemo = () => import(/* webpackChunkName: "pinia-demos" */ './views/demos/PiniaUserDemo.vue')
const PiniaCompositionDemo = () =>
  import(/* webpackChunkName: "pinia-demos" */ './views/demos/PiniaCompositionDemo.vue')
const PiniaPersistentDemo = () => import(/* webpackChunkName: "pinia-demos" */ './views/demos/PiniaPersistentDemo.vue')

// Todo App - 独立 chunk
const TodoApiApp = () => import(/* webpackChunkName: "apps" */ './views/apps/todo/TodoApiApp.vue')
const EmojiViewer = () => import(/* webpackChunkName: "apps" */ './views/apps/EmojiViewer.vue')

// VueUse Demo views - 分组到 vueuse-demos chunk
const UseMouseDemo = () => import(/* webpackChunkName: "vueuse-demos" */ './views/vueuse/UseMouseDemo.vue')
const UseDarkDemo = () => import(/* webpackChunkName: "vueuse-demos" */ './views/vueuse/UseDarkDemo.vue')
const UseDebounceDemo = () => import(/* webpackChunkName: "vueuse-demos" */ './views/vueuse/UseDebounceDemo.vue')
const UseThrottleDemo = () => import(/* webpackChunkName: "vueuse-demos" */ './views/vueuse/UseThrottleDemo.vue')
const UseLocalStorageDemo = () =>
  import(/* webpackChunkName: "vueuse-demos" */ './views/vueuse/UseLocalStorageDemo.vue')
const UseClipboardDemo = () => import(/* webpackChunkName: "vueuse-demos" */ './views/vueuse/UseClipboardDemo.vue')
const UseEventListenerDemo = () =>
  import(/* webpackChunkName: "vueuse-demos" */ './views/vueuse/UseEventListenerDemo.vue')
const UseWindowSizeDemo = () => import(/* webpackChunkName: "vueuse-demos" */ './views/vueuse/UseWindowSizeDemo.vue')

const routes = [
  { path: '/', component: HomeView },
  { path: '/about', component: AboutView },
  {
    path: '/apps',
    children: [
      { path: 'todo-api', component: TodoApiApp },
      { path: 'emoji-viewer', component: EmojiViewer }
    ]
  },
  {
    path: '/demos',
    children: [
      { path: 'buttons', component: ButtonsDemo },
      { path: 'forms', component: FormsDemo },
      { path: 'tables', component: TablesDemo },
      { path: 'notifications', component: NotificationsDemo },
      { path: 'dialogs', component: DialogsDemo },
      { path: 'echarts', component: EChartsDemo }
    ]
  },
  {
    path: '/pinia-demos',
    children: [
      { path: 'basic', component: PiniaBasicDemo },
      { path: 'todos', component: PiniaTodoDemo },
      { path: 'user', component: PiniaUserDemo },
      { path: 'composition', component: PiniaCompositionDemo },
      { path: 'persistent', component: PiniaPersistentDemo }
    ]
  },
  {
    path: '/vueuse-demos',
    children: [
      { path: 'mouse', component: UseMouseDemo },
      { path: 'dark', component: UseDarkDemo },
      { path: 'debounce', component: UseDebounceDemo },
      { path: 'throttle', component: UseThrottleDemo },
      { path: 'localstorage', component: UseLocalStorageDemo },
      { path: 'clipboard', component: UseClipboardDemo },
      { path: 'eventlistener', component: UseEventListenerDemo },
      { path: 'windowsize', component: UseWindowSizeDemo }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
