<template>
  <div class="modern-home">
    <!-- 动态背景层 -->
    <div class="ambient-background">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
      <div class="noise-overlay"></div>
    </div>

    <!-- 顶部 Hero 区域：极致的大字排版 -->
    <section v-if="!authStore.isAuthenticated" class="hero-wrapper">
      <div class="hero-container">
        <div class="hero-text-group">
          <h1 class="display-title">
            Share <br />
            <span class="gradient-text">Insights.</span>
          </h1>
          <p class="hero-desc">
            捕捉瞬时的灵感，构建你的知识网络。
            <br />一个纯粹、优雅的写作社区。
          </p>
          
          <div class="hero-btn-group">
            <button class="btn-primary" @click="$router.push('/register')">
              开始创作 <span class="arrow">↗</span>
            </button>
            <button class="btn-text" @click="$router.push('/posts')">
              随便逛逛
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 主布局：非对称栅格 -->
    <div class="layout-container">
      <div class="main-grid">
        
        <!-- 左侧流 -->
        <main class="content-flow">
          <!-- 仪表盘区域 -->
          <div class="glass-panel network-panel-wrapper">
            <div class="panel-label">System Status</div>
            <NetworkPanel />
          </div>

          <!-- 精选文章 (Bento Grid 风格) -->
          <section v-if="featuredPosts.length > 0" class="section-block">
            <div class="section-head">
              <h2>Featured</h2>
              <router-link to="/posts" class="link-hover">View All</router-link>
            </div>
            <div class="featured-grid">
              <!-- 这里假设 PostCard 能自适应父容器高度 -->
              <div 
                v-for="post in featuredPosts" 
                :key="post.id" 
                class="featured-item"
              >
                <PostCard :post="post" :featured="true" />
              </div>
            </div>
          </section>

          <!-- 最新流 -->
          <section class="section-block">
            <div class="section-head">
              <h2>Latest Stories</h2>
            </div>
            <div class="feed-list">
              <div 
                v-for="post in latestPosts" 
                :key="post.id" 
                class="feed-item-wrapper"
              >
                <PostItem :post="post" />
              </div>
            </div>

            <div v-if="hasMorePosts" class="load-more-wrapper">
              <el-button 
                class="minimal-btn" 
                :loading="loading" 
                @click="loadMorePosts"
              >
                Load More
              </el-button>
            </div>
          </section>
        </main>

        <!-- 右侧侧边栏：模块化组件 -->
        <aside class="sidebar-col">
          <div class="sticky-wrapper">
            
            <!-- 用户卡片 -->
            <div v-if="authStore.isAuthenticated" class="widget-box user-widget">
              <UserCard />
            </div>

            <!-- 数据统计 (极简数字) -->
            <div class="widget-box stats-widget">
              <div class="widget-header">Overview</div>
              <div class="stats-matrix">
                <div class="stat-cell">
                  <span class="stat-num">{{ stats.totalPosts }}</span>
                  <span class="stat-meta">Posts</span>
                </div>
                <div class="stat-cell">
                  <span class="stat-num">{{ stats.totalTags }}</span>
                  <span class="stat-meta">Tags</span>
                </div>
                <div class="stat-cell">
                  <span class="stat-num">{{ stats.runningDays }}</span>
                  <span class="stat-meta">Days</span>
                </div>
                <div v-if="onlineCount > 0" class="stat-cell highlight">
                  <span class="stat-num">{{ onlineCount }}</span>
                  <span class="stat-meta">Online</span>
                </div>
              </div>
            </div>

            <!-- 热门文章 (榜单风格) -->
            <div class="widget-box">
              <div class="widget-header">Trending</div>
              <ul class="trend-list">
                <li
                  v-for="(post, index) in hotPosts"
                  :key="post.id"
                  class="trend-item"
                  @click="$router.push(`/post/${post.id}`)"
                >
                  <span class="trend-rank">{{ index + 1 }}</span>
                  <span class="trend-title">{{ post.title }}</span>
                </li>
              </ul>
            </div>

            <!-- 标签 (胶囊风格) -->
            <div v-if="tags.length > 0" class="widget-box">
              <div class="widget-header">Explore</div>
              <div class="tags-flex">
                <span
                  v-for="tag in tags"
                  :key="tag.id"
                  class="tag-pill"
                  @click="$router.push(`/tags/${tag.slug}`)"
                >
                  #{{ tag.name }}
                </span>
              </div>
            </div>

          </div>
        </aside>
      </div>
    </div>
  </div>
  <LittleHelper />
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { usePostsStore } from "@/stores/posts";
import { useSocketStore } from "@/stores/socket";
import PostCard from "@/components/posts/PostCard.vue";
import PostItem from "@/components/posts/PostItem.vue";
import UserCard from "@/components/user/UserCard.vue";
import NetworkPanel from "@/components/monitor/NetworkPanel.vue";
import LittleHelper from "@/components/interactive/LittleHelper.vue";

