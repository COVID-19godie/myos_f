import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Login',
    component: () => import('../components/LoginScreen.vue')
  },
  {
    path: '/desktop',
    name: 'Desktop',
    component: () => import('../components/DesktopInterface.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查认证
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    // 需要认证但未登录，重定向到登录页
    next('/')
  } else if (to.path === '/' && token) {
    // 已登录用户访问登录页，重定向到桌面
    next('/desktop')
  } else {
    next()
  }
})

export default router