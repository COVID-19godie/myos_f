<template>
  <div class="browser-container">
    <div class="browser-toolbar">
      <div class="nav-actions">
        <button class="tool-btn disabled"><i class="fa-solid fa-arrow-left"></i></button>
        <button class="tool-btn disabled"><i class="fa-solid fa-arrow-right"></i></button>
        <button class="tool-btn" @click="reload"><i class="fa-solid fa-rotate-right"></i></button>
      </div>
      
      <div class="url-bar">
        <i class="fa-solid fa-lock is-secure"></i>
        <input type="text" :value="displayUrl" readonly />
      </div>

      <div class="window-actions">
        <button class="tool-btn" @click="openExternal"><i class="fa-solid fa-up-right-from-square"></i></button>
      </div>
    </div>

    <div class="browser-content">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>正在连接 {{ displayHost }}...</p>
      </div>

      <iframe
        v-if="isMounted"
        ref="iframeRef"
        class="web-view"
        :src="activeSrc"
        frameborder="0"
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals"
        referrerpolicy="no-referrer"
        @load="onLoad"
      ></iframe>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps<{
  url?: string;
}>();

const iframeRef = ref<HTMLIFrameElement>();
const isLoading = ref(true);
const isMounted = ref(false); // 控制延迟加载
const activeSrc = ref(''); // 实际赋给 iframe 的地址

// 1. 处理 URL 显示
const displayUrl = computed(() => props.url || 'about:blank');
const displayHost = computed(() => {
  try {
    return new URL(displayUrl.value).hostname;
  } catch {
    return 'Web Page';
  }
});

// 2. 延迟加载逻辑 (Lazy Load)
onMounted(() => {
  // 延迟 50ms 渲染 iframe，让窗口动画先跑完，避免卡顿
  setTimeout(() => {
    isMounted.value = true;
    // 确保 URL 有协议头
    let target = props.url || '';
    if (target && !target.startsWith('http')) {
      target = 'https://' + target;
    }
    activeSrc.value = target;
  }, 100);
});

// 3. Iframe 加载完成回调
const onLoad = () => {
  // 这里有个坑：跨域 iframe 触发 onload 可能不准，但作为 UI 反馈够用了
  isLoading.value = false;
};

// 4. 刷新功能
const reload = () => {
  if (iframeRef.value) {
    isLoading.value = true;
    // 强制刷新 iframe
    iframeRef.value.src = iframeRef.value.src;
  }
};

// 5. 外部打开
const openExternal = () => {
  window.open(activeSrc.value, '_blank');
};

onUnmounted(() => {
  // 清理工作 (Vue 会自动销毁 DOM，这里主要是清理可能的定时器或事件监听)
  activeSrc.value = '';
});
</script>

<style scoped>
.browser-container {
  display: flex; flex-direction: column; height: 100%;
  background: #fff;
  overflow: hidden; /* 防止 iframe 撑破圆角 */
}

/* 顶部工具栏 - 仿 Chrome/Safari 风格 */
.browser-toolbar {
  height: 40px;
  background: #f3f3f3;
  border-bottom: 1px solid #e0e0e0;
  display: flex; align-items: center;
  padding: 0 10px; gap: 10px;
  flex-shrink: 0;
}

.nav-actions { display: flex; gap: 4px; }
.tool-btn {
  width: 28px; height: 28px;
  border: none; background: transparent;
  border-radius: 4px; color: #5f6368;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.tool-btn:hover { background: #e0e0e0; }
.tool-btn.disabled { opacity: 0.4; cursor: default; }
.tool-btn.disabled:hover { background: transparent; }

.url-bar {
  flex: 1;
  background: #fff;
  border: 1px solid #dfdfdf;
  border-radius: 14px;
  height: 28px;
  display: flex; align-items: center;
  padding: 0 10px;
  font-size: 12px; color: #333;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.is-secure { margin-right: 6px; color: #1a73e8; font-size: 10px; }
.url-bar input {
  border: none; outline: none; width: 100%;
  color: #333; font-family: inherit;
}

/* 内容区 */
.browser-content {
  flex: 1; position: relative;
  background: #fff;
}

.web-view {
  width: 100%; height: 100%;
  display: block;
}

/* 加载状态 */
.loading-state {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: #fff; z-index: 1;
  color: #666; font-size: 14px;
}
.spinner {
  width: 24px; height: 24px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #1a73e8;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>