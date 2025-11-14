<template>
  <div class="post-skeleton">
    <div class="skeleton-header">
      <div class="skeleton-avatar"></div>
      <div class="skeleton-meta">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line medium"></div>
      </div>
    </div>
    
    <div class="skeleton-content">
      <div class="skeleton-line title"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
    </div>
    
    <div class="skeleton-footer">
      <div class="skeleton-stats">
        <div class="skeleton-stat"></div>
        <div class="skeleton-stat"></div>
        <div class="skeleton-stat"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 骨架屏组件，用于加载状态显示
</script>

<style scoped>
.post-skeleton {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  animation: pulse 1.5s ease-in-out infinite;
}

.skeleton-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.skeleton-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--el-fill-color-lighter);
}

.skeleton-meta {
  flex: 1;
}

.skeleton-line {
  height: 14px;
  background: var(--el-fill-color-lighter);
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-line.short {
  width: 30%;
}

.skeleton-line.medium {
  width: 50%;
}

.skeleton-line.title {
  width: 80%;
  height: 18px;
  margin-bottom: 12px;
}

.skeleton-content {
  margin-bottom: 16px;
}

.skeleton-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skeleton-stats {
  display: flex;
  gap: 16px;
}

.skeleton-stat {
  width: 40px;
  height: 14px;
  background: var(--el-fill-color-lighter);
  border-radius: 4px;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}
</style>