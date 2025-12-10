<template>
  <el-config-provider :locale="locale">
    <div id="app">
      <AppHeader />

      <main class="main-content">
        <router-view />
      </main>

      <AppFooter />

      <!-- 返回顶部按钮 -->
      <el-backtop :right="100" :bottom="100" />

      <!-- 在线用户计数 -->
      <el-popover
        v-if="onlineCount > 0 && !hideOnlineBadge"
        v-model:visible="showOnlinePopover"
        placement="left-start"
        :width="240"
        trigger="manual"
      >
        <template #default>
          <div ref="onlinePopoverRef" class="online-popover">
            <div class="title">当前在线用户</div>
            <div class="count">
              <el-icon><User /></el-icon><span>{{ onlineCount }}</span>
            </div>
            <div class="actions">
              <el-button size="small" @click="showOnlinePopover = false"
                >关闭</el-button
              >
              <el-button size="small" type="text" @click="hideBadgeForever"
                >不再显示</el-button
              >
            </div>
          </div>
        </template>
        <template #reference>
          <div
            class="online-count"
            @click.stop="showOnlinePopover = !showOnlinePopover"
          >
            <el-badge :value="onlineCount" class="item">
              <el-icon><User /></el-icon>
            </el-badge>
          </div>
        </template>
      </el-popover>

      <!-- 新通知提示 -->
      <div
        v-if="hasNewNotification"
        class="new-notification"
        @click="handleNotificationClick"
      >
        <el-icon><Bell /></el-icon>
        <span>您有新通知</span>
      </div>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { ElConfigProvider } from "element-plus";
import zhCn from "element-plus/dist/locale/zh-cn.mjs";
import { User, Bell } from "@element-plus/icons-vue";

import AppHeader from "@/components/layout/AppHeader.vue";
import AppFooter from "@/components/layout/AppFooter.vue";
import { useAuthStore } from "@/stores/auth";
import { useSocketStore } from "@/stores/socket";
import { useNotificationStore } from "@/stores/notification";

const locale = zhCn;
const authStore = useAuthStore();
const socketStore = useSocketStore();
const notificationStore = useNotificationStore();

const onlineCount = computed(() => socketStore.onlineCount);
const showOnlinePopover = ref(false);
const hideOnlineBadge = ref(false);
const hasNewNotification = computed(() => notificationStore.hasNewNotification);

// 处理通知点击
const handleNotificationClick = () => {
  notificationStore.markNotificationsAsRead();
  // 跳转到通知页面
  // router.push('/notifications')
};

const hideBadgeForever = () => {
  hideOnlineBadge.value = true;
  try {
    localStorage.setItem("hide_online_badge", "1");
  } catch {}
};

onMounted(() => {
  // 组件挂载时初始化
  if (authStore.isAuthenticated) {
    socketStore.initializeSocket();
  }
  try {
    hideOnlineBadge.value = localStorage.getItem("hide_online_badge") === "1";
  } catch {}
});

onUnmounted(() => {
  // 组件卸载时断开Socket连接
  socketStore.disconnectSocket();
});
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 20px 0;
}

.online-count {
  position: fixed;
  right: 30px;
  bottom: 150px;
  z-index: 1000;
  background: var(--el-bg-color);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--el-box-shadow-lighter);
  cursor: pointer;
}

.online-popover .title {
  font-weight: 600;
  margin-bottom: 8px;
}

.online-popover .count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  margin-bottom: 8px;
}

.online-popover .actions {
  display: flex;
  gap: 8px;
}

.new-notification {
  position: fixed;
  top: 100px;
  right: 30px;
  background: var(--el-color-primary);
  color: white;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: var(--el-box-shadow);
  animation: slideInRight 0.3s ease;
  z-index: 1000;
}

.new-notification:hover {
  background: var(--el-color-primary-dark-2);
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial,
    sans-serif;
  line-height: 1.65;
  color: var(--el-text-color-primary);
  background:
    radial-gradient(
      1000px 500px at 10% -10%,
      rgba(64, 158, 255, 0.08),
      transparent 60%
    ),
    radial-gradient(
      800px 400px at 90% -10%,
      rgba(64, 158, 255, 0.06),
      transparent 60%
    ),
    var(--el-bg-color);
}

/* 文章样式 */
.article-content {
  line-height: 1.8;
  font-size: 16px;
  color: var(--el-text-color-primary);
}

.article-content h1,
.article-content h2,
.article-content h3,
.article-content h4,
.article-content h5,
.article-content h6 {
  margin: 24px 0 16px;
  font-weight: 600;
  line-height: 1.25;
}

.article-content h1 {
  font-size: 2em;
  border-bottom: 1px solid var(--el-border-color);
  padding-bottom: 0.3em;
}

.article-content h2 {
  font-size: 1.5em;
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding-bottom: 0.3em;
}

.article-content h3 {
  font-size: 1.25em;
}

.article-content h4 {
  font-size: 1em;
}

.article-content h5 {
  font-size: 0.875em;
}

.article-content h6 {
  font-size: 0.85em;
  color: var(--el-text-color-secondary);
}

.article-content p {
  margin-bottom: 16px;
}

.article-content blockquote {
  padding: 0 1em;
  color: var(--el-text-color-secondary);
  border-left: 0.25em solid var(--el-border-color);
  margin: 0 0 16px;
}

.article-content ul,
.article-content ol {
  margin-bottom: 16px;
  padding-left: 2em;
}

.article-content li {
  margin-bottom: 0.25em;
}

.article-content code {
  background-color: var(--el-fill-color-light);
  border-radius: 3px;
  font-size: 85%;
  margin: 0;
  padding: 0.2em 0.4em;
}

.article-content pre {
  background-color: var(--el-fill-color-lighter);
  border-radius: 6px;
  font-size: 85%;
  line-height: 1.45;
  overflow: auto;
  padding: 16px;
  margin-bottom: 16px;
}

.article-content pre code {
  background-color: transparent;
  border: 0;
  display: inline;
  line-height: inherit;
  margin: 0;
  max-width: auto;
  overflow: visible;
  padding: 0;
  word-wrap: normal;
}

.article-content table {
  border-collapse: collapse;
  margin-bottom: 16px;
  width: 100%;
}

.article-content table th,
.article-content table td {
  border: 1px solid var(--el-border-color);
  padding: 6px 13px;
}

.article-content table th {
  background-color: var(--el-fill-color-light);
  font-weight: 600;
}

.article-content table tr:nth-child(2n) {
  background-color: var(--el-fill-color-lighter);
}

.article-content img {
  max-width: 100%;
  height: auto;
  margin: 16px 0;
  border-radius: 6px;
}

.article-content a {
  color: var(--el-color-primary);
  text-decoration: none;
}

.article-content a:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 10px 0;
  }

  .article-content {
    font-size: 14px;
  }

  .article-content h1 {
    font-size: 1.5em;
  }

  .article-content h2 {
    font-size: 1.25em;
  }

  .article-content h3 {
    font-size: 1.1em;
  }
}
</style>
const onlinePopoverRef = ref(null); onClickOutside(onlinePopoverRef, () => { if
(showOnlinePopover.value) { showOnlinePopover.value = false; } });
