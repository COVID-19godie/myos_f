<template>
  <div class="settings-app">
    <div class="settings-sidebar">
      <div class="user-profile">
        <el-avatar :size="60" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
        <span class="username">Admin</span>
      </div>
      <div class="menu-list">
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'personalization' }"
          @click="activeTab = 'personalization'"
        >
          <el-icon><Brush /></el-icon> 个性化
        </div>
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'system' }"
          @click="activeTab = 'system'"
        >
          <el-icon><Monitor /></el-icon> 系统信息
        </div>
      </div>
    </div>

    <div class="settings-content">
      <div v-if="activeTab === 'personalization'" class="panel">
        <h2>背景壁纸</h2>
        <div class="wallpaper-grid">
          <div 
            v-for="wp in wallpapers" 
            :key="wp" 
            class="wp-item"
            :class="{ active: themeStore.wallpaper === wp }"
            :style="{ backgroundImage: `url(${wp})` }"
            @click="themeStore.setWallpaper(wp)"
          ></div>
        </div>

        <el-divider />
        
        <h2>显示模式</h2>
        <div class="theme-toggle">
          <span>暗黑模式</span>
          <el-switch 
            v-model="isDarkModel" 
            @change="themeStore.toggleDark()"
          />
        </div>
      </div>

      <div v-if="activeTab === 'system'" class="panel">
        <h2>关于 MyOS</h2>
        <p>版本: v1.0.0 (Vue 3 + Vite)</p>
        <p>开发者: 你</p>
        <p>核心: Pinia State Management</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useThemeStore } from '@/stores/theme';
import { Brush, Monitor } from '@element-plus/icons-vue';

const themeStore = useThemeStore();
const activeTab = ref('personalization');

// 用于绑定 switch
const isDarkModel = computed({
  get: () => themeStore.isDark,
  set: () => themeStore.toggleDark()
});

// 预设几张好看的壁纸
const wallpapers = [
  'https://images.unsplash.com/photo-1477346611705-65d1883cee1e?q=80&w=2070&auto=format&fit=crop', // 城市
  'https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=2070&auto=format&fit=crop', // 风景
  'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1964&auto=format&fit=crop', // 抽象
  'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop', // 科技
];
</script>

<style scoped>
.settings-app {
  display: flex; height: 100%; background: #f5f7fa; color: #333;
}
.settings-sidebar {
  width: 200px; background: white; border-right: 1px solid #e4e7ed;
  display: flex; flex-direction: column;
}
.user-profile {
  padding: 30px 0; display: flex; flex-direction: column; align-items: center; gap: 10px;
}
.menu-item {
  padding: 12px 20px; cursor: pointer; display: flex; align-items: center; gap: 10px;
  font-size: 14px; color: #606266;
}
.menu-item:hover { background: #f0f2f5; }
.menu-item.active { background: #e6f7ff; color: #409eff; border-right: 3px solid #409eff; }

.settings-content { flex: 1; padding: 30px; overflow-y: auto; }
.panel h2 { margin-top: 0; font-size: 18px; margin-bottom: 20px; }

.wallpaper-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 15px;
}
.wp-item {
  aspect-ratio: 16/10; border-radius: 8px; background-size: cover; cursor: pointer;
  border: 2px solid transparent; transition: all 0.2s;
}
.wp-item:hover { transform: scale(1.05); }
.wp-item.active { border-color: #409eff; box-shadow: 0 0 10px rgba(64,158,255,0.4); }

.theme-toggle {
  display: flex; align-items: center; justify-content: space-between;
  background: white; padding: 15px; border-radius: 8px; border: 1px solid #dcdfe6;
}
</style>