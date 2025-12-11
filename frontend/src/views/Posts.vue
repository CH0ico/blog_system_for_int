<template>
  <div class="cassette-posts-terminal">
    <!-- CRT 屏幕特效层 -->
    <div class="crt-overlay">
      <div class="scanlines"></div>
      <div class="noise"></div>
    </div>

    <div class="posts-directory">
      <!-- 页面标题 -->
      <div class="directory-header">
        <h1>ARCHIVE DIRECTORY</h1>
        <div class="header-actions">
          <button
            v-if="
              authStore.isAuthenticated &&
              authStore.hasPermission('create_posts')
            "
            class="cassette-btn"
            @click="$router.push('/write')"
          >
            <span class="icon">✎</span>
            NEW LOG
          </button>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="filter-console">
        <div class="search-console">
          <input
            v-model="searchQuery"
            placeholder="SEARCH ARCHIVES..."
            class="cassette-search-input"
            @keyup.enter="handleSearch"
          />
          <button class="cassette-btn" @click="handleSearch">
            <span class="icon">🔍</span>
            SEARCH
          </button>
        </div>

        <div class="filter-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.name"
            class="echo-btn"
            :class="{ active: activeTab === tab.name }"
            @click="handleTabChange(tab.name)"
          >
            <span class="icon">{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </div>

        <div class="filter-options">
          <!-- 简化版本，隐藏标签和分类筛选 -->
        </div>
      </div>

      <!-- 文章列表 -->
      <div class="posts-archive">
        <div v-if="loading" class="loading-skeleton">
          <PostSkeleton v-for="i in 6" :key="i" />
        </div>

        <div v-else-if="posts.length > 0" class="archive-files">
          <div v-for="post in posts" :key="post.id" class="file-entry">
            <PostItem :post="post" />
          </div>
        </div>

        <div v-else class="empty-archive">
          <div class="empty-icon">📁</div>
          <div class="empty-text">NO ARCHIVES FOUND</div>
          <div class="empty-subtext">SYSTEM AWAITING INPUT</div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination-console">
        <div class="pagination-info">
          <span
            >ARCHIVES {{ (currentPage - 1) * pageSize + 1 }}-{{
              Math.min(currentPage * pageSize, totalPosts)
            }}
            OF {{ totalPosts }}</span
          >
        </div>
        <div class="pagination-controls">
          <button
            class="cassette-btn"
            :disabled="currentPage <= 1"
            @click="handleCurrentChange(currentPage - 1)"
          >
            <span class="icon">◀</span>
            PREV
          </button>
          <span class="page-indicator"
            >PAGE {{ currentPage }} / {{ totalPages }}</span
          >
          <button
            class="cassette-btn"
            :disabled="currentPage >= totalPages"
            @click="handleCurrentChange(currentPage + 1)"
          >
            NEXT
            <span class="icon">▶</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { usePostsStore } from "@/stores/posts";
import PostItem from "@/components/PostItem.vue";
import PostSkeleton from "@/components/PostSkeleton.vue";
import { ElMessage } from "element-plus";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const postStore = usePostsStore();

// 标签配置
const tabs = [
  { name: "latest", label: "LATEST", icon: "📅" },
  { name: "popular", label: "POPULAR", icon: "🔥" },
  { name: "featured", label: "FEATURED", icon: "⭐" },
];

// 状态
const loading = ref(false);
const searchQuery = ref("");
const activeTab = ref("latest");
const selectedTag = ref("");
const selectedCategory = ref("");
const tags = ref([]);
const categories = ref([]);

// 计算属性
const posts = computed(() => postStore.posts);
const currentPage = computed({
  get: () => postStore.pagination.page,
  set: (val) => {
    handleCurrentChange(val);
  },
});
const pageSize = computed({
  get: () => postStore.pagination.per_page,
  set: (val) => {
    handleSizeChange(val);
  },
});
const totalPosts = computed(() => postStore.pagination.total);
const totalPages = computed(() => postStore.pagination.pages);

// 获取文章列表
const fetchPosts = async (params = {}) => {
  loading.value = true;
  try {
    await postStore.fetchPosts(params);
  } catch (error) {
    ElMessage.error("ARCHIVE RETRIEVAL FAILED");
  } finally {
    loading.value = false;
  }
};

// 获取标签和分类
const fetchTagsAndCategories = async () => {
  try {
    // 简化处理，直接设置空数组
    tags.value = [];
    categories.value = [];
  } catch (error) {
    console.error("FILTER DATA RETRIEVAL FAILED:", error);
  }
};

// 处理搜索
const handleSearch = () => {
  const query = {
    ...route.query,
    page: 1,
  };

  if (searchQuery.value.trim()) {
    query.search = searchQuery.value.trim();
  } else {
    delete query.search;
  }

  router.push({ query });
};

// 处理标签筛选
const handleTagFilter = () => {
  const query = {
    ...route.query,
    page: 1,
  };

  if (selectedTag.value) {
    query.tag = selectedTag.value;
  } else {
    delete query.tag;
  }

  router.push({ query });
};

// 处理分类筛选
const handleCategoryFilter = () => {
  const query = {
    ...route.query,
    page: 1,
  };

  if (selectedCategory.value) {
    query.category = selectedCategory.value;
  } else {
    delete query.category;
  }

  router.push({ query });
};

// 处理标签页切换
const handleTabChange = (tab) => {
  activeTab.value = tab;
  const query = { ...route.query };

  switch (tab) {
    case "latest":
      delete query.sort_by;
      delete query.order;
      break;
    case "popular":
      query.sort_by = "view_count";
      query.order = "desc";
      break;
    case "featured":
      // 推荐文章需要特殊处理
      fetchFeaturedPosts();
      return;
  }

  router.push({ query });
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  const query = {
    ...route.query,
    per_page: size,
    page: 1,
  };
  router.push({ query });
};

// 处理页码变化
const handleCurrentChange = (page) => {
  const query = {
    ...route.query,
    page,
  };
  router.push({ query });
};

// 获取推荐文章
const fetchFeaturedPosts = async () => {
  loading.value = true;
  try {
    await postStore.clearPosts();
    const featuredPosts = await postStore.fetchFeaturedPosts({ limit: 20 });
    // 简化处理，直接使用返回的数据
    if (featuredPosts && featuredPosts.length > 0) {
      postStore.posts = featuredPosts;
      postStore.pagination = {
        page: 1,
        per_page: 20,
        total: featuredPosts.length,
        pages: 1,
      };
    }
  } catch (error) {
    console.error("FEATURED ARCHIVE RETRIEVAL FAILED:", error);
  } finally {
    loading.value = false;
  }
};

// 监听路由变化
watch(
  () => route.query,
  (newQuery) => {
    const params = {
      page: parseInt(newQuery.page) || 1,
      per_page: parseInt(newQuery.per_page) || 10,
      search: newQuery.search || "",
      tag: newQuery.tag || "",
      category: newQuery.category || "",
      sort_by: newQuery.sort_by || "",
      order: newQuery.order || "",
    };

    // 更新筛选状态
    searchQuery.value = params.search;
    selectedTag.value = params.tag;
    selectedCategory.value = params.category;

    // 更新标签页状态
    if (params.sort_by === "view_count") {
      activeTab.value = "popular";
    } else {
      activeTab.value = "latest";
    }

    // 获取文章列表
    if (activeTab.value !== "featured") {
      fetchPosts(params);
    }
  },
  { immediate: true },
);

onMounted(async () => {
  await fetchTagsAndCategories();
});
</script>

<style scoped>
.cassette-posts-terminal {
  position: relative;
  min-height: 100vh;
  background-color: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  overflow: hidden;
}

/* CRT 屏幕特效 */
.crt-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.scanlines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    rgba(21, 21, 21, 0.1) 0px,
    rgba(21, 21, 21, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
  animation: scanlines 8s linear infinite;
}

.noise {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
  animation: noise 0.5s steps(10) infinite;
}

@keyframes scanlines {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(10px);
  }
}

