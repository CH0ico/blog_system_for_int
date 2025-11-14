<template>
  <div class="post-card" :class="{ featured: featured }">
    <!-- 文章封面 -->
    <div class="post-cover" v-if="post.cover">
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
          <div class="author-info" @click="goToAuthor">
            <el-avatar
              :src="post.author.avatar"
              :size="24"
              class="author-avatar"
            >
              {{ post.author.nickname?.charAt(0) || post.author.username?.charAt(0) }}
            </el-avatar>
            <span class="author-name">{{ post.author.nickname || post.author.username }}</span>
          </div>
          
          <!-- 时间 -->
          <span class="post-time">{{ formatTime(post.created_at) }}</span>
          
          <!-- 分类和标签 -->
          <div class="post-tags" v-if="post.categories.length > 0 || post.tags.length > 0">
            <el-tag
              v-for="category in post.categories.slice(0, 1)"
              :key="category.id"
              size="small"
              @click.stop="goToCategory(category.slug)"
              class="category-tag"
            >
              {{ category.name }}
            </el-tag>
            
            <el-tag
              v-for="tag in post.tags.slice(0, 2)"
              :key="tag.id"
              size="small"
              type="info"
              @click.stop="goToTag(tag.slug)"
              class="tag-item"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
        
        <!-- 统计数据 -->
        <div class="meta-right">
          <div class="stat-item">
            <el-icon><View /></el-icon>
            <span>{{ post.view_count }}</span>
          </div>
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
    
    <!-- 特色标记 -->
    <div v-if="featured" class="featured-badge">
      <el-icon><Star /></el-icon>
      推荐
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { 
  View, StarFilled, Collection, ChatDotRound, Star
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
  },
  featured: {
    type: Boolean,
    default: false
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

const goToTag = (slug) => {
  router.push(`/tags/${slug}`)
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
.post-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--el-box-shadow);
}

.post-card.featured {
  border-color: var(--el-color-primary);
}

.post-cover {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.post-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.post-card:hover .post-cover img {
  transform: scale(1.05);
}

.post-content {
  padding: 20px;
}

.post-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 12px 0;
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
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
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

.post-tags {
  display: flex;
  gap: 4px;
}

.category-tag {
  cursor: pointer;
}

.tag-item {
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

.featured-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: var(--el-color-primary);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.featured-badge .el-icon {
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-content {
    padding: 16px;
  }
  
  .post-title {
    font-size: 1.1rem;
  }
  
  .post-summary {
    font-size: 13px;
  }
  
  .post-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .meta-left {
    order: 2;
  }
  
  .meta-right {
    order: 1;
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .post-cover {
    height: 150px;
  }
  
  .post-content {
    padding: 12px;
  }
  
  .post-title {
    font-size: 1rem;
    margin-bottom: 8px;
  }
  
  .post-summary {
    font-size: 12px;
    margin-bottom: 12px;
  }
  
  .post-meta {
    gap: 6px;
  }
  
  .stat-item {
    font-size: 12px;
  }
  
  .stat-item .el-icon {
    font-size: 12px;
  }
}
</style>