<template>
  <div class="search-page">
    <el-container>
      <el-main>
        <div class="search-header">
          <h1 class="search-title">搜索结果</h1>
          <div class="search-input-wrapper">
            <el-input
              v-model="searchQuery"
              placeholder="输入关键词搜索"
              class="search-input"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button type="primary" @click="handleSearch">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
              </template>
            </el-input>
          </div>
        </div>

        <div v-if="loading" class="search-loading">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else-if="searchResults.length > 0" class="search-results">
          <div class="results-count">
            找到 {{ searchResults.length }} 条相关结果
          </div>
          <el-divider />
          <div class="results-list">
            <post-card
              v-for="post in searchResults"
              :key="post.id"
              :post="post"
              class="result-item"
            />
          </div>
        </div>

        <div v-else-if="searchPerformed" class="no-results">
          <el-empty
            description="未找到相关结果"
            :image="Empty"
          >
            <el-button type="primary" @click="handleSearch">
              重新搜索
            </el-button>
          </el-empty>
        </div>

        <div v-else class="search-hint">
          <el-empty
            description="请输入关键词进行搜索"
            :image="Search"
          />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Search, Empty } from '@element-plus/icons-vue';
import PostCard from '@/components/posts/PostCard.vue';
import { usePostsStore } from '@/stores/posts';

const route = useRoute();
const router = useRouter();
const postsStore = usePostsStore();

// 状态
const searchQuery = ref('');
const searchResults = ref([]);
const loading = ref(false);
const searchPerformed = ref(false);

// 处理搜索
const handleSearch = async () => {
  if (!searchQuery.value.trim()) return;

  loading.value = true;
  searchPerformed.value = true;

  try {
    // 调用搜索API
    const results = await postsStore.searchPosts({
      q: searchQuery.value,
      per_page: 20,
      page: 1,
    });
    searchResults.value = results;
  } catch (error) {
    console.error('Search error:', error);
  } finally {
    loading.value = false;
  }
};

// 组件挂载时，如果URL中有搜索参数，则自动搜索
onMounted(() => {
  const query = route.query.q || '';
  if (query) {
    searchQuery.value = query;
    handleSearch();
  }
});
</script>

<style scoped>
.search-page {
  min-height: calc(100vh - var(--header-height) - var(--footer-height));
  padding: 20px 0;
}

.search-header {
  margin-bottom: 30px;
  text-align: center;
}

.search-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin-bottom: 20px;
}

.search-input-wrapper {
  max-width: 600px;
  margin: 0 auto;
}

.search-input {
  --el-input-height: 50px;
  font-size: 16px;
}

.search-loading {
  margin: 20px 0;
}

.search-results {
  margin: 20px 0;
}

.results-count {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 12px;
}

.results-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.result-item {
  transition: transform 0.2s ease;
}

.result-item:hover {
  transform: translateY(-2px);
}

.no-results,
.search-hint {
  margin: 40px 0;
  text-align: center;
}

@media (max-width: 768px) {
  .search-title {
    font-size: 1.5rem;
  }

  .results-list {
    grid-template-columns: 1fr;
  }
}
</style>