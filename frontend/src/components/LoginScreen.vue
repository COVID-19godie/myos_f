<template>
  <div class="login-screen">
    <div class="login-container glass">
      <div class="login-header">
        <h1>ZMG Cloud OS</h1>
        <p>云端操作系统管理平台</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <el-input
            v-model="username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
            required
          />
        </div>
        
        <div class="input-group">
          <el-input
            v-model="password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            required
          />
        </div>
        
        <el-button 
          type="primary" 
          size="large" 
          :loading="loading"
          class="login-btn"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登录' }}
        </el-button>
      </form>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { desktopApi } from '../services/api'
import { ElMessage } from 'element-plus'

const emit = defineEmits<{
  loginSuccess: [void]
}>()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    errorMessage.value = '请输入用户名和密码'
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await desktopApi.login(username.value, password.value)
    const data = response.data
    
    localStorage.setItem('token', data.access)
    ElMessage.success('登录成功')
    emit('loginSuccess')
  } catch (error: any) {
    console.error('登录失败:', error)
    errorMessage.value = error.response?.data?.detail || '登录失败，请检查用户名密码'
    ElMessage.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-screen {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: cover;
}

.login-container {
  width: 400px;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #fff;
  font-size: 28px;
  margin: 0 0 10px 0;
  font-weight: 300;
}

.login-header p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 14px;
}

.login-form {
  width: 100%;
}

.input-group {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.error-message {
  margin-top: 15px;
  padding: 10px;
  background: rgba(245, 101, 101, 0.2);
  border: 1px solid rgba(245, 101, 101, 0.3);
  border-radius: 8px;
  color: #fed7d7;
  text-align: center;
  font-size: 14px;
}

.glass {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
</style>