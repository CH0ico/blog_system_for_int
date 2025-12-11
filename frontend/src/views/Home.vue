<template>
  <div class="echo-terminal">
    <!-- CRT 屏幕特效层 -->
    <div class="crt-overlay">
      <div class="scanlines"></div>
      <div class="noise"></div>
    </div>

    <!-- 左侧工业风侧边栏 (模仿 DIRECTORY) -->
    <aside class="echo-sidebar">
      <div class="brand-box">
        <div class="brand-logo">◎</div>
        <div class="brand-text">
          <h1>
            PROJECT <br />
            INSIGHT
          </h1>
          <span class="sub-log">// CLASSIFIED LOG</span>
        </div>
      </div>

      <nav class="nav-directory">
        <div class="dir-header">DIRECTORY</div>

        <div class="nav-item-wrapper" @click="$router.push('/posts')">
          <div class="echo-btn">
            <span class="icon">✎</span>
            BRIEF & STORIES
          </div>
        </div>

        <div class="nav-item-wrapper" @click="$router.push('/register')">
          <div class="echo-btn">
            <span class="icon">👤</span>
            PROTAGONISTS
          </div>
        </div>

        <div v-if="authStore.isAuthenticated" class="nav-item-wrapper">
          <div class="echo-btn active">
            <span class="icon">⦿</span>
            LOGGED IN: USER
          </div>
        </div>
      </nav>

      <!-- 系统配置区 (模仿 SYSTEM CONFIG) -->
      <div class="system-config">
        <div class="config-header">SYSTEM CONFIG</div>
        <div class="config-box">
          <div class="toggle-row">
            <span>🔊 BGM: OFF</span>
          </div>
        </div>
        <div class="config-box active-green">
          <div class="toggle-row">
            <span>📺 CRT: ON</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主内容区 (档案纸风格) -->
    <main class="echo-main-content">
      <!-- 顶部装饰栏 -->
      <div class="top-bar-deco">
        <span class="tag-black">NOVEL ARCHIVE</span>
        <div class="line-fill"></div>
        <span class="rec-date">REC_DATE: 2025-12-12</span>
      </div>

      <!-- 巨大标题 (ECHO LOG 风格) -->
      <header class="echo-header">
        <h1 class="glitch-text" data-text="ECHO: choco">
          ECHO: choco
        </h1>
      </header>

      <!-- 登录者信息条 (黄色胶带风格) -->
      <div class="logger-strip">
        <span class="label"
          >LOGGED BY: {{ authStore.user?.name || "choco" }}</span
        >
        <div class="blinking-cursor"></div>
      </div>

      <!-- 警告区域 (模仿 Societal Impact Report) -->
      <!-- 这里放置你的 NetworkPanel 组件，作为系统状态监控 -->
      <section class="warning-section">
        <div class="hazard-stripe"></div>
        <div class="warning-content">
          <div class="warning-text">
            <h3>SOCIETAL IMPACT REPORT</h3>
          </div>
        </div>
      </section>

      <!-- 主要实体/统计数据 (模仿 ECHO 主要公司实体) -->
      <section class="corporate-section">
        <div class="section-title">
          <span class="icon">💼</span> MAJOR CORPORATE ENTITIES
        </div>

        <div class="entity-grid">
          <!-- 统计卡片 1 -->
          <div class="entity-card">
            <div class="card-head">
              <span>OVERVIEW</span>
              <span class="badge-black">STATS</span>
            </div>
            <div class="card-body">
              <p>Total Archives tracked in system.</p>
              <div class="stat-big">+{{ stats.totalPosts }} FILES</div>
              <div class="stat-row">Running: {{ stats.runningDays }} Days</div>
            </div>
          </div>

          <!-- 统计卡片 2 -->
          <div class="entity-card">
            <div class="card-head">
              <span>SYSTEM CONFIG</span>
              <span class="badge-black">SETTINGS</span>
            </div>
            <div class="card-body">
              <div class="config-grid">
                <div class="config-item">
                  <span class="config-label">BGM:</span>
                  <span class="config-value">OFF</span>
                </div>
                <div class="config-item">
                  <span class="config-label">CRT:</span>
                  <span class="config-value active">ON</span>
                </div>
                <div class="config-item">
                  <span class="config-label">ACCESS:</span>
                  <span class="config-value">RESTRICTED</span>
                </div>
                <div class="config-item">
                  <span class="config-label">VERSION:</span>
                  <span class="config-value">v1.0.0</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 档案记录列表 (模仿 ECHO 日志条目) -->
      <section class="chapters-section">
        <!-- Latest List -->
        <div class="log-entries">
          <div v-for="(post, index) in [...featuredPosts, ...latestPosts]" :key="post.id" class="log-entry">
            <div class="log-header">
              <div class="log-number">0{{ index + 1 }}</div>
              <div class="log-content">
                <h3 class="log-title">{{ post.title }}</h3>
                <p class="log-description">{{ post.excerpt || '无描述' }}</p>
              </div>
              <div class="log-difficulty">阶段 {{ post.difficulty || 1 }}</div>
            </div>
            <div class="log-actions">
              <button class="read-entry-btn" @click="$router.push(`/post/${post.id}`)">
                📖 READ ENTRY
              </button>
            </div>
          </div>
        </div>

        <div v-if="hasMorePosts" class="load-more-btn-wrapper">
          <button
            class="industrial-btn"
            :disabled="loading"
            @click="loadMorePosts"
          >
            [ LOAD_MORE_DATA ]
          </button>
        </div>
      </section>
    </main>
  </div>
  <LittleHelper />
