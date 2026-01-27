<template>
  <div 
    class="desktop-container" 
    :style="{ backgroundImage: `url(${themeStore.wallpaper})` }"
    @click.self="clearSelection"
    @contextmenu.prevent="handleRightClick"
  >
    <div class="desktop-icons" v-loading="loading">
      <div 
        v-for="icon in icons" 
        :key="icon.id"
        class="app-icon"
        :class="{ 'is-selected': selectedId === icon.id }"
        @click="selectIcon(icon.id)"
        @dblclick="openIcon(icon)"
      >
        <div class="icon-visual glass-effect">
          <i :class="icon.icon_class || getIconClass(icon)"></i>
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
      <div class="dock-bar glass-effect">
        <div class="dock-item" @click="openApp('file-manager')" title="资源管理器">
          <i class="fa-solid fa-folder-open" style="color: #409eff;"></i>
        </div>
        <div class="dock-item" @click="openApp('browser')" title="浏览器">
          <i class="fa-brands fa-chrome" style="color: #67c23a;"></i>
        </div>
        <div class="dock-item" @click="openApp('settings')" title="设置">
          <i class="fa-solid fa-gear" style="color: #909399;"></i>
        </div>
        
        <div class="dock-divider"></div>

        <div class="dock-item" title="回收站">
          <i class="fa-solid fa-trash" style="color: #f56c6c;"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useWindowStore } from '@/stores/windows';
import { useThemeStore } from '@/stores/theme';
import { desktopApi } from '@/services/api'; 
import WindowContainer from '@/components/windows/WindowContainer.vue';

const windowStore = useWindowStore();
const themeStore = useThemeStore();

const icons = ref<any[]>([]);
const loading = ref(false);
const selectedId = ref<number | null>(null);

// 初始化：加载桌面图标
onMounted(async () => {
  loading.value = true;
  try {
    // 调用后端 API 获取桌面文件
    const res = await desktopApi.getIcons('root'); 
    icons.value = res.data;
  } catch (e) {
    console.error('Failed to load desktop icons', e);
    // 失败时的 mock 数据，保证你能看到效果
    icons.value = [
      { id: 1, title: '我的文档', type: 'category', icon_class: 'fa-solid fa-folder' },
      { id: 2, title: 'GitHub', type: 'resource', data: { kind: 'link', link: 'https://github.com' }, icon_class: 'fa-brands fa-github' },
    ];
  } finally {
    loading.value = false;
  }
});

// 图标交互逻辑
const selectIcon = (id: number) => {
  selectedId.value = id;
};

const clearSelection = () => {
  selectedId.value = null;
};

// 核心：打开逻辑
const openIcon = (icon: any) => {
  // 1. 文件夹 -> 打开 FileManager
  if (icon.type === 'category' || icon.kind === 'folder') {
    windowStore.createWindow(icon.title, 'file-manager', { path: icon.id });
  } 
  // 2. 链接/网页 -> 打开 Browser
  else if (icon.data?.kind === 'link' || icon.kind === 'link') {
    const url = icon.data?.link || icon.url;
    windowStore.createWindow(icon.title, 'browser', { url });
  } 
  // 3. 其他 -> 默认行为 (例如打开设置)
  else {
    windowStore.createWindow(icon.title, 'settings');
  }
};

// Dock 栏快速启动
const openApp = (type: string) => {
  const titles: Record<string, string> = {
    'file-manager': '我的电脑',
    'browser': '浏览器',
    'settings': '系统设置'
  };
  windowStore.createWindow(titles[type], type);
};

// 辅助函数：根据类型获取默认图标
const getIconClass = (icon: any) => {
  if (icon.type === 'category') return 'fa-solid fa-folder';
  if (icon.kind === 'link') return 'fa-solid fa-link';
  return 'fa-solid fa-file';
};

const handleRightClick = (e: MouseEvent) => {
  console.log('右键点击坐标:', e.clientX, e.clientY);
  // 后续任务：在这里弹出右键菜单
};
</script>

<style scoped>
.desktop-container {
  width: 100vw; height: 100vh;
  background-size: cover; background-position: center;
  position: relative; overflow: hidden;
  /* 禁止文字被选中，像真 OS 一样 */
  user-select: none; 
}

/* 图标网格布局 */
.desktop-icons {
  padding: 20px;
  display: grid;
  /* 自动填充列，每列最小 90px */
  grid-template-columns: repeat(auto-fill, 90px);
  grid-template-rows: repeat(auto-fill, 100px);
  gap: 15px;
  height: calc(100vh - 120px); /* 留出 Dock 高度 */
  align-content: start;
}

.app-icon {
  display: flex; flex-direction: column; align-items: center;
  cursor: pointer; padding: 5px; border-radius: 8px;
  transition: all 0.2s;
  color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.app-icon:hover { background: rgba(255, 255, 255, 0.1); }
.app-icon.is-selected { 
  background: var(--os-selection-bg); 
  border: 1px solid rgba(255,255,255,0.3);
}

.icon-visual {
  width: 56px; height: 56px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; margin-bottom: 8px;
  /* 图标本身也是毛玻璃，增加层次感 */
  background: rgba(255,255,255,0.2);
}

.icon-label {
  font-size: 13px; text-align: center;
  line-height: 1.3;
  width: 100%;
  overflow: hidden; text-overflow: ellipsis; 
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
}

/* 底部 Dock 栏 */
.dock-wrapper {
  position: absolute; bottom: 20px; left: 0; right: 0;
  display: flex; justify-content: center;
  z-index: 9000;
}

.dock-bar {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 15px; border-radius: 24px;
  background: var(--os-dock-bg); /* 使用 CSS 变量 */
}

.dock-item {
  width: 48px; height: 48px;
  border-radius: 12px;
  background: rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; cursor: pointer;
  transition: transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.dock-item:hover {
  transform: translateY(-10px) scale(1.1);
  background: rgba(255,255,255,0.2);
}

.dock-divider {
  width: 1px; height: 30px; 
  background: rgba(255,255,255,0.2); 
  margin: 0 5px;
}
</style>