const authStore = useAuthStore();
const postsStore = usePostsStore();
const socketStore = useSocketStore();

// 状态
const loading = ref(false);
const featuredPosts = ref([]);
const hotPosts = ref([]);
const tags = ref([]);
const stats = ref({
  totalPosts: 0,
  totalTags: 0,
  runningDays: 0,
});

// 计算属性
const latestPosts = computed(() => postsStore.posts);
const hasMorePosts = computed(() => postsStore.hasMorePosts);
const onlineCount = computed(() => socketStore.onlineCount);

// 获取推荐文章
const fetchFeaturedPosts = async () => {
  try {
    const posts = await postsStore.fetchFeaturedPosts({ limit: 3 });
    featuredPosts.value = posts;
  } catch (error) {
    console.error("Failed to fetch featured posts:", error);
  }
};

// 获取热门文章
const fetchHotPosts = async () => {
  try {
    const posts = await postsStore.fetchPopularPosts({
      limit: 5,
      period: "week",
    });
    hotPosts.value = posts;
  } catch (error) {
    console.error("Failed to fetch hot posts:", error);
  }
};

// 获取标签
const fetchTags = async () => {
  try {
    const response = await fetch("/api/posts/tags");
    const data = await response.json();
    tags.value = data.tags || [];
  } catch (error) {
    console.error("Failed to fetch tags:", error);
  }
};

// 计算标签大小 (虽然Template里改用了统一大小的胶囊，但逻辑保留以免报错)
const getTagSize = (postCount) => {
  const minSize = 12;
  const maxSize = 20;
  const validTags = tags.value || [];
  if (validTags.length === 0) return minSize;

  const maxCount = Math.max(...validTags.map((t) => t.post_count || 0), 1);
  const ratio = postCount / maxCount;
  return Math.max(
    minSize,
    Math.min(maxSize, minSize + (maxSize - minSize) * ratio),
  );
};

// 加载更多文章
const loadMorePosts = async () => {
  if (loading.value || !hasMorePosts.value) return;

  loading.value = true;
  try {
    await postsStore.loadMorePosts();
  } catch (error) {
    console.error("Failed to load more posts:", error);
  } finally {
    loading.value = false;
  }
};

// 获取统计信息
const fetchStats = async () => {
  try {
    await postsStore.fetchPosts({ per_page: 1 });
    stats.value.totalPosts = postsStore.pagination.total;
    stats.value.totalTags = (tags.value || []).length;
    const startDate = new Date("2024-01-01");
    const now = new Date();
    const diffTime = Math.abs(now - startDate);
    stats.value.runningDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  } catch (error) {
    console.error("Failed to fetch stats:", error);
  }
};

onMounted(async () => {
  await postsStore.fetchPosts();
  await Promise.all([
    fetchFeaturedPosts(),
    fetchHotPosts(),
    fetchTags(),
    fetchStats(),
  ]);

  if (authStore.isAuthenticated) {
    socketStore.initializeSocket();
  }
});
</script>

<style scoped>
/* =========================================
   DESIGN SYSTEM - MINIMALIST
   ========================================= */
:root {
  --font-display: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --bg-color: #FAFAFA; /* 极淡的灰白，比纯白更护眼 */
  --text-primary: #111111; /* 接近纯黑 */
  --text-secondary: #666666;
  --text-tertiary: #999999;
  --accent-color: #000000; /* 高级感往往来自于纯黑色的点缀 */
  --border-light: rgba(0, 0, 0, 0.06);
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: rgba(255, 255, 255, 0.5);
  --shadow-soft: 0 20px 40px -10px rgba(0, 0, 0, 0.05);
}

.modern-home {
  position: relative;
  min-height: 100vh;
  background-color: var(--bg-color);
  color: var(--text-primary);
  font-family: var(--font-display);
  overflow-x: hidden;
}

/* --- Ambient Background (氛围背景) --- */
.ambient-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.noise-overlay {
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #E0F2FE 0%, transparent 70%);
  top: -100px;
  left: -100px;
  animation: float 20s infinite ease-in-out;
}

.orb-2 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #F3E8FF 0%, transparent 70%);
  bottom: -100px;
  right: -100px;
  animation: float 25s infinite ease-in-out reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 50px); }
}

/* --- Hero Section (大字报风格) --- */
.hero-wrapper {
  position: relative;
  z-index: 1;
  padding: 120px 20px 80px;
  display: flex;
  justify-content: center;
}