</template>

<script setup>
// 原有的逻辑完全保持不变，确保功能正常
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { usePostsStore } from "@/stores/posts";
import { useSocketStore } from "@/stores/socket";
import PostCard from "@/components/posts/PostCard.vue";
import PostItem from "@/components/posts/PostItem.vue";
import NetworkPanel from "@/components/monitor/NetworkPanel.vue"; // 确保这些组件内部没有写死太强的样式，或者你可以用CSS穿透覆盖
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
@import url("https://fonts.googleapis.com/css2?family=Archivo+Black&family=JetBrains+Mono:wght@400;700&display=swap");

/* =========================================
   PROJECT ECHO / CYBERPUNK INDUSTRIAL STYLE
   ========================================= */

:root {
  --echo-orange: #f7931e; /* Project Echo 主题橙 - 工业风 */
  --echo-yellow: #e6b800; /* 警告黄 - 工业风 */
  --echo-bg: #e6e4d8; /* 档案纸米色 - 工业风 */
  --echo-dark: #111111; /* 墨黑 */
  --echo-border: 4px solid #111; /* 更粗的边框 */
  --echo-shadow: 8px 8px 0px rgba(0, 0, 0, 1); /* 更强的硬阴影 */
  --font-display: "Archivo Black", sans-serif;
  --font-mono: "JetBrains Mono", monospace;
}

/* 全局重置与基础样式 */
.echo-terminal {
  background-color: var(--echo-bg);
  color: var(--echo-dark);
  font-family: var(--font-mono);
  min-height: 100vh;
  display: flex;
  position: relative;
  overflow-x: hidden;
  border: 10px solid var(--echo-dark); /* 工业风外边框 */
  box-sizing: border-box;
}

/* 基础元素 - 工业风样式统一 */
h4 {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--echo-dark);
  background: var(--echo-orange);
  border: 2px solid var(--echo-dark);
  padding: 8px 12px;
  box-shadow: 3px 3px 0 var(--echo-dark);
  display: inline-block;
  margin: 0 0 10px 0;
}

p {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--echo-dark);
  line-height: 1.6;
  background: #f5f5f5;
  padding: 8px;
  border: 1px solid var(--echo-dark);
  box-shadow: 2px 2px 0 var(--echo-dark);
  margin: 0 0 12px 0;
}

/* --- CRT & Noise Effects - 增强工业风效果 --- */
.crt-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.6; /* 增强CRT效果透明度 */
  mix-blend-mode: overlay;
}
.scanlines {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0),
    rgba(255, 255, 255, 0) 50%,
    rgba(0, 0, 0, 0.15) 50%, /* 增强扫描线浓度 */
    rgba(0, 0, 0, 0.15)
  );
  background-size: 100% 4px;
  animation: scanline-move 0.1s linear infinite; /* 扫描线动画效果 */
}

/* 扫描线移动动画 */
@keyframes scanline-move {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 0 4px;
  }
}

.noise {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.1'/%3E%3C/svg%3E"); /* 增强噪点浓度 */
  animation: noise-flicker 0.2s infinite alternate; /* 噪点闪烁效果 */
}

