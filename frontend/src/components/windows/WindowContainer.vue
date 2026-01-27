<template>
  <teleport to="body">
    <div
      v-show="!window.isMinimized"
      ref="windowRef"
      class="window-container glass-effect"
      :class="{ 
        'is-active': isActive, 
        'is-maximized': window.isMaximized 
      }"
      :style="windowStyle"
      @mousedown.capture="windowStore.focusWindow(window.id)"
    >
      <div class="window-header" ref="dragHandle" @dblclick="toggleMaximize">
        <div class="header-left">
          <i :class="window.icon || getDefaultIcon()" class="window-icon"></i>
          <span class="window-title">{{ window.title }}</span>
        </div>
        
        <div class="header-controls">
          <button class="win-btn minimize" @click.stop="windowStore.minimize(window.id)">
            <i class="fa-solid fa-minus"></i>
          </button>
          <button class="win-btn maximize" @click.stop="toggleMaximize">
             <i :class="window.isMaximized ? 'fa-regular fa-window-restore' : 'fa-regular fa-square'"></i>
          </button>
          <button class="win-btn close" @click.stop="windowStore.closeWindow(window.id)">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
      </div>

      <div class="window-body">
        <component 
          :is="componentMap[window.type]" 
          v-bind="window.content || {}"
        />
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { computed, ref, defineAsyncComponent } from 'vue';
import { useWindowStore } from '@/stores/windows';
import { useWindowDraggable } from '@/composables/useWindowDraggable';
import type { WindowInstance } from '@/types';

const props = defineProps<{ window: WindowInstance }>();
const windowStore = useWindowStore();

// 1. 动态组件映射表
const componentMap: Record<string, any> = {
  'settings': defineAsyncComponent(() => import('@/views/Settings.vue')),
  'file-manager': defineAsyncComponent(() => import('@/views/FileManager.vue')),
  'browser': defineAsyncComponent(() => import('@/views/Browser.vue')),
  // 其他应用类型可以在这里添加
};

// 2. 状态判断
const isActive = computed(() => windowStore.activeId === props.window.id);
const windowRef = ref<HTMLElement | null>(null);
const dragHandle = ref<HTMLElement | null>(null);

// 3. 拖拽逻辑集成
const { position, handleMouseDown } = useWindowDraggable(windowRef, {
  initialValue: { x: props.window.x, y: props.window.y },
  handle: dragHandle,
  disabled: computed(() => props.window.isMaximized)
});

// 4. 样式计算
const windowStyle = computed(() => {
  if (props.window.isMaximized) {
    return {
      top: '0px', left: '0px', width: '100%', height: '100%',
      transform: 'none', zIndex: props.window.zIndex
    };
  }
  return {
    width: `${props.window.width}px`,
    height: `${props.window.height}px`,
    // 使用 transform 提升渲染性能
    transform: `translate(${position.x}px, ${position.y}px)`,
    zIndex: props.window.zIndex
  };
});

// 5. 默认图标
const getDefaultIcon = () => {
  switch (props.window.type) {
    case 'settings': return 'fa-solid fa-gear';
    case 'file-manager': return 'fa-solid fa-folder';
    case 'browser': return 'fa-solid fa-globe';
    default: return 'fa-solid fa-window-maximize';
  }
};

// 6. 最大化切换
const toggleMaximize = () => {
  windowStore.toggleMaximize(props.window.id);
};

// 7. 暴露拖拽事件给header
onMounted(() => {
  const header = dragHandle.value;
  if (header) {
    header.addEventListener('mousedown', handleMouseDown);
  }
});
</script>

<style scoped>
.window-container {
  position: fixed; top: 0; left: 0;
  display: flex; flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  /* 初始颜色，会被 theme.css 的变量覆盖 */
  background: white; 
}

/* 激活状态高亮边框 */
.is-active {
  box-shadow: 0 15px 50px rgba(0,0,0,0.4);
  border: 1px solid var(--os-border-color);
}

.window-header {
  height: 40px; flex-shrink: 0;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid var(--os-glass-border);
  user-select: none;
  cursor: move;
}

.header-left { display: flex; align-items: center; gap: 10px; color: var(--os-text-primary); }
.header-controls { display: flex; gap: 8px; }

.win-btn {
  width: 28px; height: 28px; border-radius: 6px;
  border: none; background: transparent;
  color: var(--os-text-secondary);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.win-btn:hover { background: rgba(0,0,0,0.1); }
.win-btn.close:hover { background: #ff5f57; color: white; }

.window-body { flex: 1; overflow: hidden; position: relative; background: var(--os-bg-color); }

/* 最大化时移除圆角 */
.is-maximized { border-radius: 0; }

.window-icon {
  font-size: 14px;
  color: var(--os-text-secondary);
}

.window-title {
  font-size: 14px;
  font-weight: 600;
}
</style>