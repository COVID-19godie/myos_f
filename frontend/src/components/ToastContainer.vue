<template>
  <div class="toast-container">
    <transition-group name="toast" tag="div">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="`toast-${toast.type}`"
        @click="removeToast(toast.id)"
      >
        <div class="toast-icon">
          <i :class="getIconClass(toast.type)"></i>
        </div>
        <div class="toast-content">
          <div v-if="toast.title" class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button class="toast-close" @click.stop="removeToast(toast.id)">×</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Toast } from '../types'

interface Props {
  toasts: Toast[]
}

interface Emits {
  close: [id: number]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const removeToast = (id: number) => {
  emit('close', id)
}

const getIconClass = (type: Toast['type']) => {
  const iconMap = {
    success: 'fas fa-check-circle',
    warning: 'fas fa-exclamation-triangle',
    error: 'fas fa-times-circle',
    info: 'fas fa-info-circle'
  }
  return iconMap[type] || 'fas fa-info-circle'
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 300px;
  max-width: 400px;
  padding: 16px;
  margin-bottom: 10px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  border-left: 4px solid;
  pointer-events: auto;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toast:hover {
  transform: translateX(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
}

.toast-success {
  border-left-color: #27ae60;
}

.toast-warning {
  border-left-color: #f39c12;
}

.toast-error {
  border-left-color: #e74c3c;
}

.toast-info {
  border-left-color: #3498db;
}

.toast-icon {
  font-size: 20px;
  margin-top: 2px;
}

.toast-success .toast-icon {
  color: #27ae60;
}

.toast-warning .toast-icon {
  color: #f39c12;
}

.toast-error .toast-icon {
  color: #e74c3c;
}

.toast-info .toast-icon {
  color: #3498db;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
}

.toast-message {
  font-size: 13px;
  color: #555;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-close:hover {
  color: #333;
}

/* 动画效果 */
.toast-enter-active {
  transition: all 0.3s ease;
}

.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>