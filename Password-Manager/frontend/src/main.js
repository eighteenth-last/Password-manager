import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'
import axios from './utils/axios'

// 创建Vue应用
const app = createApp(App)

// 使用Pinia状态管理
app.use(createPinia())

// 使用Vue Router
app.use(router)

// 使用Element Plus并设置中文
app.use(ElementPlus, {
  locale: zhCn
})

// 全局挂载axios
app.config.globalProperties.$axios = axios

// 挂载应用
app.mount('#app')