@keyframes noise {
  0%,
  100% {
    transform: translate(0, 0);
  }
  10% {
    transform: translate(-5%, -5%);
  }
  20% {
    transform: translate(-10%, 5%);
  }
  30% {
    transform: translate(5%, -10%);
  }
  40% {
    transform: translate(-5%, 15%);
  }
  50% {
    transform: translate(-10%, 5%);
  }
  60% {
    transform: translate(15%, 0);
  }
  70% {
    transform: translate(0, 10%);
  }
  80% {
    transform: translate(-15%, 0);
  }
  90% {
    transform: translate(10%, 5%);
  }
}

.posts-directory {
  position: relative;
  z-index: 2;
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.directory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 20px;
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
}

.directory-header h1 {
  font-size: 32px;
  font-weight: 900;
  color: var(--color-dark-black);
  text-shadow: 3px 3px 0 var(--color-warning-orange);
  margin: 0;
  letter-spacing: 2px;
}

.filter-console {
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
  padding: 30px;
  margin-bottom: 30px;
}

.search-console {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  align-items: center;
}

.cassette-search-input {
  flex: 1;
  padding: 15px 20px;
  border: 3px solid var(--color-dark-black);
  background: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 2px 2px 0 var(--color-dark-black);
  outline: none;
  transition: all 0.1s ease;
}

