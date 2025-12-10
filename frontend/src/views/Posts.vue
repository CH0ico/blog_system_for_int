<template>
  <div class="posts-page">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>文章列表</h1>
        <div class="header-actions">
          <el-button
            v-if="
              authStore.isAuthenticated &&
              authStore.hasPermission('create_posts')
            "
            type="primary"
            @click="$router.push('/write')"
          >
            <el-icon><EditPen /></el-icon>
            写文章
          </el-button>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索文章..."
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="filter-tabs">
          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="最新" name="latest" />
            <el-tab-pane label="热门" name="popular" />
            <el-tab-pane label="推荐" name="featured" />
          </el-tabs>
        </div>

        <div class="filter-options">
          <el-select
            v-model="selectedTag"
            placeholder="选择标签"
            clearable
            @change="handleTagFilter"
          >
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.slug"
            />
          </el-select>

          <el-select
            v-model="selectedCategory"
            placeholder="选择分类"
            clearable
            @change="handleCategoryFilter"
          >
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.slug"
            />
          </el-select>
        </div>
      </div>

      <!-- 文章列表 -->
      <div class="posts-container">
        <div v-if="loading" class="loading-skeleton">
          <PostSkeleton v-for="i in 6" :key="i" />
        </div>

        <div v-else-if="posts.length > 0" class="posts-list">
          <PostItem v-for="post in posts" :key="post.id" :post="post" />
        </div>

        <div v-else class="empty-state">
          <el-empty description="暂无文章" />
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalPosts"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { EditPen, Search } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import { usePostsStore } from "@/stores/posts";
import PostItem from "@/components/posts/PostItem.vue";
import PostSkeleton from "@/components/posts/PostSkeleton.vue";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const postsStore = usePostsStore();

// 状态
const loading = ref(false);
const searchQuery = ref("");
const activeTab = ref("latest");
const selectedTag = ref("");
const selectedCategory = ref("");
const tags = ref([]);
const categories = ref([]);

// 计算属性
const posts = computed(() => postsStore.posts);
const currentPage = computed({
  get: () => postsStore.pagination.page,
  set: (val) => {
    handleCurrentChange(val);
  },
});
const pageSize = computed({
  get: () => postsStore.pagination.per_page,
  set: (val) => {
    handleSizeChange(val);
  },
});
const totalPosts = computed(() => postsStore.pagination.total);
const totalPages = computed(() => postsStore.pagination.pages);

// 获取文章列表
const fetchPosts = async (params = {}) => {
  loading.value = true;
  try {
    await postsStore.fetchPosts(params);
  } catch (error) {
    console.error("Failed to fetch posts:", error);
  } finally {
    loading.value = false;
  }
};

// 获取标签和分类
const fetchTagsAndCategories = async () => {
  try {
    const [tagsResponse, categoriesResponse] = await Promise.all([
      fetch("/api/posts/tags"),
      fetch("/api/posts/categories"),
    ]);

    tags.value = (await tagsResponse.json()).tags || [];
    categories.value = (await categoriesResponse.json()).categories || [];
  } catch (error) {
    console.error("Failed to fetch tags and categories:", error);
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
    await postsStore.clearPosts();
    const posts = await postsStore.fetchFeaturedPosts({ limit: 20 });
    postsStore.posts = posts;
    postsStore.pagination = {
      page: 1,
      per_page: 20,
      total: posts.length,
      pages: 1,
    };
  } catch (error) {
    console.error("Failed to fetch featured posts:", error);
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
.posts-page {
  min-height: 100vh;
  padding: 40px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.filter-section {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.search-box {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  max-width: 400px;
}

.filter-tabs {
  margin-bottom: 20px;
}

.filter-options {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.posts-container {
  min-height: 400px;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading-skeleton {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .filter-options {
    flex-direction: column;
  }

  .filter-options .el-select {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 16px;
  }

  .filter-section {
    padding: 16px;
  }
}
</style>