/* 噪点闪烁动画 */
@keyframes noise-flicker {
  0% {
    opacity: 0.08;
  }
  100% {
    opacity: 0.12;
  }
}

/* --- Sidebar (Left Column) --- */
.echo-sidebar {
  width: 320px;
  background-color: #e6e4d8;
  border-right: 4px solid #111;
  display: flex;
  flex-direction: column;
  padding: 0;
  flex-shrink: 0;
  /* 橙色装饰头 */
  border-top: 10px solid var(--echo-orange);
}

/* Brand Logo */
.brand-box {
  background-color: var(--echo-orange);
  padding: 30px 20px;
  display: flex;
  gap: 15px;
  align-items: center;
  border-bottom: 4px solid #111;
}

.brand-logo {
  font-size: 2.5rem;
  font-weight: 900;
}

.brand-text h1 {
  font-family: var(--font-display);
  font-size: 1.8rem;
  line-height: 0.9;
  margin: 0;
  text-transform: uppercase;
}

.sub-log {
  font-size: 0.7rem;
  letter-spacing: 0.2em;
  opacity: 0.7;
}

/* Navigation Directory */
.nav-directory {
  padding: 20px;
  flex-grow: 1;
}

.dir-header {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  margin-bottom: 20px;
  border-bottom: 2px dashed #999;
  padding-bottom: 5px;
}

.nav-item-wrapper {
  margin-bottom: 15px;
}

.echo-btn {
  background: #fff;
  border: 2px solid #111;
  padding: 12px 15px;
  font-weight: 700;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.1);
  transition: all 0.1s;
}

.echo-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0px #111;
  background: var(--echo-yellow);
}

.echo-btn.active {
  background: #111;
  color: #fff;
}

/* System Config (Bottom Left) */
.system-config {
  padding: 20px;
  border-top: 4px solid #111;
  background: #dcdacf;
}