.hero-text-group {
  text-align: center;
  max-width: 800px;
}

.display-title {
  font-size: clamp(3rem, 8vw, 6rem); /* 响应式超大字体 */
  font-weight: 800;
  letter-spacing: -0.04em;
  line-height: 0.95;
  margin-bottom: 2rem;
  color: var(--text-primary);
}

.gradient-text {
  background: linear-gradient(120deg, #111, #555);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 1.25rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 3rem;
  font-weight: 400;
}

.hero-btn-group {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.btn-primary {
  background: #111;
  color: #fff;
  border: none;
  padding: 14px 32px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 50px;
  cursor: pointer;
  transition: transform 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  transform: scale(1.05);
}

.btn-text {
  background: transparent;
  border: 1px solid var(--border-light);
  color: var(--text-primary);
  padding: 14px 32px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-text:hover {
  background: #fff;
  border-color: #000;
}

/* --- Layout Grid (主布局) --- */
.layout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 80px;
  position: relative;
  z-index: 2;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 340px; /* 左宽右窄 */
  gap: 60px;
  align-items: start;
}

/* --- Content Flow (左侧内容) --- */
.content-flow {
  display: flex;
  flex-direction: column;
  gap: 60px;
}

.network-panel-wrapper {
  padding: 24px;
  background: #fff;
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
  position: relative;
}

.panel-label {
  position: absolute;
  top: 16px;
  left: 20px;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-tertiary);
  font-weight: 600;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.section-head h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.02em;
}

.link-hover {
  font-size: 0.9rem;
  color: var(--text-secondary);
  text-decoration: none;
  position: relative;
}

.link-hover::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 1px;
  background: currentColor;
  transition: width 0.3s;
}

.link-hover:hover::after {
  width: 100%;
}

/* Featured Posts Grid */
.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.featured-item {
  transition: transform 0.3s ease;
}

.featured-item:hover {
  transform: translateY(-4px);
}

/* Latest Feed */
.feed-list {
  display: flex;
  flex-direction: column;
  gap: 0; /* 紧凑列表 */
}

.feed-item-wrapper {
  padding: 24px 0;
  border-bottom: 1px solid var(--border-light);
  transition: background 0.2s;
}

.feed-item-wrapper:first-child {
  padding-top: 0;
}

.load-more-wrapper {
  margin-top: 40px;
  text-align: center;
}

.minimal-btn {
  background: transparent;
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  padding: 10px 24px;
  border-radius: 4px;
  letter-spacing: 0.05em;
  font-size: 0.85rem;
  text-transform: uppercase;
  transition: all 0.2s;
}

.minimal-btn:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}

/* --- Sidebar (侧边栏) --- */
.sidebar-col {
  height: 100%;
}

.sticky-wrapper {
  position: sticky;
  top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.widget-box {
  background: transparent;
}

.widget-header {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-tertiary);
  margin-bottom: 16px;
  font-weight: 700;
}

/* 统计矩阵 */
.stats-matrix {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-cell {
  background: #fff;
  padding: 16px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  transition: transform 0.2s;
}

.stat-cell:hover {
  transform: translateY(-2px);
}

.stat-cell.highlight {
  background: #111;
}

.stat-cell.highlight .stat-num,
.stat-cell.highlight .stat-meta {
  color: #fff;
}

.stat-num {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 6px;
}

.stat-meta {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

/* 趋势列表 */
.trend-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.trend-item {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 10px 0;
  cursor: pointer;
  border-bottom: 1px dashed var(--border-light);
  transition: opacity 0.2s;
}

.trend-item:hover {
  opacity: 0.7;
}

.trend-rank {
  font-family: 'Times New Roman', serif;
  font-style: italic;
  font-size: 1.2rem;
  color: var(--text-tertiary);
  width: 20px;
}

.trend-title {
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.4;
}

/* 标签云 */
.tags-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-pill {
  font-size: 0.85rem;
  padding: 6px 14px;
  background: #fff;
  border: 1px solid var(--border-light);
  border-radius: 100px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tag-pill:hover {
  background: #111;
  color: #fff;
  border-color: #111;
}

/* --- Responsive --- */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
  
  .hero-wrapper {
    padding-top: 80px;
  }

  .display-title {
    font-size: 3.5rem;
  }
  
  .sticky-wrapper {
    position: static;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

@media (max-width: 600px) {
  .display-title {
    font-size: 2.5rem;
  }
  
  .hero-desc {
    font-size: 1rem;
  }
  
  .sticky-wrapper {
    grid-template-columns: 1fr;
  }
  
  .btn-primary, .btn-text {
    width: 100%;
    justify-content: center;
  }
  
  .hero-btn-group {
    flex-direction: column;
    width: 100%;
  }
}
</style>