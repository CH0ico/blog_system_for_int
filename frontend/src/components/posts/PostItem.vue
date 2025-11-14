<template>
  <div class="post-item">
    <!-- 文章封面 -->
    <div class="post-cover" v-if="post.cover" @click="goToPost">
      <img :src="post.cover" :alt="post.title" />
    </div>
    
    <!-- 文章内容 -->
    <div class="post-content">
      <!-- 标题 -->
      <h3 class="post-title" @click="goToPost">
        {{ post.title }}
      </h3>
      
      <!-- 摘要 -->
      <p class="post-summary" v-if="post.summary">
        {{ post.summary }}
      </p>
      
      <!-- 元信息 -->
      <div class="post-meta">
        <div class="meta-left">
          <!-- 作者 -->
          <div class="author-info" @click.stop="goToAuthor">
            <el-avatar
              :src="post.author.avatar"
              :size="20"
              class="author-avatar"
            >
              {{ post.author.nickname?.charAt(0) || post.author.username?.charAt(0) }}
            </el-avatar>
            <span class="author-name">{{ post.author.nickname || post.author.username }}</span>
          </div>
          
          <!-- 时间 -->
          <span class="post-time">{{ formatTime(post.created_at) }}</span>
          
          <!-- 分类 -->
          <el-tag
            v-if="post.categories.length > 0"
            size="small"
            @click.stop="goToCategory(post.categories[0].slug)"
            class="category-tag"
          >
            {{ post.categories[0].name }}
          </el-tag>
        </div>
        
        <!-- 统计数据 -->
        <div class="meta-right">
          <div class="stat-item" @click.stop="handleLike">
            <el-icon :class="{ liked: post.liked }"><StarFilled /></el-icon>
            <span>{{ post.like_count }}</span>
          </div>
          <div class="stat-item" @click.stop="handleFavorite">
            <el-icon :class="{ favorited: post.favorited }"><Collection /></el-icon>
            <span>{{ post.favorite_count }}</span>
          </div>
          <div class="stat-item">
            <el-icon><ChatDotRound /></el-icon>
            <span>{{ post.comment_count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { 
  StarFilled, Collection, ChatDotRound
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { usePostsStore } from '@/stores/posts'
import { formatTime } from '@/utils/formatters'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const postsStore = usePostsStore()

// Props
const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

// 计算属性
const canLike = computed(() => {
  return authStore.isAuthenticated
})

const canFavorite = computed(() => {
  return authStore.isAuthenticated
})

// 方法
const goToPost = () => {
  router.push(`/post/${props.post.id}`)
}

const goToAuthor = () => {
  router.push(`/users/${props.post.author.username}`)
}

const goToCategory = (slug) => {
  router.push(`/categories/${slug}`)
}

const handleLike = async () => {
  if (!canLike.value) {
    toast.info('请先登录')
    return
  }
  
  try {
    await postsStore.likePost(props.post.id)
  } catch (error) {
    console.error('Like post error:', error)
  }
}

const handleFavorite = async () => {
  if (!canFavorite.value) {
    toast.info('请先登录')
    return
  }
  
  try {
    await postsStore.favoritePost(props.post.id)
  } catch (error) {
    console.error('Favorite post error:', error)
  }
}
</script>

<style scoped>
.post-item {
  display: flex;
  gap: 20px;
  padding: 20px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: all 0.3s ease;
}

.post-item:last-child {
  border-bottom: none;
}

.post-item:hover {
  background-color: var(--el-fill-color-light);
  margin: 0 -20px;
  padding: 20px;
  border-radius: 8px;
}

.post-cover {
  flex-shrink: 0;
  width: 120px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
}

.post-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.post-item:hover .post-cover img {
  transform: scale(1.05);
}

.post-content {
  flex: 1;
  min-width: 0;
}

.post-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
  line-height: 1.4;
  cursor: pointer;
  transition: color 0.3s;
}

.post-title:hover {
  color: var(--el-color-primary);
}

.post-summary {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: color 0.3s;
}

.author-info:hover {
  color: var(--el-color-primary);
}

.author-avatar {
  flex-shrink: 0;
}

.author-name {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.post-time {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.category-tag {
  cursor: pointer;
}

.meta-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  cursor: pointer;
  transition: color 0.3s;
}

.stat-item:hover {
  color: var(--el-color-primary);
}

.stat-item .el-icon {
  font-size: 14px;
}

.stat-item .el-icon.liked {
  color: var(--el-color-danger);
}

.stat-item .el-icon.favorited {
  color: var(--el-color-warning);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-item {
    flex-direction: column;
    gap: 12px;
  }
  
  .post-cover {
    width: 100%;
    height: 150px;
  }
  
  .post-title {
    font-size: 1rem;
  }
  
  .post-summary {
    font-size: 13px;
  }
  
  .post-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
  
  .meta-right {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .post-item {
    padding: 16px 0;
  }
  
  .post-item:hover {
    margin: 0 -16px;
    padding: 16px;
  }
  
  .post-cover {
    height: 120px;
  }
  
  .post-title {
    font-size: 0.95rem;
  }
  
  .post-summary {
    font-size: 12px;
  }
  
  .post-meta {
    gap: 4px;
  }
  
  .stat-item {
    font-size: 12px;
  }
  
  .stat-item .el-icon {
    font-size: 12px;
  }
}
</style>