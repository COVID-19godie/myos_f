<!-- src/views/FileManager.vue -->
<template>
  <div class="file-manager">
    <h2>文件管理器</h2>
    <p>这里是文件管理器的内容...</p>
    <div class="placeholder-content">
      <el-icon size="64"><FolderOpened /></el-icon>
      <p>文件管理功能开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 文件管理器视图组件
</script>

<style scoped>
.file-manager {
  padding: 20px;
  color: var(--os-text-primary);
  height: 100%;
  overflow-y: auto;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--os-text-secondary);
}
</style>