.cassette-search-input:focus {
  box-shadow: 4px 4px 0 var(--color-warning-orange);
  transform: translate(-2px, -2px);
}

.cassette-search-input::placeholder {
  color: var(--color-dark-black);
  opacity: 0.6;
}

.filter-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.filter-options {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.cassette-select {
  padding: 12px 20px;
  border: 3px solid var(--color-dark-black);
  background: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 2px 2px 0 var(--color-dark-black);
  outline: none;
  cursor: pointer;
  transition: all 0.1s ease;
}

.cassette-select:focus {
  box-shadow: 4px 4px 0 var(--color-warning-orange);
  transform: translate(-2px, -2px);
}

.posts-archive {
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
  padding: 30px;
  margin-bottom: 30px;
}

.archive-files {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.file-entry {
  border: 2px solid var(--color-dark-black);
  background: var(--color-eggshell);
  box-shadow: 2px 2px 0 var(--color-dark-black);
  transition: all 0.1s ease;
}

.file-entry:hover {
  box-shadow: 4px 4px 0 var(--color-warning-orange);
  transform: translate(-2px, -2px);
}

.loading-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.empty-archive {
  text-align: center;
  padding: 80px 20px;
  border: 3px dashed var(--color-dark-black);
  background: rgba(21, 21, 21, 0.05);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.3;
}

.empty-text {
  font-size: 24px;
  font-weight: 900;
  color: var(--color-dark-black);
  margin-bottom: 10px;
  letter-spacing: 2px;
}

.empty-subtext {
  font-size: 16px;
  color: var(--color-dark-black);
  opacity: 0.6;
  font-family: "Courier New", monospace;
}

.pagination-console {
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.pagination-info {
  font-family: "Courier New", monospace;
  font-weight: 600;
  color: var(--color-dark-black);
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.page-indicator {
  font-family: "Courier New", monospace;
  font-weight: 900;
  color: var(--color-dark-black);
  font-size: 16px;
  letter-spacing: 1px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .directory-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .directory-header h1 {
    font-size: 24px;
  }

  .search-console {
    flex-direction: column;
  }

  .cassette-search-input {
    width: 100%;
  }

  .filter-tabs {
    justify-content: center;
  }

  .filter-options {
    flex-direction: column;
  }

  .cassette-select {
    width: 100%;
  }

  .archive-files,
  .loading-skeleton {
    grid-template-columns: 1fr;
  }

  .pagination-console {
    flex-direction: column;
    text-align: center;
  }

  .pagination-controls {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .posts-directory {
    padding: 20px 15px;
  }

  .filter-console,
  .posts-archive {
    padding: 20px;
  }

  .directory-header h1 {
    font-size: 20px;
  }

  .empty-text {
    font-size: 18px;
  }

  .page-indicator {
    font-size: 14px;
  }
}
</style>
