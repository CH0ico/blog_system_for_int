<template>
  <div class="post-item">
    <!-- 文章卡片 -->
    <div class="post-card">
      <!-- 卡片头部 -->
      <div class="post-card-header">
        <div class="post-meta-info">
          <div class="post-date">
            <span class="date-label">LOG DATE:</span>
            <span class="date-value">{{ formatTime(post.created_at) }}</span>
          </div>
          <div class="post-title-section">
            <h3 class="post-title" @click="goToPost">
              {{ post.title }}
            </h3>
            <div class="post-status">
              <span class="status-label">EMOTIONAL STATE:</span>
              <span class="status-value">{{ getEmotionalState(post) }}</span>
            </div>
          </div>
        </div>
        <div class="post-version">
          ECHO V{{ (post.id % 10) + 1 }}.{{ (post.id % 5) + 1 }}
        </div>
      </div>

      <!-- 卡片内容 -->
      <div class="post-card-content">
        <!-- 摘要 -->
        <p v-if="post.summary" class="post-summary">
          {{ post.summary }}
        </p>

        <!-- 封面图 -->
        <div v-if="post.cover" class="post-cover-section">
          <img :src="post.cover" :alt="post.title" class="post-cover" />
        </div>
      </div>

      <!-- 卡片底部 -->
      <div class="post-card-footer">
        <!-- 操作按钮 -->
        <div class="post-actions">
          <button class="action-btn view-btn" @click="goToPost">
            <span class="icon">👁️</span>
            VIEW
          </button>
          <button
            class="action-btn like-btn"
            :class="{ liked: post.liked }"
            @click.stop="handleLike"
          >
            <span class="icon">❤️</span>
            LIKE ({{ post.like_count }})
          </button>
          <button class="action-btn comment-btn" @click="goToPost">
            <span class="icon">💬</span>
            COMMENT ({{ post.comment_count }})
          </button>
        </div>

        <!-- 访问链接 -->
        <div class="post-access">
          <span class="access-label">[ACCESS FILE]</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { StarFilled, Collection, ChatDotRound } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import { usePostsStore } from "@/stores/posts";
import { formatTime } from "@/utils/formatters";

const router = useRouter();
const toast = useToast();
const authStore = useAuthStore();
const postsStore = usePostsStore();

// Props
const props = defineProps({
  post: {
    type: Object,
    required: true,
  },
});

// 计算属性
const canLike = computed(() => {
  return authStore.isAuthenticated;
});

const canFavorite = computed(() => {
  return authStore.isAuthenticated;
});

// 情感状态映射
const emotionalStates = [
  "探索",
  "学习",
  "好奇",
  "认知",
  "连接",
  "理解",
  "成长",
  "觉醒",
  "进化",
  "超越",
];

// 获取情感状态
const getEmotionalState = (post) => {
  const index = post.id % emotionalStates.length;
  return emotionalStates[index];
};

// 方法
const goToPost = () => {
  router.push(`/post/${props.post.id}`);
};

const goToAuthor = () => {
  router.push(`/users/${props.post.author.username}`);
};

const goToCategory = (slug) => {
  router.push(`/categories/${slug}`);
};

const handleLike = async () => {
  if (!canLike.value) {
    toast.info("请先登录");
    return;
  }

  try {
    await postsStore.likePost(props.post.id);
  } catch (error) {
    console.error("Like post error:", error);
  }
};

const handleFavorite = async () => {
  if (!canFavorite.value) {
    toast.info("请先登录");
    return;
  }

  try {
    await postsStore.favoritePost(props.post.id);
  } catch (error) {
    console.error("Favorite post error:", error);
  }
};
</script>

<style scoped>
.post-item {
  width: 100%;
}

/* 文档卡片样式 */
.post-card {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  transition: all 0.3s ease;
  overflow: hidden;
  font-family: "Courier New", monospace;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 6px 6px 0 #e67e22;
}

/* 卡片头部 */
.post-card-header {
  background: #fff9ed;
  padding: 15px 20px;
  border-bottom: 2px solid #2c2c2c;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.post-meta-info {
  flex: 1;
}

.post-date {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.date-label {
  font-size: 12px;
  font-weight: bold;
  color: #e67e22;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.date-value {
  font-size: 12px;
  font-weight: bold;
  color: #2c2c2c;
}

.post-title-section {
  flex: 1;
}

.post-title {
  font-size: 18px;
  font-weight: 900;
  color: #2c2c2c;
  margin: 0 0 8px 0;
  line-height: 1.3;
  cursor: pointer;
  transition: color 0.2s;
}

.post-title:hover {
  color: #e67e22;
}

.post-status {
  display: flex;
  gap: 10px;
  align-items: center;
}

.status-label {
  font-size: 11px;
  font-weight: bold;
  color: #e67e22;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-value {
  font-size: 12px;
  font-weight: bold;
  color: #2c2c2c;
  background: white;
  padding: 3px 8px;
  border: 1px solid #2c2c2c;
  box-shadow: 1px 1px 0 #2c2c2c;
}

.post-version {
  font-size: 12px;
  font-weight: bold;
  color: #e67e22;
  background: white;
  padding: 5px 10px;
  border: 1px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  align-self: center;
}

/* 卡片内容 */
.post-card-content {
  padding: 20px;
  background: white;
}

.post-summary {
  font-size: 14px;
  color: #2c2c2c;
  line-height: 1.6;
  margin: 0 0 15px 0;
  text-align: justify;
}

.post-cover-section {
  margin: 15px 0;
  border: 1px solid #2c2c2c;
  box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.post-cover {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.3s ease;
}

.post-card:hover .post-cover {
  transform: scale(1.02);
}

/* 卡片底部 */
.post-card-footer {
  background: #fff9ed;
  padding: 15px 20px;
  border-top: 2px solid #2c2c2c;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

/* 操作按钮 */
.post-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-btn {
  background: white;
  border: 1px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  padding: 8px 12px;
  font-family: "Courier New", monospace;
  font-size: 11px;
  font-weight: bold;
  color: #2c2c2c;
  cursor: pointer;
  transition: all 0.1s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.action-btn:hover {
  background: #e67e22;
  color: white;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

.action-btn:active {
  box-shadow: 1px 1px 0 #2c2c2c;
  transform: translate(1px, 1px);
}

.action-btn.liked {
  background: #e74c3c;
  color: white;
}

.action-btn.liked:hover {
  background: #c0392b;
}

.action-btn .icon {
  font-size: 12px;
}

/* 访问链接 */
.post-access {
  display: flex;
  align-items: center;
}

.access-label {
  font-size: 12px;
  font-weight: bold;
  color: #2c2c2c;
  border: 1px solid #2c2c2c;
  padding: 5px 10px;
  background: white;
  box-shadow: 2px 2px 0 #e67e22;
  cursor: pointer;
  transition: all 0.2s ease;
}

.access-label:hover {
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .post-actions {
    justify-content: center;
  }

  .post-card-footer {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .access-label {
    text-align: center;
  }
}

@media (max-width: 480px) {
  .post-card-header,
  .post-card-content,
  .post-card-footer {
    padding: 15px;
  }

  .post-title {
    font-size: 16px;
  }

  .post-date,
  .post-status {
    flex-direction: column;
    gap: 5px;
    align-items: flex-start;
  }

  .post-actions {
    justify-content: stretch;
  }

  .action-btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