.config-header {
  font-size: 0.7rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.config-box {
  background: #cac8be;
  border: 2px solid #111;
  margin-bottom: 10px;
  padding: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  text-align: center;
}

.config-box.active-green {
  background: #66cc00;
  color: #000;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
}

/* --- Main Content (Right Area) --- */
.echo-main-content {
  flex-grow: 1;
  background-image:
    linear-gradient(#ccc 1px, transparent 1px),
    linear-gradient(90deg, #ccc 1px, transparent 1px);
  background-size: 20px 20px; /* Graph Paper Effect */
  padding: 40px;
  overflow-y: auto;
}

/* Top Decorative Bar */
.top-bar-deco {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.tag-black {
  background: #111;
  color: #fff;
  padding: 4px 10px;
  font-size: 0.75rem;
  font-weight: 700;
}

.line-fill {
  height: 2px;
  background: #111;
  flex-grow: 1;
  margin: 0 10px;
}

.rec-date {
  font-size: 0.8rem;
  font-weight: 700;
}

/* Hero Header */
.echo-header {
  margin-bottom: 20px;
}

.echo-header h1 {
  font-family: var(--font-display);
  font-size: clamp(4rem, 10vw, 8rem);
  line-height: 1;
  color: var(--echo-orange);
  text-transform: uppercase;
  margin: 0;
  /* Complex Shadow for 3D effect */
  text-shadow:
    2px 2px 0 #111,
    -1px -1px 0 #d1660f,
    1px -1px 0 #111,
    -1px 1px 0 #da9740,
    1px 1px 0 #111,
    8px 8px 0px rgba(216, 114, 31, 0.8);
  letter-spacing: -2px;
}

/* Logger Strip */
.logger-strip {
  background: var(--echo-yellow);
  border: 2px solid #111;
  padding: 8px 15px;
  font-weight: 700;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 40px;
  transform: rotate(-1deg); /* Slight skew */
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.2);
}

.blinking-cursor {
  width: 10px;
  height: 10px;
  background: #111;
  animation: blink 1s infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

/* Warning Section */
.warning-section {
  border: var(--echo-border);
  background: var(--echo-yellow);
  position: relative;
  margin-bottom: 50px;
  box-shadow: var(--echo-shadow);
}

.hazard-stripe {
  height: 10px;
  background: repeating-linear-gradient(
    45deg,
    #111,
    #111 10px,
    var(--echo-yellow) 10px,
    var(--echo-yellow) 20px
  );
  border-bottom: 2px solid #111;
}

.warning-content {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.warning-icon {
  font-size: 2.5rem;
}

.warning-text h3 {
  font-family: var(--font-display);
  margin: 0;
  font-size: 1.5rem;
  text-transform: uppercase;
}

.panel-embed {
  padding: 0 20px 20px;
  /* Force override NetworkPanel styles if possible, otherwise rely on the container */
  mix-blend-mode: multiply;
}

/* Major Corporate Entities (Stats) */
.section-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  text-transform: uppercase;
}

.corporate-section {
  margin-bottom: 50px;
  border-top: 4px solid #111;
  border-bottom: 4px solid #111;
  padding: 30px 0;
  background: rgba(255, 255, 255, 0.4);
}

.entity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.entity-card {
  border: 2px solid #111;
  background: #fff;
}

.card-head {
  background: #eee;
  border-bottom: 2px solid #111;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
  font-size: 0.8rem;
}

.badge-black {
  background: #111;
  color: #fff;
  padding: 2px 6px;
  font-size: 0.6rem;
}

.card-body {
  padding: 15px;
}

.card-body p {
  font-size: 0.8rem;
  color: #555;
  margin-bottom: 10px;
}

.stat-big {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--echo-orange);
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tech-tag {
  background: #ddd;
  padding: 2px 6px;
  font-size: 0.7rem;
  border: 1px solid #111;
  cursor: pointer;
}
.tech-tag:hover {
  background: #111;
  color: #fff;
}

.raw-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.raw-list li {
  padding: 4px 0;
  border-bottom: 1px dashed #ccc;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.raw-list li:hover {
  background: yellow;
}

/* System Config Grid */
.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f0f0f0;
  border: 2px solid #111;
}

.config-label {
  font-weight: 700;
  font-size: 0.9rem;
}

.config-value {
  font-weight: 900;
  font-family: var(--font-mono);
}

.config-value.active {
  color: var(--echo-orange);
}

/* Archives (Posts) */
.featured-archives {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.archive-file {
  border: 2px solid #111;
  padding: 5px; /* Double border effect inner gap */
  background: #fff;
  box-shadow: 6px 6px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.archive-file:hover {
  transform: translateY(-4px);
  box-shadow: 8px 8px 0 #111;
}

/* Log Entries (ECHO Style) */
.log-entries {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.log-entry {
  border: 4px solid #111;
  background: #fff;
  box-shadow: 8px 8px 0 rgba(0, 0, 0, 1);
  overflow: hidden;
}

.log-header {
  display: flex;
  align-items: flex-start;
  background: #f0f0f0;
  border-bottom: 2px solid #111;
}

.log-number {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 900;
  color: var(--echo-orange);
  padding: 20px;
  background: #111;
  color: #fff;
  min-width: 80px;
  text-align: center;
  border-right: 4px solid #111;
}

.log-content {
  flex-grow: 1;
  padding: 20px;
}

.log-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  margin: 0 0 10px 0;
  text-transform: uppercase;
}

.log-description {
  font-size: 0.9rem;
  color: #333;
  margin: 0;
}

.log-difficulty {
  font-weight: 900;
  padding: 10px 20px;
  background: #ddd;
  border-left: 2px solid #111;
  align-self: stretch;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 100px;
}

.log-actions {
  padding: 15px 20px;
  background: #f9f9f9;
  border-top: 2px solid #111;
}

.read-entry-btn {
  background: transparent;
  border: 2px solid #111;
  padding: 8px 15px;
  font-family: var(--font-mono);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.1s;
}

.read-entry-btn:hover {
  background: var(--echo-orange);
  color: #fff;
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 1);
  transform: translate(-2px, -2px);
}

/* Load More Button */
.load-more-btn-wrapper {
  text-align: center;
  padding: 20px;
}

.industrial-btn {
  background: transparent;
  border: 2px solid #111;
  padding: 15px 40px;
  font-family: var(--font-mono);
  font-weight: 900;
  text-transform: uppercase;
  font-size: 1.1rem;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.industrial-btn:hover {
  background: #111;
  color: var(--echo-orange);
}

/* --- Responsive --- */
@media (max-width: 900px) {
  .echo-terminal {
    flex-direction: column;
  }

  .echo-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 4px solid #111;
  }

  .echo-main-content {
    padding: 20px;
  }

  .nav-directory {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }

  .system-config {
    display: none;
  }

  .echo-header h1 {
    font-size: 2.5rem;
  }
}
</style>
