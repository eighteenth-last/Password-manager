import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard-home',
        component: () => import('../views/dashboard/HomeView.vue')
      },
      {
        path: 'passwords',
        name: 'passwords',
        component: () => import('../views/dashboard/PasswordsView.vue')
      },
      {
        path: 'bindings',
        name: 'bindings',
        component: () => import('../views/dashboard/BindingsView.vue')
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('../views/dashboard/SettingsView.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue')
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    // 如果用户未登录，重定向到登录页
    if (!authStore.isLoggedIn) {
      next({ name: 'login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  } else {
    // 如果用户已登录且尝试访问登录或注册页，重定向到仪表盘
    if (authStore.isLoggedIn && (to.name === 'login' || to.name === 'register')) {
      next({ name: 'dashboard' })
    } else {
      next()
    }
  }
})

export default router
