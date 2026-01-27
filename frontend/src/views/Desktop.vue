<template>
  <div 
    class="desktop-container" 
    :style="{ backgroundImage: `url(${themeStore.wallpaper})` }"
    @click.self="clearSelection"
  >
    <div class="desktop-icons">
      <div 
        v-for="icon in desktopIcons" 
        :key="icon.id"
        class="app-icon"
        :class="{ 'is-selected': selectedIds.includes(icon.id) }"
        @click="selectIcon(icon.id)"
        @dblclick="openIcon(icon)"
      >
        <div class="icon-visual glass-icon">
          <i :class="icon.icon_class || 'fa-solid fa-file'" :style="{ color: icon.color || '#fff' }"></i>
        </div>
        <span class="icon-label">{{ icon.title }}</span>
      </div>
    </div>

    <WindowContainer 
      v-for="win in windowStore.instances" 
      :key="win.id" 
      :window="win" 
    />

    <div class="dock-wrapper">
      <div class="dock-bar glass">
        <div class="dock-item" @click="openApp('browser')">
          <i class="fa-brands fa-chrome" style="color: #fff;"></i>
        </div>
        <div class="dock-item" @click="openApp('file-manager')">
          <i class="fa-solid fa-folder-open" style="color: #409eff;"></i>
        </div>
        <div class="dock-item" @click="openApp('editor')">
          <i class="fa-solid fa-code" style="color: #67c23a;"></i>
        </div>
        <div class="divider"></div>
        <div class="dock-item" @click="openApp('settings')">
          <i class="fa-solid fa-gear" style="color: #909399;"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'; // 保持原有的引用
import { useWindowStore } from '@/stores/windows';
import { useThemeStore } from '@/stores/theme'; // 1. 引入 Theme Store
import { desktopApi } from '@/services/api'; // 使用你之前封装的 API
import WindowContainer from '@/components/windows/WindowContainer.vue';

const windowStore = useWindowStore();
const themeStore = useThemeStore(); // 2. 初始化

const desktopIcons = ref<any[]>([]);
const selectedIds = ref<number[]>([]);

// 初始化加载桌面图标
onMounted(async () => {
  try {
    // 假设后端 API 返回桌面根目录内容
    const res = await desktopApi.getIcons('root'); 
    desktopIcons.value = res.data;
  } catch (e) {
    console.error('Failed to load desktop icons', e);
  }
});

// 图标交互
const selectIcon = (id: number) => {
  selectedIds.value = [id];
};

const clearSelection = () => {
  selectedIds.value = [];
};

const openIcon = (icon: any) => {
  // 1. 调试一下，看看后端到底返回了什么，方便你排查
  console.log('打开图标:', icon);

  // 2. 处理文件夹 (后端 type 为 'category')
  if (icon.type === 'category') {
    windowStore.createWindow(icon.title, 'file-manager', { 
      path: icon.data.id // 注意：文件夹ID在 data 里
    });
    return;
  }

  // 3. 处理资源文件 (后端 type 为 'resource')
  if (icon.type === 'resource' && icon.data) {
    const res = icon.data;
    
    // 如果是 Web 应用或链接 (kind === 'link')
    if (res.kind === 'link') {
      windowStore.createWindow(icon.title, 'browser', { 
        url: res.link // 将链接传给浏览器组件
      });
    } 
    // 其他文件 (图片、代码等) -> 暂时都用编辑器打开
    else {
      windowStore.createWindow(icon.title, 'editor', { 
        fileId: res.id,
        content: res.url // 或者是 file url
      });
    }
  }
};

const openApp = (type: string) => {
  windowStore.createWindow('New Window', type, {});
};
</script>

<style scoped>
.desktop-container {
  width: 100vw; height: 100vh;
  background-size: cover; background-position: center;
  position: relative; overflow: hidden;
  user-select: none;
}

/* 图标网格布局 */
.desktop-icons {
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, 100px);
  grid-template-rows: repeat(auto-fill, 110px);
  gap: 10px;
  height: calc(100vh - 100px); /* 留出 Dock 空间 */
}

.app-icon {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
  color: white;
  text-shadow: 0 1px 3px rgba(0,0,0,0.8);
}
.app-icon:hover { background: rgba(255, 255, 255, 0.1); }
.app-icon.is-selected { background: rgba(64, 158, 255, 0.4); border: 1px solid rgba(64, 158, 255, 0.6); }

.icon-visual {
  font-size: 40px; margin-bottom: 8px;
  width: 60px; height: 60px;
  display: flex; align-items: center; justify-content: center;
}

.icon-label {
  font-size: 13px; text-align: center;
  line-height: 1.2;
  word-break: break-all;
  max-width: 90px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

/* Dock 栏样式 */
.dock-wrapper {
  position: absolute; bottom: 20px; left: 0; right: 0;
  display: flex; justify-content: center;
  z-index: 9000; /* 确保在大多数窗口之上，但在全屏窗口之下 */
}

.dock-bar {
  display: flex; gap: 15px; padding: 12px 20px;
  border-radius: 24px;
  align-items: center;
  transition: transform 0.2s;
}
.dock-bar:hover { transform: scale(1.02); }

.dock-item {
  width: 50px; height: 50px;
  background: rgba(0,0,0,0.2);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.2s;
}
.dock-item:hover {
  background: rgba(255,255,255,0.2);
  transform: translateY(-10px) scale(1.1);
}
.divider { width: 1px; height: 30px; background: rgba(255,255,255,0.3); margin: 0 5px; }

/* 复用毛玻璃 */
.glass {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}
</style>