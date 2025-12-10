<template>
  <div class="notifications-page">
    <div class="container">
      <div class="page-header">
        <h1>通知中心</h1>
        <div class="header-actions">
          <el-badge
            :value="notificationStore.unreadCount"
            :hidden="notificationStore.unreadCount === 0"
          >
            <el-button
              type="primary"
              :disabled="notificationStore.unreadCount === 0"
              @click="handleMarkAllRead"
            >
              全部标记已读
            </el-button>
          </el-badge>
        </div>
      </div>

      <div v-if="notificationStore.hasNotifications" class="list">
        <div
          v-for="n in notificationStore.notifications"
          :key="n.id"
          class="item"
          :class="{ unread: !n.is_read }"
        >
          <div class="item-main" @click="openNotification(n)">
            <div class="item-title">
              <span class="type">{{
                notificationStore.getNotificationTypeText(n.type)
              }}</span>
              <strong>{{ n.title }}</strong>
            </div>
            <p class="message">{{ n.message }}</p>
            <div class="meta">
              <span class="time">{{
                notificationStore.formatNotificationTime(n.created_at)
              }}</span>
            </div>
          </div>
          <div class="item-actions">
            <el-button
              size="small"
              type="text"
              :disabled="n.is_read"
              @click.stop="handleMarkRead(n)"
              >标记已读</el-button
            >
            <el-button size="small" type="text" @click.stop="handleDelete(n)"
              >删除</el-button
            >
          </div>
        </div>

        <div class="list-footer">
          <el-button
            :loading="notificationStore.loading"
            plain
            @click="loadMore"
            >加载更多</el-button
          >
        </div>
      </div>

      <el-empty v-else description="暂无通知" />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useNotificationStore } from "@/stores/notification";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const notificationStore = useNotificationStore();
const authStore = useAuthStore();

const handleMarkAllRead = async () => {
  await notificationStore.markAllAsRead();
};

const handleMarkRead = async (n) => {
  await notificationStore.markAsRead(n.id);
};

const handleDelete = async (n) => {
  await notificationStore.deleteNotification(n.id);
};

const openNotification = (n) => {
  if (n.post) {
    router.push(`/post/${n.post.id}`);
    return;
  }
  if (n.comment && n.post) {
    router.push(`/post/${n.post.id}`);
    return;
  }
};

const loadMore = async () => {
  // 简单的分页加载，按当前数量计算下一页
  const current = notificationStore.notifications.length;
  const page = Math.floor(current / 20) + 1;
  await notificationStore.fetchNotifications({ page: page + 1, per_page: 20 });
};

onMounted(async () => {
  if (!authStore.isAuthenticated) return;
  await notificationStore.fetchNotifications({ per_page: 20 });
});
</script>

<style scoped>
.notifications-page {
  min-height: 100vh;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-header h1 {
  font-size: 1.6rem;
  font-weight: 700;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  padding: 16px;
}

.item.unread {
  border-color: var(--el-color-primary);
}

.item-main {
  flex: 1;
  cursor: pointer;
}

.item-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 6px;
}

.item-title .type {
  color: var(--el-color-primary);
}

.message {
  margin: 0;
  color: var(--el-text-color-primary);
}

.meta {
  margin-top: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.list-footer {
  text-align: center;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .container {
    padding: 16px;
  }
}
</style>
