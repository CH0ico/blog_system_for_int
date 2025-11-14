<template>
  <div class="home-page">
    <!-- 英雄区域 -->
    <section class="hero-section" v-if="!authStore.isAuthenticated">
      <div class="hero-content">
        <h1 class="hero-title">欢迎来到博客系统</h1>
        <p class="hero-subtitle">分享你的想法，连接更多可能</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/register')">
            开始写作
          </el-button>
          <el-button size="large" @click="$router.push('/posts')">
            浏览文章
          </el-button>
        </div>
      </div>
    </section>
    
    <!-- 主要内容区域 -->
    <div class="main-container">
      <div class="content-wrapper">
        <!-- 左侧内容 -->
        <div class="main-content">
          <!-- 推荐文章 -->
          <section class="featured-posts" v-if="featuredPosts.length > 0">
            <div class="section-header">
              <h2>推荐文章</h2>
              <router-link to="/posts" class="more-link">查看更多</router-link>
            </div>
            <div class="posts-grid">
              <PostCard
                v-for="post in featuredPosts"
                :key="post.id"
                :post="post"
                :featured="true"
              />
            </div>
          </section>
          
          <!-- 最新文章 -->
          <section class="latest-posts">
            <div class="section-header">
              <h2>最新文章</h2>
              <router-link to="/posts" class="more-link">查看更多</router-link>
            </div>
            <div class="posts-list">
              <PostItem
                v-for="post in latestPosts"
                :key="post.id"
                :post="post"
              />
            </div>
            
            <!-- 加载更多 -->
            <div v-if="hasMorePosts" class="load-more">
              <el-button
                :loading="loading"
                @click="loadMorePosts"
              >
                加载更多
              </el-button>
            </div>
          </section>
        </div>
        
        <!-- 右侧边栏 -->
        <aside class="sidebar">
          <!-- 用户信息卡片 -->
          <UserCard v-if="authStore.isAuthenticated" />
          
          <!-- 热门文章 -->
          <section class="sidebar-section">
            <h3>热门文章</h3>
            <div class="hot-posts">
              <div
                v-for="(post, index) in hotPosts"
                :key="post.id"
                class="hot-post-item"
                @click="$router.push(`/post/${post.id}`)"
              >
                <span class="post-rank">{{ index + 1 }}</span>
                <span class="post-title">{{ post.title }}</span>
              </div>
            </div>
          </section>
          
          <!-- 标签云 -->
          <section class="sidebar-section" v-if="tags.length > 0">
            <h3>标签云</h3>
            <div class="tag-cloud">
              <el-tag
                v-for="tag in tags"
                :key="tag.id"
                :style="{ fontSize: getTagSize(tag.post_count) + 'px' }"
                @click="$router.push(`/tags/${tag.slug}`)"
                class="tag-item"
              >
                {{ tag.name }}
              </el-tag>
            </div>
          </section>
          
          <!-- 统计信息 -->
          <section class="sidebar-section">
            <h3>网站统计</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">文章总数</span>
                <span class="stat-value">{{ stats.totalPosts }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">标签数量</span>
                <span class="stat-value">{{ stats.totalTags }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">运行天数</span>
                <span class="stat-value">{{ stats.runningDays }}</span>
              </div>
              <div class="stat-item" v-if="onlineCount > 0">
                <span class="stat-label">在线用户</span>
                <span class="stat-value">{{ onlineCount }}</span>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePostsStore } from '@/stores/posts'
import { useSocketStore } from '@/stores/socket'
import PostCard from '@/components/posts/PostCard.vue'
import PostItem from '@/components/posts/PostItem.vue'
import UserCard from '@/components/user/UserCard.vue'

const authStore = useAuthStore()
const postsStore = usePostsStore()
const socketStore = useSocketStore()

// 状态
const loading = ref(false)
const featuredPosts = ref([])
const hotPosts = ref([])
const tags = ref([])
const stats = ref({
  totalPosts: 0,
  totalTags: 0,
  runningDays: 0
})

// 计算属性
const latestPosts = computed(() => postsStore.posts)
const hasMorePosts = computed(() => postsStore.hasMorePosts)
const onlineCount = computed(() => socketStore.onlineCount)

// 获取推荐文章
const fetchFeaturedPosts = async () => {
  try {
    const posts = await postsStore.fetchFeaturedPosts({ limit: 3 })
    featuredPosts.value = posts
  } catch (error) {
    console.error('Failed to fetch featured posts:', error)
  }
}

// 获取热门文章
const fetchHotPosts = async () => {
  try {
    const posts = await postsStore.fetchPopularPosts({ limit: 5, period: 'week' })
    hotPosts.value = posts
  } catch (error) {
    console.error('Failed to fetch hot posts:', error)
  }
}

// 获取标签
const fetchTags = async () => {
  try {
    const response = await fetch('/api/posts/tags')
    const data = await response.json()
    tags.value = data.tags || []
  } catch (error) {
    console.error('Failed to fetch tags:', error)
  }
}

// 计算标签大小
const getTagSize = (postCount) => {
  const minSize = 12
  const maxSize = 20
  // 确保tags存在且有数据
  const validTags = tags.value || []
  if (validTags.length === 0) return minSize
  
  const maxCount = Math.max(...validTags.map(t => t.post_count || 0), 1)
  const ratio = postCount / maxCount
  return Math.max(minSize, Math.min(maxSize, minSize + (maxSize - minSize) * ratio))
}

// 加载更多文章
const loadMorePosts = async () => {
  if (loading.value || !hasMorePosts.value) return
  
  loading.value = true
  try {
    await postsStore.loadMorePosts()
  } catch (error) {
    console.error('Failed to load more posts:', error)
  } finally {
    loading.value = false
  }
}

// 获取统计信息
const fetchStats = async () => {
  try {
    // 获取文章总数
    await postsStore.fetchPosts({ per_page: 1 })
    stats.value.totalPosts = postsStore.pagination.total
    
    // 获取标签数量 - 确保tags已经加载
    stats.value.totalTags = (tags.value || []).length
    
    // 计算运行天数
    const startDate = new Date('2024-01-01')
    const now = new Date()
    const diffTime = Math.abs(now - startDate)
    stats.value.runningDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

onMounted(async () => {
  // 获取最新文章
  await postsStore.fetchPosts()
  
  // 并行获取其他数据
  await Promise.all([
    fetchFeaturedPosts(),
    fetchHotPosts(),
    fetchTags(),
    fetchStats()
  ])
  
  // 初始化Socket连接
  if (authStore.isAuthenticated) {
    socketStore.initializeSocket()
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
}

/* 英雄区域 */
.hero-section {
  background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #fff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

/* 主要内容区域 */
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 40px;
}

.main-content {
  min-height: 600px;
}

/* 章节样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--el-border-color-lighter);
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0;
}

.more-link {
  color: var(--el-color-primary);
  text-decoration: none;
  font-size: 14px;
}

.more-link:hover {
  text-decoration: underline;
}

/* 文章网格 */
.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.load-more {
  text-align: center;
  margin-top: 24px;
}

/* 侧边栏 */
.sidebar {
  position: sticky;
  top: 100px;
  height: fit-content;
}

.sidebar-section {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.sidebar-section h3 {
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* 热门文章 */
.hot-posts {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hot-post-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  cursor: pointer;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.hot-post-item:hover {
  background-color: var(--el-fill-color-light);
  margin: 0 -20px;
  padding: 8px 20px;
  border-radius: 4px;
}

.hot-post-item:last-child {
  border-bottom: none;
}

.post-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--el-color-primary);
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

.post-title {
  flex: 1;
  font-size: 14px;
  color: var(--el-text-color-primary);
  line-height: 1.4;
}

/* 标签云 */
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
  transition: all 0.3s;
}

.tag-item:hover {
  transform: scale(1.1);
}

/* 统计信息 */
.stats-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.stat-value {
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .sidebar {
    position: static;
    order: -1;
  }
  
  .sidebar-section {
    margin-bottom: 16px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 60px 20px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .main-container {
    padding: 20px 16px;
  }
  
  .posts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .section-header h2 {
    font-size: 1.25rem;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 40px 16px;
  }
  
  .hero-title {
    font-size: 1.5rem;
  }
  
  .main-container {
    padding: 16px;
  }
}
</style>