<template>
  <teleport to="body">
    <div 
      ref="windowRef"
      class="window-container glass"
      :class="{ 'is-active': activeId === window.id }"
      :style="windowStyle"
      @mousedown="windowStore.focusWindow(window.id)"
    >
      <div class="window-header" ref="dragHandle">
        <div class="title-area">
          <i :class="window.icon || 'fa-solid fa-window-maximize'"></i>
          <span class="title-text">{{ window.title }}</span>
        </div>
        <div class="window-controls">
          <button @click.stop="windowStore.minimize(window.id)" class="ctrl-btn min">
            <el-icon><SemiSelect /></el-icon>
          </button>
          <button @click.stop="windowStore.closeWindow(window.id)" class="ctrl-btn close">
            <el-icon><Close /></el-icon>
          </button>
        </div>
      </div>

      <div class="window-content">
        <component 
          :is="currentApp" 
          v-bind="window.props" 
        />
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { computed, ref, defineAsyncComponent } from 'vue';
import { useWindowStore } from '@/stores/windows';
import { useDraggable } from '@/composables/useDraggable';
import { storeToRefs } from 'pinia';
import { SemiSelect, Close } from '@element-plus/icons-vue';

const props = defineProps<{ window: any }>();
const windowStore = useWindowStore();
const { activeId } = storeToRefs(windowStore);

const windowRef = ref<HTMLElement>();
const dragHandle = ref<HTMLElement>();

// 1. 集成你写好的 Hook
const { position } = useDraggable(windowRef, {
  handle: dragHandle, // 只有标题栏能拖拽
  bounds: 'viewport'
});

// 2. 窗口动态样式
const windowStyle = computed(() => ({
  zIndex: props.window.zIndex,
  transform: `translate(${position.value.x}px, ${position.value.y}px)`,
  display: props.window.isMinimized ? 'none' : 'flex'
}));

// 3. 应用映射表：根据 window.type 动态加载组件
const currentApp = computed(() => {
  const apps: any = {
    'file-manager': defineAsyncComponent(() => import('@/views/FileManager.vue')),
    'editor': defineAsyncComponent(() => import('@/views/Editor.vue')),
    'browser': defineAsyncComponent(() => import('@/views/Browser.vue'))
  };
  return apps[props.window.type];
});
</script>

<style scoped>
.window-container {
  position: fixed;
  top: 0; left: 0;
  width: 800px; height: 500px;
  display: flex; flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
/* 毛玻璃效果 */
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.window-header {
  height: 40px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 15px;
  cursor: default; /* 这里配合 handle 使用 */
}
.window-content {
  flex: 1; overflow: auto;
  background: white;
}
</style>