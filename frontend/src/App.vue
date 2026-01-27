<template>
  <div id="app">
    <!-- 登录界面 -->
    <LoginScreen v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
    
    <!-- 主界面 -->
    <DesktopInterface v-else />
    
    <!-- Toast容器 -->
    <ToastContainer :toasts="toasts" @close="removeToast" />
  </div>
</template>

<script setup lang="ts">
import { ref, provide, onMounted, onUnmounted } from 'vue'
import LoginScreen from './components/LoginScreen.vue'
import DesktopInterface from './components/DesktopInterface.vue'
import ToastContainer from './components/ToastContainer.vue'
import type { Toast } from './types'

const isLoggedIn = ref(false)
const toasts = ref<Toast[]>([])

const handleLoginSuccess = () => {
  isLoggedIn.value = true
}

const showToast = (message: string, title: string = '提示', type: Toast['type'] = 'info', duration = 2000) => {
  const id = Date.now()
  toasts.value.push({ id, message, title, type, duration })
}

const removeToast = (id: number) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

// 提供全局方法
provide('showToast', showToast)

// 全局错误处理
onMounted(() => {
  // 捕获未处理的错误
  window.addEventListener('error', (e) => {
    console.error('Global error:', e.error)
    showToast('发生未知错误', '错误', 'error')
  })
  
  // 捕获Promise错误
  window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason)
    showToast('请求失败', '错误', 'error')
  })
})
</script>

<style>
#app {
  height: 100vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>