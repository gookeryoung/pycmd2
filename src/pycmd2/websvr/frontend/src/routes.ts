import { createMemoryHistory, createRouter } from 'vue-router'

import HomeView from './HomeView.vue'
import AboutView from './AboutView.vue'

// Demo views - 我们将在后面创建这些组件
const ButtonsDemo = () => import('./views/demos/ButtonsDemo.vue')
const FormsDemo = () => import('./views/demos/FormsDemo.vue')
const TablesDemo = () => import('./views/demos/TablesDemo.vue')
const NotificationsDemo = () => import('./views/demos/NotificationsDemo.vue')
const DialogsDemo = () => import('./views/demos/DialogsDemo.vue')

const routes = [
    { path: '/', component: HomeView },
    { path: '/about', component: AboutView },
    {
        path: '/demos',
        children: [
            { path: 'buttons', component: ButtonsDemo },
            { path: 'forms', component: FormsDemo },
            { path: 'tables', component: TablesDemo },
            { path: 'notifications', component: NotificationsDemo },
            { path: 'dialogs', component: DialogsDemo },
        ]
    },
]

const router = createRouter({
    history: createMemoryHistory(),
    routes,
})

export default router
