<template>
  <div class="desktop-interface">
    <!-- 桌面背景 -->
    <div 
      class="desktop-background"
      :style="{ backgroundImage: `url(${wallpaperUrl})` }"
    ></div>
    
    <!-- 桌面图标区域 -->
    <div class="desktop-icons">
      <div 
        v-for="icon in desktopIcons" 
        :key="icon.id" 
        class="desktop-icon glass"
        @dblclick="openIcon(icon)"
        @contextmenu.prevent="showContextMenu($event, icon)"
      >
        <div class="icon-visual">
          <i :class="getIconClass(icon)"></i>
        </div>
        <span class="icon-label">{{ icon.title }}</span>
      </div>
    </div>
    
    <!-- Dock栏 -->
    <div class="dock-container">
      <div class="dock glass">
        <div class="dock-item" @click="openPC">
          <i class="fas fa-desktop"></i>
        </div>
        <div class="dock-item" @click="uploadFile">
          <i class="fas fa-upload"></i>
        </div>
        <div class="dock-item" @click="createFolder">
          <i class="fas fa-folder-plus"></i>
        </div>
        <div class="dock-item" @click="refreshDesktop">
          <i class="fas fa-refresh"></i>
        </div>
      </div>
    </div>
    
    <!-- 右键菜单 -->
    <div 
      v-if="contextMenu.visible"
      class="context-menu glass"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      @click="hideContextMenu"
    >
      <div class="menu-item" @click="openSelected">📂 打开</div>
      <div class="menu-item" @click="renameSelected">✏️ 重命名</div>
      <div class="menu-item" @click="deleteSelected" style="color: #ff4757;">🗑️ 删除</div>
      <div class="menu-separator"></div>
      <div class="menu-item" @click="createFolder">📁 新建文件夹</div>
    </div>
    
    <!-- 加载提示 -->
    <div v-if="loading" class="loading-overlay">
      <i class="fas fa-spinner fa-spin"></i>
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { desktopApi } from '../services/api'
import type { DesktopItem } from '../types'

// 响应式数据
const wallpaperUrl = ref('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')
const desktopIcons = ref<DesktopItem[]>([])
const loading = ref(false)
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  selectedItem: null as DesktopItem | null
})

// 获取图标类名
const getIconClass = (item: DesktopItem) => {
  if (item.type === 'category') {
    return 'fas fa-folder' + ' fa-icon-lg'
  }
  
  // 根据文件类型返回对应图标
  const iconMap: { [key: string]: string } = {
    'doc': 'fas fa-file-word',
    'image': 'fas fa-file-image', 
    'video': 'fas fa-file-video',
    'audio': 'fas fa-file-audio',
    'archive': 'fas fa-file-zipper',
    'link': 'fas fa-link',
    'pdf': 'fas fa-file-pdf'
  }
  
  const iconClass = iconMap[item.data.kind || ''] || 'fas fa-file'
  return iconClass + ' fa-icon-lg'
}

// 加载桌面图标
const loadDesktopIcons = async () => {
  loading.value = true
  try {
    const response = await desktopApi.getIcons('root')
    desktopIcons.value = response.data.results || response.data || []
    ElMessage.success('桌面加载完成')
  } catch (error) {
    console.error('加载桌面图标失败:', error)
    ElMessage.error('加载桌面失败')
  } finally {
    loading.value = false
  }
}

// 打开图标
const openIcon = (item: DesktopItem) => {
  console.log('打开项目:', item)
  ElMessage.info(`打开: ${item.title}`)
  
  // TODO: 根据项目类型创建对应的窗口
  if (item.type === 'category') {
    // 创建文件夹窗口
  } else {
    // 创建文件预览窗口
  }
}

// Dock栏功能
const openPC = () => {
  ElMessage.info('打开我的电脑')
}

const uploadFile = () => {
  ElMessage.info('文件上传功能')
}

const createFolder = () => {
  ElMessage.info('创建文件夹功能')
}

const refreshDesktop = () => {
  loadDesktopIcons()
}

// 右键菜单
const showContextMenu = (event: MouseEvent, item: DesktopItem) => {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    selectedItem: item
  }
}

const hideContextMenu = () => {
  contextMenu.value.visible = false
}

const openSelected = () => {
  if (contextMenu.value.selectedItem) {
    openIcon(contextMenu.value.selectedItem)
  }
  hideContextMenu()
}

const renameSelected = () => {
  if (contextMenu.value.selectedItem) {
    const newName = prompt('请输入新名称:', contextMenu.value.selectedItem.title)
    if (newName && newName !== contextMenu.value.selectedItem.title) {
      ElMessage.info(`重命名为: ${newName}`)
    }
  }
  hideContextMenu()
}

const deleteSelected = () => {
  if (contextMenu.value.selectedItem) {
    if (confirm(`确定要删除 "${contextMenu.value.selectedItem.title}" 吗？`)) {
      ElMessage.info('删除功能待实现')
    }
  }
  hideContextMenu()
}

// 生命周期
onMounted(() => {
  loadDesktopIcons()
})
</script>

<style scoped>
.desktop-interface {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.desktop-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  z-index: 1;
}

.desktop-icons {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: calc(100% - 100px);
  padding: 20px;
  z-index: 2;
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 20px;
}

.desktop-icon {
  width: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 10px;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.desktop-icon:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.icon-visual {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 14px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  font-size: 32px;
  margin-bottom: 8px;
}

.icon-label {
  color: white;
  font-size: 13px;
  text-align: center;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 4px;
  backdrop-filter: blur(5px);
}

.fa-icon-lg {
  font-size: 32px;
}

.dock-container {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
}

.dock {
  padding: 10px 20px;
  border-radius: 25px;
  display: flex;
  gap: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.dock-item {
  width: 60px;
  height: 60px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #333;
}

.dock-item:hover {
  transform: scale(1.2) translateY(-5px);
  background: rgba(255, 255, 255, 0.6);
}

.context-menu {
  position: fixed;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 10px;
  padding: 8px 0;
  min-width: 150px;
  z-index: 10000;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.menu-item {
  padding: 10px 20px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: background 0.2s;
}

.menu-item:hover {
  background: rgba(0, 0, 0, 0.1);
}

.menu-separator {
  height: 1px;
  background: rgba(0, 0, 0, 0.1);
  margin: 5px 0;
}

.loading-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 20px 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 10000;
}

.fa-spinner {
  font-size: 20px;
}
</style>