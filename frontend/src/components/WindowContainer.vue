<template>
  <Teleport to="body">
    <div 
      v-show="!windowData.isMinimized"
      class="window-frame glass"
      :class="{ 'window-maximized': windowData.isMaximized }"
      :style="windowStyle"
      @mousedown="focusWindow"
      @mouseenter="showControls = true"
      @mouseleave="showControls = false"
    >
      <!-- 窗口头部 -->
      <div 
        class="window-header" 
        @mousedown="startDrag"
        :class="{ 'header-dragging': isDragging }"
      >
        <div class="window-title">
          <el-icon v-if="windowData.type === 'folder'" class="title-icon">
            <FolderOpened />
          </el-icon>
          <el-icon v-else-if="windowData.type === 'pdf'" class="title-icon">
            <Document />
          </el-icon>
          <el-icon v-else-if="windowData.type === 'image'" class="title-icon">
            <Picture />
          </el-icon>
          <el-icon v-else class="title-icon">
            <Monitor />
          </el-icon>
          <span class="title-text">{{ windowData.title }}</span>
        </div>
        
        <!-- 窗口控制按钮 -->
        <div class="window-controls" :class="{ 'controls-visible': showControls || isDragging }">
          <button 
            class="control-btn minimize-btn" 
            @click="minimizeWindow"
            title="最小化"
          >
            <el-icon><SemiSelect /></el-icon>
          </button>
          <button 
            class="control-btn maximize-btn" 
            @click="toggleMaximize"
            title="最大化/还原"
          >
            <el-icon v-if="windowData.isMaximized"><Crop /></el-icon>
            <el-icon v-else><FullScreen /></el-icon>
          </button>
          <button 
            class="control-btn close-btn" 
            @click="closeWindow"
            title="关闭"
          >
            <el-icon><Close /></el-icon>
          </button>
        </div>
      </div>

      <!-- 窗口内容区域 -->
      <div class="window-content">
        <component 
          :is="getContentComponent"
          v-if="contentComponent"
          :data="windowData.content"
          :window-id="windowData.id"
          @close="closeWindow"
        />
        
        <!-- iframe 内容 -->
        <iframe 
          v-else-if="windowData.type === 'iframe' || windowData.type === 'app'"
          :src="windowData.content"
          frameborder="0"
          allowfullscreen
          class="content-iframe"
        ></iframe>
        
        <!-- 图片预览 -->
        <div v-else-if="windowData.type === 'image'" class="image-viewer">
          <img :src="windowData.content" alt="预览图片" @load="onImageLoad" />
        </div>
        
        <!-- 默认内容 -->
        <div v-else class="default-content">
          <el-empty description="暂不支持预览此类型文件" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, defineAsyncComponent } from 'vue'
import { useWindowStore } from '../stores/windows'
import type { WindowInstance } from '../types'
import { 
  FolderOpened, Document, Picture, Monitor, 
  SemiSelect, Close, FullScreen, Crop 
} from '@element-plus/icons-vue'

interface Props {
  window: WindowInstance
}

interface Emits {
  close: [windowId: string]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const windowStore = useWindowStore()

// 响应式数据
const isDragging = ref(false)
const showControls = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

// 计算属性
const windowData = computed(() => props.window)

const windowStyle = computed(() => {
  if (windowData.value.isMaximized) {
    return {
      position: 'fixed',
      top: '0px',
      left: '0px',
      width: '100vw',
      height: '100vh',
      zIndex: windowData.value.zIndex
    }
  }
  
  return {
    position: 'fixed',
    left: windowData.value.x + 'px',
    top: windowData.value.y + 'px',
    width: (windowData.value.width || 600) + 'px',
    height: (windowData.value.height || 400) + 'px',
    zIndex: windowData.value.zIndex,
    minWidth: '300px',
    minHeight: '200px'
  }
})

// 动态组件
const contentComponent = computed(() => {
  switch (windowData.value.type) {
    case 'folder':
      return defineAsyncComponent(() => import('./FileManager.vue'))
    case 'pdf':
      return defineAsyncComponent(() => import('./PDFViewer.vue'))
    default:
      return null
  }
})

const getContentComponent = computed(() => contentComponent.value)

// 事件处理
const focusWindow = () => {
  windowStore.focusWindow(windowData.value.id)
}

const startDrag = (e: MouseEvent) => {
  if (windowData.value.isMaximized) return
  
  isDragging.value = true
  focusWindow()
  
  const rect = (e.currentTarget as HTMLElement).parentElement!.getBoundingClientRect()
  dragOffset.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
  
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
}

const handleDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  
  const newX = e.clientX - dragOffset.value.x
  const newY = e.clientY - dragOffset.value.y
  
  windowStore.updateWindowPosition(windowData.value.id, newX, newY)
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}

const minimizeWindow = () => {
  windowStore.minimizeWindow(windowData.value.id)
}

const toggleMaximize = () => {
  windowStore.maximizeWindow(windowData.value.id)
}

const closeWindow = () => {
  windowStore.closeWindow(windowData.value.id)
  emit('close', windowData.value.id)
}

const onImageLoad = () => {
  // 图片加载完成后的处理
  console.log('图片加载完成')
}

// 生命周期
onMounted(() => {
  focusWindow()
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.window-frame {
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow: hidden;
  border: 1px solid var(--os-glass-border);
  background: var(--os-glass-bg);
  backdrop-filter: blur(var(--os-glass-blur));
  -webkit-backdrop-filter: blur(var(--os-glass-blur));
}

.window-frame.window-maximized {
  border-radius: 0;
  box-shadow: none;
}

.window-header {
  height: 40px;
  background: var(--os-glass-bg);
  backdrop-filter: blur(var(--os-glass-blur));
  border-bottom: 1px solid var(--os-border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  cursor: move;
  user-select: none;
  transition: all 0.2s ease;
}

.header-dragging {
  background: var(--os-glass-bg);
}

.window-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--os-text-primary);
}

.title-icon {
  font-size: 16px;
  color: var(--os-text-secondary);
}

.title-text {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.window-controls {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.controls-visible {
  opacity: 1;
}

.control-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: var(--os-text-secondary);
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.minimize-btn:hover {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.maximize-btn:hover {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.close-btn:hover {
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.window-content {
  flex: 1;
  background: var(--os-glass-bg);
  backdrop-filter: blur(var(--os-glass-blur));
  -webkit-backdrop-filter: blur(var(--os-glass-blur));
  position: relative;
  overflow: hidden;
  color: var(--os-text-primary);
}

.content-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.image-viewer {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.image-viewer img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.default-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>