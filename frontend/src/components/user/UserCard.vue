<template>
  <div class="user-card">
    <div class="user-header">
      <el-avatar :src="user.avatar" :size="64" class="user-avatar">
        {{ user.nickname?.charAt(0) || user.username?.charAt(0) }}
      </el-avatar>
      <div class="user-info">
        <h3 class="user-name">{{ user.nickname || user.username }}</h3>
        <p v-if="user.bio" class="user-bio">{{ user.bio }}</p>
      </div>
    </div>

    <div class="user-stats">
      <div class="stat-item" @click="goToPosts">
        <span class="stat-value">{{ user.posts_count || 0 }}</span>
        <span class="stat-label">文章</span>
      </div>
      <div class="stat-item" @click="goToFollowers">
        <span class="stat-value">{{ user.followers_count || 0 }}</span>
        <span class="stat-label">粉丝</span>
      </div>
      <div class="stat-item" @click="goToFollowing">
        <span class="stat-value">{{ user.following_count || 0 }}</span>
        <span class="stat-label">关注</span>
      </div>
    </div>

    <div class="user-actions">
      <el-button size="small" @click="$router.push('/profile')">
        个人中心
      </el-button>
      <el-button size="small" type="primary" @click="$router.push('/write')">
        写文章
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

const user = computed(() => authStore.user || {});

const goToPosts = () => {
  // 跳转到用户的文章列表
};

const goToFollowers = () => {
  // 跳转到粉丝列表
};

const goToFollowing = () => {
  // 跳转到关注列表
};
</script>

<style scoped>
.user-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.user-avatar {
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.user-bio {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.stat-item:hover {
  background-color: var(--el-fill-color-light);
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--el-color-primary);
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.user-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}
</style>
