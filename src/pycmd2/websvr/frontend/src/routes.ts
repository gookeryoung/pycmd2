import { createMemoryHistory, createRouter } from 'vue-router'

import HomeView from './views/HomeView.vue'
import AboutView from './views/AboutView.vue'

// Demo views - 我们将在后面创建这些组件
const ButtonsDemo = () => import('./views/demos/ButtonsDemo.vue')
const FormsDemo = () => import('./views/demos/FormsDemo.vue')
const TablesDemo = () => import('./views/demos/TablesDemo.vue')
const NotificationsDemo = () => import('./views/demos/NotificationsDemo.vue')
const DialogsDemo = () => import('./views/demos/DialogsDemo.vue')
const EChartsDemo = () => import('./views/demos/EChartsDemo.vue')

// Pinia Demo views
const PiniaBasicDemo = () => import('./views/demos/PiniaBasicDemo.vue')
const PiniaTodoDemo = () => import('./views/demos/PiniaTodoDemo.vue')
const PiniaUserDemo = () => import('./views/demos/PiniaUserDemo.vue')
const PiniaCompositionDemo = () => import('./views/demos/PiniaCompositionDemo.vue')
const PiniaPersistentDemo = () => import('./views/demos/PiniaPersistentDemo.vue')

// Todo App
const TodoApp = () => import('./views/apps/todo/TodoApp.vue')

// VueUse Demo views
const UseMouseDemo = () => import('./views/vueuse/UseMouseDemo.vue')
const UseDarkDemo = () => import('./views/vueuse/UseDarkDemo.vue')
const UseDebounceDemo = () => import('./views/vueuse/UseDebounceDemo.vue')
const UseThrottleDemo = () => import('./views/vueuse/UseThrottleDemo.vue')
const UseLocalStorageDemo = () => import('./views/vueuse/UseLocalStorageDemo.vue')
const UseClipboardDemo = () => import('./views/vueuse/UseClipboardDemo.vue')
const UseEventListenerDemo = () => import('./views/vueuse/UseEventListenerDemo.vue')
const UseWindowSizeDemo = () => import('./views/vueuse/UseWindowSizeDemo.vue')

const routes = [
  { path: '/', component: HomeView },
  { path: '/about', component: AboutView },
  {
    path: '/apps',
    children: [{ path: 'todo', component: TodoApp }]
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
  history: createMemoryHistory(),
  routes
})

export default router
