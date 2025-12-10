<template>
  <div class="archives-page">
    <div class="container">
      <div class="page-header">
        <h1>文章归档</h1>
        <p>按时间顺序浏览所有文章</p>
      </div>

      <div v-if="loading" class="loading-state">
        <el-loading :loading="true" text="加载中..." />
      </div>

      <div v-else-if="archives.length > 0" class="archives-container">
        <div class="timeline">
          <div
            v-for="(archive, index) in archives"
            :key="archive.id"
            class="timeline-item"
            :class="{
              'timeline-item-left': index % 2 === 0,
              'timeline-item-right': index % 2 === 1,
            }"
          >
            <div class="timeline-marker">
              <el-icon><Document /></el-icon>
            </div>
            <div class="timeline-content">
              <div class="archive-card">
                <div class="archive-date">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDate(archive.date) }}
                </div>
                <h3 class="archive-title">{{ archive.title }}</h3>
                <p class="archive-excerpt">{{ archive.excerpt }}</p>
                <div class="archive-meta">
                  <span class="archive-author">
                    <el-icon><User /></el-icon>
                    {{ archive.author }}
                  </span>
                  <span class="archive-views">
                    <el-icon><View /></el-icon>
                    {{ archive.view_count }}
                  </span>
                </div>
                <div class="archive-actions">
                  <el-button
                    type="primary"
                    size="small"
                    @click="$router.push(`/post/${archive.id}`)"
                  >
                    阅读全文
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载更多 -->
        <div v-if="hasMore" class="load-more">
          <el-button :loading="loadingMore" @click="loadMoreArchives">
            加载更多
          </el-button>
        </div>
      </div>

      <div v-else class="empty-state">
        <el-empty description="暂无归档文章" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Document, Calendar, User, View } from "@element-plus/icons-vue";
import { usePostsStore } from "@/stores/posts";

const postsStore = usePostsStore();

const loading = ref(false);
const loadingMore = ref(false);
const archives = ref([]);
const hasMore = ref(true);
const currentPage = ref(1);
const perPage = ref(10);

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const fetchArchives = async (page = 1, append = false) => {
  if (page === 1) {
    loading.value = true;
  } else {
    loadingMore.value = true;
  }

  try {
    const response = await fetch(
      `/api/posts/archives?page=${page}&per_page=${perPage.value}`,
    );
    const data = await response.json();

    // 确保数据存在且为数组
    const posts = data.posts || [];

    if (append) {
      archives.value.push(...posts);
    } else {
      archives.value = posts;
    }

    hasMore.value = posts.length === perPage.value && data.has_next;
    currentPage.value = page;
  } catch (error) {
    console.error("Failed to fetch archives:", error);
    // 发生错误时清空数据
    if (!append) {
      archives.value = [];
    }
    hasMore.value = false;
  } finally {
    loading.value = false;
    loadingMore.value = false;
  }
};

const loadMoreArchives = () => {
  fetchArchives(currentPage.value + 1, true);
};

onMounted(() => {
  fetchArchives();
});
</script>

<style scoped>
.archives-page {
  min-height: 100vh;
  padding: 40px 0;
  background-color: var(--el-bg-color-page);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-header h1 {
  margin: 0 0 16px 0;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.page-header p {
  margin: 0;
  font-size: 1.1rem;
  color: var(--el-text-color-secondary);
}

.timeline {
  position: relative;
  padding: 20px 0;
}

.timeline::before {
  content: "";
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--el-border-color-lighter);
  transform: translateX(-50%);
}

.timeline-item {
  position: relative;
  margin-bottom: 40px;
  display: flex;
  align-items: center;
}

.timeline-item-left {
  justify-content: flex-start;
}

.timeline-item-right {
  justify-content: flex-end;
}

.timeline-marker {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  background: var(--el-color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 1;
}

.timeline-content {
  width: 45%;
  padding: 0 20px;
}

.timeline-item-left .timeline-content {
  margin-right: 55%;
}

.timeline-item-right .timeline-content {
  margin-left: 55%;
}

.archive-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.archive-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.archive-date {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin-bottom: 12px;
}

.archive-title {
  margin: 0 0 12px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.archive-excerpt {
  margin: 0 0 16px 0;
  color: var(--el-text-color-regular);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.archive-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.archive-author,
.archive-views {
  display: flex;
  align-items: center;
  gap: 4px;
}

.archive-actions {
  display: flex;
  justify-content: flex-end;
}

.load-more {
  text-align: center;
  margin-top: 40px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-skeleton {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (max-width: 768px) {
  .timeline::before {
    left: 20px;
  }

  .timeline-item {
    justify-content: flex-start !important;
  }

  .timeline-marker {
    left: 20px !important;
  }

  .timeline-content {
    width: calc(100% - 60px);
    margin-left: 60px !important;
    margin-right: 0 !important;
  }

  .archive-card {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 2rem;
  }

  .archive-card {
    padding: 16px;
  }

  .archive-meta {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
